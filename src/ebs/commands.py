"""
云硬盘(EBS)命令行接口
"""

import click
from functools import wraps
from typing import Optional
from .client import EBSClient
from utils import OutputFormatter


def handle_error(func):
    """错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import sys
            click.echo(f"错误: {e}", err=True)
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
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            table = OutputFormatter.format_table(data, headers)
            click.echo(table)
        elif isinstance(data, dict):
            headers = ['字段', '值']
            table_data = [[key, value] for key, value in data.items()]
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


@click.group()
def ebs():
    """云硬盘(EBS)管理"""
    pass


@ebs.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页数量，默认10，最大300')
@click.option('--az-name', help='可用区')
@click.option('--project-id', help='企业项目ID')
@click.option('--disk-type', help='云硬盘类型（SATA/SAS/SSD/FAST-SSD）')
@click.option('--disk-mode', help='云硬盘模式（VBD/ISCSI/FCSAN）')
@click.option('--disk-status', help='云硬盘状态（in-use/available等）')
@click.option('--multi-attach', help='是否共享盘（true/false）')
@click.option('--is-system-volume', help='是否系统盘（true/false）')
@click.option('--is-encrypt', help='是否加密盘（true/false）')
@click.option('--query-content', help='模糊查询内容')
@click.option('--query-keys', help='模糊查询键（name,diskID,instanceID,instanceName）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_ebs(ctx, region_id: str, page: int, page_size: int,
             az_name: Optional[str], project_id: Optional[str],
             disk_type: Optional[str], disk_mode: Optional[str],
             disk_status: Optional[str], multi_attach: Optional[str],
             is_system_volume: Optional[str], is_encrypt: Optional[str],
             query_content: Optional[str], query_keys: Optional[str],
             output: Optional[str]):
    """查询云硬盘列表"""
    try:
        client = ctx.obj['client']
        output_format = output or ctx.obj.get('output', 'table')
        
        ebs_client = EBSClient(client)
        result = ebs_client.list_ebs(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            az_name=az_name,
            project_id=project_id,
            disk_type=disk_type,
            disk_mode=disk_mode,
            disk_status=disk_status,
            multi_attach=multi_attach,
            is_system_volume=is_system_volume,
            is_encrypt=is_encrypt,
            query_content=query_content,
            query_keys=query_keys
        )
        
        if result.get('statusCode') != 800:
            error_msg = result.get('message', '未知错误')
            click.echo(f"❌ 查询失败: {error_msg}", err=True)
            import sys
            sys.exit(1)
        
        return_obj = result.get('returnObj', {})
        disk_list = return_obj.get('diskList', [])
        
        if output_format in ['json', 'yaml']:
            format_output(disk_list, output_format)
        else:
            if disk_list:
                from tabulate import tabulate
                from datetime import datetime
                
                table_data = []
                headers = ['云硬盘ID', '名称', '大小(GB)', '类型', '状态', '挂载主机', '创建时间']
                
                for disk in disk_list:
                    disk_id = disk.get('diskID', '')
                    disk_name = disk.get('diskName', '')
                    disk_size = disk.get('diskSize', 0)
                    disk_type = disk.get('diskType', '')
                    disk_status = disk.get('diskStatus', '')
                    instance_name = disk.get('instanceName', '-')
                    
                    create_time = disk.get('createTime', 0)
                    if isinstance(create_time, int) and create_time > 0:
                        try:
                            create_time = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M')
                        except:
                            create_time = str(create_time)
                    else:
                        create_time = '-'
                    
                    table_data.append([
                        disk_id,
                        disk_name,
                        disk_size,
                        disk_type,
                        disk_status,
                        instance_name,
                        create_time
                    ])
                
                total_count = return_obj.get('totalCount', 0)
                current_count = return_obj.get('currentCount', len(disk_list))
                total_page = return_obj.get('totalPage', 1)
                
                click.echo(f"\n云硬盘列表 (总计: {total_count} 个, 当前页: {current_count} 个, 第{page}/{total_page}页)\n")
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
                
                if page < total_page:
                    click.echo(f"\n提示: 使用 --page 参数查看其他页")
            else:
                click.echo("未找到云硬盘")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


# ==================== 新增查询类命令（6个） ====================

@ebs.command('info')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--disk-id', '-d', required=True, help='云硬盘ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def ebs_info(ctx, region_id, disk_id, output):
    """查询云硬盘详情（基于diskID）"""
    client = EBSClient(ctx.obj['client'])
    result = client.get_ebs_info(region_id=region_id, disk_id=disk_id)
    if output == 'json' or result.get('statusCode') != 800:
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {}) or {}
    click.echo(f"云硬盘详情 ({disk_id}):")
    if isinstance(ro, dict):
        for k, v in ro.items():
            click.echo(f"  {k}: {v}")


@ebs.command('info-by-name')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--disk-name', '-n', required=True, help='云硬盘名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def ebs_info_by_name(ctx, region_id, disk_name, output):
    """查询云硬盘详情（基于regionID和diskName）"""
    client = EBSClient(ctx.obj['client'])
    result = client.get_ebs_info_by_name(region_id=region_id, disk_name=disk_name)
    if output == 'json' or result.get('statusCode') != 800:
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {}) or {}
    click.echo(f"云硬盘详情 (name={disk_name}):")
    if isinstance(ro, dict):
        for k, v in ro.items():
            click.echo(f"  {k}: {v}")


@ebs.command('list-by-name')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--disk-name', '-n', required=True, help='云硬盘名称')
@click.option('--page', type=int, default=1, help='页码，默认1')
@click.option('--page-size', type=int, default=10, help='每页大小，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def ebs_list_by_name(ctx, region_id, disk_name, page, page_size, output):
    """查询云硬盘列表（基于regionID和diskName）"""
    client = EBSClient(ctx.obj['client'])
    result = client.list_ebs_by_name(
        region_id=region_id, disk_name=disk_name,
        page_no=page, page_size=page_size)
    if output == 'json' or result.get('statusCode') != 800:
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {}) or {}
    disk_list = ro.get('ebsList', []) or ro.get('diskList', []) or ro.get('list', []) or (ro if isinstance(ro, list) else [])
    click.echo(f"云硬盘列表 (name={disk_name}, 共 {len(disk_list) if isinstance(disk_list, list) else 0} 个)")
    if isinstance(disk_list, list):
        for d in disk_list:
            if isinstance(d, dict):
                click.echo(f"  {d.get('diskID','')} | {d.get('name', d.get('diskName',''))} | {d.get('size','')}GB | {d.get('status','')}")


@ebs.command('snapshots')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--disk-id', '-d', help='云硬盘ID过滤')
@click.option('--snapshot-id', help='快照ID过滤')
@click.option('--snapshot-name', help='快照名称（模糊匹配）')
@click.option('--snapshot-status',
              type=click.Choice(['available', 'freezing', 'creating', 'deleting', 'rollbacking', 'cloning', 'error']),
              help='快照状态过滤')
@click.option('--snapshot-type', type=click.Choice(['manu', 'timer']), help='创建类型：manu 手动 / timer 自动')
@click.option('--volume-attr', type=click.Choice(['data', 'system']), help='云硬盘属性：data 数据盘 / system 系统盘')
@click.option('--retention-policy', type=click.Choice(['forever', 'custom']), help='保留策略')
@click.option('--max-results', type=int, help='期望返回数量（默认10，最大1000）')
@click.option('--next-token', help='接续查询token')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def ebs_snapshots(ctx, region_id, disk_id, snapshot_id, snapshot_name,
                  snapshot_status, snapshot_type, volume_attr,
                  retention_policy, max_results, next_token, output):
    """查询云硬盘快照列表"""
    client = EBSClient(ctx.obj['client'])
    result = client.list_ebs_snapshots(
        region_id=region_id, disk_id=disk_id, snapshot_id=snapshot_id,
        snapshot_name=snapshot_name, snapshot_status=snapshot_status,
        snapshot_type=snapshot_type, volume_attr=volume_attr,
        retention_policy=retention_policy, max_results=max_results,
        next_token=next_token)
    if output == 'json' or result.get('statusCode') != 800:
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {}) or {}
    snap_list = ro.get('snapshotList', []) or ro.get('snapshots', []) or ro.get('list', []) or (ro if isinstance(ro, list) else [])
    click.echo(f"云硬盘快照列表 (共 {len(snap_list) if isinstance(snap_list, list) else 0} 个)")
    if isinstance(snap_list, list):
        for s in snap_list:
            if isinstance(s, dict):
                click.echo(f"  {s.get('snapshotID','')} | {s.get('snapshotName','')} | {s.get('status','')} | {s.get('size','')}GB")


@ebs.command('snapshot-size')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def ebs_snapshot_size(ctx, region_id, output):
    """查询云硬盘快照使用量"""
    client = EBSClient(ctx.obj['client'])
    result = client.query_ebs_snapshot_size(region_id=region_id)
    if output == 'json' or result.get('statusCode') != 800:
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {}) or {}
    click.echo(f"云硬盘快照使用量 ({region_id}):")
    if isinstance(ro, dict):
        for k, v in ro.items():
            click.echo(f"  {k}: {v}")


@ebs.command('snapshot-policy')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--snapshot-policy-id', help='快照策略ID')
@click.option('--snapshot-policy-name', help='快照策略名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def ebs_snapshot_policy(ctx, region_id, snapshot_policy_id, snapshot_policy_name, output):
    """查询云硬盘自动快照策略"""
    client = EBSClient(ctx.obj['client'])
    result = client.query_ebs_snapshot_policy(
        region_id=region_id, snapshot_policy_id=snapshot_policy_id,
        snapshot_policy_name=snapshot_policy_name)
    if output == 'json' or result.get('statusCode') != 800:
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {}) or {}
    policy_list = ro.get('policyList', []) or ro.get('snapshotPolicies', []) or ro.get('list', []) or (ro if isinstance(ro, list) else [])
    if isinstance(policy_list, list) and policy_list:
        click.echo(f"云硬盘自动快照策略列表 (共 {len(policy_list)} 个)")
        for p in policy_list:
            if isinstance(p, dict):
                click.echo(f"  {p.get('snapshotPolicyID','')} | {p.get('snapshotPolicyName','')} | status={p.get('status','')}")
    elif isinstance(ro, dict):
        click.echo(f"云硬盘自动快照策略:")
        for k, v in ro.items():
            click.echo(f"  {k}: {v}")
