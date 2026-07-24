"""微服务引擎(MSE)命令行接口"""

import click
import json
from .client import MSEClient


def _get_client(ctx):
    return MSEClient(ctx.obj['client'])


@click.group()
def mse():
    """微服务引擎(MSE)管理"""
    pass


@mse.command('create-price')
@click.option('--engine-type', required=True, type=click.Choice(['nacos', 'zookeeper']), help='引擎类型')
@click.option('--cycle-type', required=True, help='订购周期类型（3=按月, 101=按需）')
@click.option('--cycle-cnt', required=True, help='订购周期数')
@click.option('--auto-pay', required=True, type=click.Choice(['true', 'false']), help='预付费自动支付')
@click.option('--auto-renew-cycle-type', required=True, help='自动续订周期类型（3=按月）')
@click.option('--auto-renew-cycle-count', required=True, help='自动续订周期数')
@click.option('--instance-num', required=True, type=int, help='集群数量(3/5/7/9)')
@click.option('--cpu-num', required=True, type=int, help='CPU核数')
@click.option('--auto-renew-status', type=click.Choice(['true', 'false']), help='是否自动续订')
@click.option('--region-id', help='资源池ID（通过header传递）')
@click.pass_context
def mse_create_price(ctx, **kw):
    """订购询价"""
    result = _get_client(ctx).query_create_price(
        auto_pay=kw['auto_pay'], engine_type=kw['engine_type'],
        cycle_type=kw['cycle_type'], cycle_cnt=kw['cycle_cnt'],
        auto_renew_cycle_type=kw['auto_renew_cycle_type'],
        auto_renew_cycle_count=kw['auto_renew_cycle_count'],
        instance_num=kw['instance_num'], cpu_num=kw['cpu_num'],
        region_id=kw.get('region_id'),
        auto_renew_status=kw.get('auto_renew_status'))
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))
