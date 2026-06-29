"""对象存储(ZOS)命令行接口"""

import click
import sys
from typing import Optional
from utils import OutputFormatter


@click.group()
def zos():
    """对象存储(ZOS)管理"""
    pass


@zos.command('query-price')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--pkg-type', required=True,
              type=click.Choice(['zosSize', 'zosMzSize', 'zosBytesSend',
                                 'zosRequest', 'zosRetrievalFlow', 'zosRetrievalFrequency']),
              help='资源包类型。zosSize=存储空间包, zosMzSize=多AZ存储空间包, '
                   'zosBytesSend=流出流量包, zosRequest=请求次数包, '
                   'zosRetrievalFlow=数据取回流量包, zosRetrievalFrequency=数据取回次数包')
@click.option('--pkg-spec-type', required=True,
              type=click.Choice(['fixed', 'defined']),
              help='资源包规格类型。fixed=固定规格, defined=自定义规格')
@click.option('--pkg-spec', required=True, type=int,
              help='资源包规格大小(GB)，请求次数包和数据取回次数包单位为万次')
@click.option('--cycle-cnt', required=True, type=int,
              help='订购周期 (month:1-36, year:1-3)')
@click.option('--cycle-type', required=True,
              type=click.Choice(['month', 'year']),
              help='订购周期类型 month(月) / year(年)')
@click.option('--order-num', required=True, type=int,
              help='订购数量(最大50)')
@click.option('--storage-class', required=True,
              type=click.Choice(['STANDARD', 'STANDARD_IA', 'GLACIER']),
              help='存储类型。STANDARD=标准存储, STANDARD_IA=低频存储, GLACIER=归档存储')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def query_price(ctx, region_id: str, pkg_type: str, pkg_spec_type: str,
                pkg_spec: int, cycle_cnt: int, cycle_type: str,
                order_num: int, storage_class: str, output: Optional[str]):
    """询价ZOS资源包"""
    from zos.client import ZOSClient

    client = ctx.obj['client']
    zos_client = ZOSClient(client)

    result = zos_client.query_resource_package_price(
        region_id=region_id,
        pkg_type=pkg_type,
        pkg_spec_type=pkg_spec_type,
        pkg_spec=pkg_spec,
        cycle_cnt=cycle_cnt,
        cycle_type=cycle_type,
        order_num=order_num,
        storage_class=storage_class,
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
        if result.get('statusCode') != 800:
            error_msg = result.get('description') or result.get('message', '未知错误')
            click.echo(f"❌ 询价失败: {error_msg}", err=True)
            sys.exit(1)

        return_obj = result.get('returnObj', {}) or {}
        total_price = return_obj.get('totalPrice', '-')
        discount_price = return_obj.get('discountPrice', '-')
        final_price = return_obj.get('finalPrice', '-')
        sub_orders = return_obj.get('subOrderPrices', [])

        pkg_type_names = {
            'zosSize': 'ZOS存储空间包', 'zosMzSize': 'ZOS多AZ存储空间包',
            'zosBytesSend': 'ZOS流出流量包', 'zosRequest': 'ZOS请求次数包',
            'zosRetrievalFlow': 'ZOS数据取回流量包', 'zosRetrievalFrequency': 'ZOS数据取回次数包'
        }

        click.echo("=" * 60)
        click.echo(f"ZOS资源包询价  {pkg_type_names.get(pkg_type, pkg_type)}")
        click.echo("=" * 60)
        click.echo(f"  {'规格':<14}: {pkg_spec} ({pkg_spec_type})")
        click.echo(f"  {'存储类型':<14}: {storage_class}")
        click.echo(f"  {'订购周期':<14}: {cycle_cnt}{cycle_type} x {order_num}")
        click.echo(f"  {'总价 (CNY)':<14}: {total_price}")
        click.echo(f"  {'折后价 (CNY)':<14}: {discount_price}")
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
                               f"套数: {item.get('instanceCnt', '-')}  "
                               f"总价: {item.get('totalPrice', '-')}  "
                               f"最终价: {item.get('finalPrice', '-')} CNY")
