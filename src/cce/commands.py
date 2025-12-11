"""
容器引擎(CCE)命令行接口

天翼云容器引擎（Cloud Container Engine，CCE）是基于Kubernetes的企业级容器化服务平台。
"""

import click
from typing import Optional, Dict, Any
from core import CTYUNAPIError
from utils import OutputFormatter, logger
from cce import CCEClient


def handle_error(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CTYUNAPIError as e:
            click.echo(f"API错误 [{e.code}]: {e.message}", err=True)
            if e.request_id:
                click.echo(f"请求ID: {e.request_id}", err=True)
            import sys
            sys.exit(1)
        except Exception as e:
            click.echo(f"错误: {e}", err=True)
            import sys
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """格式化输出"""
    import click

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
        # table format
        if isinstance(data, list) and data:
            # 直接处理列表数据
            headers = list(data[0].keys())
            from tabulate import tabulate
            table_data = []
            for item in data:
                row = []
                for key in headers:
                    value = item.get(key, '')
                    if value is None:
                        value = ''
                    elif isinstance(value, (dict, list)):
                        value = str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                    row.append(value)
                table_data.append(row)
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        elif isinstance(data, dict):
            # 处理返回的数据
            if 'returnObj' in data:
                result_data = data['returnObj']
                if isinstance(result_data, list) and result_data:
                    # 列表数据，显示表格
                    headers = list(result_data[0].keys())
                    from tabulate import tabulate
                    table_data = []
                    for item in result_data:
                        row = []
                        for key in headers:
                            value = item.get(key, '')
                            if value is None:
                                value = ''
                            elif isinstance(value, (dict, list)):
                                value = str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                            row.append(value)
                        table_data.append(row)
                    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
                elif isinstance(result_data, dict):
                    # 单个对象，显示键值对
                    from tabulate import tabulate
                    table_data = []
                    for key, value in result_data.items():
                        if value is None:
                            value = ''
                        elif isinstance(value, (dict, list)):
                            value = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                        table_data.append([key, value])
                    click.echo(tabulate(table_data, headers=['键', '值'], tablefmt='grid'))
                else:
                    click.echo(str(result_data))
            else:
                # 没有returnObj，显示整个数据
                from tabulate import tabulate
                table_data = []
                for key, value in data.items():
                    if key == 'returnObj':
                        continue
                    if value is None:
                        value = ''
                    elif isinstance(value, (dict, list)):
                        value = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                    table_data.append([key, value])
                click.echo(tabulate(table_data, headers=['键', '值'], tablefmt='grid'))
        else:
            click.echo(str(data))


@click.group()
def cce():
    """容器引擎(CCE)服务管理"""
    pass


# ========== 集群管理命令 ==========

@cce.command('create-cluster')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-name', required=True, help='集群名称')
@click.option('--cluster-type', required=True, type=click.Choice(['Virtual', 'Host', 'Intelligent']),
              help='集群类型：Virtual(专有版), Host(托管版), Intelligent(智算版)')
@click.option('--kubernetes-version', required=True, help='Kubernetes版本')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--subnet-id', required=True, help='子网ID')
@click.option('--container-network-type', default='flannel', help='容器网络类型')
@click.option('--container-network-cidr', default='10.244.0.0/16', help='容器网络CIDR')
@click.option('--service-network-cidr', default='10.247.0.0/16', help='服务网络CIDR')
@click.option('--description', help='集群描述')
@click.pass_context
@handle_error
def create_cluster(ctx, region_id: str, cluster_name: str, cluster_type: str,
                  kubernetes_version: str, vpc_id: str, subnet_id: str,
                  container_network_type: str, container_network_cidr: str,
                  service_network_cidr: str, description: Optional[str]):
    """创建集群"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)

    cluster_config = {
        'clusterName': cluster_name,
        'clusterType': cluster_type,
        'kubernetesVersion': kubernetes_version,
        'vpcId': vpc_id,
        'subnetId': subnet_id,
        'containerNetworkType': container_network_type,
        'containerNetworkCidr': container_network_cidr,
        'serviceNetworkCidr': service_network_cidr
    }

    if description:
        cluster_config['description'] = description

    result = cce_client.create_cluster(region_id, cluster_config)
    click.echo(f"✓ 集群创建任务已提交: {result.get('returnObj', {}).get('clusterID', 'N/A')}")

    if output_format != 'table':
        format_output(result, output_format)


@cce.command('list-authorized-namespaces')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-name', required=True, help='集群名称')
@click.pass_context
@handle_error
def list_authorized_namespaces(ctx, region_id: str, cluster_name: str):
    """查询用户被授权的命名空间列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_authorized_namespaces(region_id, cluster_name)

    if output_format == 'table':
        namespaces = result.get('returnObj', [])
        if namespaces:
            click.echo(f"集群 '{cluster_name}' 中用户被授权的命名空间列表 (共 {len(namespaces)} 个):")
            # 显示命名空间列表
            from tabulate import tabulate
            table_data = []
            for i, namespace in enumerate(namespaces, 1):
                table_data.append([i, namespace])
            click.echo(tabulate(table_data, headers=['序号', '命名空间名称'], tablefmt='grid'))
        else:
            click.echo("未找到用户被授权的命名空间")
    else:
        format_output(result, output_format)


@cce.command('list-clusters')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--page-size', default=10, help='每页条数')
@click.option('--page-no', default=1, help='当前页码')
@click.option('--cluster-name', help='集群名称')
@click.option('--res-pool-id', help='资源池ID')
@click.pass_context
@handle_error
def list_clusters(ctx, region_id: str, page_size: int, page_no: int,
                  cluster_name: Optional[str], res_pool_id: Optional[str]):
    """查询集群列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_clusters(region_id, page_size, page_no, cluster_name, res_pool_id)

    if output_format == 'table':
        page_data = result.get('returnObj', {})
        clusters = page_data.get('records', [])
        total = page_data.get('total', 0)
        current = page_data.get('current', 1)

        if clusters:
            click.echo(f"集群列表 (共 {total} 个集群，第 {current} 页):")
            format_output(clusters, output_format)
        else:
            click.echo("未找到集群")
    else:
        format_output(result, output_format)


@cce.command('describe-cluster')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.pass_context
@handle_error
def describe_cluster(ctx, region_id: str, cluster_id: str):
    """查询集群详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.describe_cluster(region_id, cluster_id)

    if output_format == 'table':
        cluster_info = result.get('returnObj', {})
        if cluster_info:
            click.echo(f"集群详情:")
            format_output(result, output_format)
        else:
            click.echo("未找到集群信息")
    else:
        format_output(result, output_format)


@cce.command('delete-cluster')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--delete-efs', is_flag=True, help='是否删除弹性文件系统')
@click.confirmation_option(prompt='确定要删除这个集群吗?')
@click.pass_context
@handle_error
def delete_cluster(ctx, region_id: str, cluster_id: str, delete_efs: bool):
    """删除集群"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.delete_cluster(region_id, cluster_id, delete_efs)

    click.echo(f"✓ 集群删除任务已提交: {cluster_id}")

    if output_format != 'table':
        format_output(result, output_format)


@cce.command('modify-cluster')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--cluster-name', help='集群名称')
@click.option('--description', help='集群描述')
@click.pass_context
@handle_error
def modify_cluster(ctx, region_id: str, cluster_id: str, cluster_name: Optional[str],
                  description: Optional[str]):
    """修改集群"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)

    modify_config = {}
    if cluster_name:
        modify_config['clusterName'] = cluster_name
    if description:
        modify_config['description'] = description

    if not modify_config:
        click.echo("错误: 请指定要修改的参数", err=True)
        return

    result = cce_client.modify_cluster(region_id, cluster_id, modify_config)
    click.echo(f"✓ 集群修改任务已提交: {cluster_id}")

    if output_format != 'table':
        format_output(result, output_format)


@cce.command('cluster-quota')
@click.option('--region-id', required=True, help='区域ID')
@click.pass_context
@handle_error
def cluster_quota(ctx, region_id: str):
    """查询集群配额与使用量"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.query_cluster_quota(region_id)

    if output_format == 'table':
        quota_data = result.get('returnObj', {})
        cluster_quota = quota_data.get('clusterQuota', {})
        cluster_usage = quota_data.get('clusterUsage', {})

        if cluster_quota or cluster_usage:
            click.echo(f"集群配额与使用量:")
            format_output(result, output_format)
        else:
            click.echo("未找到配额信息")
    else:
        format_output(result, output_format)


@cce.command('cluster-quota-usage')
@click.option('--region-id', required=True, help='区域ID')
@click.pass_context
@handle_error
def cluster_quota_usage(ctx, region_id: str):
    """查询租户集群配额和使用量"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.query_cluster_quota_usage(region_id)

    if output_format == 'table':
        quota_data = result.get('returnObj', {})
        quota_center_list = quota_data.get('quotaCenterDataList', [])
        if quota_center_list:
            click.echo(f"集群配额与使用量:")
            format_output(result, output_format)
        else:
            click.echo("未找到配额信息")
    else:
        format_output(result, output_format)


@cce.command('get-kubeconfig')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--type', 'config_type', default='external',
              type=click.Choice(['internal', 'external']),
              help='KubeConfig类型：internal(内网) / external(外网)')
