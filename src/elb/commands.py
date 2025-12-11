"""
弹性负载均衡命令行接口
"""

import click
from functools import wraps
from typing import Optional
from core import CTYUNAPIError
from utils import OutputFormatter, ValidationUtils, logger
from elb import ELBClient


def handle_error(func):
    """错误处理装饰器"""
    @wraps(func)
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


def get_elb_client(ctx) -> ELBClient:
    """获取ELB客户端"""
    client = ctx.obj['client']
    return ELBClient(client)


@click.group()
@click.pass_context
def elb(ctx):
    """
    弹性负载均衡(ELB) - 负载均衡器、目标组、监听器管理
    """
    pass


@elb.group()
def loadbalancer():
    """负载均衡器管理"""
    pass


@loadbalancer.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--ids', help='负载均衡ID列表，以,分隔')
@click.option('--resource-type', type=click.Choice(['internal', 'external']), help='资源类型。internal：内网负载均衡，external：公网负载均衡')
@click.option('--name', help='负载均衡器名称')
@click.option('--subnet-id', help='子网ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_load_balancers(ctx, region_id: str, ids: Optional[str], resource_type: Optional[str],
                       name: Optional[str], subnet_id: Optional[str], output: Optional[str]):
    """
    查看负载均衡实例列表

    示例:
    \b
    # 查询指定区域的所有负载均衡器
    elb loadbalancer list --region-id 200000001852

    # 按名称过滤
    elb loadbalancer list --region-id 200000001852 --name my-elb

    # 查询公网负载均衡器
    elb loadbalancer list --region-id 200000001852 --resource-type external

    # 按子网ID过滤
    elb loadbalancer list --region-id 200000001852 --subnet-id subnet-xxx

    # 按ID列表查询
    elb loadbalancer list --region-id 200000001852 --ids "lb-xxx,lb-yyy"
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.list_load_balancers(
        region_id=region_id,
        ids=ids,
        resource_type=resource_type,
        name=name,
        subnet_id=subnet_id
    )

    # 处理输出格式
    load_balancers = result.get('returnObj', [])

    if not load_balancers:
        click.echo("未找到负载均衡实例")
        return

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式
        # 将load_balancers转换为适合format_table的格式
        formatted_data = []
        for lb in load_balancers:
            # 获取公网IP
            eip_addresses = []
            eip_info = lb.get('eipInfo', [])
            if isinstance(eip_info, list):
                for eip in eip_info:
                    if isinstance(eip, dict):
                        eip_addr = eip.get('eipAddress', '')
                        if eip_addr:
                            eip_addresses.append(eip_addr)

            formatted_data.append({
                'ID': lb.get('ID', ''),
                '名称': lb.get('name', ''),
                '类型': lb.get('resourceType', ''),
                '状态': lb.get('status', ''),
                '内网VIP': lb.get('privateIpAddress', ''),
                '公网IP': ', '.join(eip_addresses) if eip_addresses else '无',
                'VPC': lb.get('vpcID', ''),
                '子网': lb.get('subnetID', ''),
                '规格': lb.get('slaName', '')
            })

        table = OutputFormatter.format_table(formatted_data)
        click.echo(f"负载均衡实例列表 (共 {len(load_balancers)} 个)")
        click.echo(table)


@loadbalancer.command('get')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--loadbalancer-id', required=True, help='负载均衡器ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_load_balancer(ctx, region_id: str, loadbalancer_id: str, output: Optional[str]):
    """
    查看负载均衡实例详情

    示例:
    \b
    # 查询指定负载均衡器的详细信息
    elb loadbalancer get --region-id 200000001852 --loadbalancer-id lb-xxxxxxxx

    # JSON格式输出
    elb loadbalancer get --region-id 200000001852 --loadbalancer-id lb-xxxxxxxx --output json
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.get_load_balancer(
        region_id=region_id,
        elb_id=loadbalancer_id
    )

    # 处理输出格式
    return_obj = result.get('returnObj', [])
    if not return_obj:
        click.echo("未找到指定的负载均衡实例")
        return

    # 获取第一个元素（详情API返回的是单元素数组）
    lb_detail = return_obj[0]

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式 - 显示详细信息
        click.echo(f"负载均衡实例详情: {lb_detail.get('name', '')}")
        click.echo("=" * 80)

        # 基本信息
        basic_info = [
            ('ID', lb_detail.get('ID', '')),
            ('名称', lb_detail.get('name', '')),
            ('描述', lb_detail.get('description', '')),
            ('状态', lb_detail.get('status', '')),
            ('管理状态', lb_detail.get('adminStatus', '')),
            ('类型', lb_detail.get('resourceType', '')),
            ('规格', lb_detail.get('slaName', '')),
            ('项目ID', lb_detail.get('projectID', '')),
        ]

        click.echo("基本信息:")
        for key, value in basic_info:
            click.echo(f"  {key}: {value}")

        # 网络信息
        click.echo("\n网络信息:")
        network_info = [
            ('区域ID', lb_detail.get('regionID', '')),
            ('可用区', lb_detail.get('azName', '无') or '无'),
            ('VPC ID', lb_detail.get('vpcID', '')),
            ('子网ID', lb_detail.get('subnetID', '')),
            ('端口ID', lb_detail.get('portID', '')),
            ('内网VIP', lb_detail.get('privateIpAddress', '')),
            ('IPv6地址', lb_detail.get('ipv6Address', '无') or '无'),
        ]

        for key, value in network_info:
            click.echo(f"  {key}: {value}")

        # 公网IP信息
        eip_info = lb_detail.get('eipInfo', [])
        if eip_info:
            click.echo("\n公网IP信息:")
            for i, eip in enumerate(eip_info, 1):
                if isinstance(eip, dict):
                    click.echo(f"  IP {i}:")
                    click.echo(f"    地址: {eip.get('eipAddress', '')}")
                    click.echo(f"    带宽: {eip.get('bandwidth', '')} Mbps")
                    click.echo(f"    EIP ID: {eip.get('eipID', '')}")
        else:
            click.echo("\n公网IP信息: 无")

        # 其他信息
        other_info = [
            ('计费方式', lb_detail.get('billingMethod', '')),
            ('删除保护', '是' if lb_detail.get('deleteProtection') else '否'),
            ('创建时间', lb_detail.get('createdTime', '')),
            ('更新时间', lb_detail.get('updatedTime', '')),
        ]

        click.echo("\n其他信息:")
        for key, value in other_info:
            click.echo(f"  {key}: {value}")


