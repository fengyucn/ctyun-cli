"""边缘安全加速平台(Aone)命令行接口"""

import click
from typing import Optional
from .client import AoneClient
from utils import OutputFormatter


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
def aone():
    """边缘安全加速平台(Aone)管理"""
    pass


# ==================== 域名管理 ====================


@aone.command('query-domain-list')
@click.option('--access-mode', type=int, help='接入方式: 1(域名接入), 2(无域名接入)')
@click.option('--domain', help='域名')
@click.option('--instance', multiple=True, help='实例名称(可多次指定)')
@click.option('--product-code', help='产品类型编码')
@click.option('--status', type=int, help='域名状态(1-12)')
@click.option('--area-scope', type=int, help='加速区域: 1(国内), 2(海外), 3(全球)')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=50, type=int, help='每页条数，默认50')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_domain_list(ctx, access_mode, domain, instance, product_code,
                          status, area_scope, page, page_size, output):
    """查询域名列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_domain_list(
        access_mode=access_mode, domain=domain,
        instance=list(instance) if instance else None,
        product_code=product_code, status=status,
        area_scope=area_scope, page=page, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    record_list = return_obj.get('result', [])
    if not record_list:
        click.echo("未找到域名"); return
    click.echo(f"\n域名列表 (总计: {return_obj.get('total', 0)} 个, 第{page}页)\n")
    format_output(record_list, output_format)


@aone.command('query-domain-config')
@click.option('--product-code', required=True, help='产品类型: 009(应用加速), 024(边缘接入)')
@click.option('--access-mode', type=int, help='接入方式: 1(域名接入), 2(无域名接入)')
@click.option('--domain', help='加速域名')
@click.option('--instance', help='实例名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_domain_config(ctx, product_code, access_mode, domain, instance, output):
    """查询域名配置信息"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_domain_config(
        product_code=product_code, access_mode=access_mode,
        domain=domain, instance=instance
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


@aone.command('query-domain-basic-config')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品编码: 010(WAF), 011(DDoS), 020(边缘安全)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_domain_basic_config(ctx, domain, product_code, output):
    """域名基础及加速配置查询"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_domain_basic_config(domain=domain, product_code=product_code)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


@aone.command('query-domain-status')
@click.option('--domains', required=True, multiple=True, help='域名列表(可多次指定)')
@click.option('--product-code', required=True, help='产品编码: 010(WAF), 011(DDoS), 020(边缘安全)')
@click.option('--page-index', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=50, type=int, help='每页条数，默认50')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_domain_status(ctx, domains, product_code, page_index, page_size, output):
    """域名状态查询"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_domain_status(
        domains=list(domains), product_code=product_code,
        page_index=page_index, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    record_list = return_obj.get('result', [])
    if not record_list:
        click.echo("未找到域名状态"); return
    click.echo(f"\n域名状态 (总计: {return_obj.get('total', 0)} 个)\n")
    format_output(record_list, output_format)


