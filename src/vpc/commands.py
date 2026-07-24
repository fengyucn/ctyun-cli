"""
VPC(虚拟私有云)命令行接口
"""

import click
from functools import wraps
from typing import List, Optional
# 直接定义装饰器，避免循环导入
from vpc import VPCClient
from utils import ValidationUtils, OutputFormatter


def handle_error(func):
    """
    错误处理装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from core import CTYUNAPIError
            import click
            import sys

            if isinstance(e, CTYUNAPIError):
                click.echo(f"API错误 [{e.code}]: {e.message}", err=True)
                if e.request_id:
                    click.echo(f"请求ID: {e.request_id}", err=True)
            else:
                click.echo(f"错误: {e}", err=True)
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """
    格式化输出
    """
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
        # 表格格式输出
        if isinstance(data, dict):
            if data.get('statusCode') == 800:
                # API成功响应
                return_obj = data.get('returnObj', {})
                if isinstance(return_obj, dict) and 'vpcs' in return_obj:
                    vpcs = return_obj.get('vpcs', [])
                    if vpcs:
                        # 显示VPC列表表格
                        from tabulate import tabulate

                        table_data = []
                        headers = ['VPC ID', '名称', 'CIDR', 'IPv6', '子网数', 'NAT网关', '项目ID', '创建时间']

                        for vpc in vpcs:
                            # 处理IPv6状态
                            ipv6_status = '开启' if vpc.get('ipv6Enabled', False) else '关闭'

                            # 处理子网数量
                            subnet_ids = vpc.get('subnetIDs', [])
                            subnet_count = len(subnet_ids) if isinstance(subnet_ids, list) else 0

                            # 处理NAT网关数量
                            nat_gateway_ids = vpc.get('natGatewayIDs', [])
                            nat_count = len(nat_gateway_ids) if isinstance(nat_gateway_ids, list) else 0

                            # 处理创建时间
                            created_at = vpc.get('createdAt', '')

                            table_data.append([
                                vpc.get('vpcID', '')[:20],  # 限制VPC ID显示长度
                                vpc.get('name', ''),
                                vpc.get('CIDR', ''),
                                ipv6_status,
                                subnet_count,
                                nat_count,
                                vpc.get('projectID', ''),
                                created_at[:19] if created_at else ''  # 只显示日期时间部分
                            ])

                        # 显示分页信息
                        total_count = data.get('totalCount', len(vpcs))
                        current_count = data.get('currentCount', len(vpcs))
                        total_page = data.get('totalPage', 1)
                        page_no = return_obj.get('pageNo', 1)

                        click.echo(f"VPC列表 (总计: {total_count} 个, 当前页: {current_count} 个, 第{page_no}/{total_page}页)")
                        click.echo()

                        table = tabulate(table_data, headers=headers, tablefmt='grid')
                        click.echo(table)

                        # 分页提示
                        if total_page > 1:
                            click.echo()
                            click.echo(f"提示: 使用 --page-no 参数查看其他页 (共{total_page}页)")
                    else:
                        click.echo("没有找到VPC数据")
                elif 'subnets' in return_obj:
                    subnets = return_obj.get('subnets', [])
                    if subnets:
                        # 显示子网列表表格
                        from tabulate import tabulate

                        table_data = []
                        headers = ['子网ID', '名称', 'VPC ID', 'CIDR', '可用IP数', '网关', 'IPv6', '类型', '可用区', '创建时间']

                        for subnet in subnets:
                            # 处理IPv6状态
                            ipv6_status = '开启' if subnet.get('ipv6Enabled', 0) == 1 or subnet.get('enableIpv6', False) else '关闭'

                            # 处理子网类型
                            type_map = {0: '普通', 1: '裸金属'}
                            subnet_type = type_map.get(subnet.get('type', 0), '未知')

                            # 处理可用区
                            az_list = subnet.get('availabilityZones', [])
                            availability_zones = ', '.join(az_list) if isinstance(az_list, list) and az_list else '-'

                            # 处理创建时间
                            created_at = subnet.get('createAt', '')

                            table_data.append([
                                subnet.get('subnetID', '')[:20],  # 限制子网ID显示长度
                                subnet.get('name', ''),
                                subnet.get('vpcID', '')[:20],  # 限制VPC ID显示长度
                                subnet.get('CIDR', ''),
                                subnet.get('availableIPCount', 0),
                                subnet.get('gatewayIP', ''),
                                ipv6_status,
                                subnet_type,
                                availability_zones,
                                created_at[:19] if created_at else ''  # 只显示日期时间部分
                            ])

                        # 显示分页信息
                        total_count = data.get('totalCount', len(subnets))
                        current_count = data.get('currentCount', len(subnets))
                        total_page = data.get('totalPage', 1)
                        page_no = return_obj.get('pageNo', 1)

                        click.echo(f"子网列表 (总计: {total_count} 个, 当前页: {current_count} 个, 第{page_no}/{total_page}页)")
                        click.echo()

                        table = tabulate(table_data, headers=headers, tablefmt='grid')
                        click.echo(table)

                        # 分页提示
                        if total_page > 1:
                            click.echo()
                            click.echo(f"提示: 使用 --page-no 参数查看其他页 (共{total_page}页)")
                    else:
                        click.echo("没有找到子网数据")
                elif 'securityGroups' in return_obj:
                    # 安全组列表格式化
                    from tabulate import tabulate

                    security_groups = return_obj.get('securityGroups', [])
                    if security_groups:
                        headers = ['安全组ID', '名称', 'VPC ID', '描述', '状态', '创建时间']
                        table_data = []

                        for sg in security_groups:
                            table_data.append([
                                sg.get('securityGroupID', ''),
                                sg.get('securityGroupName', ''),
                                sg.get('vpcID', ''),
                                sg.get('description', ''),
                                sg.get('status', ''),
                                sg.get('createTime', '')[:19] if sg.get('createTime') else ''
                            ])

                        click.echo(f"安全组列表 (共 {len(security_groups)} 个)")
                        click.echo()

                        table = tabulate(table_data, headers=headers, tablefmt='grid')
                        click.echo(table)
                    else:
                        click.echo("没有找到安全组数据")
                elif 'securityGroup' in return_obj or 'securityGroupName' in return_obj or 'rules' in return_obj:
                    # 安全组详情格式化
                    from tabulate import tabulate

                    # 显示基本信息
                    click.echo("安全组基本信息")
                    click.echo("=" * 60)

                    basic_info = []
                    for key, value in return_obj.items():
                        if key != 'rules':
                            basic_info.append([key, str(value)])

                    if basic_info:
                        basic_table = tabulate(basic_info, headers=['字段', '值'], tablefmt='grid')
                        click.echo(basic_table)
                        click.echo()

                    # 显示规则列表
                    rules = return_obj.get('rules', [])
                    if rules:
                        click.echo("安全组规则列表")
                        click.echo("=" * 60)

                        rule_headers = ['方向', '协议', '端口范围', '源IP', '目的IP', '优先级', '动作', '描述']
                        rule_data = []

                        for rule in rules:
                            direction = rule.get('direction', '')
                            protocol = rule.get('protocol', '')
                            port_range = rule.get('portRange', '')
                            source_ip = rule.get('sourceCidr', rule.get('sourceIp', ''))
                            dest_ip = rule.get('destCidr', rule.get('destIp', ''))
                            priority = rule.get('priority', '')
                            action = rule.get('action', '')
                            description = rule.get('description', '')

                            rule_data.append([
                                direction, protocol, port_range, source_ip,
                                dest_ip, priority, action, description
                            ])

                        rule_table = tabulate(rule_data, headers=rule_headers, tablefmt='grid')
                        click.echo(rule_table)
                    else:
                        click.echo("没有找到安全组规则")
                elif 'usedIPs' in return_obj:
                    # 子网已使用IP格式化
                    from tabulate import tabulate

                    used_ips = return_obj.get('usedIPs', [])
                    if used_ips:
                        headers = ['IPv4地址', 'IPv6地址', '用途', '描述', '扩展IPv4', '扩展IPv6']
                        table_data = []

                        for ip_info in used_ips:
                            # 处理扩展IP地址
                            secondary_ipv4 = ip_info.get('secondaryPrivateIpv4', [])
                            secondary_ipv6 = ip_info.get('secondaryPrivateIpv6', [])

                            secondary_ipv4_str = ', '.join(secondary_ipv4) if secondary_ipv4 else '-'
                            secondary_ipv6_str = ', '.join(secondary_ipv6) if secondary_ipv6 else '-'

                            table_data.append([
                                ip_info.get('ipv4Address', ''),
                                ip_info.get('ipv6Address', ''),
                                ip_info.get('use', ''),
                                ip_info.get('useDesc', ''),
                                secondary_ipv4_str,
                                secondary_ipv6_str
                            ])

                        # 显示分页信息
                        total_count = return_obj.get('totalCount', len(used_ips))
                        current_count = return_obj.get('currentCount', len(used_ips))
                        total_page = return_obj.get('totalPage', 1)

                        click.echo(f"子网已使用IP列表 (总计: {total_count} 个, 当前页: {current_count} 个)")
                        click.echo()

                        table = tabulate(table_data, headers=headers, tablefmt='grid')
                        click.echo(table)
                    else:
                        click.echo("没有找到已使用的IP")
                elif isinstance(return_obj, dict):
                    # 其他类型的数据，打印键值对
                    headers = ['字段', '值']
                    table_data = []
                    for key, value in return_obj.items():
                        if key not in ['vpcs', 'subnets']:  # 已在上面处理
                            table_data.append([key, str(value)])

                    from tabulate import tabulate
                    table = tabulate(table_data, headers=headers, tablefmt='grid')
                    click.echo(table)
                else:
                    click.echo(str(return_obj))
            else:
                # 非API成功响应或其他字典数据
                headers = ['字段', '值']
                table_data = []
                for key, value in data.items():
                    table_data.append([key, str(value)])

                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
        elif isinstance(data, list):
            # 列表数据
            from tabulate import tabulate

            if data:
                headers = list(data[0].keys()) if isinstance(data[0], dict) else ['数据']
                # 处理表格数据
                table_data = []
                for item in data:
                    if isinstance(item, dict):
                        table_data.append([str(value) for value in item.values()])
                    else:
                        table_data.append([str(item)])

                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
            else:
                click.echo("列表为空")
        else:
            # 其他类型数据
            click.echo(str(data))


def get_vpc_client(ctx):
    """获取VPC客户端"""
    return VPCClient(ctx.obj['client'])


@click.group()
def vpc():
    """VPC(虚拟私有云)管理"""
    pass


# ==================== VPC管理命令 ====================

@vpc.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID，多个ID用半角逗号分隔')
@click.option('--vpc-name', help='VPC名称')
@click.option('--project-id', help='企业项目ID，默认为0')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为200，默认值为10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def describe_vpcs(ctx, region_id: str, vpc_id: Optional[str], vpc_name: Optional[str],
                  project_id: Optional[str], page_no: int, page_size: int, output: Optional[str]):
    """
    查询VPC列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_vpcs(
        region_id=region_id,
        vpc_id=vpc_id,
        vpc_name=vpc_name,
        project_id=project_id,
        page_no=page_no,
        page_size=page_size
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@vpc.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID，多个ID用半角逗号分隔')
@click.option('--vpc-name', help='VPC名称')
@click.option('--project-id', help='企业项目ID，默认为0')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1，推荐使用该字段')
@click.option('--page-number', type=int, help='列表的页码，默认值为1，后续会废弃')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为200，默认值为10')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大分页数')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def new_describe_vpcs(ctx, region_id: str, vpc_id: Optional[str], vpc_name: Optional[str],
                      project_id: Optional[str], page_no: int, page_number: Optional[int],
                      page_size: int, next_token: Optional[str], max_results: Optional[int],
                      output: Optional[str]):
    """
    查询VPC列表 (新版API，支持游标分页)
    """
    client = get_vpc_client(ctx)
    result = client.new_describe_vpcs(
        region_id=region_id,
        vpc_id=vpc_id,
        vpc_name=vpc_name,
        project_id=project_id,
        page_no=page_no,
        page_number=page_number,
        page_size=page_size,
        next_token=next_token,
        max_results=max_results
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@vpc.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def show_vpc(ctx, region_id: str, vpc_id: str, output: Optional[str]):
    """
    查询VPC详情
    """
    client = get_vpc_client(ctx)
    result = client.show_vpc(
        region_id=region_id,
        vpc_id=vpc_id
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


# ==================== 子网管理命令 ====================

@vpc.group()
def subnet():
    """子网查询"""
    pass


@subnet.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--subnet-id', help='子网ID，多个ID用半角逗号分隔')
@click.option('--client-token', help='客户端存根，用于保证订单幂等性，长度 1 - 64')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为200，默认值为10')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def describe_subnets(ctx, region_id: str, vpc_id: Optional[str], subnet_id: Optional[str],
                     client_token: Optional[str], page_no: int, page_size: int,
                     next_token: Optional[str], max_results: Optional[int], output: Optional[str]):
    """
    查询子网列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_subnets(
        region_id=region_id,
        vpc_id=vpc_id,
        subnet_id=subnet_id,
        client_token=client_token,
        page_no=page_no,
        page_size=page_size,
        next_token=next_token,
        max_results=max_results
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@subnet.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--subnet-id', help='子网ID，多个ID用半角逗号分隔')
@click.option('--client-token', help='客户端存根，用于保证订单幂等性，长度 1 - 64')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1，推荐使用该字段')
@click.option('--page-number', type=int, help='列表的页码，默认值为1，后续会废弃')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为200，默认值为10')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def new_describe_subnets(ctx, region_id: str, vpc_id: Optional[str], subnet_id: Optional[str],
                         client_token: Optional[str], page_no: int, page_number: Optional[int],
                         page_size: int, next_token: Optional[str], max_results: Optional[int],
                         output: Optional[str]):
    """
    查询子网列表 (新版API，支持游标分页)
    """
    client = get_vpc_client(ctx)
    result = client.new_describe_subnets(
        region_id=region_id,
        vpc_id=vpc_id,
        subnet_id=subnet_id,
        client_token=client_token,
        page_no=page_no,
        page_number=page_number,
        page_size=page_size,
        next_token=next_token,
        max_results=max_results
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@subnet.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--subnet-id', required=True, help='子网ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def show_subnet(ctx, region_id: str, subnet_id: str, output: Optional[str]):
    """
    查询子网详情
    """
    client = get_vpc_client(ctx)
    result = client.show_subnet(
        region_id=region_id,
        subnet_id=subnet_id
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@subnet.command('used-ips')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--subnet-id', required=True, help='子网ID')
@click.option('--ip', help='子网内的IP地址')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为50，默认值为10')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_subnet_used_ips(ctx, region_id: str, subnet_id: str, ip: Optional[str],
                         page_no: int, page_size: int, output: Optional[str]):
    """
    查询子网已使用IP列表
    """
    client = get_vpc_client(ctx)
    result = client.list_subnet_used_ips(
        region_id=region_id,
        subnet_id=subnet_id,
        ip=ip,
        page_no=page_no,
        page_size=page_size
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


# ==================== 路由表管理命令 ====================

@vpc.group()
def route_table():
    """路由表查询"""
    pass


@route_table.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--route-table-id', help='路由表 ID')
@click.option('--route-table-name', help='路由表名称过滤')
@click.option('--status', help='路由表状态过滤')
@click.pass_context
@handle_error
def describe_route_tables(ctx, region_id: str, vpc_id: Optional[str], route_table_id: Optional[str],
                         route_table_name: Optional[str], status: Optional[str]):
    """
    查询路由表列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_route_tables(
        region_id=region_id,
        vpc_id=vpc_id,
        route_table_id=route_table_id,
        route_table_name=route_table_name,
        status=status
    )
    format_output(result, ctx.obj['output'])


# ==================== 安全组管理命令 ====================

@vpc.group()
def security_group():
    """安全组查询"""
    pass


@security_group.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='安全组所在的专有网络ID')
@click.option('--query-content', help='【模糊查询】安全组ID或名称')
@click.option('--project-id', help='企业项目ID，默认为0')
@click.option('--instance-id', help='实例ID')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为50，默认值为10')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def describe_security_groups(ctx, region_id: str, vpc_id: Optional[str], query_content: Optional[str],
                             project_id: Optional[str], instance_id: Optional[str], page_no: int, page_size: int,
                             next_token: Optional[str], max_results: Optional[int], output: Optional[str]):
    """
    查询安全组列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_security_groups(
        region_id=region_id,
        vpc_id=vpc_id,
        query_content=query_content,
        project_id=project_id,
        instance_id=instance_id,
        page_no=page_no,
        page_size=page_size,
        next_token=next_token,
        max_results=max_results
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@security_group.command('new-query')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='安全组所在的专有网络ID')
@click.option('--query-content', help='【模糊查询】安全组ID或名称')
@click.option('--instance-id', help='实例ID')
@click.option('--page-no', type=int, default=1, help='列表的页码，默认值为1，推荐使用该字段')
@click.option('--page-number', type=int, help='列表的页码，默认值为1，后续会废弃')
@click.option('--page-size', type=int, default=10, help='分页查询时每页的行数，最大值为50，默认值为10')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def new_describe_security_groups(ctx, region_id: str, vpc_id: Optional[str],
                                query_content: Optional[str], instance_id: Optional[str],
                                page_no: int, page_number: Optional[int], page_size: int,
                                next_token: Optional[str], max_results: Optional[int],
                                output: Optional[str]):
    """
    查询安全组列表 (新版API，支持游标分页)
    """
    client = get_vpc_client(ctx)
    result = client.new_describe_security_groups(
        region_id=region_id,
        vpc_id=vpc_id,
        query_content=query_content,
        instance_id=instance_id,
        page_no=page_no,
        page_number=page_number,
        page_size=page_size,
        next_token=next_token,
        max_results=max_results
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


@security_group.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--security-group-id', required=True, help='安全组 ID')
@click.option('--direction', help='规则方向：ingress或egress')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def show_security_group(ctx, region_id: str, security_group_id: str,
                       direction: Optional[str], output: Optional[str]):
    """
    查询安全组详情（包括规则列表）
    """
    client = get_vpc_client(ctx)
    result = client.show_security_group(
        region_id=region_id,
        security_group_id=security_group_id,
        direction=direction
    )
    # 优先使用子命令的output参数，否则使用全局output设置
    output_format = output or ctx.obj['output']
    format_output(result, output_format)


# ==================== 弹性公网IP管理命令 ====================

@vpc.group()
def eip():
    """弹性公网IP查询"""
    pass


@eip.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--eip-id', help='弹性公网IP ID')
@click.option('--eip-address', help='弹性公网IP地址过滤')
@click.option('--status', help='弹性公网IP状态过滤')
@click.option('--instance-id', help='绑定的实例ID过滤')
@click.pass_context
@handle_error
def describe_eips(ctx, region_id: str, eip_id: Optional[str], eip_address: Optional[str],
                  status: Optional[str], instance_id: Optional[str]):
    """
    查询弹性公网IP列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_eips(
        region_id=region_id,
        eip_id=eip_id,
        eip_address=eip_address,
        status=status,
        instance_id=instance_id
    )
    format_output(result, ctx.obj['output'])