@click.option('--expire-hours', default=24, type=int, help='过期时间（小时），默认24小时')
@click.option('--output-file', help='保存KubeConfig到文件路径')
@click.pass_context
@handle_error
def get_kubeconfig(ctx, region_id: str, cluster_id: str, config_type: str,
                  expire_hours: int, output_file: Optional[str]):
    """获取集群KubeConfig配置文件"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_cluster_kubeconfig(region_id, cluster_id, config_type, expire_hours)

    kubeconfig_data = result.get('returnObj', {})
    kubeconfig_content = kubeconfig_data.get('kubeConfig', '')
    expire_time = kubeconfig_data.get('expireTime', '')

    if output_format == 'table':
        click.echo(f"KubeConfig信息:")
        click.echo(f"集群ID: {cluster_id}")
        click.echo(f"访问类型: {config_type}")
        click.echo(f"过期时间: {expire_time}")

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(kubeconfig_content)
            click.echo(f"✓ KubeConfig已保存到: {output_file}")
        else:
            click.echo(f"\nKubeConfig内容:")
            click.echo(kubeconfig_content)
    else:
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(kubeconfig_content)
            click.echo(f"✓ KubeConfig已保存到: {output_file}")
        format_output(result, output_format)


@cce.command('list-kubernetes-versions')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-type', type=click.Choice(['0', '2']),
              help='集群类型：0-专有版, 2-托管版')
@click.pass_context
@handle_error
def list_kubernetes_versions(ctx, region_id: str, cluster_type: Optional[str]):
    """查询Kubernetes版本列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    cluster_type_int = int(cluster_type) if cluster_type else None
    result = cce_client.get_kubernetes_versions(region_id, cluster_type_int)

    if output_format == 'table':
        versions_data = result.get('returnObj', {})
        versions = versions_data.get('versions', [])
        if versions:
            click.echo(f"Kubernetes版本列表:")
            format_output(result, output_format)
        else:
            click.echo("未找到可用的Kubernetes版本")
    else:
        format_output(result, output_format)


