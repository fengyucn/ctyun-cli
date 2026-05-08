"""
模型推理服务(AIServer)命令行接口
"""

import click
import json
import sys
from typing import Optional, List

from .client import AIServerClient


@click.group()
def aiserver():
    """模型推理服务(AIServer)管理"""
    pass


# ========== 工具函数 ==========

def _format_output(result, output_format):
    if output_format == 'json':
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        return True
    return False


def _check_result(result):
    if not result or result.get("error"):
        # 有些服务即使成功也返回error字段，以statusCode为准
        sc = result.get("statusCode")
        if sc == 800 or sc == 200:
            return True
        click.echo(f"❌ 请求失败: {result.get('message', '未知错误')}")
        return False
    return True


# ========== 计费查询 ==========

@aiserver.command('billing-models')
@click.option('--product-type', type=click.Choice(['TOKENS_BY_USE', 'TOKENS_QUANTITY', 'TPM']),
              help='产品类型过滤')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']), default='summary')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def billing_models(ctx, product_type, output_format, timeout):
    """计费查询预置模型列表"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📋 查询预置模型列表...")
    result = ac.billing_preset_models(product_type)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    data = result.get("returnObj", [])
    click.echo(f"\n📊 预置模型列表 (共{len(data)}个)")
    click.echo("=" * 80)
    if not data:
        click.echo("📭 无数据")
        return
    for m in data:
        click.echo(f"  • {m.get('modelName', 'N/A')} ({m.get('modelId', 'N/A')})")
        click.echo(f"    类型: {m.get('typeLabelName', 'N/A')} | 系列: {m.get('seriesLabelName', 'N/A')}")


@aiserver.command('billing-product')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']), default='summary')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def billing_product(ctx, model_id, output_format, timeout):
    """获取指定模型的售卖销售品信息"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📋 查询模型销售品: {model_id}")
    result = ac.billing_product_details(model_id)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    obj = result.get("returnObj", {})
    click.echo(f"\n📊 销售品信息")
    click.echo("=" * 60)
    click.echo(f"  标题: {obj.get('title', 'N/A')}")
    click.echo(f"  模型ID: {obj.get('modelId', 'N/A')}")
    for key in ['tokenByUse', 'tokenQuantityInfo', 'tpm']:
        if obj.get(key):
            click.echo(f"  {key}: ✓")


# ========== 订单管理 ==========

@aiserver.command('create-order')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--token-by-use', help='按量销售品配置 (JSON字符串)')
@click.option('--token-quantities', help='Token量包配置 (JSON字符串)')
@click.option('--tpm', help='TPM包配置 (JSON字符串)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']), default='json')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def create_order(ctx, model_id, token_by_use, token_quantities, tpm, output_format, timeout):
    """创建订单（按量/token量包/tpm包）"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📋 创建订单: {model_id}")
    body = {}
    if token_by_use:
        body['tokenByUse'] = json.loads(token_by_use)
    if token_quantities:
        body['tokenQuantities'] = json.loads(token_quantities)
    if tpm:
        body['tpm'] = json.loads(tpm)
    result = ac.create_order(model_id, **body)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('orders')
@click.option('--model-id', help='模型ID')
@click.option('--order-id', help='订单ID')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=10, help='每页大小')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']), default='table')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def orders(ctx, model_id, order_id, page, size, output_format, timeout):
    """分页查询订单"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📋 分页查询订单...")
    result = ac.page_query_orders(model_id, order_id, page, size)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    obj = result.get("returnObj", {})
    data = obj.get("list", [])
    total = obj.get("total", 0)
    click.echo(f"\n📊 订单列表 (共{total}条)")
    click.echo("=" * 120)
    if not data:
        click.echo("📭 无订单")
        return
    for o in data:
        oid = o.get("orderId", "N/A")
        rid = o.get("resourceId", "N/A")
        title = o.get("title", "N/A")
        status = o.get("status", "N/A")
        it_type = o.get("itType", "N/A")
        create = o.get("createTime", "N/A")
        click.echo(f"  • {title}")
        click.echo(f"    订单: {oid} | 资源: {rid}")
        click.echo(f"    状态: {status} | 类型: {it_type} | 创建: {create}")


@aiserver.command('unsubscribe')
@click.option('--resource-id', required=True, help='资源ID')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']), default='summary')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def unsubscribe(ctx, resource_id, output_format, timeout):
    """订单退订（单个）"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📋 退订订单: {resource_id}")
    result = ac.unsubscribe_order(resource_id)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    click.echo("✅ 退订成功")


# ========== 服务组管理 ==========

@aiserver.command('service-groups')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']), default='table')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def service_groups(ctx, user_ids, model_id, output_format, timeout):
    """查询服务组"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📋 查询服务组...")
    result = ac.query_service_group(user_ids.split(','), model_id)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    data = result.get("returnObj", [])
    click.echo(f"\n📊 服务组列表 (共{len(data)}个)")
    click.echo("=" * 80)
    for g in data:
        click.echo(f"  • {g.get('name', 'N/A')} (ID: {g.get('id', 'N/A')})")


