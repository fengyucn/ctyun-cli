"""微服务引擎(MSE)命令行接口"""

import click
import json
from .client import MSEClient


def _get_client(ctx):
    return MSEClient(ctx.obj['client'])


def _echo(result):
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


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
    _echo(result)


# ==================== 实例管理 ====================

@mse.group()
def instance():
    """实例管理"""
    pass


@instance.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', help='实例ID过滤')
@click.option('--inst-name', help='实例名过滤')
@click.option('--engine-type', type=click.Choice(['nacos', 'eureka', 'zookeeper']), help='引擎类型')
@click.option('--status', type=int, help='实例状态(1/2/3/5/101/201/998/999)')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='分页大小')
@click.pass_context
def instance_list(ctx, region_id, instance_id, inst_name, engine_type, status, page_num, page_size):
    """获取实例列表"""
    result = _get_client(ctx).list_instances(
        region_id, instance_id=instance_id, inst_name=inst_name,
        engine_type=engine_type, status=status,
        page_num=page_num, page_size=page_size)
    _echo(result)


@instance.command('detail')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.pass_context
def instance_detail(ctx, region_id, instance_id):
    """获取实例详情"""
    _echo(_get_client(ctx).get_instance_detail(region_id, instance_id))


@instance.command('node-status')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.pass_context
def instance_node_status(ctx, region_id, instance_id):
    """获取实例节点状态"""
    _echo(_get_client(ctx).get_cluster_node_status(region_id, instance_id))


@instance.command('metrics')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--spu-inst-id', '-i', required=True, help='实例ID')
@click.option('--region-code', required=True, help='资源池编码')
@click.option('--start-time', required=True, type=int, help='开始时间（毫秒时间戳）')
@click.option('--end-time', required=True, type=int, help='结束时间（毫秒时间戳）')
@click.option('--type', 'type_', required=True, help='指标类型（如 nacos_config_count）')
@click.pass_context
def instance_metrics(ctx, region_id, spu_inst_id, region_code, start_time, end_time, type_):
    """获取集群监控指标数据"""
    _echo(_get_client(ctx).get_cluster_metrics(
        region_id, spu_inst_id, region_code, start_time, end_time, type_))


# ==================== Nacos ====================

@mse.group()
def nacos():
    """Nacos 注册配置中心"""
    pass


@nacos.group()
def service():
    """Nacos 服务管理"""
    pass


@service.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--namespace-id', help='命名空间ID（默认public）')
@click.option('--service-name', help='服务名过滤')
@click.option('--group-name', help='分组过滤')
@click.option('--has-ip-count', type=bool, help='是否隐藏空服务')
@click.option('--with-instances', type=bool, help='是否返回实例信息')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.pass_context
def nacos_service_list(ctx, region_id, instance_id, namespace_id, service_name,
                       group_name, has_ip_count, with_instances, page_num, page_size):
    """查询Nacos服务列表"""
    _echo(_get_client(ctx).list_nacos_services(
        region_id, instance_id, namespace_id=namespace_id,
        service_name=service_name, group_name=group_name,
        has_ip_count=has_ip_count, with_instances=with_instances,
        page_num=page_num, page_size=page_size))


@service.command('detail')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--service-name', required=True, help='服务名')
@click.option('--namespace-id', help='命名空间ID（默认public）')
@click.option('--group-name', help='分组名')
@click.pass_context
def nacos_service_detail(ctx, region_id, instance_id, service_name, namespace_id, group_name):
    """查询Nacos服务详情"""
    _echo(_get_client(ctx).get_nacos_service_detail(
        region_id, instance_id, service_name,
        namespace_id=namespace_id, group_name=group_name))


@service.command('service-and-group')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--namespace-id', help='命名空间ID（public为空）')
@click.pass_context
def nacos_service_and_group(ctx, region_id, instance_id, namespace_id):
    """查询Nacos服务和分组"""
    _echo(_get_client(ctx).get_nacos_service_and_group(
        region_id, instance_id, namespace_id=namespace_id))


@service.command('instances')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--service-name', required=True, help='服务名')
@click.option('--group-name', required=True, help='Group ID')
@click.option('--namespace-id', help='命名空间ID（默认public）')
@click.option('--client-ip', help='实例IP过滤')
@click.option('--clusters', help='cluster名称')
@click.option('--healthy-only', type=bool, help='只返回健康实例')
@click.option('--app', help='所属应用')
@click.pass_context
def nacos_service_instances(ctx, region_id, instance_id, service_name, group_name,
                            namespace_id, client_ip, clusters, healthy_only, app):
    """查询Nacos服务实例列表"""
    _echo(_get_client(ctx).get_nacos_instance_list(
        region_id, instance_id, service_name, group_name,
        namespace_id=namespace_id, client_ip=client_ip, clusters=clusters,
        healthy_only=healthy_only, app=app))