@elb.group()
def targetgroup():
    """目标组管理"""
    pass


@targetgroup.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--ids', help='后端主机组ID列表，以,分隔')
@click.option('--vpc-id', help='VPC ID')
@click.option('--health-check-id', help='健康检查ID')
@click.option('--name', help='后端主机组名称')
@click.option('--client-token', help='客户端存根，用于保证订单幂等性')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_target_groups(ctx, region_id: str, ids: Optional[str], vpc_id: Optional[str],
                        health_check_id: Optional[str], name: Optional[str],
                        client_token: Optional[str], output: Optional[str]):
    """
    查看后端主机组列表

    示例:
    \b
    # 查询指定区域的所有目标组
    elb targetgroup list --region-id 200000001852

    # 按名称过滤
    elb targetgroup list --region-id 200000001852 --name my-targetgroup

    # 按VPC过滤
    elb targetgroup list --region-id 200000001852 --vpc-id vpc-xxx

    # 按健康检查ID过滤
    elb targetgroup list --region-id 200000001852 --health-check-id hc-xxx

    # 按ID列表查询
    elb targetgroup list --region-id 200000001852 --ids "tg-xxx,tg-yyy"
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.list_target_groups(
        region_id=region_id,
        ids=ids,
        vpc_id=vpc_id,
        health_check_id=health_check_id,
        name=name,
        client_token=client_token
    )

    # 处理输出格式
    target_groups = result.get('returnObj', [])

    if not target_groups:
        click.echo("未找到后端主机组")
        return

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式
        # 将target_groups转换为适合format_table的格式
        formatted_data = []
        for tg in target_groups:
            # 获取会话保持信息
            session_sticky = tg.get('sessionSticky', {})
            session_sticky_mode = session_sticky.get('sessionStickyMode', 'CLOSE')

            formatted_data.append({
                'ID': tg.get('ID', ''),
                '名称': tg.get('name', ''),
                '描述': tg.get('description', ''),
                '状态': tg.get('status', ''),
                '协议': tg.get('protocol', ''),
                '调度算法': tg.get('algorithm', ''),
                '会话保持': session_sticky_mode,
                'VPC': tg.get('vpcID', ''),
                '健康检查': tg.get('healthCheckID', '') or '无',
                '创建时间': tg.get('createdTime', '')
            })

        table = OutputFormatter.format_table(formatted_data)
        click.echo(f"后端主机组列表 (共 {len(target_groups)} 个)")
        click.echo(table)


@targetgroup.command('get')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--targetgroup-id', required=True, help='目标组ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_target_group(ctx, region_id: str, targetgroup_id: str, output: Optional[str]):
    """
    查看后端主机组详情

    示例:
    \b
    # 查询指定目标组的详细信息
    elb targetgroup get --region-id 200000001852 --targetgroup-id tg-xxxxxxxx

    # JSON格式输出
    elb targetgroup get --region-id 200000001852 --targetgroup-id tg-xxxxxxxx --output json
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.get_target_group(
        region_id=region_id,
        target_group_id=targetgroup_id
    )

    # 处理输出格式
    return_obj = result.get('returnObj', [])
    if not return_obj:
        click.echo("未找到指定的后端主机组")
        return

    # 获取第一个元素（详情API返回的是单元素数组）
    tg_detail = return_obj[0]

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式 - 显示详细信息
        click.echo(f"后端主机组详情: {tg_detail.get('name', '')}")
        click.echo("=" * 80)

        # 基本信息
        basic_info = [
            ('ID', tg_detail.get('ID', '')),
            ('名称', tg_detail.get('name', '')),
            ('描述', tg_detail.get('description', '')),
            ('状态', tg_detail.get('status', '')),
            ('协议', tg_detail.get('protocol', '')),
            ('调度算法', tg_detail.get('algorithm', '')),
            ('项目ID', tg_detail.get('projectID', '')),
        ]

        click.echo("基本信息:")
        for key, value in basic_info:
            click.echo(f"  {key}: {value}")

        # 网络信息
        click.echo("\n网络信息:")
        network_info = [
            ('区域ID', tg_detail.get('regionID', '')),
            ('可用区', tg_detail.get('azName', '无') or '无'),
            ('VPC ID', tg_detail.get('vpcID', '')),
            ('子网ID', tg_detail.get('subnetID', '')),
        ]

        for key, value in network_info:
            click.echo(f"  {key}: {value}")

        # 会话保持配置
        session_sticky = tg_detail.get('sessionSticky', {})
        if session_sticky:
            click.echo("\n会话保持配置:")
            sticky_info = [
                ('会话保持模式', session_sticky.get('sessionStickyMode', 'CLOSE')),
                ('会话保持时长', f"{session_sticky.get('sessionStickyTimeOut', 0)}秒"),
                ('类型', session_sticky.get('type', '')),
                ('Cookie名称', session_sticky.get('sessionStickyCookieName', '无') or '无'),
            ]
            for key, value in sticky_info:
                click.echo(f"  {key}: {value}")
        else:
            click.echo("\n会话保持配置: 未启用")

        # 健康检查配置
        health_check = tg_detail.get('healthCheck', {})
        if health_check:
            click.echo("\n健康检查配置:")
            health_info = [
                ('健康检查ID', tg_detail.get('healthCheckID', '') or '无'),
                ('检查间隔', f"{health_check.get('intervalTime', 0)}秒"),
                ('超时时间', f"{health_check.get('timeout', 0)}秒"),
                ('健康阈值', health_check.get('healthyThreshold', '')),
                ('不健康阈值', health_check.get('unhealthyThreshold', '')),
                ('检查协议', health_check.get('protocol', '')),
                ('检查端口', health_check.get('port', '')),
                ('检查路径', health_check.get('uri', '') or '无'),
            ]
            for key, value in health_info:
                click.echo(f"  {key}: {value}")
        else:
            click.echo("\n健康检查配置: 无")

        # 端口配置
        click.echo("\n端口配置:")
        port_info = [
            ('前端端口', str(tg_detail.get('protocolPort', ''))),
            ('后端端口', str(tg_detail.get('backendPort', ''))),
        ]
        for key, value in port_info:
            click.echo(f"  {key}: {value}")

        # 其他信息
        other_info = [
            ('创建时间', tg_detail.get('createdTime', '')),
            ('更新时间', tg_detail.get('updatedTime', '')),
        ]

        click.echo("\n其他信息:")
        for key, value in other_info:
            click.echo(f"  {key}: {value}")


