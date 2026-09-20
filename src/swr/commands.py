"""容器镜像服务(SWR)命令行接口"""

import click

from swr.client import SWRClient
from utils import OutputFormatter


def _format_output(data, output_format):
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            raise SystemExit(1)
    else:
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            click.echo(OutputFormatter.format_table(data, headers))
        else:
            click.echo("没有数据")


@click.group()
def swr():
    """容器镜像服务(SWR)管理"""
    pass


@swr.command('list-instances')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-name', help='实例名称（包含匹配）')
@click.option('--all-region', is_flag=True, help='查询所有资源池的实例')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=50, help='每页数量（默认50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_instances(ctx, region_id: str, instance_name: str, all_region: bool,
                   page_num: int, page_size: int, output: str):
    """查询镜像实例列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_instances(
        region_id, instance_name, all_region, page_num, page_size)
    if result.get('statusCode') != 800:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return
    records = (result.get('returnObj') or {}).get('records', [])
    total = (result.get('returnObj') or {}).get('total', len(records))
    if output_format == 'table':
        click.echo(f"SWR实例列表 (共 {total} 个，第 {page_num} 页):")
    _format_output(records, output_format)


@swr.command('list-repositories')
@click.option('--region-id', required=True, help='实例所属资源池ID（取实例列表返回的region）')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--page-num', type=int, default=1, help='页码（默认1）')
@click.option('--page-size', type=int, default=50, help='每页数量（默认50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_repositories(ctx, region_id: str, instance_id: str,
                      page_num: int, page_size: int, output: str):
    """查询镜像仓库列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    result = SWRClient(client).list_repositories(
        region_id, instance_id, page_num, page_size)
    if result.get('statusCode') != 800:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return
    records = (result.get('returnObj') or {}).get('records', [])
    total = (result.get('returnObj') or {}).get('total', len(records))
    if output_format == 'table':
        click.echo(f"SWR镜像仓库列表 (共 {total} 个，第 {page_num} 页):")
    _format_output(records, output_format)