@service.command('instance-detail')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--service-name', required=True, help='服务名')
@click.option('--group-name', required=True, help='Group ID')
@click.option('--ip', required=True, help='实例IP')
@click.option('--port', required=True, type=int, help='实例端口')
@click.option('--namespace-id', help='命名空间ID（默认public）')
@click.option('--cluster-name', help='cluster名称')
@click.pass_context
def nacos_service_instance_detail(ctx, region_id, instance_id, service_name, group_name,
                                  ip, port, namespace_id, cluster_name):
    """查询Nacos服务实例详情"""
    _echo(_get_client(ctx).get_nacos_instance_detail(
        region_id, instance_id, service_name, group_name, ip, port,
        namespace_id=namespace_id, cluster_name=cluster_name))


@service.command('clusters')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--service-name', required=True, help='服务名')
@click.option('--group-name', required=True, help='Group ID')
@click.option('--namespace-id', help='命名空间ID（public为空）')
@click.pass_context
def nacos_service_clusters(ctx, region_id, instance_id, service_name, group_name, namespace_id):
    """查询Nacos服务集群"""
    _echo(_get_client(ctx).get_nacos_clusters(
        region_id, instance_id, service_name, group_name, namespace_id=namespace_id))


@service.command('cluster-instances')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--service-name', required=True, help='服务名')
@click.option('--group-name', required=True, help='Group ID')
@click.option('--namespace-id', help='命名空间ID（public为空）')
@click.option('--cluster-name', help='集群名称')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.pass_context
def nacos_cluster_instances(ctx, region_id, instance_id, service_name, group_name,
                            namespace_id, cluster_name, page_num, page_size):
    """查询Nacos服务集群实例"""
    _echo(_get_client(ctx).get_nacos_cluster_instances(
        region_id, instance_id, service_name, group_name,
        namespace_id=namespace_id, cluster_name=cluster_name,
        page_num=page_num, page_size=page_size))


@service.command('push-trace')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--spu-inst-id', '-i', required=True, help='实例ID')
@click.option('--query-type', required=True, type=click.Choice(['SERVICE', 'IP']), help='查询维度')
@click.option('--start-time', required=True, help='开始时间（yyyy-MM-dd HH:mm:ss）')
@click.option('--end-time', required=True, help='结束时间（yyyy-MM-dd HH:mm:ss）')
@click.option('--service-name', help='服务名（SERVICE时必填）')
@click.option('--group', help='分组')
@click.option('--ip', help='IP地址（IP时必填）')
@click.option('--namespace', help='命名空间（默认public）')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='分页大小')
@click.pass_context
def nacos_push_trace(ctx, region_id, spu_inst_id, query_type, start_time, end_time,
                     service_name, group, ip, namespace, page_number, page_size):
    """查询Nacos服务推送轨迹"""
    _echo(_get_client(ctx).list_service_push_trace(
        region_id, spu_inst_id, query_type, start_time, end_time,
        service_name=service_name, group=group, ip=ip, namespace=namespace,
        page_number=page_number, page_size=page_size))


@service.command('properties')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--page-num', type=int, help='页数')
@click.option('--page-size', type=int, help='每页数量')
@click.pass_context
def nacos_properties(ctx, region_id, instance_id, page_num, page_size):
    """查询Nacos属性列表"""
    _echo(_get_client(ctx).list_nacos_properties(
        region_id, instance_id, page_num=page_num, page_size=page_size))


@nacos.group()
def config():
    """Nacos 配置管理"""
    pass


@config.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--namespace-id', help='NamespaceId')
@click.option('--data-id', help='配置的dataId过滤')
@click.option('--group', help='配置所属group过滤')
@click.option('--app-name', help='所属应用名称')
@click.option('--config-tags', help='配置标签，逗号分隔')
@click.option('--page-num', type=int, help='页数')
@click.option('--page-size', type=int, help='每页数量')
@click.pass_context
def nacos_config_list(ctx, region_id, instance_id, namespace_id, data_id, group,
                      app_name, config_tags, page_num, page_size):
    """查询Nacos配置列表"""
    _echo(_get_client(ctx).list_nacos_configs(
        region_id, instance_id, namespace_id=namespace_id,
        data_id=data_id, group=group, app_name=app_name,
        config_tags=config_tags, page_num=page_num, page_size=page_size))


