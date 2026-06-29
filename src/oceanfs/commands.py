"""海量文件服务(OceanFS)命令行接口"""

import click
import sys
from typing import Optional
from utils import OutputFormatter


@click.group()
def oceanfs():
    """海量文件服务(OceanFS)管理"""
    pass


def _display_price_result(result: dict, title: str):
    """统一展示询价结果"""
    if result.get('statusCode') != 800:
        error_msg = result.get('description') or result.get('message', '未知错误')
        click.echo(f"❌ 询价失败: {error_msg}", err=True)
        sys.exit(1)

    return_obj = result.get('returnObj', {}) or {}
    total_price = return_obj.get('totalPrice', '-')
    final_price = return_obj.get('finalPrice', '-')
    sub_orders = return_obj.get('subOrderPrices', [])

    click.echo("=" * 60)
    click.echo(title)
    click.echo("=" * 60)
    click.echo(f"  {'总价 (CNY)':<14}: {total_price}")
    click.echo(f"  {'最终价 (CNY)':<14}: {final_price}")

    if sub_orders:
        click.echo("\n子订单明细:")
        click.echo("-" * 60)
        for sub in sub_orders:
            click.echo(f"  服务标签: {sub.get('serviceTag', '-')}  "
                       f"总价: {sub.get('totalPrice', '-')}  "
                       f"最终价: {sub.get('finalPrice', '-')} CNY")
            for item in sub.get('orderItemPrices', []):
                click.echo(f"    [{item.get('resourceType', '-')}] "
                           f"容量: {item.get('instanceCnt', '-')}GB  "
                           f"总价: {item.get('totalPrice', '-')}  "
                           f"最终价: {item.get('finalPrice', '-')} CNY")


@oceanfs.command('renew-price')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--sfs-uid', required=True, help='文件系统ID')
@click.option('--cycle-type', required=True,
              type=click.Choice(['year', 'month']),
              help='订购周期类型 year(年) / month(月)')
@click.option('--cycle-cnt', required=True, type=int,
              help='周期数量 (year:1-3, month:1-36)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def renew_price(ctx, region_id: str, sfs_uid: str,
                cycle_type: str, cycle_cnt: int, output: Optional[str]):
    """续订文件系统询价"""
    from oceanfs.client import OceanFSClient

    client = ctx.obj['client']
    oceanfs_client = OceanFSClient(client)

    result = oceanfs_client.renew_order_query_prices(
        region_id=region_id, sfs_uid=sfs_uid,
        cycle_type=cycle_type, cycle_cnt=cycle_cnt
    )

    output_format = output or ctx.obj.get('output', 'table')

    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
    else:
        _display_price_result(result, f"续订询价  文件系统: {sfs_uid}  周期: {cycle_cnt}{cycle_type}")


@oceanfs.command('upgrade-price')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--sfs-uid', required=True, help='文件系统ID')
@click.option('--sfs-size', required=True, type=int, help='扩容后的容量大小(GB)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def upgrade_price(ctx, region_id: str, sfs_uid: str,
                  sfs_size: int, output: Optional[str]):
    """扩容文件系统询价"""
    from oceanfs.client import OceanFSClient

    client = ctx.obj['client']
    oceanfs_client = OceanFSClient(client)

    result = oceanfs_client.upgrade_order_query_prices(
        region_id=region_id, sfs_uid=sfs_uid, sfs_size=sfs_size
    )

    output_format = output or ctx.obj.get('output', 'table')

    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
    else:
        _display_price_result(result, f"扩容询价  文件系统: {sfs_uid}  目标容量: {sfs_size}GB")