@aiserver.command('service-group-models')
@click.option('--app-id', required=True, help='服务组App ID')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']), default='table')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def service_group_models(ctx, app_id, output_format, timeout):
    """查询服务组的模型列表"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📋 查询服务组模型: {app_id}")
    result = ac.query_service_group_models(app_id)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    obj = result.get("returnObj", {})
    click.echo(f"\n📊 服务组详情")
    click.echo("=" * 60)
    click.echo(f"  名称: {obj.get('name', 'N/A')}")
    click.echo(f"  描述: {obj.get('description', 'N/A')}")
    models = obj.get('modelSynDTOList', [])
    click.echo(f"  模型列表 ({len(models)}个):")
    for m in models:
        click.echo(f"    • {m.get('name', 'N/A')} ({m.get('modelId', 'N/A')})")


@aiserver.command('add-service-group')
@click.option('--name', required=True, help='服务组名称')
@click.option('--public-model-ids', required=True, help='模型ID列表，逗号分隔')
@click.option('--app-id', help='服务组App ID（更新时使用）')
@click.option('--description', help='描述')
@click.option('--expire-at', help='过期时间')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']), default='summary')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def add_service_group(ctx, name, public_model_ids, app_id, description, expire_at, output_format, timeout):
    """添加或更新服务组"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📋 {'更新' if app_id else '添加'}服务组: {name}")
    result = ac.add_or_update_service_group(
        name=name, public_model_id_list=public_model_ids.split(','),
        app_id=app_id, description=description, expire_at_str=expire_at
    )
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    obj = result.get("returnObj", {})
    click.echo(f"✅ 成功")
    click.echo(f"  App ID: {obj.get('appId', 'N/A')} | App Key: {obj.get('appKey', 'N/A')}")


@aiserver.command('delete-service-group')
@click.option('--app-id', required=True, help='服务组App ID')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']), default='summary')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def delete_service_group(ctx, app_id, output_format, timeout):
    """删除服务组"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📋 删除服务组: {app_id}")
    result = ac.delete_service_group(app_id)
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    click.echo("✅ 删除成功")


@aiserver.command('models')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']), default='table')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def models(ctx, user_ids, output_format, timeout):
    """查询预置模型和我的模型"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📋 查询模型列表...")
    result = ac.public_and_my_models(user_ids.split(','))
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    data = result.get("returnObj", [])
    click.echo(f"\n📊 模型列表 (共{len(data)}个)")
    click.echo("=" * 80)
    for m in data:
        click.echo(f"  • {m.get('name', 'N/A')} ({m.get('modelId', 'N/A')}) - {m.get('modelType', 'N/A')}")


@aiserver.command('child-accounts')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']), default='table')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def child_accounts(ctx, output_format, timeout):
    """获取可使用的子账号列表"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📋 查询子账号列表...")
    result = ac.list_child_accounts()
    if _format_output(result, output_format):
        return
    if not _check_result(result):
        return
    data = result.get("returnObj", [])
    click.echo(f"\n👤 子账号列表 (共{len(data)}个)")
    click.echo("=" * 60)
    for a in data:
        marker = "👑 " if a.get("isMainAccount") else "  "
        click.echo(f"  {marker}{a.get('userName', 'N/A')} (ID: {a.get('userId', 'N/A')})")


# ========== 服务监控 ==========

def _monitor_command(ctx, region_id, user_ids, model_id, start_time, end_time,
                     type_, application_id, output_format, timeout, label, func):
    """监控命令通用处理"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo(f"📊 查询{label}...")
    result = func(
        user_ids=user_ids.split(','), model_id=model_id,
        start_time=start_time, end_time=end_time, type_=type_,
        application_id=application_id
    )
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-call')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_call(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用次数"""
    _monitor_command(ctx, None, user_ids, model_id, start_time, end_time, type_,
                     application_id, 'json', timeout, '调用次数',
                     lambda **kw: AIServerClient(ctx.obj['client']).report_call(**kw))


@aiserver.command('report-fail')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_fail(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用失败率"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询调用失败率...")
    result = ac.report_fail(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-qps')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_qps(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用QPS"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询QPS...")
    result = ac.report_qps(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-response-time')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_response_time(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用平均响应时延"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询响应时延...")
    result = ac.report_average_response_time(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-first-token')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_first_token(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用首token延迟"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询首token延迟...")
    result = ac.report_first_token_latency(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-non-first-token')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_non_first_token(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用非首token时延"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询非首token时延...")
    result = ac.report_non_first_token_latency(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-talk-time')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_talk_time(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """模型调用整句Token时延"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询整句Token时延...")
    result = ac.report_talk_time(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@aiserver.command('report-tokens')
@click.option('--user-ids', required=True, help='用户ID列表，逗号分隔')
@click.option('--model-id', required=True, help='模型ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--type', 'type_', required=True, help='聚合类型 (minute/hour/day)')
@click.option('--application-id', help='应用ID')
@click.option('--timeout', '-t', default=30)
@click.pass_context
def report_tokens(ctx, user_ids, model_id, start_time, end_time, type_, application_id, timeout):
    """查询模型服务Token调用量"""
    client = ctx.obj['client']
    ac = AIServerClient(client)
    ac.set_timeout(timeout)
    click.echo("📊 查询Token调用量...")
    result = ac.report_tokens_usage(user_ids.split(','), model_id, start_time, end_time, type_, application_id)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))