@aone.command('query-domain-protocol')
@click.option('--product-code', required=True, help='产品类型: 009(应用加速), 024(边缘接入)')
@click.option('--access-mode', type=int, help='接入方式: 1(域名接入), 2(无域名接入)')
@click.option('--domain', help='加速域名')
@click.option('--instance', help='实例名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_domain_protocol(ctx, product_code, access_mode, domain, instance, output):
    """查询域名协议类型"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_domain_protocol(
        product_code=product_code, access_mode=access_mode,
        domain=domain, instance=instance
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


@aone.command('query-domain-list-basic')
@click.option('--domain', help='域名')
@click.option('--product-code', help='产品类型编码')
@click.option('--status', type=int, help='域名状态(1-12)')
@click.option('--area-scope', type=int, help='加速区域: 1(国内), 2(海外), 3(全球)')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=50, type=int, help='每页条数，默认50')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_domain_list_basic(ctx, domain, product_code, status,
                                area_scope, page, page_size, output):
    """查询域名列表基础信息"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_domain_list_basic(
        domain=domain, product_code=product_code, status=status,
        area_scope=area_scope, page=page, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    record_list = return_obj.get('result', [])
    if not record_list:
        click.echo("未找到域名"); return
    click.echo(f"\n域名列表 (总计: {return_obj.get('total', 0)} 个, 第{page}页)\n")
    format_output(record_list, output_format)


# ==================== 服务管理 ====================


@aone.command('query-service-detail')
@click.option('--product-code', multiple=True, help='产品类型编码(可多次指定，如 024)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_service_detail(ctx, product_code, output):
    """查询开通服务基本信息"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_service_detail(
        product_code=list(product_code) if product_code else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    service_list = return_obj.get('result', [])
    if not service_list:
        click.echo("未查询到服务信息"); return
    format_output(service_list, output_format)


@aone.command('query-resource-packages')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_resource_packages(ctx, output):
    """查询安全与加速资源包列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_resource_packages()
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


# ==================== 证书管理 ====================


@aone.command('query-cert-list')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--per-page', default=1000, type=int, help='每页条数，默认1000')
@click.option('--usage-mode', type=int, help='证书用途: 0(加速域名证书), 1(客户端CA), 2(来源CA), 3(CDN来源证书), 4(国密证书)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_cert_list(ctx, page, per_page, usage_mode, output):
    """查询用户名下证书列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_cert_list(page=page, per_page=per_page, usage_mode=usage_mode)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    cert_list = return_obj.get('result', [])
    if not cert_list:
        click.echo("未找到证书"); return
    click.echo(f"\n证书列表 (总计: {return_obj.get('total_records', 0)} 个)\n")
    format_output(cert_list, output_format)


@aone.command('query-cert-detail')
@click.option('--name', help='证书名称')
@click.option('--id', type=int, help='证书ID')
@click.option('--usage-mode', type=int, help='证书用途: 0(加速域名证书), 1(客户端CA), 2(来源CA), 3(CDN来源证书), 4(国密证书)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_cert_detail(ctx, name, id, usage_mode, output):
    """查询证书详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_cert_detail(name=name, id=id, usage_mode=usage_mode)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    cert_info = result.get('returnObj', {}).get('result', {})
    if not cert_info:
        click.echo("未找到证书"); return
    format_output(cert_info, output_format)


@aone.command('query-cert-domains')
@click.option('--name', required=True, help='证书名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_cert_domains(ctx, name, output):
    """查询证书关联域名列表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_cert_domains(name=name)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    domain_list = result.get('returnObj', {}).get('result', [])
    if not domain_list:
        click.echo("该证书未关联任何域名"); return
    format_output(domain_list, output_format)


# ==================== 缓存管理 ====================


@aone.command('query-refresh-tasks')
@click.option('--type', 'query_type', default=0, type=int, help='查询方式: 0(按时间), 1(按提交ID), 2(按任务ID)')
@click.option('--url', help='URL(支持模糊匹配)')
@click.option('--start-time', type=int, help='开始时间戳(秒); type=0时必填')
@click.option('--end-time', type=int, help='结束时间戳(秒); type=0时必填')
@click.option('--submit-id', help='提交ID; type=1时必填')
@click.option('--task-id', help='任务ID; type=2时必填')
@click.option('--task-type', type=int, help='刷新类型: 1(url), 2(dir), 3(regex), 4(fuzzy)')
@click.option('--page', default=1, type=int, help='页码，默认1; 仅type=0有效')
@click.option('--page-size', default=50, type=int, help='每页条数，默认50')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_refresh_tasks(ctx, query_type, url, start_time, end_time,
                            submit_id, task_id, task_type, page, page_size, output):
    """查询刷新任务"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_refresh_tasks(
        type=query_type, url=url, start_time=start_time, end_time=end_time,
        submit_id=submit_id, task_id=task_id, task_type=task_type,
        page=page, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    task_list = return_obj.get('result', [])
    if not task_list:
        click.echo("未找到刷新任务"); return
    click.echo(f"\n刷新任务 (总计: {return_obj.get('total', 0)} 个)\n")
    format_output(task_list, output_format)


@aone.command('query-refresh-task-quota')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_refresh_task_quota(ctx, output):
    """查询刷新任务额度"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_refresh_task_quota()
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    result_data = result.get('returnObj', {}).get('result', {})
    quotas = result_data.get('quotas', [])
    if quotas:
        click.echo("刷新任务额度:")
        format_output(quotas, output_format)
    else:
        format_output(result_data, output_format)


@aone.command('query-preload-tasks')
@click.option('--type', 'query_type', default=0, type=int, help='查询方式: 0(按时间), 1(按提交ID), 2(按任务ID)')
@click.option('--url', help='URL(支持模糊匹配)')
@click.option('--start-time', type=int, help='开始时间戳(秒); type=0时必填')
@click.option('--end-time', type=int, help='结束时间戳(秒); type=0时必填')
@click.option('--submit-id', help='提交ID; type=1时必填')
@click.option('--task-id', help='任务ID; type=2时必填')
@click.option('--page', default=1, type=int, help='页码，默认1; 仅type=0有效')
@click.option('--page-size', default=50, type=int, help='每页条数，默认50')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_preload_tasks(ctx, query_type, url, start_time, end_time,
                            submit_id, task_id, page, page_size, output):
    """查询预取任务"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_preload_tasks(
        type=query_type, url=url, start_time=start_time, end_time=end_time,
        submit_id=submit_id, task_id=task_id, page=page, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    task_list = return_obj.get('result', [])
    if not task_list:
        click.echo("未找到预取任务"); return
    click.echo(f"\n预取任务 (总计: {return_obj.get('total', 0)} 个)\n")
    format_output(task_list, output_format)


@aone.command('query-preload-task-quota')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_preload_task_quota(ctx, output):
    """查询预取任务额度"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_preload_task_quota()
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    result_data = result.get('returnObj', {}).get('result', {})
    quotas = result_data.get('quotas', [])
    if quotas:
        click.echo("预取任务额度:")
        format_output(quotas, output_format)
    else:
        format_output(result_data, output_format)


# ==================== 数据统计 ====================


@aone.command('query-bandwidth-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--access-mode', type=int, help='接入方式: 1(域名), 2(无域名)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--instance', multiple=True, help='实例名称(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--abroad', type=int, help='区域: 0(国内), 1(海外)')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定): product_type, domain, province, isp等')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_bandwidth_data(ctx, start_time, end_time, interval,
                             product_type, access_mode, domain, instance,
                             province, isp, network_layer_protocol, abroad,
                             group_by, output):
    """查询带宽数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_bandwidth_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        access_mode=access_mode,
        domain=list(domain) if domain else None,
        instance=list(instance) if instance else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        abroad=abroad,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_bandwidth_data_interval', [])
    if not data_list:
        click.echo("未查询到带宽数据"); return
    click.echo(f"\n带宽数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-flow-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--access-mode', type=int, help='接入方式: 1(域名), 2(无域名)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--instance', multiple=True, help='实例名称(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--abroad', type=int, help='区域: 0(国内), 1(海外)')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_flow_data(ctx, start_time, end_time, interval,
                        product_type, access_mode, domain, instance,
                        province, isp, network_layer_protocol, abroad,
                        group_by, output):
    """查询流量数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_flow_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        access_mode=access_mode,
        domain=list(domain) if domain else None,
        instance=list(instance) if instance else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        abroad=abroad,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_hit_flow_rate_data_interval', [])
    if not data_list:
        click.echo("未查询到流量数据"); return
    click.echo(f"\n流量数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-qps-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_qps_data(ctx, start_time, end_time, interval,
                       product_type, domain, province, isp,
                       network_layer_protocol, application_layer_protocol,
                       group_by, output):
    """查询QPS/回源QPS数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_qps_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_qps_data_interval', [])
    if not data_list:
        click.echo("未查询到QPS数据"); return
    click.echo(f"\nQPS数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-request-num-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_request_num_data(ctx, start_time, end_time, interval,
                               product_type, domain, province, isp,
                               network_layer_protocol, application_layer_protocol,
                               group_by, output):
    """查询请求数/回源请求数/请求命中率数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_request_num_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_request_num_data_interval', [])
    if not data_list:
        click.echo("未查询到请求数数据"); return
    click.echo(f"\n请求数数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-miss-bandwidth-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_miss_bandwidth_data(ctx, start_time, end_time, interval,
                                  product_type, domain, province, isp,
                                  network_layer_protocol, application_layer_protocol,
                                  group_by, output):
    """查询回源带宽数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_miss_bandwidth_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_miss_bandwidth_data_interval', [])
    if not data_list:
        click.echo("未查询到回源带宽数据"); return
    click.echo(f"\n回源带宽数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-pv-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--http-protocol', type=int, help='协议: 0(http), 1(https)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_pv_data(ctx, start_time, end_time, domain, http_protocol, output):
    """查询PV数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_pv_data(
        start_time=start_time, end_time=end_time,
        domain=list(domain) if domain else None,
        http_protocol=http_protocol
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    data_list = result.get('returnObj', {}).get('result', [])
    if not data_list:
        click.echo("未查询到PV数据"); return
    format_output(data_list, output_format)


@aone.command('query-uv-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_uv_data(ctx, start_time, end_time, domain, output):
    """查询UV数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_uv_data(
        start_time=start_time, end_time=end_time,
        domain=list(domain) if domain else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    data_list = result.get('returnObj', {}).get('result', [])
    if not data_list:
        click.echo("未查询到UV数据"); return
    format_output(data_list, output_format)


@aone.command('query-http-status-code-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--busi-type', type=int, multiple=True, help='业务类型: 0(base), 1(upload), 2(websocket)')
@click.option('--abroad', type=int, help='区域: 0(国内), 1(海外)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_http_status_code_data(ctx, start_time, end_time, interval,
                                    product_type, domain, province, isp,
                                    network_layer_protocol, application_layer_protocol,
                                    group_by, busi_type, abroad, output):
    """查询状态码请求数/请求状态码占比"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_http_status_code_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None,
        busi_type=list(busi_type) if busi_type else None,
        abroad=abroad
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_http_status_code_data_interval', [])
    if not data_list:
        click.echo("未查询到状态码数据"); return
    click.echo(f"\n状态码数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-miss-http-status-code-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_miss_http_status_code_data(ctx, start_time, end_time, interval,
                                         product_type, domain, province, isp,
                                         network_layer_protocol, application_layer_protocol,
                                         group_by, output):
    """查询回源状态码请求数/回源状态码请求数占比"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_miss_http_status_code_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_miss_http_status_code_data_interval', [])
    if not data_list:
        click.echo("未查询到回源状态码数据"); return
    click.echo(f"\n回源状态码数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-miss-request-num-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_miss_request_num_data(ctx, start_time, end_time, interval,
                                    product_type, domain, province, isp,
                                    network_layer_protocol, application_layer_protocol,
                                    group_by, output):
    """查询回源请求数数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_miss_request_num_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_miss_request_num_data_interval', [])
    if not data_list:
        click.echo("未查询到回源请求数数据"); return
    click.echo(f"\n回源请求数数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-response-time-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 5m(默认)')
@click.option('--domain', multiple=True, help='域名(仅支持单个)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6')
@click.option('--application-layer-protocol', help='应用层协议: http, https')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_response_time_data(ctx, start_time, end_time, interval,
                                 domain, province, isp,
                                 network_layer_protocol, application_layer_protocol,
                                 output):
    """查询平均响应时间"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_response_time_data(
        start_time=start_time, end_time=end_time, interval=interval,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_response_time_data_interval', [])
    if not data_list:
        click.echo("未查询到响应时间数据"); return
    click.echo(f"\n平均响应时间 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-request-success-rate')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 5m(默认)')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_request_success_rate(ctx, start_time, end_time, interval,
                                   product_type, domain, province, isp, output):
    """查询请求成功率数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_request_success_rate_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_request_success_rate_data_interval', [])
    if not data_list:
        click.echo("未查询到请求成功率数据"); return
    click.echo(f"\n请求成功率 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-request-failure-rate')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 5m(默认)')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_request_failure_rate(ctx, start_time, end_time, interval,
                                   product_type, domain, province, isp, output):
    """查询请求失败率数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_request_failure_rate_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_request_failure_rate_data_interval', [])
    if not data_list:
        click.echo("未查询到请求失败率数据"); return
    click.echo(f"\n请求失败率 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-miss-request-success-rate')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 5m(默认)')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_miss_request_success_rate(ctx, start_time, end_time, interval,
                                        product_type, domain, province, isp, output):
    """查询回源请求成功率数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_miss_request_success_rate_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_miss_request_success_rate_data_interval', [])
    if not data_list:
        click.echo("未查询到回源请求成功率数据"); return
    click.echo(f"\n回源请求成功率 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-miss-request-failure-rate')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_miss_request_failure_rate(ctx, start_time, end_time, interval,
                                        product_type, domain, province, isp,
                                        network_layer_protocol, application_layer_protocol,
                                        group_by, output):
    """查询回源请求失败率数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_miss_request_failure_rate_data(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        domain=list(domain) if domain else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_miss_request_failure_rate_data_interval', [])
    if not data_list:
        click.echo("未查询到回源请求失败率数据"); return
    click.echo(f"\n回源请求失败率 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-user-connection-num')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--product-type', multiple=True, help='产品类型(可多次指定)')
@click.option('--access-mode', type=int, help='接入方式: 1(域名), 2(无域名)')
@click.option('--domain', multiple=True, help='域名(可多次指定)')
@click.option('--instance', multiple=True, help='实例名称(可多次指定)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--abroad', type=int, help='区域: 0(国内), 1(海外)')
@click.option('--group-by', multiple=True, help='聚合维度(可多次指定)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_user_connection_num(ctx, start_time, end_time, interval,
                                  product_type, access_mode, domain, instance,
                                  province, isp, network_layer_protocol,
                                  abroad, group_by, output):
    """查询用户连接数"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_user_connection_num(
        start_time=start_time, end_time=end_time, interval=interval,
        product_type=list(product_type) if product_type else None,
        access_mode=access_mode,
        domain=list(domain) if domain else None,
        instance=list(instance) if instance else None,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        abroad=abroad,
        group_by=list(group_by) if group_by else None
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_request_num_data_interval', [])
    if not data_list:
        click.echo("未查询到连接数数据"); return
    click.echo(f"\n用户连接数 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


@aone.command('query-summary-data')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--interval', help='时间粒度: 1m, 5m(默认), 1h, 24h')
@click.option('--busi-type', type=int, multiple=True, help='业务类型: 0(base), 1(upload), 2(websocket)')
@click.option('--domain', help='域名(仅支持单个)')
@click.option('--province', type=int, multiple=True, help='省编码(可多次指定)')
@click.option('--isp', multiple=True, help='运营商编码(可多次指定)')
@click.option('--network-layer-protocol', help='网络层协议: ipv4, ipv6, other')
@click.option('--application-layer-protocol', help='应用层协议: http, https, rtmp, quic, other')
@click.option('--abroad', type=int, help='区域: 0(国内), 1(海外)')
@click.option('--group-by', help='聚合维度: busi_type, province, isp等(逗号分隔)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_summary_data(ctx, start_time, end_time, interval,
                           busi_type, domain, province, isp,
                           network_layer_protocol, application_layer_protocol,
                           abroad, group_by, output):
    """查询整体统计数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_summary_data(
        start_time=start_time, end_time=end_time, interval=interval,
        busi_type=list(busi_type) if busi_type else None,
        domain=domain,
        province=list(province) if province else None,
        isp=list(isp) if isp else None,
        network_layer_protocol=network_layer_protocol,
        application_layer_protocol=application_layer_protocol,
        abroad=abroad, group_by=group_by
    )
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    data_list = return_obj.get('req_summary_data_interval', [])
    if not data_list:
        click.echo("未查询到统计数据"); return
    click.echo(f"\n整体统计数据 ({return_obj.get('start_time')} ~ {return_obj.get('end_time')})\n")
    format_output(data_list, output_format)


# ==================== 安全防护 ====================


@aone.command('query-cc-attack-report')
@click.option('--product-code', required=True, help='产品业务类型: 020(边缘安全加速)')
@click.option('--start-time', required=True, help='开始时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--end-time', required=True, help='结束时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--domain', help='域名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_cc_attack_report(ctx, product_code, start_time, end_time, domain, output):
    """查询CC攻击报表"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_cc_attack_report(
        product_code=product_code, start_time=start_time,
        end_time=end_time, domain=domain
    )
    data_list = result.get('data', [])
    if not data_list:
        click.echo("未查询到CC攻击数据"); return
    format_output(data_list, output_format)


@aone.command('query-cc-attack-events')
@click.option('--product-code', required=True, help='产品号: 020(边缘安全与加速)')
@click.option('--start-time', required=True, help='开始时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--end-time', required=True, help='结束时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--domain', help='域名')
@click.option('--page', default=1, type=int, help='页码，默认1')
@click.option('--size', default=50, type=int, help='每页条数，默认50')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_cc_attack_events(ctx, product_code, start_time, end_time,
                               domain, page, size, output):
    """查询CC攻击事件"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_cc_attack_events(
        product_code=product_code, start_time=start_time,
        end_time=end_time, domain=domain, page=page, size=size
    )
    if result.get('statusCode') not in (800, 100000, '100000'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    event_list = return_obj.get('resultList', [])
    if not event_list:
        click.echo("未查询到CC攻击事件"); return
    click.echo(f"\nCC攻击事件 (总计: {return_obj.get('total', 0)} 个)\n")
    format_output(event_list, output_format)


@aone.command('query-cc-attack-region')
@click.option('--domain-list', required=True, multiple=True, help='域名列表(可多次指定)')
@click.option('--product-code', required=True, help='产品业务类型: 020')
@click.option('--start-time', required=True, help='开始时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--end-time', required=True, help='结束时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_cc_attack_region(ctx, domain_list, product_code, start_time, end_time, output):
    """CC攻击报表攻击来源区域分布查询"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_cc_attack_region(
        domain_list=list(domain_list), product_code=product_code,
        start_time=start_time, end_time=end_time
    )
    data_list = result.get('data', [])
    if not data_list:
        click.echo("未查询到CC攻击区域分布"); return
    format_output(data_list, output_format)


@aone.command('query-ddos-attack-trend')
@click.option('--start-time', required=True, help='开始时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--end-time', required=True, help='结束时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_ddos_attack_trend(ctx, start_time, end_time, output):
    """DDoS攻击趋势查询"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_ddos_attack_trend(start_time=start_time, end_time=end_time)
    data_list = result.get('data', [])
    if not data_list:
        click.echo("未查询到DDoS攻击趋势"); return
    format_output(data_list, output_format)


@aone.command('query-edge-attack-trend')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品业务类型: 024(边缘接入)')
@click.option('--start-time', required=True, help='开始时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--end-time', required=True, help='结束时间(yyyy-MM-dd HH:mm:ss)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_edge_attack_trend(ctx, domain, product_code, start_time, end_time, output):
    """查询边缘接入攻击趋势图数据"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_edge_attack_trend(
        domain=domain, product_code=product_code,
        start_time=start_time, end_time=end_time
    )
    data_list = result.get('data', [])
    if not data_list:
        click.echo("未查询到攻击趋势"); return
    format_output(data_list, output_format)


@aone.command('query-waf-config')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品业务类型: 020(边缘安全与加速)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_waf_config(ctx, domain, product_code, output):
    """查询Web应用防火墙基础配置信息"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_waf_config(domain=domain, product_code=product_code)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


@aone.command('query-rule-engine-config')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品类型: 020(边缘安全加速)')
@click.option('--rule-id', help='规则ID')
@click.option('--page-index', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_rule_engine_config(ctx, domain, product_code, rule_id,
                                 page_index, page_size, output):
    """查询防护规则引擎的配置信息"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_rule_engine_config(
        domain=domain, product_code=product_code, rule_id=rule_id,
        page_index=page_index, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000, '100000'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    return_obj = result.get('returnObj', {})
    rule_list = return_obj.get('results', [])
    if not rule_list:
        click.echo("未查询到规则配置"); return
    click.echo(f"\n规则配置 (总计: {return_obj.get('total', 0)} 条)\n")
    format_output(rule_list, output_format)


@aone.command('query-rule-engine-switch')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品类型: 010(云WAF)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_rule_engine_switch(ctx, domain, product_code, output):
    """查询域名的防护规则引擎总开关信息"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_rule_engine_switch(domain=domain, product_code=product_code)
    if result.get('statusCode') not in (800, 100000, '100000'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


@aone.command('query-access-control-switch')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品业务类型: 020(边缘安全与加速)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_access_control_switch(ctx, domain, product_code, output):
    """查询访问控制限流总开关"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_access_control_switch(domain=domain, product_code=product_code)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    format_output(result.get('returnObj', {}), output_format)


@aone.command('query-tamper-protect')
@click.option('--domain', required=True, help='域名')
@click.option('--product-code', required=True, help='产品类型: 010(边缘云WAF), 020(边缘安全加速)')
@click.option('--page-index', default=1, type=int, help='页码，默认1')
@click.option('--page-size', default=10, type=int, help='每页条数，默认10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_tamper_protect(ctx, domain, product_code, page_index, page_size, output):
    """网页防篡改查询接口"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_tamper_protect(
        domain=domain, product_code=product_code,
        page_index=page_index, page_size=page_size
    )
    if result.get('statusCode') not in (800, 100000, '100000'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    page_result = result.get('returnObj', {}).get('pageResult', {})
    rule_list = page_result.get('results', [])
    if not rule_list:
        click.echo("未查询到防篡改规则"); return
    click.echo(f"\n防篡改规则 (总计: {page_result.get('total', 0)} 条)\n")
    format_output(rule_list, output_format)


@aone.command('query-ipv6-no-sup-links')
@click.option('--request-id', required=True, type=int, help='IPv6检测任务ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_ipv6_no_sup_links(ctx, request_id, output):
    """查询IPv6检测不支持链接详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_ipv6_no_sup_links(request_id=request_id)
    if result.get('statusCode') not in (800, 100000, '100000'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    link_list = result.get('returnObj', [])
    if not link_list:
        click.echo("该检测任务无不支持链接"); return
    format_output(link_list, output_format)


# ==================== 辅助工具 ====================


@aone.command('query-ip-detail')
@click.option('--ipv4', help='IPv4地址(最多20个,逗号分隔)')
@click.option('--ipv6', help='IPv6地址(最多20个,逗号分隔)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_ip_detail(ctx, ipv4, ipv6, output):
    """查询IP地址归属详情"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_ip_detail(ipv4=ipv4, ipv6=ipv6)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    ip_list = result.get('returnObj', {}).get('result', [])
    if not ip_list:
        click.echo("未查询到IP信息"); return
    format_output(ip_list, output_format)


@aone.command('query-backorigin-ip')
@click.option('--config-name', required=True, help='回源IP方案配置名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def cmd_query_backorigin_ip(ctx, config_name, output):
    """查询回源IP"""
    client = ctx.obj['client']
    output_format = output or ctx.obj.get('output', 'table')
    aone_client = AoneClient(client)
    result = aone_client.query_backorigin_ip(config_name=config_name)
    if result.get('statusCode') not in (800, 100000):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True); return
    click.echo(f"回源IP: {result.get('ips', '未获取到')}")