# ========== 节点与节点池管理命令 ==========

@cce.group()
def nodepool():
    """节点池管理"""
    pass


@nodepool.command('create')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--nodepool-name', required=True, help='节点池名称')
@click.option('--flavor', required=True, help='节点规格')
@click.option('--initial-node-count', required=True, type=int, help='初始节点数')
@click.option('--az', required=True, help='可用区')
@click.option('--root-volume-type', default='SATA', help='根盘类型')
@click.option('--root-volume-size', default=40, type=int, help='根盘大小(GB)')
@click.option('--data-volume-type', default='SATA', help='数据盘类型')
@click.option('--data-volume-size', default=100, type=int, help='数据盘大小(GB)')
@click.option('--key-pair', help='密钥对名称')
@click.pass_context
@handle_error
def create_nodepool(ctx, region_id: str, cluster_id: str, nodepool_name: str,
                   flavor: str, initial_node_count: int, az: str,
                   root_volume_type: str, root_volume_size: int,
                   data_volume_type: str, data_volume_size: int,
                   key_pair: Optional[str]):
    """创建节点池"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)

    node_pool_config = {
        'nodePoolName': nodepool_name,
        'flavor': flavor,
        'initialNodeCount': initial_node_count,
        'az': az,
        'rootVolume': {
            'volumeType': root_volume_type,
            'size': root_volume_size
        },
        'dataVolume': {
            'volumeType': data_volume_type,
            'size': data_volume_size
        }
    }

    if key_pair:
        node_pool_config['keyPair'] = key_pair

    result = cce_client.create_node_pool(region_id, cluster_id, node_pool_config)
    click.echo(f"✓ 节点池创建任务已提交")

    if output_format != 'table':
        format_output(result, output_format)


@cce.command('list-nodes')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--node-name', help='集群节点名称')
@click.pass_context
@handle_error
def list_nodes(ctx, region_id: str, cluster_id: str, node_name: Optional[str]):
    """查询节点列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_cluster_nodes(region_id, cluster_id, node_name)

    if output_format == 'table':
        nodes = result.get('returnObj', [])
        if nodes:
            click.echo(f"节点列表 (共 {len(nodes)} 个节点):")
            format_output(result, output_format)
        else:
            click.echo("未找到节点")
    else:
        format_output(result, output_format)


@cce.command('list-node-pools')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--page-size', default=10, help='每页条数')
@click.option('--page-no', default=1, help='当前页码')
@click.option('--node-pool-name', help='节点池名称')
@click.pass_context
@handle_error
def list_node_pools(ctx, region_id: str, cluster_id: str, page_size: int, page_no: int, node_pool_name: Optional[str]):
    """查询节点池列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_node_pools(region_id, cluster_id, page_size, page_no, node_pool_name)

    if output_format == 'table':
        page_data = result.get('returnObj', {})
        node_pools = page_data.get('records', [])
        total = page_data.get('total', 0)
        current = page_data.get('current', 1)

        if node_pools:
            click.echo(f"节点池列表 (共 {total} 个节点池，第 {current} 页):")
            format_output(result, output_format)
        else:
            click.echo("未找到节点池")
    else:
        format_output(result, output_format)


@cce.command('get-node-pool')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--node-pool-id', required=True, help='节点池ID')
@click.pass_context
@handle_error
def get_node_pool(ctx, region_id: str, cluster_id: str, node_pool_id: str):
    """查询节点池详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_node_pool(region_id, cluster_id, node_pool_id)

    if output_format == 'table':
        node_pool_info = result.get('returnObj', {})
        if node_pool_info:
            click.echo(f"节点池详情:")
            format_output(result, output_format)
        else:
            click.echo("未找到节点池信息")
    else:
        format_output(result, output_format)


