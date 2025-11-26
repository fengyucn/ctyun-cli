"""
服务器安全卫士命令行接口
"""

import click
from typing import Optional
from core import CTYUNAPIError
from utils import OutputFormatter, ValidationUtils, logger
from security import SecurityClient


def handle_error(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CTYUNAPIError as e:
            click.echo(f"API错误 [{e.code}]: {e.message}", err=True)
            if e.request_id:
                click.echo(f"请求ID: {e.request_id}", err=True)
            import sys
            sys.exit(1)
        except Exception as e:
            click.echo(f"错误: {e}", err=True)
            import sys
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """格式化输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        # 表格格式
        if isinstance(data, list) and data:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else []
            table = OutputFormatter.format_table(data, headers)
            click.echo(table)
        elif isinstance(data, dict):
            # 单个对象，转换为表格
            headers = ['字段', '值']
            table_data = []
            for key, value in data.items():
                table_data.append([key, value])
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


def format_vulnerability_table(vulnerabilities, output_format='table'):
    """格式化漏洞列表输出"""
    if not vulnerabilities:
        click.echo("没有找到漏洞信息")
        return

    if output_format in ['json', 'yaml']:
        format_output(vulnerabilities, output_format)
        return

    # 表格格式 - 精简显示关键字段
    table_data = []
    headers = ['ID', '漏洞标题', '危险等级', '状态', 'CVE', '发现时间']

    for vuln in vulnerabilities:
        status_map = {0: '未处理', 1: '已处理', 2: '已忽略'}
        level_map = {'LOW': '低', 'MIDDLE': '中', 'HIGH': '高'}

        table_data.append([
            vuln.get('vulAnnouncementId', '')[-12:],  # 取后12位
            vuln.get('vulAnnouncementTitle', '')[:40],  # 截断标题
            level_map.get(vuln.get('fixLevel', ''), vuln.get('fixLevel', '')),
            status_map.get(vuln.get('status', 0), '未知'),
            vuln.get('cve', ''),
            vuln.get('timestamp', '')
        ])

    table = OutputFormatter.format_table(table_data, headers)
    click.echo(table)


@click.group()
def security():
    """服务器安全卫士管理"""
    pass


@security.command()
@click.argument('agent_guid')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--title', help='漏洞名称过滤')
@click.option('--cve', help='CVE编号过滤')
@click.option('--status', 'handle_status',
              type=click.Choice(['HANDLED', 'UN_HANDLED', 'IGNORED']),
              help='处理状态过滤')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
@handle_error
def vuln_list(ctx, agent_guid: str, page: int, page_size: int,
              title: Optional[str], cve: Optional[str],
              handle_status: Optional[str], output: Optional[str]):
    """查询服务器漏洞扫描列表"""
    client = ctx.obj['client']
    security_client = SecurityClient(client)

    result = security_client.get_vulnerability_list(
        agent_guid=agent_guid,
        current_page=page,
        page_size=page_size,
        title=title,
        cve=cve,
        handle_status=handle_status
    )

    if result.get('error') != 'CTCSSCN_000000':
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    return_obj = result.get('returnObj', {})
    vulnerabilities = return_obj.get('list', [])

    # 显示分页信息
    total = return_obj.get('total', 0)
    current_page = return_obj.get('pageNum', 1)
    page_size = return_obj.get('pageSize', 10)
    total_pages = return_obj.get('pages', 1)

    if total > 0:
        click.echo(f"漏洞列表 (总计: {total} 条, 第 {current_page}/{total_pages} 页, 每页 {page_size} 条)")
        click.echo("-" * 80)
        format_vulnerability_table(vulnerabilities, output or ctx.obj.get('output', 'table'))

        if total_pages > 1:
            click.echo(f"\n提示: 使用 --page 参数查看其他页的数据")
    else:
        click.echo("没有找到漏洞信息")


@security.command()
@click.argument('agent_guid')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
@handle_error
def summary(ctx, agent_guid: str, output: Optional[str]):
    """获取漏洞统计摘要"""
    client = ctx.obj['client']
    security_client = SecurityClient(client)

    summary = security_client.get_vulnerability_summary(agent_guid)

    if output and output in ['json', 'yaml']:
        format_output(summary, output)
    else:
        click.echo("漏洞统计摘要")
        click.echo("=" * 40)
        click.echo(f"总漏洞数: {summary['total_vulnerabilities']}")
        click.echo(f"高危漏洞: {summary['high_risk']}")
        click.echo(f"中危漏洞: {summary['medium_risk']}")
        click.echo(f"低危漏洞: {summary['low_risk']}")
        click.echo("-" * 40)
        click.echo(f"未处理: {summary['unhandled']}")
        click.echo(f"已处理: {summary['handled']}")
        click.echo(f"已忽略: {summary['ignored']}")
        click.echo(f"需要重启: {summary['reboot_required']}")


@security.command()
@click.argument('agent_guid')
@click.argument('cve')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
@handle_error
def vuln_detail(ctx, agent_guid: str, cve: str, output: Optional[str]):
    """根据CVE编号查询漏洞详情"""
    client = ctx.obj['client']
    security_client = SecurityClient(client)

    vuln = security_client.get_vulnerability_by_cve(agent_guid, cve)

    if not vuln:
        click.echo(f"没有找到CVE编号为 '{cve}' 的漏洞信息")
        return

    format_output(vuln, output or ctx.obj.get('output', 'table'))


@security.command()
@click.argument('agent_guid')
@click.pass_context
@handle_error
def scan(ctx, agent_guid: str):
    """启动漏洞扫描"""
    client = ctx.obj['client']
    security_client = SecurityClient(client)

    result = security_client.scan_vulnerability(agent_guid)

    OutputFormatter.color_print("✓ 漏洞扫描已启动", 'green')
    click.echo(f"任务ID: {result['taskId']}")
    click.echo(f"状态: {result['status']}")
    click.echo(f"说明: {result['message']}")
    click.echo(f"请稍后使用 'ctyun_cli security vuln-list {agent_guid}' 查看扫描结果")


@security.command()
def examples():
    """显示使用示例"""
    click.echo("服务器安全卫士使用示例:")
    click.echo()
    click.echo("1. 查询漏洞列表:")
    click.echo("   ctyun_cli security vuln-list <agent_guid>")
    click.echo()
    click.echo("2. 分页查询漏洞:")
    click.echo("   ctyun_cli security vuln-list <agent_guid> --page 1 --page-size 5")
    click.echo()
    click.echo("3. 按CVE编号查询:")
    click.echo("   ctyun_cli security vuln-list <agent_guid> --cve CVE-2024-20696")
    click.echo()
    click.echo("4. 查询未处理的高危漏洞:")
    click.echo("   ctyun_cli security vuln-list <agent_guid> --status UN_HANDLED")
    click.echo()
    click.echo("5. 获取漏洞统计:")
    click.echo("   ctyun_cli security summary <agent_guid>")
    click.echo()
    click.echo("6. 查询特定漏洞详情:")
    click.echo("   ctyun_cli security vuln-detail <agent_guid> CVE-2024-20696")
    click.echo()
    click.echo("7. 启动漏洞扫描:")
    click.echo("   ctyun_cli security scan <agent_guid>")
    click.echo()
    click.echo("注意: <agent_guid> 是服务器安全卫士客户端的唯一标识符")
    click.echo("      可以通过天翼云控制台获取")