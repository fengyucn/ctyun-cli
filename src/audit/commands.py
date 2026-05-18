"""
云审计 (Cloud Audit) CLI命令
"""

import json
import sys
from typing import Optional

import click

from core import CTYUNClient
from utils import OutputFormatter

from .client import AuditClient


def format_output(data, output_format='table'):
    """格式化输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("请安装 PyYAML: pip install PyYAML", err=True)
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _get_audit_client(ctx) -> AuditClient:
    """获取 AuditClient 实例"""
    if 'audit_client' not in ctx.obj:
        client: CTYUNClient = ctx.obj['client']
        ctx.obj['audit_client'] = AuditClient(client)
    return ctx.obj['audit_client']


def _display_result(result, output, title="结果"):
    """通用结果显示"""
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj')
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        click.echo(f"{title}")
        click.echo("=" * 60)
        if isinstance(return_obj, list):
            click.echo(f"共 {len(return_obj)} 条记录")
            for i, item in enumerate(return_obj, 1):
                click.echo(f"\n--- #{i} ---")
                if isinstance(item, dict):
                    for k, v in item.items():
                        click.echo(f"  {k}: {v}")
                else:
                    click.echo(f"  {item}")
        elif isinstance(return_obj, dict):
            for k, v in return_obj.items():
                click.echo(f"  {k}: {v}")
        else:
            click.echo(f"  {return_obj}")


# ========== 命令组 ==========

@click.group()
def audit():
    """云审计服务"""
    pass


# ========== 获取云审计支持的资源池列表 ==========

@audit.command('get-available-regions')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_available_regions(ctx, region_id: str, account_id: str,
                           user_id: str, output: Optional[str]):
    """获取云审计支持的资源池列表"""
    client = _get_audit_client(ctx)
    result = client.get_available_regions(
        region_id=region_id, account_id=account_id, user_id=user_id
    )
    _display_result(result, output, "云审计支持的资源池列表")


# ========== 获取用户授权的桶信息 ==========

@audit.command('get-user-authority')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_user_authority(ctx, region_id: str, account_id: str,
                        user_id: str, output: Optional[str]):
    """获取用户授权的桶信息"""
    client = _get_audit_client(ctx)
    result = client.get_user_authority(
        region_id=region_id, account_id=account_id, user_id=user_id
    )
    _display_result(result, output, "用户授权的桶信息")


# ========== 获取服务开通状态 ==========

@audit.command('get-service-status')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_service_status(ctx, region_id: str, account_id: str,
                        user_id: str, output: Optional[str]):
    """获取云审计服务开通状态"""
    client = _get_audit_client(ctx)
    result = client.get_service_enable_status(
        region_id=region_id, account_id=account_id, user_id=user_id
    )
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        if result.get('statusCode') in (0, '0', 800):
            enabled = result.get('returnObj')
            status_text = "✅ 已开通" if enabled else "❌ 未开通"
            click.echo(f"云审计服务开通状态")
            click.echo("=" * 40)
            click.echo(f"  状态: {status_text}")
        else:
            click.echo(f"错误: {result.get('message', '未知错误')}", err=True)


# ========== 获取操作事件存储的资源池信息 ==========

@audit.command('get-storage-region')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_storage_region(ctx, region_id: str, account_id: str,
                        user_id: str, output: Optional[str]):
    """获取操作事件存储的资源池信息"""
    client = _get_audit_client(ctx)
    result = client.get_storage_region_info(
        region_id=region_id, account_id=account_id, user_id=user_id
    )
    _display_result(result, output, "操作事件存储的资源池信息")


# ========== 查询事件列表 ==========

@audit.command('list-events')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--event-act-type', type=int, help='读写类型：0=读, 1=写, -1=全部')
@click.option('--time-label', type=click.Choice(['30M', '1H', '1D', '7D']), help='快捷时间标签')
@click.option('--from-time', help='查询时间段起点，格式: yyyy-MM-dd HH:mm:ss')
@click.option('--to-time', help='查询时间段终点，格式: yyyy-MM-dd HH:mm:ss')
@click.option('--event-level', type=int, help='事件级别：0=normal, 1=warning, 2=incident')
@click.option('--user-id', help='用户唯一标识')
@click.option('--src-service-type', help='事件来源服务名称（计算/存储/网络/安全）')
@click.option('--src-prod-type', help='事件来源的资源类型')
@click.option('--filter-key', type=click.Choice(['-1', 'resName', 'resId', 'eventName']),
              help='筛选类型（需与filter-value同时使用）')
@click.option('--filter-value', help='筛选值（需与filter-key同时使用）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_events(ctx, region_id: str, page: int, page_size: int,
                event_act_type: Optional[int], time_label: Optional[str],
                from_time: Optional[str], to_time: Optional[str],
                event_level: Optional[int], user_id: Optional[str],
                src_service_type: Optional[str], src_prod_type: Optional[str],
                filter_key: Optional[str], filter_value: Optional[str],
                output: Optional[str]):
    """查询审计事件列表"""
    client = _get_audit_client(ctx)
    result = client.list_events(
        region_id=region_id, page_number=page, page_size=page_size,
        event_act_type=event_act_type, time_label=time_label,
        from_time=from_time, to_time=to_time,
        event_level=event_level, user_id=user_id,
        src_service_type=src_service_type, src_prod_type_name=src_prod_type,
        filter_key=filter_key, filter_value=filter_value
    )
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj', {})
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        data = return_obj.get('data', [])
        total = return_obj.get('total', 0)
        click.echo(f"审计事件列表 (共 {total} 条)")
        click.echo("=" * 120)
        if data:
            event_level_map = {0: 'normal', 1: 'warning', 2: 'incident'}
            event_type_map = {0: 'API调用', 1: '控制台操作', 2: '登录登出', 3: '其他'}
            act_type_map = {0: '读', 1: '写'}
            for idx, evt in enumerate(data, 1):
                level = event_level_map.get(evt.get('eventLevel'), 'N/A')
                etype = event_type_map.get(evt.get('eventType'), 'N/A')
                act = act_type_map.get(evt.get('eventActType'), 'N/A')
                click.echo(f"\n{idx}. 事件: {evt.get('eventName', 'N/A')}")
                click.echo(f"   时间: {evt.get('eventTime', 'N/A')} | 级别: {level}")
                click.echo(f"   类型: {etype} ({act})")
                click.echo(f"   来源: {evt.get('srcServiceType', 'N/A')} / {evt.get('srcProdTypeName', 'N/A')}")
                click.echo(f"   资源: {evt.get('srcProdName', 'N/A')} (ID: {evt.get('srcResId', 'N/A')})")
                click.echo(f"   操作者: {evt.get('subUserEmail', evt.get('userId', 'N/A'))}")
                click.echo(f"   源IP: {evt.get('srcIp', 'N/A')}")
        else:
            click.echo("\n无事件数据")


# ========== 查询筛选事件的条件列表 ==========

@audit.command('get-event-selection')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--field-name', required=True,
              type=click.Choice(['eventActType', 'eventLevel', 'userId',
                                 'srcServiceType', 'srcProdTypeName', 'eventName']),
              help='字段名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_event_selection(ctx, region_id: str, account_id: str,
                         user_id: str, field_name: str, output: Optional[str]):
    """查询筛选事件的条件列表"""
    client = _get_audit_client(ctx)
    result = client.get_event_selection(
        region_id=region_id, account_id=account_id,
        user_id=user_id, field_name=field_name
    )
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj', [])
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        click.echo(f"事件筛选条件 ({field_name})")
        click.echo("=" * 60)
        if isinstance(return_obj, list) and return_obj:
            for item in return_obj:
                click.echo(f"  {item.get('code', 'N/A')}: {item.get('value', 'N/A')}")
        else:
            click.echo("  无数据")


# ========== 查询跟踪任务详情 ==========

@audit.command('get-track')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--task-name', required=True, help='跟踪任务名称')
@click.option('--task-id', required=True, help='跟踪任务ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def get_track(ctx, region_id: str, account_id: str, user_id: str,
               task_name: str, task_id: str, output: Optional[str]):
    """查询跟踪任务详情"""
    client = _get_audit_client(ctx)
    result = client.get_audit_track(
        region_id=region_id, account_id=account_id,
        user_id=user_id, task_name=task_name, task_id=task_id
    )
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj', {})
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        state_map = {0: '未启用', 1: '已启用'}
        storage_map = {0: '失败', 1: '成功'}
        click.echo("跟踪任务详情")
        click.echo("=" * 60)
        click.echo(f"  任务名称: {return_obj.get('taskName', 'N/A')}")
        click.echo(f"  任务ID: {return_obj.get('taskId', 'N/A')}")
        rw_type = return_obj.get('rwType', {})
        if isinstance(rw_type, dict):
            click.echo(f"  事件范围: {rw_type.get('value', rw_type.get('code', 'N/A'))}")
        click.echo(f"  启用状态: {state_map.get(return_obj.get('state'), 'N/A')}")
        click.echo(f"  转储桶: {return_obj.get('targetDomain', 'N/A')}")
        click.echo(f"  转储目录: {return_obj.get('targetSpace', 'N/A')}")
        click.echo(f"  转储资源池: {return_obj.get('targetRegion', 'N/A')}")
        click.echo(f"  转储状态: {storage_map.get(return_obj.get('storageState'), 'N/A')}")
        if return_obj.get('errorReason'):
            click.echo(f"  错误原因: {return_obj.get('errorReason')}")
        click.echo(f"  创建时间: {return_obj.get('createTime', 'N/A')}")


# ========== 查询跟踪任务列表 ==========

@audit.command('list-tracks')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--account-id', required=True, help='租户账户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list_tracks(ctx, region_id: str, account_id: str, user_id: str,
                 page: int, page_size: int, output: Optional[str]):
    """查询跟踪任务列表"""
    client = _get_audit_client(ctx)
    result = client.list_audit_tracks(
        region_id=region_id, account_id=account_id,
        user_id=user_id, page_number=page, page_size=page_size
    )
    if result.get('statusCode') not in (0, '0', 800):
        click.echo(f"错误: {result.get('message', '未知错误')}", err=True)
        return
    return_obj = result.get('returnObj', {})
    if output in ('json', 'yaml'):
        format_output(result, output)
    else:
        records = return_obj.get('records', [])
        total = return_obj.get('total', 0)
        state_map = {0: '未启用', 1: '已启用'}
        click.echo(f"跟踪任务列表 (共 {total} 条)")
        click.echo("=" * 80)
        if records:
            for idx, track in enumerate(records, 1):
                click.echo(f"\n{idx}. 任务: {track.get('taskName', 'N/A')}")
                click.echo(f"   ID: {track.get('taskId', 'N/A')}")
                click.echo(f"   状态: {state_map.get(track.get('state'), 'N/A')}")
                click.echo(f"   转储桶: {track.get('targetDomain', 'N/A')}")
                click.echo(f"   转储目录: {track.get('targetSpace', 'N/A')}")
                click.echo(f"   创建时间: {track.get('createTime', 'N/A')}")
        else:
            click.echo("\n无跟踪任务数据")