@cce.command('get-node-detail')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--node-id', required=True, help='节点ID')
@click.pass_context
@handle_error
def get_node_detail(ctx, region_id: str, cluster_id: str, node_id: str):
    """查询节点详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_node_detail(region_id, cluster_id, node_id)

    if output_format == 'table':
        node_info = result.get('returnObj', {})
        if node_info:
            click.echo(f"节点详情:")
            format_output(result, output_format)
        else:
            click.echo("未找到节点信息")
    else:
        format_output(result, output_format)


@nodepool.command('scale')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--nodepool-id', required=True, help='节点池ID')
@click.option('--desired-node-count', required=True, type=int, help='期望节点数')
@click.option('--current-node-count', type=int, help='当前节点数')
@click.pass_context
@handle_error
def scale_nodepool(ctx, region_id: str, cluster_id: str, nodepool_id: str,
                  desired_node_count: int, current_node_count: Optional[int]):
    """节点池扩缩容"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.scale_node_pool(region_id, cluster_id, nodepool_id,
                                       desired_node_count, current_node_count)

    click.echo(f"✓ 节点池扩缩容任务已提交: 期望节点数 {desired_node_count}")

    if output_format != 'table':
        format_output(result, output_format)


# ========== 弹性伸缩命令 ==========

@cce.group()
def autoscaling():
    """弹性伸缩管理"""
    pass