@eip.command('detail')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--eip-id', required=True, help='弹性公网IP ID')
@click.pass_context
@handle_error
def eip_detail(ctx, region_id: str, eip_id: str):
    """
    查看EIP详情
    """
    client = get_vpc_client(ctx)
    result = client.show_eip(region_id=region_id, eip_id=eip_id)
    format_output(result, ctx.obj['output'])


@eip.command('shared-bandwidths')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--query-content', help='模糊查询（实例名称/带宽ID）')
@click.option('--project-id', help='企业项目ID')
@click.option('--page', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量')
@click.pass_context
@handle_error
def shared_bandwidths(ctx, region_id: str, query_content: str,
                      project_id: str, page: int, page_size: int):
    """
    查询共享带宽列表
    """
    client = get_vpc_client(ctx)
    result = client.list_bandwidths_new(
        region_id=region_id, query_content=query_content,
        project_id=project_id, page_no=page, page_size=page_size
    )
    format_output(result, ctx.obj['output'])


# ==================== NAT网关管理命令 ====================

@vpc.group()
def nat_gateway():
    """NAT网关查询"""
    pass


@nat_gateway.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--nat-gateway-id', help='NAT网关 ID')
@click.option('--nat-gateway-name', help='NAT网关名称过滤')
@click.option('--status', help='NAT网关状态过滤')
@click.option('--subnet-id', help='子网ID过滤')
@click.pass_context
@handle_error
def describe_nat_gateways(ctx, region_id: str, vpc_id: Optional[str], nat_gateway_id: Optional[str],
                          nat_gateway_name: Optional[str], status: Optional[str], subnet_id: Optional[str]):
    """
    查询NAT网关列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_nat_gateways(
        region_id=region_id,
        vpc_id=vpc_id,
        nat_gateway_id=nat_gateway_id,
        nat_gateway_name=nat_gateway_name,
        status=status,
        subnet_id=subnet_id
    )
    format_output(result, ctx.obj['output'])


# ==================== VPC对等连接管理命令 ====================

@vpc.group()
def peering():
    """VPC对等连接查询"""
    pass


@peering.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--peering-connection-id', help='对等连接 ID')
@click.option('--peering-connection-name', help='对等连接名称过滤')
@click.option('--status', help='对等连接状态过滤')
@click.pass_context
@handle_error
def describe_vpc_peering_connections(ctx, region_id: str, vpc_id: Optional[str], peering_connection_id: Optional[str],
                                     peering_connection_name: Optional[str], status: Optional[str]):
    """
    查询VPC对等连接列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_vpc_peering_connections(
        region_id=region_id,
        vpc_id=vpc_id,
        peering_connection_id=peering_connection_id,
        peering_connection_name=peering_connection_name,
        status=status
    )
    format_output(result, ctx.obj['output'])

# ==================== NAT/SNAT/DNAT 详情查询命令 ====================

@nat_gateway.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--nat-gateway-id', required=True, help='NAT网关ID')
@click.pass_context
@handle_error
def show_nat_gateway(ctx, region_id: str, nat_gateway_id: str):
    """查询NAT网关详情"""
    client = get_vpc_client(ctx)
    result = client.show_nat_gateway(region_id=region_id, nat_gateway_id=nat_gateway_id)
    format_output(result, ctx.obj['output'])


@nat_gateway.group()
def snat():
    """SNAT规则查询"""
    pass


@snat.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--nat-gateway-id', help='NAT网关ID')
@click.option('--snat-id', help='SNAT规则ID')
@click.option('--subnet-id', help='子网ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def list_snats(ctx, region_id: str, nat_gateway_id: Optional[str], snat_id: Optional[str],
               subnet_id: Optional[str], page_number: Optional[int], page_size: Optional[int]):
    """查看SNAT列表"""
    client = get_vpc_client(ctx)
    result = client.list_snats(region_id=region_id, nat_gateway_id=nat_gateway_id,
                               s_nat_id=snat_id, subnet_id=subnet_id,
                               page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@snat.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--snat-id', required=True, help='SNAT规则ID')
@click.pass_context
@handle_error
def show_snat(ctx, region_id: str, snat_id: str):
    """查看SNAT详情"""
    client = get_vpc_client(ctx)
    result = client.show_snat(region_id=region_id, s_nat_id=snat_id)
    format_output(result, ctx.obj['output'])


@nat_gateway.group()
def dnat():
    """DNAT规则查询"""
    pass


@dnat.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--nat-gateway-id', required=True, help='NAT网关ID')
@click.pass_context
@handle_error
def list_dnats(ctx, region_id: str, nat_gateway_id: str):
    """查询DNAT列表"""
    client = get_vpc_client(ctx)
    result = client.list_dnats(region_id=region_id, nat_gateway_id=nat_gateway_id)
    format_output(result, ctx.obj['output'])


@dnat.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--nat-gateway-id', required=True, help='NAT网关ID')
@click.option('--dnat-id', required=True, help='DNAT规则ID')
@click.pass_context
@handle_error
def show_dnat(ctx, region_id: str, nat_gateway_id: str, dnat_id: str):
    """查询DNAT详情"""
    client = get_vpc_client(ctx)
    result = client.show_dnat(region_id=region_id, nat_gateway_id=nat_gateway_id, d_nat_id=dnat_id)
    format_output(result, ctx.obj['output'])


@peering.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--peering-connection-id', required=True, help='对等连接ID')
@click.pass_context
@handle_error
def show_vpc_peering_connection_cmd(ctx, region_id: str, peering_connection_id: str):
    """查询对等连接详情"""
    client = get_vpc_client(ctx)
    result = client.show_vpc_peering_connection(region_id=region_id, peering_connection_id=peering_connection_id)
    format_output(result, ctx.obj['output'])


# ==================== 流日志管理命令 ====================

@vpc.group()
def flow_log():
    """流日志查询"""
    pass


# ==================== 路由表/安全组/网卡 列表查询命令 ====================

@route_table.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--query-content', help='对路由表名字/描述/ID进行模糊查询')
@click.option('--route-table-id', help='路由表ID')
@click.option('--type', 'type_', type=click.Choice(['0', '2']), help='路由表类型：0-子网路由表 2-网关路由表')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def new_list_route_tables(ctx, region_id: str, vpc_id: Optional[str], query_content: Optional[str],
                          route_table_id: Optional[str], type_: Optional[str],
                          page_no: Optional[int], page_size: Optional[int]):
    """新查询路由表列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_route_tables(
        region_id=region_id, vpc_id=vpc_id, query_content=query_content,
        route_table_id=route_table_id,
        type_=int(type_) if type_ is not None else None,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@route_table.command('rules')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--route-table-id', required=True, help='路由表ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def list_route_table_rules_cmd(ctx, region_id: str, route_table_id: str,
                               page_no: Optional[int], page_size: Optional[int]):
    """查询路由表规则列表"""
    client = get_vpc_client(ctx)
    result = client.list_route_table_rules(region_id=region_id, route_table_id=route_table_id,
                                           page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@route_table.command('new-rules')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--route-table-id', required=True, help='路由表ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def new_list_route_table_rules_cmd(ctx, region_id: str, route_table_id: str,
                                   page_no: Optional[int], page_size: Optional[int]):
    """新查询路由表规则列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_route_table_rules(region_id=region_id, route_table_id=route_table_id,
                                               page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@security_group.command('rules')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--security-group-id', help='安全组ID')
@click.option('--remote-security-group-id', help='远端安全组ID')
@click.option('--security-group-rule-ids', help='安全组规则ID，逗号分隔（最多20个）')
@click.option('--page-no', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def list_security_group_rules_cmd(ctx, region_id: str, security_group_id: Optional[str],
                                  remote_security_group_id: Optional[str],
                                  security_group_rule_ids: Optional[str],
                                  page_no: Optional[int], page_size: Optional[int]):
    """获取安全组规则列表"""
    client = get_vpc_client(ctx)
    result = client.list_security_group_rules(
        region_id=region_id, security_group_id=security_group_id,
        remote_security_group_id=remote_security_group_id,
        security_group_rule_ids=security_group_rule_ids,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@security_group.command('vms')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--security-group-id', required=True, help='安全组ID')
@click.option('--page-no', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def list_security_group_vms_cmd(ctx, region_id: str, security_group_id: str,
                                page_no: Optional[int], page_size: Optional[int]):
    """获取安全组绑定机器列表"""
    client = get_vpc_client(ctx)
    result = client.list_security_group_vms(region_id=region_id, security_group_id=security_group_id,
                                            page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def port():
    """网卡查询"""
    pass


@port.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='所属VPC ID')
@click.option('--device-id', help='关联设备ID')
@click.option('--subnet-id', help='所属子网ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大数量')
@click.pass_context
@handle_error
def list_ports_cmd(ctx, region_id: str, vpc_id: Optional[str], device_id: Optional[str],
                   subnet_id: Optional[str], page_no: Optional[int], page_size: Optional[int],
                   next_token: Optional[str], max_results: Optional[int]):
    """查询网卡列表"""
    client = get_vpc_client(ctx)
    result = client.list_ports(region_id=region_id, vpc_id=vpc_id, device_id=device_id,
                               subnet_id=subnet_id, page_no=page_no, page_size=page_size,
                               next_token=next_token, max_results=max_results)
    format_output(result, ctx.obj['output'])


@port.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='所属VPC ID')
@click.option('--device-id', help='关联设备ID')
@click.option('--subnet-id', help='所属子网ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.option('--next-token', help='下一页游标')
@click.option('--max-results', type=int, help='最大数量')
@click.pass_context
@handle_error
def new_list_ports_cmd(ctx, region_id: str, vpc_id: Optional[str], device_id: Optional[str],
                       subnet_id: Optional[str], page_no: Optional[int], page_size: Optional[int],
                       next_token: Optional[str], max_results: Optional[int]):
    """新查询网卡列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_ports(region_id=region_id, vpc_id=vpc_id, device_id=device_id,
                                   subnet_id=subnet_id, page_no=page_no, page_size=page_size,
                                   next_token=next_token, max_results=max_results)
    format_output(result, ctx.obj['output'])


@flow_log.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--resource-type', help='资源类型')
@click.option('--resource-id', help='资源ID')
@click.option('--flow-log-id', help='流日志 ID')
@click.option('--log-group-name', help='日志组名称过滤')
@click.option('--traffic-type', help='流量类型过滤')
@click.option('--status', help='流日志状态过滤')
@click.pass_context
@handle_error
def describe_flow_logs(ctx, region_id: str, resource_type: Optional[str],
                      resource_id: Optional[str], flow_log_id: Optional[str],
                      log_group_name: Optional[str], traffic_type: Optional[str], status: Optional[str]):
    """
    查询流日志列表
    """
    client = get_vpc_client(ctx)
    result = client.describe_flow_logs(
        region_id=region_id,
        resource_type=resource_type,
        resource_id=resource_id,
        flow_log_id=flow_log_id,
        log_group_name=log_group_name,
        traffic_type=traffic_type,
        status=status
    )
    format_output(result, ctx.obj['output'])


# ==================== 标签查询 ====================

def _label_output(ctx, result):
    """标签查询统一输出"""
    fmt = ctx.obj.get('output', 'table')
    if fmt == 'json':
        click.echo(OutputFormatter.format_json(result))
        return
    return_obj = result.get('returnObj', {})
    items = return_obj.get('results', [])
    total = return_obj.get('totalCount', 0)
    click.echo(f"标签列表 (共 {total} 个)")
    if items:
        click.echo(OutputFormatter.format_table(items))


@vpc.command('label-query-resources')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--label-id', default=None, help='标签ID')
@click.option('--label-key', default=None, help='标签Key')
@click.option('--label-value', default=None, help='标签Value')
@click.option('--page-number', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.pass_context
def label_query_resources(ctx, region_id, label_id, label_key, label_value, page_number, page_size):
    """根据标签获取资源列表"""
    from vpc.client import VPCClient
    result = VPCClient(ctx.obj['client']).query_resources_by_label(
        region_id=region_id, label_id=label_id, label_key=label_key,
        label_value=label_value, page_number=page_number, page_size=page_size)
    fmt = ctx.obj.get('output', 'table')
    if fmt == 'json':
        click.echo(OutputFormatter.format_json(result)); return
    ro = result.get('returnObj', {})
    items = ro.get('results', [])
    click.echo(f"资源列表 (共 {ro.get('totalCount', 0)} 个)")
    if items:
        click.echo(OutputFormatter.format_table(items))


@vpc.command('label-query-by-resource')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--resource-type', required=True,
              help='资源类型: vpc/subnet/acl/security_group/route_table/havip/vpc_peer/vpce_endpoint等')
@click.option('--resource-id', required=True, help='资源ID')
@click.option('--page-number', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.pass_context
def label_query_by_resource(ctx, region_id, resource_type, resource_id, page_number, page_size):
    """根据资源获取标签"""
    from vpc.client import VPCClient
    result = VPCClient(ctx.obj['client']).query_labels_by_resource(
        region_id=region_id, resource_type=resource_type, resource_id=resource_id,
        page_number=page_number, page_size=page_size)
    _label_output(ctx, result)


@vpc.command('label-vpc-peer')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--vpc-peer-id', required=True, help='对等链接ID')
@click.option('--page-number', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.pass_context
def label_vpc_peer(ctx, region_id, vpc_peer_id, page_number, page_size):
    """获取对等链接绑定的标签"""
    from vpc.client import VPCClient
    result = VPCClient(ctx.obj['client']).list_vpc_peer_labels(
        region_id=region_id, vpc_peer_id=vpc_peer_id, page_number=page_number, page_size=page_size)
    _label_output(ctx, result)


@vpc.command('label-vpce-endpoint')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--endpoint-id', required=True, help='终端节点ID')
@click.option('--page-number', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.pass_context
def label_vpce_endpoint(ctx, region_id, endpoint_id, page_number, page_size):
    """获取终端节点绑定的标签"""
    from vpc.client import VPCClient
    result = VPCClient(ctx.obj['client']).list_vpce_endpoint_labels(
        region_id=region_id, endpoint_id=endpoint_id, page_number=page_number, page_size=page_size)
    _label_output(ctx, result)


@vpc.command('label-vpce-service')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--endpoint-service-id', required=True, help='终端节点服务ID')
@click.option('--page-number', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.pass_context
def label_vpce_service(ctx, region_id, endpoint_service_id, page_number, page_size):
    """获取终端节点服务绑定的标签"""
    from vpc.client import VPCClient
    result = VPCClient(ctx.obj['client']).list_vpce_service_labels(
        region_id=region_id, endpoint_service_id=endpoint_service_id,
        page_number=page_number, page_size=page_size)
    _label_output(ctx, result)


@vpc.command('label-private-dns')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--zone-id', required=True, help='内网DNS ID')
@click.option('--page-no', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.pass_context
def label_private_dns(ctx, region_id, zone_id, page_no, page_size):
    """获取内网DNS绑定的标签"""
    from vpc.client import VPCClient
    result = VPCClient(ctx.obj['client']).list_private_dns_labels(
        region_id=region_id, zone_id=zone_id, page_no=page_no, page_size=page_size)
    _label_output(ctx, result)

# ==================== EIP监控/共享带宽/流量包 命令 ====================

@eip.command('realtime-monitor')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--device-ids', help='EIP地址列表，逗号分隔（例：192.2.3.3,192.2.3.4）')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（1-50）')
@click.pass_context
@handle_error
def eip_realtime_monitor(ctx, region_id: str, device_ids: Optional[str],
                         page_no: Optional[int], page_size: Optional[int]):
    """查询EIP实时监控（旧版）"""
    client = get_vpc_client(ctx)
    result = client.query_eip_realtime_monitor(
        region_id=region_id,
        device_ids=device_ids.split(',') if device_ids else None,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@eip.command('new-realtime-monitor')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--device-ids', help='EIP地址列表，逗号分隔')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（1-50）')
@click.pass_context
@handle_error
def eip_new_realtime_monitor(ctx, region_id: str, device_ids: Optional[str],
                             page_no: Optional[int], page_size: Optional[int]):
    """查询EIP实时监控（新版）"""
    client = get_vpc_client(ctx)
    result = client.query_eip_realtime_monitor_new(
        region_id=region_id,
        device_ids=device_ids.split(',') if device_ids else None,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@eip.command('history-monitor')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--device-ids', required=True, help='EIP地址列表，逗号分隔')
@click.option('--metric-names', required=True, help='监控指标，逗号分隔（如：ingress_throughput）')
@click.option('--start-time', required=True, help='开始时间（YYYY-mm-dd HH:MM:SS）')
@click.option('--end-time', required=True, help='结束时间（YYYY-mm-dd HH:MM:SS）')
@click.option('--period', type=int, help='聚合周期（秒），最小300')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（1-50）')
@click.pass_context
@handle_error
def eip_history_monitor(ctx, region_id: str, device_ids: str, metric_names: str,
                        start_time: str, end_time: str, period: Optional[int],
                        page_no: Optional[int], page_size: Optional[int]):
    """查询EIP历史监控数据（旧版）"""
    client = get_vpc_client(ctx)
    result = client.query_eip_history_monitor(
        region_id=region_id, device_ids=device_ids.split(','),
        metric_names=metric_names.split(','), start_time=start_time, end_time=end_time,
        period=period, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@eip.command('new-history-monitor')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--device-ids', required=True, help='EIP地址列表，逗号分隔')
@click.option('--metric-names', required=True, help='监控指标，逗号分隔')
@click.option('--start-time', required=True, help='开始时间（YYYY-mm-dd HH:MM:SS）')
@click.option('--end-time', required=True, help='结束时间（YYYY-mm-dd HH:MM:SS）')
@click.option('--period', type=int, help='聚合周期（秒），默认60')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（1-50）')
@click.pass_context
@handle_error
def eip_new_history_monitor(ctx, region_id: str, device_ids: str, metric_names: str,
                            start_time: str, end_time: str, period: Optional[int],
                            page_no: Optional[int], page_size: Optional[int]):
    """查询EIP历史监控数据（新版）"""
    client = get_vpc_client(ctx)
    result = client.query_eip_history_monitor_new(
        region_id=region_id, device_ids=device_ids.split(','),
        metric_names=metric_names.split(','), start_time=start_time, end_time=end_time,
        period=period, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@eip.command('filing-status')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--eip-id', required=True, help='弹性公网IP ID')
@click.pass_context
@handle_error
def eip_filing_status(ctx, region_id: str, eip_id: str):
    """查看端口备案状态"""
    client = get_vpc_client(ctx)
    result = client.get_eip_filing_status(region_id=region_id, eip_id=eip_id)
    format_output(result, ctx.obj['output'])


@eip.command('check-address')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--eip-address', required=True, help='弹性公网IP地址')
@click.pass_context
@handle_error
def eip_check_address(ctx, region_id: str, eip_address: str):
    """检查EIP地址是否可用"""
    client = get_vpc_client(ctx)
    result = client.check_eip_address(region_id=region_id, eip_address=eip_address)
    format_output(result, ctx.obj['output'])


@vpc.group()
def bandwidth():
    """共享带宽查询"""
    pass


@bandwidth.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth-id', required=True, help='共享带宽ID')
@click.pass_context
@handle_error
def bandwidth_show(ctx, region_id: str, bandwidth_id: str):
    """查询共享带宽详情"""
    client = get_vpc_client(ctx)
    result = client.show_shared_bandwidth(region_id=region_id, bandwidth_id=bandwidth_id)
    format_output(result, ctx.obj['output'])


@bandwidth.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--query-content', help='模糊查询（名称/带宽ID）')
@click.option('--project-id', help='企业项目ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def bandwidth_new_list(ctx, region_id: str, query_content: Optional[str],
                       project_id: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """新查询共享带宽列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_shared_bandwidths(
        region_id=region_id, query_content=query_content, project_id=project_id,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def flow_package():
    """共享流量包查询"""
    pass


@flow_package.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.pass_context
@handle_error
def flow_package_list(ctx, region_id: str):
    """查询共享流量包列表"""
    client = get_vpc_client(ctx)
    result = client.list_flow_packages(region_id=region_id)
    format_output(result, ctx.obj['output'])


@flow_package.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--sdp-id', required=True, help='流量包记录标识')
@click.pass_context
@handle_error
def flow_package_show(ctx, region_id: str, sdp_id: str):
    """查询共享流量包详情"""
    client = get_vpc_client(ctx)
    result = client.show_flow_package(region_id=region_id, sdp_id=sdp_id)
    format_output(result, ctx.obj['output'])


@flow_package.command('metric')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--sdp-id', required=True, help='流量包记录标识')
@click.option('--start-time', required=True, help='开始时间（YYYY-mm-dd HH:MM:SS）')
@click.option('--end-time', required=True, help='结束时间（YYYY-mm-dd HH:MM:SS）')
@click.pass_context
@handle_error
def flow_package_metric(ctx, region_id: str, sdp_id: str, start_time: str, end_time: str):
    """获取共享流量包监控"""
    client = get_vpc_client(ctx)
    result = client.get_flow_package_metric(
        region_id=region_id, sdp_id=sdp_id, start_time=start_time, end_time=end_time)
    format_output(result, ctx.obj['output'])


# ==================== VPC 终端节点 / 内网DNS 查询命令 ====================

@vpc.group()
def vpce():
    """VPC 终端节点查询"""
    pass


@vpce.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--project-id', help='企业项目ID')
@click.option('--endpoint-name', help='终端节点名（精确匹配）')
@click.option('--query-content', help='终端节点名模糊匹配')
@click.option('--endpoint-service-id', help='终端节点服务ID')
@click.option('--endpoint-id', help='终端节点ID')
@click.pass_context
@handle_error
def vpce_list(ctx, region_id: str, page_no: Optional[int], page_size: Optional[int],
              project_id: Optional[str], endpoint_name: Optional[str],
              query_content: Optional[str], endpoint_service_id: Optional[str],
              endpoint_id: Optional[str]):
    """查看终端节点列表"""
    client = get_vpc_client(ctx)
    result = client.list_vpce_endpoints(
        region_id=region_id, page_no=page_no, page_size=page_size,
        project_id=project_id, endpoint_name=endpoint_name,
        query_content=query_content, endpoint_service_id=endpoint_service_id,
        endpoint_id=endpoint_id)
    format_output(result, ctx.obj['output'])


@vpce.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--project-id', help='企业项目ID')
@click.option('--endpoint-name', help='终端节点名（精确匹配）')
@click.option('--query-content', help='终端节点名模糊匹配')
@click.option('--endpoint-service-id', help='终端节点服务ID')
@click.option('--endpoint-id', help='终端节点ID')
@click.pass_context
@handle_error
def vpce_new_list(ctx, region_id: str, page_no: Optional[int], page_size: Optional[int],
                  project_id: Optional[str], endpoint_name: Optional[str],
                  query_content: Optional[str], endpoint_service_id: Optional[str],
                  endpoint_id: Optional[str]):
    """新查看终端节点列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_vpce_endpoints(
        region_id=region_id, page_no=page_no, page_size=page_size,
        project_id=project_id, endpoint_name=endpoint_name,
        query_content=query_content, endpoint_service_id=endpoint_service_id,
        endpoint_id=endpoint_id)
    format_output(result, ctx.obj['output'])


@vpce.group()
def service():
    """VPC 终端节点服务查询"""
    pass


@service.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--id', 'id_', help='终端节点服务ID')
@click.option('--endpoint-service-name', help='终端节点服务名称（精确匹配）')
@click.option('--query-content', help='终端节点服务名称模糊匹配')
@click.pass_context
@handle_error
def vpce_service_list(ctx, region_id: str, page_no: Optional[int], page_size: Optional[int],
                      id_: Optional[str], endpoint_service_name: Optional[str],
                      query_content: Optional[str]):
    """查看终端节点服务列表"""
    client = get_vpc_client(ctx)
    result = client.list_vpce_services(
        region_id=region_id, page_no=page_no, page_size=page_size,
        id_=id_, endpoint_service_name=endpoint_service_name, query_content=query_content)
    format_output(result, ctx.obj['output'])


@service.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量')
@click.option('--id', 'id_', help='终端节点服务ID')
@click.option('--endpoint-service-name', help='终端节点服务名称（精确匹配）')
@click.option('--query-content', help='终端节点服务名称模糊匹配')
@click.pass_context
@handle_error
def vpce_service_new_list(ctx, region_id: str, page_no: Optional[int], page_size: Optional[int],
                          id_: Optional[str], endpoint_service_name: Optional[str],
                          query_content: Optional[str]):
    """新查看终端节点服务列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_vpce_services(
        region_id=region_id, page_no=page_no, page_size=page_size,
        id_=id_, endpoint_service_name=endpoint_service_name, query_content=query_content)
    format_output(result, ctx.obj['output'])


@service.command('backends')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--endpoint-service-id', required=True, help='终端节点服务ID')
@click.pass_context
@handle_error
def vpce_service_backends(ctx, region_id: str, endpoint_service_id: str):
    """查看终端节点服务后端列表"""
    client = get_vpc_client(ctx)
    result = client.list_vpce_backends(
        region_id=region_id, endpoint_service_id=endpoint_service_id)
    format_output(result, ctx.obj['output'])


@vpc.group()
def dns():
    """内网DNS查询"""
    pass


@dns.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--zone-id', help='zoneID')
@click.option('--zone-name', help='zone名称')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大200）')
@click.pass_context
@handle_error
def dns_list(ctx, region_id: str, zone_id: Optional[str], zone_name: Optional[str],
             page_no: Optional[int], page_size: Optional[int]):
    """查询内网DNS列表"""
    client = get_vpc_client(ctx)
    result = client.list_private_zones(
        region_id=region_id, zone_id=zone_id, zone_name=zone_name,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@dns.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--zone-id', help='zoneID')
@click.option('--zone-name', help='zone名称')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大200）')
@click.pass_context
@handle_error
def dns_new_list(ctx, region_id: str, zone_id: Optional[str], zone_name: Optional[str],
                 page_no: Optional[int], page_size: Optional[int]):
    """新内网DNS列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_private_zones(
        region_id=region_id, zone_id=zone_id, zone_name=zone_name,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@dns.group()
def record():
    """内网DNS记录查询"""
    pass


@record.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--zone-id', help='zoneID')
@click.option('--zone-record-name', help='DNS记录集名称')
@click.option('--zone-record-id', help='zoneRecordID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def dns_record_list(ctx, region_id: str, zone_id: Optional[str], zone_record_name: Optional[str],
                    zone_record_id: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """查询内网DNS记录列表"""
    client = get_vpc_client(ctx)
    result = client.list_private_zone_records(
        region_id=region_id, zone_id=zone_id, zone_record_name=zone_record_name,
        zone_record_id=zone_record_id, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@record.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--zone-id', help='zoneID')
@click.option('--zone-record-name', help='DNS记录集名称')
@click.option('--zone-record-id', help='zoneRecordID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大200）')
@click.pass_context
@handle_error
def dns_record_new_list(ctx, region_id: str, zone_id: Optional[str], zone_record_name: Optional[str],
                        zone_record_id: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """新内网DNS记录列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_private_zone_records(
        region_id=region_id, zone_id=zone_id, zone_record_name=zone_record_name,
        zone_record_id=zone_record_id, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


# ==================== 网络 ACL / 前缀列表 / 流量 / GWLB / L2GW / havip 命令 ====================

@vpc.group()
def acl():
    """网络 ACL 查询"""
    pass


@acl.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--acl-id', help='aclID')
@click.option('--project-id', help='企业项目ID')
@click.option('--name', help='acl名称')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def acl_list(ctx, region_id: str, acl_id: Optional[str], project_id: Optional[str],
             name: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """查看ACL列表信息"""
    client = get_vpc_client(ctx)
    result = client.list_acls(region_id=region_id, acl_id=acl_id, project_id=project_id,
                              name=name, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@acl.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--acl-id', help='aclID')
@click.option('--name', help='acl名称')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def acl_new_list(ctx, region_id: str, acl_id: Optional[str], name: Optional[str],
                 page_no: Optional[int], page_size: Optional[int]):
    """新查看ACL列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_acls(region_id=region_id, acl_id=acl_id, name=name,
                                  page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@acl.command('rules')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--acl-id', required=True, help='aclID')
@click.pass_context
@handle_error
def acl_rules(ctx, region_id: str, acl_id: str):
    """查看ACL规则列表"""
    client = get_vpc_client(ctx)
    result = client.list_acl_rules(region_id=region_id, acl_id=acl_id)
    format_output(result, ctx.obj['output'])


@vpc.group()
def prefix_list():
    """前缀列表查询"""
    pass


@prefix_list.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--prefix-list-id', help='prefixlistID')
@click.option('--query-content', help='模糊查询关键字')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def prefix_list_list(ctx, region_id: str, prefix_list_id: Optional[str],
                     query_content: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """查询前缀列表"""
    client = get_vpc_client(ctx)
    result = client.list_prefix_lists(region_id=region_id, prefix_list_id=prefix_list_id,
                                      query_content=query_content, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@prefix_list.command('show')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--prefix-list-id', required=True, help='prefixlistID')
@click.pass_context
@handle_error
def prefix_list_show(ctx, region_id: str, prefix_list_id: str):
    """查询前缀列表详情"""
    client = get_vpc_client(ctx)
    result = client.show_prefix_list(region_id=region_id, prefix_list_id=prefix_list_id)
    format_output(result, ctx.obj['output'])


@prefix_list.command('associations')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--prefix-list-id', required=True, help='prefixlistID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def prefix_list_associations(ctx, region_id: str, prefix_list_id: str,
                             page_no: Optional[int], page_size: Optional[int]):
    """查询前缀列表关联资源"""
    client = get_vpc_client(ctx)
    result = client.get_prefix_list_associations(region_id=region_id, prefix_list_id=prefix_list_id,
                                                 page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def flow():
    """流量控制查询"""
    pass


@flow.command('filter-rules')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--mirror-filter-id', required=True, help='过滤条件ID')
@click.option('--direction', type=click.Choice(['in', 'out']), required=True, help='方向：in/out')
@click.option('--query-content', help='模糊过滤内容')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def flow_filter_rules(ctx, region_id: str, mirror_filter_id: str, direction: str,
                      query_content: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """查看过滤规则列表"""
    client = get_vpc_client(ctx)
    result = client.list_flow_filter_rules(region_id=region_id, mirror_filter_id=mirror_filter_id,
                                           direction=direction, query_content=query_content,
                                           page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@flow.command('filters')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--query-content', help='按名字模糊过滤')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def flow_filters(ctx, region_id: str, query_content: Optional[str],
                 page_no: Optional[int], page_size: Optional[int]):
    """查看过滤条件列表"""
    client = get_vpc_client(ctx)
    result = client.list_flow_filters(region_id=region_id, query_content=query_content,
                                      page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@flow.command('sessions')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--mirror-filter-id', help='过滤条件ID')
@click.option('--query-content', help='按名字模糊过滤')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def flow_sessions(ctx, region_id: str, mirror_filter_id: Optional[str], query_content: Optional[str],
                  page_no: Optional[int], page_size: Optional[int]):
    """查看流量会话列表"""
    client = get_vpc_client(ctx)
    result = client.list_flow_sessions(region_id=region_id, mirror_filter_id=mirror_filter_id,
                                       query_content=query_content, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def gwlb():
    """网关负载均衡 GWLB 查询"""
    pass


@gwlb.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--project-id', help='企业项目ID')
@click.option('--gw-lb-id', help='GWLB ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def gwlb_list(ctx, region_id: str, project_id: Optional[str], gw_lb_id: Optional[str],
              page_number: Optional[int], page_size: Optional[int]):
    """查看GWLB列表"""
    client = get_vpc_client(ctx)
    result = client.list_gwlbs(region_id=region_id, project_id=project_id, gw_lb_id=gw_lb_id,
                               page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@gwlb.command('ip-listener-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--ip-listener-id', help='监听器ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def gwlb_ip_listener_list(ctx, region_id: str, ip_listener_id: Optional[str],
                          page_number: Optional[int], page_size: Optional[int]):
    """查看IP监听器列表"""
    client = get_vpc_client(ctx)
    result = client.list_ip_listeners(region_id=region_id, ip_listener_id=ip_listener_id,
                                      page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def l2gw():
    """二层网关 L2GW 查询"""
    pass


@l2gw.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--l2gw-id', help='l2gw ID')
@click.option('--query-content', help='名称模糊查询')
@click.option('--page-no', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def l2gw_list(ctx, region_id: str, l2gw_id: Optional[str], query_content: Optional[str],
              page_no: Optional[int], page_size: Optional[int]):
    """查询L2GW列表"""
    client = get_vpc_client(ctx)
    result = client.list_l2gws(region_id=region_id, l2gw_id=l2gw_id, query_content=query_content,
                               page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@l2gw.command('connection-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--l2gw-id', help='l2gw ID（3.0资源池必填）')
@click.option('--l2-connection-id', help='l2gw_connection ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def l2gw_connection_list(ctx, region_id: str, l2gw_id: Optional[str],
                         l2_connection_id: Optional[str],
                         page_no: Optional[int], page_size: Optional[int]):
    """查询L2GW connection列表"""
    client = get_vpc_client(ctx)
    result = client.list_l2gw_connections(region_id=region_id, l2gw_id=l2gw_id,
                                          l2_connection_id=l2_connection_id,
                                          page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def havip():
    """高可用虚拟IP HaVip 查询"""
    pass


@havip.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--project-id', help='企业项目ID')
@click.option('--filter', multiple=True,
              help='筛选条件，格式 key=value（key 支持 haVipID/vpcID/subnetID），可多次指定')
@click.pass_context
@handle_error
def havip_list(ctx, region_id: str, project_id: Optional[str], filter):
    """查看HaVip列表"""
    filters = []
    for f in filter:
        if '=' in f:
            k, v = f.split('=', 1)
            filters.append({'key': k.strip(), 'value': v.strip()})
    client = get_vpc_client(ctx)
    result = client.list_havips(region_id=region_id, project_id=project_id,
                                filters=filters if filters else None)
    format_output(result, ctx.obj['output'])


# ==================== 网络诊断 / DHCP-VPC绑定 / IPv6 / IPv4网关 命令 ====================

@vpc.group()
def diagnose():
    """网络诊断查询"""
    pass


@diagnose.command('instances')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--resource-id', help='资源ID')
@click.option('--resource-type', type=click.Choice(['eip', 'natgw', 'elb']), help='资源类型')
@click.option('--diagnosis-record-id', help='实例诊断记录ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def diagnose_instances(ctx, region_id: str, resource_id: Optional[str], resource_type: Optional[str],
                       diagnosis_record_id: Optional[str], page_number: Optional[int], page_size: Optional[int]):
    """获取实例诊断列表"""
    client = get_vpc_client(ctx)
    result = client.list_instance_diagnoses(
        region_id=region_id, resource_id=resource_id, resource_type=resource_type,
        diagnosis_record_id=diagnosis_record_id, page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@diagnose.command('records')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--resource-id', help='资源ID')
@click.option('--resource-type', type=click.Choice(['eip', 'natgw', 'elb']), help='资源类型')
@click.option('--diagnosis-record-id', help='实例诊断记录ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def diagnose_records(ctx, region_id: str, resource_id: Optional[str], resource_type: Optional[str],
                     diagnosis_record_id: Optional[str], page_number: Optional[int], page_size: Optional[int]):
    """获取实例诊断记录列表"""
    client = get_vpc_client(ctx)
    result = client.list_instance_diagnosis_records(
        region_id=region_id, resource_id=resource_id, resource_type=resource_type,
        diagnosis_record_id=diagnosis_record_id, page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@diagnose.command('paths')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--network-path-id', help='网络路径ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def diagnose_paths(ctx, region_id: str, network_path_id: Optional[str],
                   page_number: Optional[int], page_size: Optional[int]):
    """获取网络路径列表"""
    client = get_vpc_client(ctx)
    result = client.list_network_paths(region_id=region_id, network_path_id=network_path_id,
                                       page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@diagnose.command('analyses')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--network-path-id', help='网络路径ID')
@click.option('--analysis-id', help='路径分析ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def diagnose_analyses(ctx, region_id: str, network_path_id: Optional[str], analysis_id: Optional[str],
                      page_number: Optional[int], page_size: Optional[int]):
    """获取网络路径分析列表"""
    client = get_vpc_client(ctx)
    result = client.list_network_path_analyses(
        region_id=region_id, network_path_id=network_path_id, analysis_id=analysis_id,
        page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@diagnose.command('reports')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--analysis-id', required=True, help='路径分析ID')
@click.option('--page-number', type=int, help='页码')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def diagnose_reports(ctx, region_id: str, analysis_id: str,
                     page_number: Optional[int], page_size: Optional[int]):
    """获取网络路径分析报告列表"""
    client = get_vpc_client(ctx)
    result = client.list_network_path_reports(
        region_id=region_id, analysis_id=analysis_id,
        page_number=page_number, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def dhcp():
    """DHCP 与 VPC 绑定关系查询"""
    pass


@dhcp.command('bound-vpcs')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--dhcp-option-sets-id', required=True, help='DHCP 集合ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def dhcp_bound_vpcs(ctx, region_id: str, dhcp_option_sets_id: str,
                    page_no: Optional[int], page_size: Optional[int]):
    """获取DHCP绑定的VPC列表"""
    client = get_vpc_client(ctx)
    result = client.list_dhcp_bound_vpcs(
        region_id=region_id, dhcp_option_sets_id=dhcp_option_sets_id,
        page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@dhcp.command('unbound-vpcs')
@click.option('--region-id', required=True, help='区域ID')
@click.pass_context
@handle_error
def dhcp_unbound_vpcs(ctx, region_id: str):
    """获取未绑定DHCP的VPC列表"""
    client = get_vpc_client(ctx)
    result = client.list_dhcp_unbound_vpcs(region_id=region_id)
    format_output(result, ctx.obj['output'])


@dns.command('vpcs')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--zone-id', required=True, help='zoneID')
@click.pass_context
@handle_error
def dns_vpcs(ctx, region_id: str, zone_id: str):
    """获取zone绑定的VPC列表"""
    client = get_vpc_client(ctx)
    result = client.list_zone_bound_vpcs(region_id=region_id, zone_id=zone_id)
    format_output(result, ctx.obj['output'])


@vpc.group()
def ipv6():
    """IPv6 网关/地址/带宽查询"""
    pass


@ipv6.command('gateways')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--project-id', help='企业项目ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def ipv6_gateways(ctx, region_id: str, project_id: Optional[str],
                  page_no: Optional[int], page_size: Optional[int]):
    """查询IPv6网关列表"""
    client = get_vpc_client(ctx)
    result = client.list_ipv6_gateways(region_id=region_id, project_id=project_id,
                                       page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@ipv6.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--subnet-id', help='子网ID')
@click.option('--ip-address', help='IPv6地址')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（1-50）')
@click.pass_context
@handle_error
def ipv6_list(ctx, region_id: str, vpc_id: Optional[str], subnet_id: Optional[str],
              ip_address: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """查询IPv6地址列表"""
    client = get_vpc_client(ctx)
    result = client.list_ipv6_addresses(region_id=region_id, vpc_id=vpc_id, subnet_id=subnet_id,
                                        ip_address=ip_address, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@ipv6.command('new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.option('--subnet-id', help='子网ID')
@click.option('--ip-address', help='IPv6地址')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（1-50）')
@click.pass_context
@handle_error
def ipv6_new_list(ctx, region_id: str, vpc_id: Optional[str], subnet_id: Optional[str],
                  ip_address: Optional[str], page_no: Optional[int], page_size: Optional[int]):
    """新查询IPv6地址列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_ipv6_addresses(region_id=region_id, vpc_id=vpc_id, subnet_id=subnet_id,
                                            ip_address=ip_address, page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@ipv6.command('bw-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--query-content', help='模糊查询（名称/带宽ID）')
@click.option('--bandwidth-id', help='IPv6带宽ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def ipv6_bw_list(ctx, region_id: str, query_content: Optional[str], bandwidth_id: Optional[str],
                 page_no: Optional[int], page_size: Optional[int]):
    """查看IPv6带宽列表"""
    client = get_vpc_client(ctx)
    result = client.list_ipv6_bandwidths(region_id=region_id, query_content=query_content,
                                         bandwidth_id=bandwidth_id,
                                         page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@ipv6.command('bw-new-list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--query-content', help='模糊查询（名称/带宽ID）')
@click.option('--bandwidth-id', help='IPv6带宽ID')
@click.option('--page-no', type=int, help='页码（推荐使用）')
@click.option('--page-size', type=int, help='每页数量（最大50）')
@click.pass_context
@handle_error
def ipv6_bw_new_list(ctx, region_id: str, query_content: Optional[str], bandwidth_id: Optional[str],
                     page_no: Optional[int], page_size: Optional[int]):
    """新查看IPv6带宽列表"""
    client = get_vpc_client(ctx)
    result = client.new_list_ipv6_bandwidths(region_id=region_id, query_content=query_content,
                                             bandwidth_id=bandwidth_id,
                                             page_no=page_no, page_size=page_size)
    format_output(result, ctx.obj['output'])


@vpc.group()
def ipv4_gw():
    """IPv4 网关查询"""
    pass


@ipv4_gw.command('list')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', help='VPC ID')
@click.pass_context
@handle_error
def ipv4_gw_list(ctx, region_id: str, vpc_id: Optional[str]):
    """获取IPv4网关列表"""
    client = get_vpc_client(ctx)
    result = client.list_ipv4_gateways(region_id=region_id, vpc_id=vpc_id)
    format_output(result, ctx.obj['output'])


# ==================== VPC 询价命令（18个） ====================

@vpc.group()
def price():
    """VPC 询价"""
    pass


@price.group()
def eip():
    """EIP 询价"""
    pass


@eip.command('create')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month', 'year', 'on_demand']), help='订购类型')
@click.option('--name', required=True, help='EIP名称')
@click.option('--cycle-count', type=int, help='订购时长')
@click.option('--bandwidth', type=int, help='带宽峰值(Mbps 1-300)')
@click.option('--demand-billing-type', type=click.Choice(['bandwidth', 'upflowc']), help='按需计费类型')
@click.pass_context
@handle_error
def price_eip_create(ctx, **kw):
    """EIP创建询价"""
    result = get_vpc_client(ctx).eip_create_price(**{k.replace('-','_'):v for k,v in kw.items() if v is not None})
    format_output(result, ctx.obj.get('output', 'table'))


@eip.command('modify')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--eip-id', required=True, help='EIP ID')
@click.option('--bandwidth', required=True, type=int, help='变更后带宽(Mbps)')
@click.pass_context
@handle_error
def price_eip_modify(ctx, region_id, eip_id, bandwidth):
    """EIP变配询价"""
    result = get_vpc_client(ctx).eip_modify_price(region_id, eip_id, bandwidth)
    format_output(result, ctx.obj.get('output', 'table'))


@eip.command('renew')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--eip-id', required=True, help='EIP ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month', 'year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.pass_context
@handle_error
def price_eip_renew(ctx, region_id, eip_id, cycle_type, cycle_count):
    """EIP续订询价"""
    result = get_vpc_client(ctx).eip_renew_price(region_id, eip_id, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@price.group()
def nat():
    """NAT 询价"""
    pass


@nat.command('create')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--name', required=True, help='NAT网关名称')
@click.option('--spec', required=True, type=click.Choice([1,2,3,4]), help='规格：1小/2中/3大/4超大')
@click.option('--az-name', required=True, help='可用区')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.pass_context
@handle_error
def price_nat_create(ctx, region_id, vpc_id, name, spec, az_name, cycle_type, cycle_count):
    """NAT创建询价"""
    result = get_vpc_client(ctx).nat_create_price(region_id, vpc_id, name, spec, az_name, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@nat.command('modify')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--nat-gateway-id', required=True, help='NAT网关ID')
@click.option('--spec', required=True, type=click.Choice([1,2,3,4]), help='规格：1小/2中/3大/4超大')
@click.pass_context
@handle_error
def price_nat_modify(ctx, region_id, nat_gateway_id, spec):
    """NAT变配询价"""
    result = get_vpc_client(ctx).nat_modify_price(region_id, nat_gateway_id, spec)
    format_output(result, ctx.obj.get('output', 'table'))


@nat.command('renew')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--nat-gateway-id', required=True, help='NAT网关ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.pass_context
@handle_error
def price_nat_renew(ctx, region_id, nat_gateway_id, cycle_type, cycle_count):
    """NAT续订询价"""
    result = get_vpc_client(ctx).nat_renew_price(region_id, nat_gateway_id, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@price.group()
def bw():
    """共享带宽询价"""
    pass


@bw.command('create')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth', required=True, type=int, help='带宽峰值(Mbps >=5)')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year','on_demand']), help='订购类型')
@click.option('--cycle-count', type=int, help='订购时长')
@click.option('--name', required=True, help='共享带宽名称')
@click.pass_context
@handle_error
def price_bw_create(ctx, region_id, bandwidth, cycle_type, cycle_count, name):
    """共享带宽创建询价"""
    result = get_vpc_client(ctx).bandwidth_create_price(region_id, bandwidth, cycle_type, cycle_count or 1, name)
    format_output(result, ctx.obj.get('output', 'table'))


@bw.command('modify')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth-id', required=True, help='共享带宽ID')
@click.option('--bandwidth', required=True, type=int, help='变更后带宽(Mbps)')
@click.pass_context
@handle_error
def price_bw_modify(ctx, region_id, bandwidth_id, bandwidth):
    """共享带宽变配询价"""
    result = get_vpc_client(ctx).bandwidth_modify_price(region_id, bandwidth_id, bandwidth)
    format_output(result, ctx.obj.get('output', 'table'))


@bw.command('renew')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth-id', required=True, help='共享带宽ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.pass_context
@handle_error
def price_bw_renew(ctx, region_id, bandwidth_id, cycle_type, cycle_count):
    """共享带宽续订询价"""
    result = get_vpc_client(ctx).bandwidth_renew_price(region_id, bandwidth_id, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@price.command('flow-package')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--cycle-type', required=True, type=click.Choice(['MONTH','YEAR']), help='订阅周期')
@click.option('--cycle-count', required=True, type=int, help='周期时长（仅支持1）')
@click.option('--count', required=True, type=int, help='购买数量(1-20)')
@click.option('--spec', required=True, type=int, help='流量包规格(GB)')
@click.pass_context
@handle_error
def price_flow_pkg(ctx, region_id, cycle_type, cycle_count, count, spec):
    """共享流量包询价"""
    result = get_vpc_client(ctx).flow_package_price(region_id, cycle_type, cycle_count, count, spec)
    format_output(result, ctx.obj.get('output', 'table'))


@price.group()
def ipv6():
    """IPv6带宽询价"""
    pass


@ipv6.command('create')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth', required=True, type=int, help='带宽峰值(Mbps)')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.option('--name', required=True, help='IPv6带宽名称')
@click.pass_context
@handle_error
def price_ipv6_create(ctx, region_id, bandwidth, cycle_type, cycle_count, name):
    """IPv6带宽创建询价"""
    result = get_vpc_client(ctx).ipv6_bw_create_price(region_id, bandwidth, cycle_type, cycle_count, name)
    format_output(result, ctx.obj.get('output', 'table'))


@ipv6.command('modify')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth-id', required=True, help='IPv6带宽ID')
@click.option('--bandwidth', required=True, type=int, help='变更后带宽(Mbps)')
@click.pass_context
@handle_error
def price_ipv6_modify(ctx, region_id, bandwidth_id, bandwidth):
    """IPv6带宽变配询价"""
    result = get_vpc_client(ctx).ipv6_bw_modify_price(region_id, bandwidth_id, bandwidth)
    format_output(result, ctx.obj.get('output', 'table'))


@ipv6.command('renew')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--bandwidth-id', required=True, help='IPv6带宽ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.pass_context
@handle_error
def price_ipv6_renew(ctx, region_id, bandwidth_id, cycle_type, cycle_count):
    """IPv6带宽续订询价"""
    result = get_vpc_client(ctx).ipv6_bw_renew_price(region_id, bandwidth_id, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@price.command('vpce')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--endpoint-service-id', required=True, help='终端节点服务ID')
@click.option('--endpoint-name', required=True, help='终端节点名称')
@click.option('--subnet-id', required=True, help='子网ID')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--ip', help='指定IP地址')
@click.pass_context
@handle_error
def price_vpce(ctx, region_id, endpoint_service_id, endpoint_name, subnet_id, vpc_id, ip):
    """终端节点创建询价"""
    result = get_vpc_client(ctx).vpce_create_price(region_id, endpoint_service_id, endpoint_name, subnet_id, vpc_id, ip)
    format_output(result, ctx.obj.get('output', 'table'))


@price.group()
def l2gw():
    """L2GW询价"""
    pass


@l2gw.command('create')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--spec', required=True, type=click.Choice(['STANDARD','ENHANCED']), help='规格')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year','on_demand']), help='订购类型')
@click.option('--cycle-count', type=int, help='订购时长')
@click.pass_context
@handle_error
def price_l2gw_create(ctx, region_id, spec, cycle_type, cycle_count):
    """L2GW订购询价"""
    result = get_vpc_client(ctx).l2gw_create_price(region_id, spec, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@l2gw.command('renew')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--l2gw-id', required=True, help='L2GW ID')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='订购类型')
@click.option('--cycle-count', required=True, type=int, help='订购时长')
@click.pass_context
@handle_error
def price_l2gw_renew(ctx, region_id, l2gw_id, cycle_type, cycle_count):
    """L2GW续订询价"""
    result = get_vpc_client(ctx).l2gw_renew_price(region_id, l2gw_id, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@price.command('to-cycle')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--resource-id', required=True, help='资源ID')
@click.option('--resource-type', required=True, type=click.Choice(['eip','bandwidth','elb','private_nat','public_nat']), help='资源类型')
@click.option('--cycle-type', required=True, type=click.Choice(['month','year']), help='周期类型')
@click.option('--cycle-count', required=True, type=int, help='周期数')
@click.pass_context
@handle_error
def price_to_cycle(ctx, region_id, resource_id, resource_type, cycle_type, cycle_count):
    """包周期询价（按需转包周期）"""
    result = get_vpc_client(ctx).to_cycle_price(region_id, resource_id, resource_type, cycle_type, cycle_count)
    format_output(result, ctx.obj.get('output', 'table'))


@price.command('to-ondemand')
@click.option('--region-id', required=True, help='区域ID')
@click.option('--resource-id', required=True, help='资源ID')
@click.option('--resource-type', required=True, type=click.Choice(['eip','bandwidth','elb','private_nat','public_nat']), help='资源类型')
@click.pass_context
@handle_error
def price_to_ondemand(ctx, region_id, resource_id, resource_type):
    """转按需询价（包周期转按需）"""
    result = get_vpc_client(ctx).to_ondemand_price(region_id, resource_id, resource_type)
    format_output(result, ctx.obj.get('output', 'table'))