@targetgroup.group()
def targets():
    """后端主机管理"""
    pass


@targets.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--target-group-id', help='后端主机组ID')
@click.option('--ids', help='后端主机ID列表，以,分隔')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_targets(ctx, region_id: str, target_group_id: Optional[str], ids: Optional[str], output: Optional[str]):
    """
    查看后端主机列表

    示例:
    \b
    # 查询指定区域的所有后端主机
    elb targetgroup targets list --region-id 200000001852

    # 按目标组ID过滤
    elb targetgroup targets list --region-id 200000001852 --target-group-id tg-xxx

    # 按主机ID列表查询
    elb targetgroup targets list --region-id 200000001852 --ids "target-xxx,target-yyy"

    # 组合查询
    elb targetgroup targets list --region-id 200000001852 --target-group-id tg-xxx --ids "target-xxx"
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.list_targets(
        region_id=region_id,
        target_group_id=target_group_id,
        ids=ids
    )

    # 处理输出格式
    targets = result.get('returnObj', [])

    if not targets:
        click.echo("未找到后端主机")
        return

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式
        # 将targets转换为适合format_table的格式
        formatted_data = []
        for target in targets:
            formatted_data.append({
                'ID': target.get('ID', ''),
                '名称': target.get('description', ''),
                '目标组ID': target.get('targetGroupID', ''),
                '实例ID': target.get('instanceID', ''),
                '实例类型': target.get('instanceType', ''),
                'IP地址': target.get('targetIP', ''),
                '端口': target.get('protocolPort', ''),
                '权重': target.get('weight', ''),
                'IPv4状态': target.get('healthCheckStatus', ''),
                'IPv6状态': target.get('healthCheckStatusIpv6', ''),
                '状态': target.get('status', ''),
                '可用区': target.get('azName', '') or '无',
                '创建时间': target.get('createdTime', '')
            })

        table = OutputFormatter.format_table(formatted_data)
        click.echo(f"后端主机列表 (共 {len(targets)} 个)")
        click.echo(table)


@elb.group()
def listener():
    """监听器管理"""
    pass


@listener.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--ids', help='监听器ID列表，以,分隔')
@click.option('--name', help='监听器名称')
@click.option('--loadbalancer-id', help='负载均衡器ID')
@click.option('--access-control-id', help='访问控制ID')
@click.option('--project-id', help='项目ID，默认为0')
@click.option('--client-token', help='客户端存根，用于保证订单幂等性')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_listeners(ctx, region_id: str, ids: Optional[str], name: Optional[str],
                   loadbalancer_id: Optional[str], access_control_id: Optional[str],
                   project_id: Optional[str], client_token: Optional[str], output: Optional[str]):
    """
    查看监听器列表

    示例:
    \b
    # 查询指定区域的所有监听器
    elb listener list --region-id 200000001852

    # 查询指定负载均衡器的监听器
    elb listener list --region-id 200000001852 --loadbalancer-id lb-xxxxxxxx

    # 按名称过滤
    elb listener list --region-id 200000001852 --name my-listener

    # 按ID列表查询
    elb listener list --region-id 200000001852 --ids "listener-xxx,listener-yyy"

    # 按访问控制ID过滤
    elb listener list --region-id 200000001852 --access-control-id ac-xxx

    # JSON格式输出
    elb listener list --region-id 200000001852 --output json
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.list_listeners(
        region_id=region_id,
        ids=ids,
        name=name,
        load_balancer_id=loadbalancer_id,
        access_control_id=access_control_id,
        project_id=project_id or '0',
        client_token=client_token
    )

    # 处理输出格式
    listeners = result.get('returnObj', [])

    if not listeners:
        click.echo("未找到监听器")
        return

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式
        # 将listeners转换为适合format_table的格式
        formatted_data = []
        for listener in listeners:
            # 获取转发配置信息
            default_action = listener.get('defaultAction', {})
            target_groups = []
            if default_action.get('forwardConfig'):
                tg_list = default_action['forwardConfig'].get('targetGroups', [])
                target_groups = [f"{tg.get('targetGroupID', '')}({tg.get('weight', '')})" for tg in tg_list]

            formatted_data.append({
                'ID': listener.get('ID', ''),
                '名称': listener.get('name', ''),
                '描述': listener.get('description', ''),
                '协议': listener.get('protocol', ''),
                '端口': listener.get('protocolPort', ''),
                '状态': listener.get('status', ''),
                '负载均衡器': listener.get('loadBalancerID', ''),
                '访问控制': listener.get('accessControlType', ''),
                '证书ID': listener.get('certificateID', '') or '无',
                '目标组': ', '.join(target_groups) if target_groups else '无',
                '创建时间': listener.get('createdTime', '')
            })

        table = OutputFormatter.format_table(formatted_data)
        click.echo(f"监听器列表 (共 {len(listeners)} 个)")
        click.echo(table)