@autoscaling.command('create-policy')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--policy-name', required=True, help='策略名称')
@click.option('--nodepool-id', required=True, help='节点池ID')
@click.option('--min-replicas', required=True, type=int, help='最小副本数')
@click.option('--max-replicas', required=True, type=int, help='最大副本数')
@click.option('--target-cpu-utilization', type=float, help='目标CPU使用率')
@click.pass_context
@handle_error
def create_autoscaling_policy(ctx, region_id: str, cluster_id: str, policy_name: str,
                             nodepool_id: str, min_replicas: int, max_replicas: int,
                             target_cpu_utilization: Optional[float]):
    """创建节点弹性伸缩策略"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)

    scaling_policy = {
        'policyName': policy_name,
        'nodePoolId': nodepool_id,
        'minReplicas': min_replicas,
        'maxReplicas': max_replicas
    }

    if target_cpu_utilization:
        scaling_policy['metrics'] = [
            {
                'type': 'RESOURCE',
                'resource': {
                    'name': 'cpu',
                    'target': {
                        'type': 'Utilization',
                        'averageUtilization': int(target_cpu_utilization * 100)
                    }
                }
            }
        ]

    result = cce_client.create_auto_scaling_policy(region_id, cluster_id, scaling_policy)
    click.echo(f"✓ 弹性伸缩策略创建成功: {policy_name}")

    if output_format != 'table':
        format_output(result, output_format)


# ========== Kubernetes资源查询命令 ==========

@cce.command('list-deployments')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_deployments(ctx, region_id: str, cluster_id: str, namespace: str,
                     label_selector: Optional[str], field_selector: Optional[str]):
    """查询Deployment列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_deployments(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        deployments_info = result.get('returnObj', '')
        if deployments_info:
            click.echo(f"命名空间 '{namespace}' 中的Deployment列表:")
            # Kubernetes资源通常返回YAML格式，需要特殊处理显示
            if isinstance(deployments_info, str):
                click.echo(deployments_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Deployment")
    else:
        format_output(result, output_format)


@cce.command('get-deployment')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--deployment-name', required=True, help='Deployment名称')
@click.pass_context
@handle_error
def get_deployment(ctx, region_id: str, cluster_id: str, namespace: str, deployment_name: str):
    """查询Deployment详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_deployment(region_id, cluster_id, namespace, deployment_name)

    if output_format == 'table':
        deployment_info = result.get('returnObj', '')
        if deployment_info:
            click.echo(f"Deployment '{deployment_name}' 详情:")
            if isinstance(deployment_info, str):
                click.echo(deployment_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Deployment")
    else:
        format_output(result, output_format)


@cce.command('list-pods')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_pods(ctx, region_id: str, cluster_id: str, namespace: str,
              label_selector: Optional[str], field_selector: Optional[str]):
    """查询Pod列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_pods(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        pods_info = result.get('returnObj', '')
        if pods_info:
            click.echo(f"命名空间 '{namespace}' 中的Pod列表:")
            if isinstance(pods_info, str):
                click.echo(pods_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Pod")
    else:
        format_output(result, output_format)


@cce.command('list-daemonsets')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_daemonsets(ctx, region_id: str, cluster_id: str, namespace: str,
                   label_selector: Optional[str], field_selector: Optional[str]):
    """查询指定集群下的DaemonSet列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_daemonsets(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        daemonsets_info = result.get('returnObj', '')
        if daemonsets_info:
            click.echo(f"集群 '{cluster_id}' 命名空间 '{namespace}' 中的DaemonSet列表:")
            if isinstance(daemonsets_info, str):
                click.echo(daemonsets_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到DaemonSet")
    else:
        format_output(result, output_format)


@cce.command('get-daemonset')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--daemonset-name', required=True, help='DaemonSet名称')
@click.pass_context
@handle_error
def get_daemonset(ctx, region_id: str, cluster_id: str, namespace: str, daemonset_name: str):
    """查询指定集群下的DaemonSet详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_daemonset(region_id, cluster_id, namespace, daemonset_name)

    if output_format == 'table':
        daemonset_info = result.get('returnObj', '')
        if daemonset_info:
            click.echo(f"集群 '{cluster_id}' 命名空间 '{namespace}' 中DaemonSet '{daemonset_name}' 的详情:")
            if isinstance(daemonset_info, str):
                click.echo(daemonset_info)
            else:
                format_output(result, output_format)
        else:
            click.echo(f"未找到DaemonSet '{daemonset_name}'")
    else:
        format_output(result, output_format)


@cce.command('list-replicasets')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_replicasets(ctx, region_id: str, cluster_id: str, namespace: str,
                     label_selector: Optional[str], field_selector: Optional[str]):
    """获取指定集群下的ReplicaSet资源列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_replicasets(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        replicasets_info = result.get('returnObj', '')
        if replicasets_info:
            click.echo(f"集群 '{cluster_id}' 命名空间 '{namespace}' 中的ReplicaSet列表:")
            if isinstance(replicasets_info, str):
                click.echo(replicasets_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到ReplicaSet")
    else:
        format_output(result, output_format)


@cce.command('get-replicaset')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--replicaset-name', required=True, help='ReplicaSet名称')
@click.pass_context
@handle_error
def get_replicaset(ctx, region_id: str, cluster_id: str, namespace: str, replicaset_name: str):
    """查询指定集群下的ReplicaSet资源详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_replicaset(region_id, cluster_id, namespace, replicaset_name)

    if output_format == 'table':
        replicaset_info = result.get('returnObj', '')
        if replicaset_info:
            click.echo(f"ReplicaSet '{replicaset_name}' 详情:")
            if isinstance(replicaset_info, str):
                click.echo(replicaset_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到ReplicaSet")
    else:
        format_output(result, output_format)


@cce.command('get-pod')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--pod-name', required=True, help='Pod名称')
@click.pass_context
@handle_error
def get_pod(ctx, region_id: str, cluster_id: str, namespace: str, pod_name: str):
    """查询指定Pod的详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_pod(region_id, cluster_id, namespace, pod_name)

    if output_format == 'table':
        pod_info = result.get('returnObj', '')
        if pod_info:
            click.echo(f"Pod '{pod_name}' 在命名空间 '{namespace}' 中的详情:")
            click.echo("=" * 80)
            if isinstance(pod_info, str):
                click.echo(pod_info)
            else:
                format_output(result, output_format)
        else:
            click.echo(f"未找到Pod '{pod_name}' 在命名空间 '{namespace}' 中")
    else:
        format_output(result, output_format)


@cce.command('list-services')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_services(ctx, region_id: str, cluster_id: str, namespace: str,
                  label_selector: Optional[str], field_selector: Optional[str]):
    """查询Service列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_services(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        services_info = result.get('returnObj', '')
        if services_info:
            click.echo(f"命名空间 '{namespace}' 中的Service列表:")
            if isinstance(services_info, str):
                click.echo(services_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Service")
    else:
        format_output(result, output_format)


@cce.command('get-service')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--service-name', required=True, help='Service名称')
@click.pass_context
@handle_error
def get_service(ctx, region_id: str, cluster_id: str, namespace: str, service_name: str):
    """查询Service详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_service(region_id, cluster_id, namespace, service_name)

    if output_format == 'table':
        service_info = result.get('returnObj', '')
        if service_info:
            click.echo(f"Service '{service_name}' 详情:")
            if isinstance(service_info, str):
                click.echo(service_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Service")
    else:
        format_output(result, output_format)


@cce.command('list-jobs')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_jobs(ctx, region_id: str, cluster_id: str, namespace: str,
              label_selector: Optional[str], field_selector: Optional[str]):
    """查询Job列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_jobs(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        jobs_info = result.get('returnObj', '')
        if jobs_info:
            click.echo(f"命名空间 '{namespace}' 中的Job列表:")
            if isinstance(jobs_info, str):
                click.echo(jobs_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Job")
    else:
        format_output(result, output_format)


@cce.command('get-job')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--job-name', required=True, help='Job名称')
@click.pass_context
@handle_error
def get_job(ctx, region_id: str, cluster_id: str, namespace: str, job_name: str):
    """查询Job详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_job(region_id, cluster_id, namespace, job_name)

    if output_format == 'table':
        job_info = result.get('returnObj', '')
        if job_info:
            click.echo(f"Job '{job_name}' 详情:")
            if isinstance(job_info, str):
                click.echo(job_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到Job")
    else:
        format_output(result, output_format)


@cce.command('list-statefulsets')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='Kubernetes标签选择器')
@click.option('--field-selector', help='Kubernetes字段选择器')
@click.pass_context
@handle_error
def list_statefulsets(ctx, region_id: str, cluster_id: str, namespace: str,
                      label_selector: Optional[str], field_selector: Optional[str]):
    """查询StatefulSet列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_statefulsets(region_id, cluster_id, namespace, label_selector, field_selector)

    if output_format == 'table':
        statefulsets_info = result.get('returnObj', '')
        if statefulsets_info:
            click.echo(f"命名空间 '{namespace}' 中的StatefulSet列表:")
            if isinstance(statefulsets_info, str):
                click.echo(statefulsets_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到StatefulSet")
    else:
        format_output(result, output_format)


@cce.command('get-statefulset')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--statefulset-name', required=True, help='StatefulSet名称')
@click.pass_context
@handle_error
def get_statefulset(ctx, region_id: str, cluster_id: str, namespace: str, statefulset_name: str):
    """查询StatefulSet详情"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_statefulset(region_id, cluster_id, namespace, statefulset_name)

    if output_format == 'table':
        statefulset_info = result.get('returnObj', '')
        if statefulset_info:
            click.echo(f"StatefulSet '{statefulset_name}' 详情:")
            if isinstance(statefulset_info, str):
                click.echo(statefulset_info)
            else:
                format_output(result, output_format)
        else:
            click.echo("未找到StatefulSet")
    else:
        format_output(result, output_format)


# ========== 任务管理命令 ==========

@cce.command('list-tasks')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--page-number', default=1, help='分页查询页数，默认为1')
@click.option('--page-size', default=10, help='每页显示数量，默认为10')
@click.pass_context
@handle_error
def list_tasks(ctx, region_id: str, cluster_id: str, page_number: int, page_size: int):
    """查询任务列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_tasks(region_id, cluster_id, page_number, page_size)

    if output_format == 'table':
        # 检查返回数据结构
        return_obj = result.get('returnObj')
        if isinstance(return_obj, list):
            # 如果returnObj是数组，直接处理
            tasks = return_obj
            if tasks:
                click.echo(f"任务列表 (共 {len(tasks)} 个任务，第 {page_number} 页):")
                for task in tasks:
                    click.echo(f"任务ID: {task.get('taskId', 'N/A')}")
                    click.echo(f"  类型: {task.get('taskType', 'N/A')}")
                    click.echo(f"  状态: {task.get('taskStatus', 'N/A')}")
                    click.echo(f"  内容: {task.get('taskContent', 'N/A')}")
                    click.echo(f"  结果: {task.get('taskResult', 'N/A')}")
                    click.echo(f"  创建时间: {task.get('createdTime', 'N/A')}")
                    click.echo("-" * 50)
            else:
                click.echo("未找到任务")
        elif isinstance(return_obj, dict):
            # 如果returnObj是对象（包含分页信息）
            tasks = return_obj.get('records', [])
            total = return_obj.get('total', 0)
            current = return_obj.get('current', page_number)

            if tasks:
                click.echo(f"任务列表 (共 {total} 个任务，第 {current} 页):")
                for task in tasks:
                    click.echo(f"任务ID: {task.get('taskId', 'N/A')}")
                    click.echo(f"  类型: {task.get('taskType', 'N/A')}")
                    click.echo(f"  状态: {task.get('taskStatus', 'N/A')}")
                    click.echo(f" 内容: {task.get('taskContent', 'N/A')}")
                    click.echo(f"  结果: {task.get('taskResult', 'N/A')}")
                    click.echo(f" 创建时间: {task.get('createdTime', 'N/A')}")
                    click.echo("-" * 50)
            else:
                click.echo("未找到任务")
        else:
            # 如果returnObj不是预期的格式，显示整个结果
            format_output(result, output_format)
    else:
        format_output(result, output_format)


@cce.command('list-task-events')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--task-id', required=True, help='任务ID')
@click.option('--page-number', default=1, help='分页查询页数，默认为1')
@click.option('--page-size', default=10, help='每页显示数量，默认为10')
@click.pass_context
@handle_error
def list_task_events(ctx, region_id: str, cluster_id: str, task_id: str, page_number: int, page_size: int):
    """查询指定集群任务事件列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_task_events(region_id, cluster_id, task_id, page_number, page_size)

    if output_format == 'table':
        return_obj = result.get('returnObj', {})
        events = return_obj.get('records', [])
        total = return_obj.get('total', 0)
        current = return_obj.get('current', page_number)

        if events:
            click.echo(f"任务事件列表 (任务ID: {task_id}, 共 {total} 个事件，第 {current} 页):")
            for event in events:
                click.echo(f"事件ID: {event.get('eventId', 'N/A')}")
                click.echo(f"  事件类型: {event.get('eventType', 'N/A')}")
                click.echo(f"  事件源: {event.get('source', 'N/A')}")
                click.echo(f"  关联对象: {event.get('subject', 'N/A')}")
                click.echo(f"  事件内容: {event.get('eventMessage', 'N/A')}")
                click.echo(f"  创建时间: {event.get('createdTime', 'N/A')}")
                click.echo("-" * 50)
        else:
            click.echo(f"未找到任务事件 (任务ID: {task_id})")
    else:
        format_output(result, output_format)


@autoscaling.command('list-policies')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--page-size', default=10, help='分页大小')
@click.option('--page-no', default=1, help='页码')
@click.pass_context
@handle_error
def list_autoscaling_policies(ctx, region_id: str, cluster_id: str, page_size: int, page_no: int):
    """查询节点弹性伸缩策略列表"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_auto_scaling_policies(region_id, cluster_id, page_size, page_no)

    if output_format == 'table':
        policies = result.get('returnObj', [])
        if policies:
            click.echo(f"弹性伸缩策略列表 (共 {len(policies)} 个策略):")
            format_output(result, output_format)
        else:
            click.echo("未找到弹性伸缩策略")
    else:
        format_output(result, output_format)


# ========== 其他功能命令 ==========

@cce.group()
def tag():
    """标签管理"""
    pass


@tag.command('bind')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--tag-key', required=True, help='标签键')
@click.option('--tag-value', required=True, help='标签值')
@click.pass_context
@handle_error
def bind_cluster_tag(ctx, region_id: str, cluster_id: str, tag_key: str, tag_value: str):
    """绑定集群标签"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)

    tag_config = {
        'tagKey': tag_key,
        'tagValue': tag_value
    }

    result = cce_client.bind_cluster_tag(region_id, cluster_id, tag_config)
    click.echo(f"✓ 集群标签绑定成功: {tag_key}={tag_value}")

    if output_format != 'table':
        format_output(result, output_format)


@cce.command('query-task')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--task-id', required=True, help='任务ID')
@click.pass_context
@handle_error
def query_async_task(ctx, region_id: str, task_id: str):
    """查询异步任务状态"""
    client = ctx.obj['client']
    output_format = ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.query_async_task(region_id, task_id)

    if output_format == 'table':
        task_info = result.get('returnObj', {})
        if task_info:
            click.echo(f"任务详情:")
            format_output(result, output_format)
        else:
            click.echo("未找到任务信息")
    else:
        format_output(result, output_format)


# ========== ConfigMap配置管理命令 ==========

@cce.group()
def configmap():
    """ConfigMap配置管理"""
    pass


@configmap.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--label-selector', help='标签选择器，用于过滤资源')
@click.option('--field-selector', help='字段选择器，用于过滤资源')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_config_maps(ctx, region_id: str, cluster_id: str, namespace: str,
                    label_selector: Optional[str], field_selector: Optional[str],
                    output: Optional[str]):
    """
    查询ConfigMap列表

    示例:
    \b
    # 查询指定命名空间下的所有ConfigMap
    cce configmap list --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default

    # 使用标签过滤
    cce configmap list --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default \\
      --label-selector app=nginx

    # 使用字段过滤
    cce configmap list --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default \\
      --field-selector metadata.namespace=default

    # JSON格式输出
    cce configmap list --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default \\
      --output json
    """
    client = ctx.obj['client']
    output_format = output or ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.list_config_maps(
        region_id=region_id,
        cluster_id=cluster_id,
        namespace_name=namespace,
        label_selector=label_selector,
        field_selector=field_selector
    )

    # 根据输出格式显示结果
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        # table format - 显示ConfigMap列表摘要信息
        return_obj = result.get('returnObj', '')
        if return_obj:
            click.echo("ConfigMap列表 (YAML格式):")
            click.echo("=" * 80)
            # 显示YAML内容，自动换行
            import textwrap
            wrapped_text = textwrap.fill(return_obj, width=80)
            click.echo(wrapped_text)
        else:
            click.echo("未找到ConfigMap")


@configmap.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-id', required=True, help='集群ID')
@click.option('--namespace', required=True, help='命名空间名称')
@click.option('--name', required=True, help='ConfigMap名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_config_map_detail(ctx, region_id: str, cluster_id: str, namespace: str,
                         name: str, output: Optional[str]):
    """
    查询ConfigMap详情

    示例:
    \b
    # 查看ConfigMap详情
    cce configmap show --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default \\
      --name example-configmap

    # JSON格式输出
    cce configmap show --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default \\
      --name example-configmap --output json

    # YAML格式输出
    cce configmap show --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-id 9a0bc858cafd4090a45333f0c308fd5f --namespace default \\
      --name example-configmap --output yaml
    """
    client = ctx.obj['client']
    output_format = output or ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.get_config_map_detail(
        region_id=region_id,
        cluster_id=cluster_id,
        namespace_name=namespace,
        configmap_name=name
    )

    # 根据输出格式显示结果
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        # table format - 显示ConfigMap详情
        return_obj = result.get('returnObj', '')
        if return_obj:
            click.echo(f"ConfigMap详情: {name}")
            click.echo("=" * 80)
            click.echo(f"命名空间: {namespace}")
            click.echo(f"集群ID: {cluster_id}")
            click.echo(f"区域ID: {region_id}")
            click.echo()
            click.echo("YAML配置内容:")
            click.echo("-" * 80)
            # 显示YAML内容，自动换行
            import textwrap
            wrapped_text = textwrap.fill(return_obj, width=80)
            click.echo(wrapped_text)
        else:
            click.echo("未找到ConfigMap详情")


# ========== 集群日志管理命令 ==========

@cce.group()
def logs():
    """集群日志管理"""
    pass


@logs.command('query')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cluster-name', required=True, help='集群名称')
@click.option('--page-now', type=int, default=1, help='当前页码，默认为1')
@click.option('--page-size', type=int, default=10, help='每页条数，默认为10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_cluster_logs(ctx, region_id: str, cluster_name: str,
                      page_now: int, page_size: int, output: Optional[str]):
    """
    查询集群日志

    示例:
    \b
    # 查询集群日志（默认第一页，每页10条）
    cce logs query --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-name ccse-demo

    # 查询指定页的日志
    cce logs query --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-name ccse-demo --page-now 2 --page-size 20

    # JSON格式输出
    cce logs query --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-name ccse-demo --output json

    # 查询更多日志条数
    cce logs query --region-id bb9fdb42056f11eda1610242ac110002 \\
      --cluster-name ccse-demo --page-size 50
    """
    client = ctx.obj['client']
    output_format = output or ctx.obj['output']

    cce_client = CCEClient(client)
    result = cce_client.query_cluster_logs(
        region_id=region_id,
        cluster_name=cluster_name,
        page_now=page_now,
        page_size=page_size
    )

    # 根据输出格式显示结果
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        # table format - 显示日志列表
        return_obj = result.get('returnObj', {})
        if return_obj:
            records = return_obj.get('records', [])
            total = return_obj.get('total', 0)
            current = return_obj.get('current', page_now)
            pages = return_obj.get('pages', 0)
            size = return_obj.get('size', page_size)

            # 显示分页信息
            click.echo(f"集群日志: {cluster_name}")
            click.echo("=" * 100)
            click.echo(f"分页信息: 第{current}页，共{pages}页，总计{total}条记录，本页{len(records)}条")
            click.echo()

            if records:
                # 表格头
                click.echo(f"{'序号':<4} {'时间':<20} {'日志内容':<70}")
                click.echo("-" * 100)

                # 显示日志记录
                for i, record in enumerate(records, 1):
                    created_time = record.get('createdTime', '')
                    message = record.get('message', '')

                    # 截断过长的日志内容
                    if len(message) > 65:
                        display_message = message[:62] + "..."
                    else:
                        display_message = message

                    click.echo(f"{i:<4} {created_time:<20} {display_message:<70}")

                click.echo("-" * 100)
                click.echo()

                # 显示日志类型统计
                log_types = {}
                for record in records:
                    message = record.get('message', '')
                    if '[' in message and ']' in message:
                        # 提取日志类型，如 [plugins], [cluster] 等
                        start = message.find('[')
                        end = message.find(']', start)
                        if start != -1 and end != -1:
                            log_type = message[start:end + 1]
                            log_types[log_type] = log_types.get(log_type, 0) + 1

                if log_types:
                    click.echo("日志类型统计:")
                    for log_type, count in sorted(log_types.items()):
                        click.echo(f"  {log_type}: {count}条")

            else:
                click.echo("未找到日志记录")
        else:
            click.echo("未找到日志数据")


if __name__ == '__main__':
    cce()