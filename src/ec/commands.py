"""云间高速(EC)命令行接口"""

import click
import json
from .client import ECClient


def _get_client(ctx):
    return ECClient(ctx.obj['client'])


@click.group()
def ec():
    """云间高速(EC)管理"""
    pass


@ec.group()
def price():
    """云间高速询价"""
    pass


@price.command('new')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--ec-id', required=True, help='云间高速ID')
@click.option('--bandwidth', required=True, type=int, help='带宽(MB)')
@click.option('--cycle-type', required=True, type=click.Choice(['month', 'year']), help='包周期类型')
@click.option('--cycle-count', required=True, type=int, help='包周期数(最大36个月)')
@click.option('--on-demand', is_flag=True, help='按需下单（默认包周期）')
@click.pass_context
def price_new(ctx, region_id, ec_id, bandwidth, cycle_type, cycle_count, on_demand):
    """云间高速带宽包询价"""
    result = _get_client(ctx).packet_query_price_new(
        region_id, ec_id, bandwidth, cycle_type, cycle_count, on_demand)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@price.command('upgrade')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--ec-id', required=True, help='云间高速ID')
@click.option('--bandwidth', required=True, type=int, help='升配后带宽(MB)')
@click.option('--resource-id', required=True, help='带宽包资源ID')
@click.pass_context
def price_upgrade(ctx, region_id, ec_id, bandwidth, resource_id):
    """云间高速带宽包升配询价"""
    result = _get_client(ctx).packet_query_price_upgrade(
        region_id, ec_id, bandwidth, resource_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@price.command('renew')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--ec-id', required=True, help='云间高速ID')
@click.option('--resource-id', required=True, help='带宽包资源ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month', 'year']), help='包周期类型')
@click.option('--cycle-count', required=True, type=int, help='包周期数(最大36个月)')
@click.pass_context
def price_renew(ctx, region_id, ec_id, resource_id, cycle_type, cycle_count):
    """云间高速带宽包续订询价"""
    result = _get_client(ctx).packet_query_price_renew(
        region_id, ec_id, resource_id, cycle_type, cycle_count)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))
