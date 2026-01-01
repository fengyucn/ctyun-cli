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


@security.command('tamper-update')
@click.argument('agent_guid')
@click.option('--status', 'secure_status',
              type=click.Choice(['0', '1']),
              required=True,
              help='防护状态: 0=关闭防护, 1=开启防护')
@click.option('--server-name', 'cust_name', help='主机名称')
@click.option('--server-ip', 'server_ip', help='防护服务器IP')
@click.option('--os', type=click.Choice(['Linux', 'Windows']), help='操作系统')
@click.pass_context
@handle_error
def tamper_update(ctx, agent_guid: str, secure_status: str,
                  cust_name: Optional[str], server_ip: Optional[str],
                  os: Optional[str]):
    """
    更新网页防篡改配置（开启/关闭防护状态）

    注意：此功能为收费功能，需要确认已购买网页防篡改配额

    示例：
        # 开启防护
        ctyun-cli security tamper-update <agent_guid> --status 1

        # 关闭防护
        ctyun-cli security tamper-update <agent_guid> --status 0

        # 带服务器信息开启防护
        ctyun-cli security tamper-update <agent_guid> --status 1 \\
            --server-name my-server --server-ip 192.168.1.1 --os Linux
    """
    client = ctx.obj['client']
    security_client = SecurityClient(client)

    # 转换状态为整数
    status_int = int(secure_status)
    status_text = "开启" if status_int == 1 else "关闭"

    click.echo(f"正在{status_text}网页防篡改防护...")
    click.echo(f"Agent GUID: {agent_guid}")

    result = security_client.update_tamper_config(
        agent_guid=agent_guid,
        secure_status=status_int,
        cust_name=cust_name,
        server_ip=server_ip,
        os=os
    )

    # 检查返回结果
    if result.get('statusCode') == '200' and result.get('error') == 'CTCSSCN_000000':
        OutputFormatter.color_print(f"✓ 网页防篡改防护{status_text}成功", 'green')
        click.echo(f"状态码: {result.get('statusCode')}")
        click.echo(f"返回信息: {result.get('message', 'success')}")
        if result.get('traceId'):
            click.echo(f"追踪ID: {result.get('traceId')}")
    else:
        error_msg = result.get('message', '未知错误')
        error_code = result.get('error', result.get('statusCode', 'UNKNOWN'))

        # 错误码说明
        error_desc = {
            'CTCSSCN_000000': '成功',
            'CTCSSCN_000001': '失败',
            'CTCSSCN_000003': '用户未签署协议，安全卫士系统无法正常使用',
            'CTCSSCN_000004': '鉴权错误',
            'CTCSSCN_000005': '用户没有付费版配额，功能不可用'
        }.get(error_code, '')

        OutputFormatter.color_print(f"✗ 网页防篡改防护{status_text}失败", 'red')
        click.echo(f"错误码: {error_code}")
        click.echo(f"错误信息: {error_msg}")
        if error_desc:
            click.echo(f"说明: {error_desc}")

        import sys
        sys.exit(1)


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
    click.echo("8. 开启网页防篡改防护:")
    click.echo("   ctyun_cli security tamper-update <agent_guid> --status 1")
    click.echo()
    click.echo("9. 关闭网页防篡改防护:")
    click.echo("   ctyun_cli security tamper-update <agent_guid> --status 0")
    click.echo()
    click.echo("注意: <agent_guid> 是服务器安全卫士客户端的唯一标识符")
    click.echo("      可以通过天翼云控制台获取")
    click.echo("      网页防篡改为收费功能，使用前请确认已购买相关配额")