@config.command('detail')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--data-id', required=True, help='配置的dataId')
@click.option('--group', required=True, help='配置所属group')
@click.option('--namespace-id', help='NamespaceId')
@click.option('--beta', type=bool, help='是否灰度')
@click.pass_context
def nacos_config_detail(ctx, region_id, instance_id, data_id, group, namespace_id, beta):
    """查询Nacos配置详情"""
    _echo(_get_client(ctx).get_nacos_config_detail(
        region_id, instance_id, data_id, group,
        namespace_id=namespace_id, beta=beta))


@config.command('content')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--data-id', required=True, help='配置的dataId')
@click.option('--group', required=True, help='配置所属group')
@click.option('--namespace-id', help='NamespaceId')
@click.pass_context
def nacos_config_content(ctx, region_id, instance_id, data_id, group, namespace_id):
    """查询Nacos配置内容"""
    _echo(_get_client(ctx).get_nacos_config_content(
        region_id, instance_id, data_id, group, namespace_id=namespace_id))


@config.command('dataid-and-group')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--namespace-id', help='NamespaceId')
@click.pass_context
def nacos_dataid_and_group(ctx, region_id, instance_id, namespace_id):
    """查询Nacos配置的数据和分组"""
    _echo(_get_client(ctx).get_nacos_dataid_and_group(
        region_id, instance_id, namespace_id=namespace_id))


@config.command('history-list')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--data-id', required=True, help='配置的dataId')
@click.option('--group', required=True, help='配置所属group')
@click.option('--namespace-id', help='NamespaceId')
@click.option('--page-num', type=int, help='页数')
@click.option('--page-size', type=int, help='每页数量')
@click.pass_context
def nacos_config_history_list(ctx, region_id, instance_id, data_id, group,
                              namespace_id, page_num, page_size):
    """查询Nacos配置的历史列表"""
    _echo(_get_client(ctx).get_nacos_config_history_list(
        region_id, instance_id, data_id, group,
        namespace_id=namespace_id, page_num=page_num, page_size=page_size))


@config.command('history-detail')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--data-id', required=True, help='配置的dataId')
@click.option('--group', required=True, help='配置所属group')
@click.option('--id', 'id_', required=True, help='配置历史条目id（从history-list获取）')
@click.option('--namespace-id', help='NamespaceId')
@click.pass_context
def nacos_config_history_detail(ctx, region_id, instance_id, data_id, group, id_, namespace_id):
    """查询Nacos配置的历史详情"""
    _echo(_get_client(ctx).get_nacos_config_history_detail(
        region_id, instance_id, data_id, group, id_, namespace_id=namespace_id))


@config.command('trace')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--spu-inst-id', '-i', required=True, help='实例ID')
@click.option('--namespace', required=True, help='命名空间')
@click.option('--query-type', required=True, type=click.Choice(['ip', 'config']), help='查询维度')
@click.option('--start-time', required=True, help='开始时间（yyyy-MM-dd HH:mm:ss）')
@click.option('--end-time', required=True, help='结束时间（yyyy-MM-dd HH:mm:ss）')
@click.option('--data-id', help='配置的dataId（config时必填）')
@click.option('--group', help='配置所属group（config时必填）')
@click.option('--ip', help='IP地址（ip时必填）')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='分页大小')
@click.pass_context
def nacos_config_trace(ctx, region_id, spu_inst_id, namespace, query_type,
                       start_time, end_time, data_id, group, ip, page_number, page_size):
    """查询Nacos配置轨迹"""
    _echo(_get_client(ctx).list_config_trace(
        region_id, spu_inst_id, namespace, query_type, start_time, end_time,
        data_id=data_id, group=group, ip=ip,
        page_number=page_number, page_size=page_size))


@config.command('listeners')
@click.option('--region-id', '-r', required=True, help='资源池ID')
@click.option('--instance-id', '-i', required=True, help='实例ID')
@click.option('--data-id', required=True, help='配置的dataId')
@click.option('--group', required=True, help='配置所属group')
@click.option('--type', 'type_', required=True, help='监听类型（如 config）')
@click.option('--namespace-id', help='NamespaceId')
@click.option('--ip', help='监听IP')
@click.pass_context
def nacos_config_listeners(ctx, region_id, instance_id, data_id, group, type_, namespace_id, ip):
    """查询Nacos配置监听列表"""
    _echo(_get_client(ctx).get_nacos_config_listeners(
        region_id, instance_id, data_id, group, type_,
        namespace_id=namespace_id, ip=ip))