@listener.command('get')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--listener-id', required=True, help='监听器ID（推荐使用）')
@click.option('--id', help='监听器ID（即将废弃，不推荐使用）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_listener(ctx, region_id: str, listener_id: str, id: Optional[str], output: Optional[str]):
    """
    查看监听器详情

    示例:
    \b
    # 查询指定监听器的详细信息
    elb listener get --region-id 200000001852 --listener-id listener-xxxxxxxx

    # JSON格式输出
    elb listener get --region-id 200000001852 --listener-id listener-xxxxxxxx --output json

    # 注意：不推荐使用--id参数，建议使用--listener-id
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.get_listener(
        region_id=region_id,
        listener_id=listener_id,
        id_param=id
    )

    # 处理输出格式
    return_obj = result.get('returnObj', [])
    if not return_obj:
        click.echo("未找到指定的监听器")
        return

    # 获取第一个元素（详情API返回的是单元素数组）
    listener_detail = return_obj[0]

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式 - 显示详细信息
        click.echo(f"监听器详情: {listener_detail.get('name', '')}")
        click.echo("=" * 80)

        # 基本信息
        basic_info = [
            ('ID', listener_detail.get('ID', '')),
            ('名称', listener_detail.get('name', '')),
            ('描述', listener_detail.get('description', '')),
            ('状态', listener_detail.get('status', '')),
            ('协议', listener_detail.get('protocol', '')),
            ('监听端口', listener_detail.get('protocolPort', '')),
            ('负载均衡器ID', listener_detail.get('loadBalancerID', '')),
            ('项目ID', listener_detail.get('projectID', '')),
        ]

        click.echo("基本信息:")
        for key, value in basic_info:
            click.echo(f"  {key}: {value}")

        # 网络信息
        click.echo("\n网络信息:")
        network_info = [
            ('区域ID', listener_detail.get('regionID', '')),
            ('可用区', listener_detail.get('azName', '无') or '无'),
        ]

        for key, value in network_info:
            click.echo(f"  {key}: {value}")

        # 访问控制配置
        click.echo("\n访问控制配置:")
        access_control_info = [
            ('访问控制ID', listener_detail.get('accessControlID', '') or '无'),
            ('访问控制类型', listener_detail.get('accessControlType', '') or 'Close'),
            ('X-Forwarded-For', '是' if listener_detail.get('forwardedForEnabled') else '否'),
        ]

        for key, value in access_control_info:
            click.echo(f"  {key}: {value}")

        # 证书配置
        certificate_id = listener_detail.get('certificateID', '')
        if certificate_id:
            click.echo(f"\n证书配置:")
            click.echo(f"  证书ID: {certificate_id}")
            click.echo(f"  双向认证: {'是' if listener_detail.get('caEnabled') else '否'}")
            if listener_detail.get('clientCertificateID'):
                click.echo(f"  客户端证书ID: {listener_detail.get('clientCertificateID')}")
        else:
            click.echo("\n证书配置: 无")

        # 转发规则配置
        default_action = listener_detail.get('defaultAction', {})
        if default_action:
            click.echo(f"\n转发规则配置:")
            action_type = default_action.get('type', '')
            click.echo(f"  动作类型: {action_type}")

            if action_type == 'forward' and default_action.get('forwardConfig'):
                forward_config = default_action['forwardConfig']
                target_groups = forward_config.get('targetGroups', [])
                if target_groups:
                    click.echo(f"  目标组:")
                    for i, tg in enumerate(target_groups, 1):
                        tg_id = tg.get('targetGroupID', '')
                        weight = tg.get('weight', '')
                        click.echo(f"    {i}. {tg_id} (权重: {weight})")
                else:
                    click.echo(f"  目标组: 无")
            elif action_type == 'redirect':
                redirect_listener_id = default_action.get('redirectListenerID', '')
                click.echo(f"  重定向监听器ID: {redirect_listener_id or '无'}")
        else:
            click.echo("\n转发规则配置: 无")

        # 性能配置
        click.echo("\n性能配置:")
        performance_info = [
            ('连接超时时间', f"{listener_detail.get('establishTimeout', 0)}秒"),
            ('空闲超时时间', f"{listener_detail.get('idleTimeout', 0)}秒"),
            ('响应超时时间', f"{listener_detail.get('responseTimeout', 0)}秒"),
            ('CPS限制', listener_detail.get('cps', 0)),
            ('QPS限制', listener_detail.get('qps', 0)),
        ]

        for key, value in performance_info:
            click.echo(f"  {key}: {value}")

        # 功能开关
        click.echo("\n功能开关:")
        feature_info = [
            ('全端口转发', '是' if listener_detail.get('allPortForward') else '否'),
            ('Gzip压缩', '是' if listener_detail.get('gzip') else '否'),
            ('NAT64', '是' if listener_detail.get('nat64') else '否'),
        ]

        for key, value in feature_info:
            click.echo(f"  {key}: {value}")

        # 如果启用了全端口转发，显示端口范围
        if listener_detail.get('allPortForward'):
            click.echo("\n全端口转发配置:")
            port_info = [
                ('起始端口', listener_detail.get('startPort', 0)),
                ('结束端口', listener_detail.get('endPort', 0)),
            ]
            for key, value in port_info:
                click.echo(f"  {key}: {value}")

        # 时间信息
        click.echo("\n时间信息:")
        time_info = [
            ('创建时间', listener_detail.get('createdTime', '')),
            ('更新时间', listener_detail.get('updatedTime', '')),
        ]

        for key, value in time_info:
            click.echo(f"  {key}: {value}")


@elb.group()
def monitor():
    """监控数据管理"""
    pass


@monitor.command('realtime')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--device-ids', help='负载均衡ID列表，以,分隔')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=10, help='每页数据量，1-50，默认为10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_realtime_monitor(ctx, region_id: str, device_ids: Optional[str], page_no: int,
                          page_size: int, output: Optional[str]):
    """
    新查看负载均衡实时监控

    示例:
    \b
    # 查询指定区域的所有负载均衡实时监控
    elb monitor realtime --region-id 200000001852

    # 查询指定负载均衡器的实时监控
    elb monitor realtime --region-id 200000001852 --device-ids "lb-xxx,lb-yyy"

    # 分页查询
    elb monitor realtime --region-id 200000001852 --page-no 2 --page-size 20

    # JSON格式输出
    elb monitor realtime --region-id 200000001852 --output json
    """
    elb_client = get_elb_client(ctx)

    # 处理device_ids参数
    device_ids_list = None
    if device_ids:
        device_ids_list = [id.strip() for id in device_ids.split(',') if id.strip()]

    result = elb_client.query_realtime_monitor(
        region_id=region_id,
        device_ids=device_ids_list,
        page_no=page_no,
        page_size=page_size
    )

    # 处理输出格式
    return_obj = result.get('returnObj', {})
    monitors = return_obj.get('monitors', [])

    if not monitors:
        click.echo("未找到监控数据")
        return

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式
        # 将monitors转换为适合format_table的格式
        formatted_data = []
        for monitor in monitors:
            item_list = monitor.get('itemList', {})

            formatted_data.append({
                '负载均衡器ID': monitor.get('deviceID', ''),
                '最近更新': monitor.get('lastUpdated', ''),
                '请求频率': item_list.get('lbReqRate', ''),
                '出吞吐量': item_list.get('lbLbin', ''),
                '入带宽峰值': item_list.get('lbLbout', ''),
                'HTTP 2xx': item_list.get('lbHrsp2xx', ''),
                'HTTP 3xx': item_list.get('lbHrsp3xx', ''),
                'HTTP 4xx': item_list.get('lbHrsp4xx', ''),
                'HTTP 5xx': item_list.get('lbHrsp5xx', ''),
                '活跃连接数': item_list.get('lbActconn', ''),
                '采样时间': item_list.get('samplingTime', '')
            })

        table = OutputFormatter.format_table(formatted_data)

        # 显示分页信息
        total_count = return_obj.get('totalCount', 0)
        current_count = return_obj.get('currentCount', 0)
        total_page = return_obj.get('totalPage', 0)

        click.echo(f"负载均衡实时监控数据 (第{page_no}页，共{total_page}页，总计{total_count}条)")
        click.echo(table)


@monitor.command('history')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--device-ids', required=True, help='负载均衡ID列表，以,分隔')
@click.option('--metric-names', required=True, help='监控指标名称列表，以,分隔')
@click.option('--start-time', required=True, help='开始时间，格式: YYYY-mmm-dd HH:MM:SS')
@click.option('--end-time', required=True, help='结束时间，格式: YYYY-mmm-dd HH:MM:SS')
@click.option('--period', type=int, default=60, help='聚合周期，单位秒，默认60')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=10, help='每页数据量，1-50，默认为10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_history_monitor(ctx, region_id: str, device_ids: str, metric_names: str,
                        start_time: str, end_time: str, period: int, page_no: int,
                        page_size: int, output: Optional[str]):
    """
    新查看负载均衡历史监控

    示例:
    \b
    # 查询指定负载均衡器的历史监控
    elb monitor history --region-id 200000001852 \\
      --device-ids "lb-xxx" \\
      --metric-names "lb_req_rate,lb_lbin" \\
      --start-time "2025-12-01 00:00:00" \\
      --end-time "2025-12-02 00:00:00"

    # 查询多指标，设置聚合周期为4小时
    elb monitor history --region-id 200000001852 \\
      --device-ids "lb-xxx,lb-yyy" \\
      --metric-names "lb_req_rate,lb_lbin,lb_lbout" \\
      --start-time "2025-12-01 00:00:00" \\
      --end-time "2025-12-07 00:00:00" \\
      --period 14400

    # JSON格式输出
    elb monitor history --region-id 200000001852 \\
      --device-ids "lb-xxx" \\
      --metric-names "lb_req_rate" \\
      --start-time "2025-12-01 00:00:00" \\
      --end-time "2025-12-02 00:00:00" \\
      --output json

    常用监控指标:
    - lb_req_rate: 请求频率
    - lb_lbin: 出吞吐量
    - lb_lbout: 入带宽峰值
    - lb_actconn: HTTP活跃连接数
    - lb_newcreate: HTTP新创建的链接数
    - lb_inpkts: 入带宽峰值
    - lb_outpkts: 出带宽峰值
    - lb_hrsp_2xx: HTTP 2xx状态码统计数量
    - lb_hrsp_3xx: HTTP 3xx状态码统计数量
    - lb_hrsp_4xx: HTTP 4xx状态码统计数量
    - lb_hrsp_5xx: HTTP 5xx状态码统计数量
    """
    elb_client = get_elb_client(ctx)

    # 处理参数
    device_ids_list = [id.strip() for id in device_ids.split(',') if id.strip()]
    metric_names_list = [name.strip() for name in metric_names.split(',') if name.strip()]

    result = elb_client.query_history_monitor(
        region_id=region_id,
        device_ids=device_ids_list,
        metric_names=metric_names_list,
        start_time=start_time,
        end_time=end_time,
        period=period,
        page_no=page_no,
        page_size=page_size
    )

    # 处理输出格式
    return_obj = result.get('returnObj', {})
    monitors = return_obj.get('monitors', [])

    if not monitors:
        click.echo("未找到监控数据")
        return

    # 根据输出格式显示结果（命令级别优先）
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式
        # 将monitors转换为适合format_table的格式
        formatted_data = []
        for monitor in monitors:
            item_aggregate_list = monitor.get('itemAggregateList', {})

            # 基础信息
            row_data = {
                '负载均衡器ID': monitor.get('deviceID', ''),
                '最近更新': monitor.get('lastUpdated', ''),
            }

            # 添加每个监控指标的值
            for metric_name in metric_names_list:
                if metric_name in item_aggregate_list:
                    metric_values = item_aggregate_list[metric_name]
                    # 如果是数组，显示前几个值
                    if isinstance(metric_values, list) and metric_values:
                        row_data[metric_name] = f"{len(metric_values)}个数据点"
                    else:
                        row_data[metric_name] = str(metric_values)
                else:
                    row_data[metric_name] = '无数据'

            formatted_data.append(row_data)

        table = OutputFormatter.format_table(formatted_data)

        # 显示分页信息
        total_count = return_obj.get('totalCount', 0)
        current_count = return_obj.get('currentCount', 0)
        total_page = return_obj.get('totalPage', 0)

        click.echo(f"负载均衡历史监控数据 (第{page_no}页，共{total_page}页，总计{total_count}条)")
        click.echo(f"监控指标: {', '.join(metric_names_list)}")
        click.echo(f"时间范围: {start_time} ~ {end_time}")
        click.echo(f"聚合周期: {period}秒")
        click.echo(table)


@elb.group()
def health_check():
    """健康检查管理"""
    pass


@health_check.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--health-check-id', required=True, help='健康检查ID（推荐使用）')
@click.option('--id', help='健康检查ID（即将废弃，不推荐使用）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def show_health_check(ctx, region_id: str, health_check_id: str, id: Optional[str],
                     output: Optional[str]):
    """
    查看健康检查详情

    示例:
    \b
    # 查看健康检查详情（推荐方式）
    elb health-check show --region-id 200000001852 --health-check-id hc-xxx

    # 使用即将废弃的id参数
    elb health-check show --region-id 200000001852 --id hc-xxx

    # JSON格式输出
    elb health-check show --region-id 200000001852 --health-check-id hc-xxx --output json
    """
    elb_client = get_elb_client(ctx)

    result = elb_client.get_health_check(
        region_id=region_id,
        health_check_id=health_check_id,
        id_param=id
    )

    # 处理输出格式
    output_format = output or ctx.obj.get('output', 'table')

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
        # 表格格式 - 详细显示健康检查信息
        return_obj = result.get('returnObj', {})

        if not return_obj:
            click.echo("未找到健康检查详情")
            return

        # 基础信息
        click.echo("=" * 80)
        click.echo("健康检查基础信息")
        click.echo("=" * 80)
        basic_info = [
            ('健康检查ID', return_obj.get('ID', '')),
            ('健康检查名称', return_obj.get('name', '')),
            ('描述', return_obj.get('description', '') or '无'),
            ('区域ID', return_obj.get('regionID', '')),
            ('可用区名称', return_obj.get('azName', '') or '无'),
            ('项目ID', return_obj.get('projectID', '')),
            ('状态', 'UP' if return_obj.get('status') == 1 else 'DOWN' if return_obj.get('status') == 0 else '未知'),
            ('创建时间', return_obj.get('createTime', '')),
        ]

        for key, value in basic_info:
            click.echo(f"{key:12}: {value}")

        # 检查配置
        click.echo("\n" + "=" * 80)
        click.echo("健康检查配置")
        click.echo("=" * 80)
        config_info = [
            ('检查协议', return_obj.get('protocol', '')),
            ('检查端口', return_obj.get('protocolPort', 0) or '使用后端主机端口'),
            ('检查间隔', f"{return_obj.get('interval', 0)}秒"),
            ('超时时间', f"{return_obj.get('timeout', 0)}秒"),
            ('最大重试次数', return_obj.get('maxRetry', 0)),
        ]

        for key, value in config_info:
            click.echo(f"{key:12}: {value}")

        # HTTP特定配置（仅当协议为HTTP时显示）
        if return_obj.get('protocol') == 'HTTP':
            click.echo("\n" + "=" * 80)
            click.echo("HTTP健康检查配置")
            click.echo("=" * 80)
            http_info = [
                ('HTTP方法', return_obj.get('httpMethod', '') or '无'),
                ('请求路径', return_obj.get('httpUrlPath', '') or '无'),
                ('预期状态码', return_obj.get('httpExpectedCodes', '') or '无'),
            ]

            for key, value in http_info:
                click.echo(f"{key:12}: {value}")

        # 高级功能配置
        click.echo("\n" + "=" * 80)
        click.echo("高级功能配置")
        click.echo("=" * 80)

        domain_enabled = return_obj.get('domainEnabled', 0)
        custom_enabled = return_obj.get('customReqRespEnabled', 0)

        advanced_info = [
            ('域名功能', '启用' if domain_enabled == 1 else '禁用'),
            ('检查域名', return_obj.get('domain', '') or '无'),
            ('自定义请求响应', '启用' if custom_enabled == 1 else '禁用'),
            ('自定义请求', return_obj.get('customRequest', '') or '无'),
            ('自定义响应', return_obj.get('customResponse', '') or '无'),
        ]

        for key, value in advanced_info:
            click.echo(f"{key:12}: {value}")

        # 显示配置建议
        click.echo("\n" + "=" * 80)
        click.echo("配置建议")
        click.echo("=" * 80)

        timeout = return_obj.get('timeout', 0)
        interval = return_obj.get('interval', 0)
        max_retry = return_obj.get('maxRetry', 0)

        suggestions = []
        if timeout > 0 and interval > 0 and timeout >= interval:
            suggestions.append("⚠️  建议timeout应小于interval，避免检查重叠")

        if max_retry == 0:
            suggestions.append("⚠️  建议设置maxRetry为2-3次，平衡准确性和效率")

        if interval == 0:
            suggestions.append("⚠️  建议设置合理的interval，通常5-30秒为宜")

        if suggestions:
            for suggestion in suggestions:
                click.echo(suggestion)
        else:
            click.echo("✅ 配置看起来合理")