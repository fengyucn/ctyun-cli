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
@click.option('--loadbalancer-id', help='负载均衡器ID')
@click.pass_context
@handle_error
def list_listeners(ctx, region_id: str, loadbalancer_id: Optional[str]):
    """
    查看监听器列表

    示例:
    \b
    # 查询指定区域的所有监听器
    elb listener list --region-id 200000001852

    # 查询指定负载均衡器的监听器
    elb listener list --region-id 200000001852 --loadbalancer-id elb-xxxxxxxx
    """
    # TODO: 实现具体功能
    click.echo("TODO: 查看监听器列表功能待实现")


@listener.command('get')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--listener-id', required=True, help='监听器ID')
@click.pass_context
@handle_error
def get_listener(ctx, region_id: str, listener_id: str):
    """
    查看监听器详情

    示例:
    \b
    elb listener get --region-id 200000001852 --listener-id ls-xxxxxxxx
    """
    # TODO: 实现具体功能
    click.echo("TODO: 查看监听器详情功能待实现")