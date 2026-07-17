"""应用性能监控(APM)命令行接口"""

import click
from .client import APMClient
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
            click.echo(OutputFormatter.format_table(data, list(data[0].keys())))
        elif isinstance(data, dict):
            table_data = [[k, v] for k, v in data.items()]
            click.echo(OutputFormatter.format_table(table_data, ['字段', '值']))
        else:
            click.echo(data)


def _get_client(ctx):
    return APMClient(client=ctx.obj['client'])


@click.group()
def apm():
    """应用性能监控(APM)管理"""
    pass


# ==================== 1. 基础配置与元数据 ====================

@apm.group()
def meta():
    """基础配置与元数据"""
    pass


@meta.command('project-metadata')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--env-uuid', help='环境UUID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def project_metadata(ctx, region_id, env_uuid, output):
    """查询项目元数据信息"""
    result = _get_client(ctx).query_project_metadata(region_id, env_uuid)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('env-types')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def env_types(ctx, region_id, output):
    """查询环境类型信息"""
    result = _get_client(ctx).query_env_types(region_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('envs')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def envs(ctx, region_id, output):
    """查询环境信息"""
    result = _get_client(ctx).query_envs(region_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('app-conf')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', required=True, help='项目编码')
@click.option('--deployment', required=True, help='环境编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def app_conf(ctx, region_id, service_name, project_code, deployment, output):
    """查询应用配置接口"""
    result = _get_client(ctx).query_app_conf(region_id, service_name, project_code, deployment)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('license-key')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def license_key(ctx, region_id, output):
    """列出LicenseKey"""
    result = _get_client(ctx).list_license_key(region_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('monitor-status')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--environment-code', required=True, help='Prometheus环境Code')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def monitor_status(ctx, region_id, environment_code, output):
    """查询采集服务开启状态"""
    result = _get_client(ctx).query_monitor_open_status(region_id, environment_code)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('default-jobs')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--environment-code', required=True, help='Prometheus环境Code')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def default_jobs(ctx, region_id, environment_code, output):
    """查询默认Job列表"""
    result = _get_client(ctx).query_default_job_list(region_id, environment_code)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@meta.command('common-labels')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--environment-code', required=True, help='Prometheus环境Code')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def common_labels(ctx, region_id, environment_code, output):
    """查询全局标签"""
    result = _get_client(ctx).query_common_label(region_id, environment_code)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 2. 应用与实例管理 ====================

@apm.group()
def app():
    """应用与实例管理"""
    pass


@app.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--env-uuid', help='环境UUID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def app_list(ctx, region_id, env_uuid, output):
    """获取应用列表"""
    result = _get_client(ctx).list_apps(region_id, env_uuid)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@app.command('transaction-types')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def transaction_types(ctx, region_id, output):
    """查询接口调用类型列表"""
    result = _get_client(ctx).list_transaction_types(region_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@app.command('agents')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service-name', help='应用名称')
@click.option('--deployment', help='环境编码')
@click.option('--agent-ip', help='agent IP')
@click.option('--access-type', type=int, help='接入方式(1手动安装/2容器接入)')
@click.option('--agent-status', type=int, help='agent状态(1正常上报/0未上报)')
@click.option('--version', help='agent版本')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def agents(ctx, region_id, service_name, deployment, agent_ip, access_type,
           agent_status, version, page_num, page_size, output):
    """分页查询agent列表"""
    result = _get_client(ctx).list_agents_page(
        region_id, service_name, deployment, agent_ip, access_type,
        agent_status, version, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@app.command('env-instances')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--addon-template-id', help='组件标识')
@click.option('--env-type', help='资源类型(如CS)')
@click.option('--resource-id', help='资源ID')
@click.option('--resource-name', help='资源名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def env_instances(ctx, region_id, addon_template_id, env_type, resource_id,
                  resource_name, output):
    """查询环境实例列表"""
    result = _get_client(ctx).query_env_instance_list(
        region_id, addon_template_id, env_type, resource_id, resource_name)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@app.command('tasks')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--deployment', required=True, help='环境编码')
@click.option('--env-uuid', required=True, help='环境UUID')
@click.option('--service-name', help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--project-uuid', help='项目UUID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def tasks(ctx, region_id, start_time, end_time, deployment, env_uuid,
          service_name, project_code, project_uuid, page_num, page_size, output):
    """分页查询应用监控任务"""
    result = _get_client(ctx).list_app_tasks_page(
        region_id, start_time, end_time, deployment, env_uuid, service_name,
        project_code, project_uuid, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@app.command('instances-stat')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--sort', help='排序字段(count/avgDuration/failedCount/exceptionCount)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def instances_stat(ctx, region_id, start_time, end_time, service_name,
                   project_code, deployment, sort, output):
    """查询实例统计列表"""
    result = _get_client(ctx).list_instances_stat(
        region_id, start_time, end_time, service_name, project_code, deployment, sort)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 3. 调用链与拓扑 ====================

@apm.group()
def trace():
    """调用链与拓扑"""
    pass


@trace.command('detail')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--trace-id', required=True, help='调用链ID')
@click.option('--timestamp', type=int, help='调用链产生时间(ms)')
@click.option('--project-code', help='项目编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def trace_detail(ctx, region_id, trace_id, timestamp, project_code, output):
    """获取调用链详情"""
    result = _get_client(ctx).get_trace(region_id, trace_id, timestamp, project_code)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@trace.command('span-detail')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--trace-id', required=True, help='调用链ID')
@click.option('--span-id', required=True, help='span ID')
@click.option('--timestamp', type=int, help='时间戳(ms)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def span_detail(ctx, region_id, trace_id, span_id, timestamp, output):
    """调用链span详情查询"""
    result = _get_client(ctx).get_trace_span_detail(region_id, trace_id, span_id, timestamp)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@trace.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--sort', help='排序字段(timestamp/duration)')
@click.option('--duration', type=float, help='耗时大于等于(ms)')
@click.option('--outcome', help='span状态(success/failure/unknown)')
@click.option('--type', 'type_', help='调用类型(http/db/rpc/schedule/messaging/unknown)')
@click.option('--span-kind', help='span类型(SPAN_KIND_*)')
@click.option('--trace-id', help='调用链ID')
@click.option('--transaction-name', help='接口名称')
@click.option('--query-filter', help='自定义查询过滤')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def trace_list(ctx, region_id, start_time, end_time, service_name, project_code,
               deployment, sort, duration, outcome, type_, span_kind, trace_id,
               transaction_name, query_filter, page_num, page_size, output):
    """分页查询调用链列表信息"""
    result = _get_client(ctx).list_transactions_page(
        region_id, start_time, end_time, service_name, project_code, deployment,
        sort, duration, outcome, type_, span_kind, trace_id, transaction_name,
        query_filter, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@trace.command('topology')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def topology(ctx, region_id, start_time, end_time, service_name,
             project_code, deployment, output):
    """查询拓扑图"""
    result = _get_client(ctx).query_topology_graph(
        region_id, start_time, end_time, service_name, project_code, deployment)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 4. 性能监控数据 ====================

@apm.group()
def perf():
    """性能监控数据"""
    pass


@perf.command('overview')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def overview(ctx, region_id, start_time, end_time, service_name,
             project_code, deployment, output):
    """概览统计数据查询"""
    result = _get_client(ctx).query_overview_statistics(
        region_id, start_time, end_time, service_name, project_code, deployment)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('request-curve')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--query', help='查询对象类型(current/downstream)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def request_curve(ctx, region_id, start_time, end_time, service_name,
                  project_code, deployment, query, output):
    """调用曲线图"""
    result = _get_client(ctx).get_request_curve_chart(
        region_id, start_time, end_time, service_name, project_code, deployment, query)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('http-code-curve')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def http_code_curve(ctx, region_id, start_time, end_time, service_name,
                    project_code, deployment, output):
    """http响应码曲线图"""
    result = _get_client(ctx).get_http_code_curve_chart(
        region_id, start_time, end_time, service_name, project_code, deployment)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('slow-transactions')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--span-kind', help='慢调用span类型(SPAN_KIND_*)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def slow_transactions(ctx, region_id, start_time, end_time, service_name,
                      project_code, deployment, page_num, page_size, span_kind, output):
    """慢调用分页查询"""
    result = _get_client(ctx).list_slow_transactions_page(
        region_id, start_time, end_time, service_name, project_code, deployment,
        page_num, page_size, span_kind)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('exceptions')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--transaction-name', help='接口名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def exceptions(ctx, region_id, start_time, end_time, service_name,
               transaction_name, project_code, deployment, page_num, page_size, output):
    """查询异常事件列表"""
    result = _get_client(ctx).get_exception_list(
        region_id, start_time, end_time, service_name, transaction_name,
        project_code, deployment, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('sql-stat-page')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--db-types', required=True, help='数据库类型(mysql/postgresql/hbase)')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def sql_stat_page(ctx, region_id, start_time, end_time, service_name, db_types,
                  project_code, deployment, page_num, page_size, output):
    """SQL调用统计分页查询"""
    result = _get_client(ctx).list_sql_stat_page(
        region_id, start_time, end_time, service_name, db_types,
        project_code, deployment, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('sql-stat-histogram')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--db-types', help='数据库类型(mysql/postgresql/hbase)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def sql_stat_histogram(ctx, region_id, start_time, end_time, service_name,
                       project_code, deployment, db_types, output):
    """SQL调用统计列表查询"""
    result = _get_client(ctx).list_sql_stat_histogram(
        region_id, start_time, end_time, service_name, project_code, deployment, db_types)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('nosql-stat-histogram')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--db-types', help='数据库类型(redis)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def nosql_stat_histogram(ctx, region_id, start_time, end_time, service_name,
                         project_code, deployment, db_types, output):
    """NoSQL调用统计列表查询"""
    result = _get_client(ctx).list_nosql_stat_histogram(
        region_id, start_time, end_time, service_name, project_code, deployment, db_types)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('nosql-stat-page')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--db-types', help='数据库类型(redis)')
@click.option('--target-instance-id', help='目标实例ID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def nosql_stat_page(ctx, region_id, start_time, end_time, service_name,
                    project_code, deployment, db_types, target_instance_id,
                    page_num, page_size, output):
    """NoSQL调用统计分页查询"""
    result = _get_client(ctx).list_nosql_stat_page(
        region_id, start_time, end_time, service_name, project_code, deployment,
        db_types, target_instance_id, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('mq-stat-page')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--instance-id', help='实例ID')
@click.option('--type', 'type_', help='统计调用类型(consumer/producer)')
@click.option('--message-system', help='消息中间件类型(kafka等)')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def mq_stat_page(ctx, region_id, start_time, end_time, service_name, project_code,
                 deployment, instance_id, type_, message_system, page_num, page_size, output):
    """mq调用统计分页查询"""
    result = _get_client(ctx).list_mq_stat_page(
        region_id, start_time, end_time, service_name, project_code, deployment,
        instance_id, type_, message_system, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('transaction-stat')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--sort', help='排序字段(count/failedCount/exceptionCount)')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def transaction_stat(ctx, region_id, start_time, end_time, service_name,
                     sort, project_code, deployment, output):
    """查询接口调用统计列表"""
    result = _get_client(ctx).list_transaction_stat(
        region_id, start_time, end_time, service_name, sort, project_code, deployment)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('jvm-info')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--instance-id', help='实例ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def jvm_info(ctx, region_id, start_time, end_time, service_name,
             project_code, deployment, instance_id, output):
    """获取JVM信息"""
    result = _get_client(ctx).get_jvm_info(
        region_id, start_time, end_time, service_name, project_code, deployment, instance_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('app-instance-curve')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def app_instance_curve(ctx, region_id, start_time, end_time, service_name,
                       project_code, deployment, output):
    """应用实例数曲线图"""
    result = _get_client(ctx).get_app_instance_curve_chart(
        region_id, start_time, end_time, service_name, project_code, deployment)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('jvm-gc-count')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--instance-id', help='实例ID')
@click.option('--type', 'type_', help='查询方式(accumulate累计/instant瞬时)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def jvm_gc_count(ctx, region_id, start_time, end_time, service_name,
                 project_code, deployment, instance_id, type_, output):
    """JVM的GC次数曲线图"""
    result = _get_client(ctx).get_jvm_gc_count(
        region_id, start_time, end_time, service_name, project_code,
        deployment, instance_id, type_)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@perf.command('jvm-thread-count')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--service-name', required=True, help='应用名称')
@click.option('--project-code', help='项目编码')
@click.option('--deployment', help='环境编码')
@click.option('--instance-id', help='实例ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def jvm_thread_count(ctx, region_id, start_time, end_time, service_name,
                     project_code, deployment, instance_id, output):
    """JVM线程数曲线图"""
    result = _get_client(ctx).get_jvm_thread_count(
        region_id, start_time, end_time, service_name, project_code,
        deployment, instance_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 5. 用量统计 ====================

@apm.group()
def usage():
    """用量统计"""
    pass


@usage.command('total-view')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def total_view(ctx, region_id, start_time, end_time, output):
    """用量统计总览"""
    result = _get_client(ctx).usage_total_view(region_id, start_time, end_time)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@usage.command('span-report')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--step', required=True, type=int, help='时间间隔(s),3600或86400')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def span_report(ctx, region_id, start_time, end_time, step, output):
    """用量统计Span上报量趋势图"""
    result = _get_client(ctx).usage_span_report(region_id, start_time, end_time, step)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@usage.command('agent-hour')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--step', required=True, type=int, help='时间间隔(s),3600或86400')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def agent_hour(ctx, region_id, start_time, end_time, step, output):
    """用量统计agentHour趋势图"""
    result = _get_client(ctx).usage_agent_hour(region_id, start_time, end_time, step)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@usage.command('span-store')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, type=int, help='开始时间(ms)')
@click.option('--end-time', required=True, type=int, help='结束时间(ms)')
@click.option('--step', required=True, type=int, help='时间间隔(s),3600或86400')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def span_store(ctx, region_id, start_time, end_time, step, output):
    """用量统计Span存储量趋势图"""
    result = _get_client(ctx).usage_span_store(region_id, start_time, end_time, step)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 6. 告警管理 ====================

@apm.group()
def alert():
    """告警管理"""
    pass


@alert.command('rules')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--obj-type', required=True, help='对象类型编码(ctgcache/KAFKA/MQ2等)')
@click.option('--rule-name', help='规则名称模糊查询')
@click.option('--group-id', type=int, help='规则分组ID')
@click.option('--rule-status', type=int, help='规则状态(0启用/1启用中/2停用中/3失败/4停用)')
@click.option('--obj-id', help='对象实例ID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def alert_rules(ctx, region_id, obj_type, rule_name, group_id, rule_status,
                obj_id, page_num, page_size, output):
    """分页查询告警规则"""
    result = _get_client(ctx).list_alert_rules(
        region_id, obj_type, rule_name, group_id, rule_status,
        obj_id, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@alert.command('rule-templates')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--obj-type', required=True, help='对象类型编码(ctgcache/KAFKA/MQ2等)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def rule_templates(ctx, region_id, obj_type, output):
    """查询告警规则对象模板分组列表"""
    result = _get_client(ctx).list_alert_rule_templates(region_id, obj_type)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@alert.command('send-history')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--alert-name', help='告警名称模糊查询')
@click.option('--alert-status', type=int, help='告警状态(1待认领/2已解决/4处理中)')
@click.option('--start-time', type=int, help='开始时间戳(ms)')
@click.option('--end-time', type=int, help='结束时间戳(ms)')
@click.option('--strategy-id', type=int, help='通知策略ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def send_history(ctx, region_id, page_num, page_size, alert_name, alert_status,
                 start_time, end_time, strategy_id, output):
    """分页查询告警发送历史"""
    result = _get_client(ctx).list_alert_send_history(
        region_id, page_num, page_size, alert_name, alert_status,
        start_time, end_time, strategy_id)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 7. 通知管理 ====================

@apm.group()
def notify():
    """通知管理"""
    pass


@notify.command('contacts')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--group-id', type=int, help='通知组ID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def contacts(ctx, region_id, group_id, page_num, page_size, output):
    """分页获取通知联系人详细信息"""
    result = _get_client(ctx).list_contacts(region_id, group_id, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@notify.command('contact-groups')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page-num', required=True, type=int, help='页码')
@click.option('--page-size', required=True, type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def contact_groups(ctx, region_id, page_num, page_size, output):
    """通知组分页查询"""
    result = _get_client(ctx).list_contact_groups(region_id, page_num, page_size)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


@notify.command('strategies')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--strategy-name', help='策略名称模糊查询')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def strategies(ctx, region_id, page_num, page_size, strategy_name, output):
    """分页获取通知策略信息"""
    result = _get_client(ctx).list_notify_strategies(
        region_id, page_num, page_size, strategy_name)
    format_output(result, output or ctx.obj.get('output_format', 'table'))


# ==================== 8. Webhook管理 ====================

@apm.group()
def webhook():
    """Webhook管理"""
    pass


@webhook.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--name', help='名称模糊查询')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def webhook_list(ctx, region_id, page_num, page_size, name, output):
    """webhook分页查询"""
    result = _get_client(ctx).list_webhooks(region_id, page_num, page_size, name)
    format_output(result, output or ctx.obj.get('output_format', 'table'))
