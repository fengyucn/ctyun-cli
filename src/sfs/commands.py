"""弹性文件服务(SFS)命令行接口"""

import click


@click.group()
def sfs():
    """弹性文件服务(SFS)管理"""
    pass
import json as _json
from .client import SFSClient


@sfs.command('create-price')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--order-num', required=True, type=int, help='订购数量(1-50)')
@click.option('--cycle-type', required=True, type=click.Choice(['year','month']), help='订购周期类型')
@click.option('--sfs-size', required=True, type=int, help='文件系统容量(GB 500-32768)')
@click.option('--volume-type', required=True, type=click.Choice(['hdd','nvme']), help='存储类型: hdd标准型/nvme性能型')
@click.option('--cycle-cnt', required=True, type=int, help='订购时长')
@click.pass_context
def sfs_create_price(ctx, region_id, order_num, cycle_type, sfs_size, volume_type, cycle_cnt):
    """订购文件系统询价"""
    result = SFSClient(ctx.obj['client']).create_price(region_id, order_num, cycle_type, sfs_size, volume_type, cycle_cnt)
    click.echo(_json.dumps(result, indent=2, ensure_ascii=False))


@sfs.command('expand-price')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--sfs-uid', required=True, help='文件系统ID')
@click.option('--sfs-size', required=True, type=int, help='扩容后容量(GB)')
@click.pass_context
def sfs_expand_price(ctx, region_id, sfs_uid, sfs_size):
    """扩容文件系统询价"""
    result = SFSClient(ctx.obj['client']).expand_price(region_id, sfs_uid, sfs_size)
    click.echo(_json.dumps(result, indent=2, ensure_ascii=False))


@sfs.command('renew-price')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--sfs-uid', required=True, help='文件系统ID')
@click.option('--cycle-type', required=True, type=click.Choice(['year','month']), help='周期类型')
@click.option('--cycle-cnt', required=True, type=int, help='续订周期数')
@click.pass_context
def sfs_renew_price(ctx, region_id, sfs_uid, cycle_type, cycle_cnt):
    """续订文件系统询价"""
    result = SFSClient(ctx.obj['client']).renew_price(region_id, sfs_uid, cycle_type, cycle_cnt)
    click.echo(_json.dumps(result, indent=2, ensure_ascii=False))
