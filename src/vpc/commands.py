"""
VPC(虚拟私有云)命令行接口
"""

import click
from typing import List, Optional
# 直接定义装饰器，避免循环导入
from vpc import VPCClient
from utils import ValidationUtils, OutputFormatter


def handle_error(func):
    """
    错误处理装饰器
    """
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


# ==================== 流日志管理命令 ====================

@vpc.group()
def flow_log():
    """流日志查询"""
    pass


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