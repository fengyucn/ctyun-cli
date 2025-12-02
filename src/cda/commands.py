"""
云专线CDA (Cloud Dedicated Access) 服务命令行接口

提供云专线资源的CLI管理功能，包括：
- 专线网关管理 (cda-gateway)
- 物理专线管理 (cda-physical-line)
- VPC管理 (cda-vpc)
- 静态路由管理 (cda-static-route)
- BGP路由管理 (cda-bgp-route)
- 跨账号授权 (cda-account-auth)
- 健康检查和链路探测
"""

import click
from typing import Optional, List
from core import CTYUNAPIError
from utils import OutputFormatter, logger
from cda import init_cda_client, get_cda_client


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
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                table = OutputFormatter.format_table(data, headers)
                click.echo(table)
            else:
                click.echo(data)
        elif isinstance(data, dict):
            headers = ['字段', '值']
            table_data = []
            for key, value in data.items():
                table_data.append([key, value])
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


@click.group()
def cda():
    """云专线CDA服务管理"""
    pass


# ============ 专线网关相关命令 ============

@cda.group('gateway')
def gateway():
    """专线网关管理"""
    pass


@gateway.command('list')
@click.option('--account', required=True, help='天翼云客户邮箱（必填）')
@click.option('--region-id', help='资源池ID（可选）')
@click.option('--project-id', help='项目ID（可选）')
@click.option('--gateway-name', help='专线网关名称（可选）')
@click.option('--page-no', default=1, type=int, help='页码，默认为1')
@click.option('--page-size', default=10, type=int, help='每页数量，默认为10')
@click.pass_context
@handle_error
def list_gateways(ctx, account: str, region_id: Optional[str], project_id: Optional[str],
                 gateway_name: Optional[str], page_no: int, page_size: int):
    """
    查询专线网关列表

    示例：
        # 查询所有专线网关
        ctyun-cli cda gateway list --account user@example.com

        # 按资源池查询专线网关
        ctyun-cli cda gateway list --account user@example.com --region-id 81f7728662dd11ec810800155d307d5b

        # 分页查询专线网关
        ctyun-cli cda gateway list --account user@example.com --page-no 1 --page-size 20

        # 按名称搜索专线网关
        ctyun-cli cda gateway list --account user@example.com --gateway-name my-gateway
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询专线网关列表
    result = cda_client.list_gateways(
        page_no=page_no,
        page_size=page_size,
        account=account,
        region_id=region_id,
        project_id=project_id,
        gateway_name=gateway_name
    )

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    gateway_list = data.get('lineGatewayList', [])
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)

    if output_format == 'json':
        output_data = {
            'totalCount': total_count,
            'currentCount': current_count,
            'lineGatewayList': gateway_list
        }
        format_output(output_data, output_format)
    else:
        if gateway_list:
            # 格式化表格输出
            table_data = []
            headers = ['网关ID', '网关名称', '接入点', '账户', '资源池', 'VRF名称', '物理专线数', 'VPC数', '创建时间']

            for gateway in gateway_list:
                if not isinstance(gateway, dict):
                    continue

                table_data.append([
                    gateway.get('fuid', ''),  # 完整显示网关ID，不截断
                    gateway.get('gatewayName', gateway.get('vrfName', '')),
                    gateway.get('accessPoint', ''),
                    gateway.get('account', ''),
                    gateway.get('resourcePoolName', ''),
                    gateway.get('vrfName', ''),
                    str(len(gateway.get('lineList', []))),
                    str(len(gateway.get('vpclist', []))),
                    gateway.get('lgcreateTime', '')
                ])

            from tabulate import tabulate
            click.echo(f"专线网关列表 (总计: {total_count}个, 当前页: {current_count}个)")
            if region_id:
                click.echo(f"资源池ID: {region_id}")
            if project_id:
                click.echo(f"项目ID: {project_id}")
            if gateway_name:
                click.echo(f"网关名称: {gateway_name}")
            click.echo("=" * 120)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo("没有找到专线网关记录。")


@gateway.command('count')
@click.option('--account', required=True, help='天翼云客户邮箱（必填）')
@click.option('--region-id', help='资源池ID（实际必填）')
@click.pass_context
@handle_error
def count_gateways(ctx, account: str, region_id: Optional[str]):
    """
    查询专线网关数量

    示例：
        ctyun-cli cda gateway count --account user@example.com --region-id 200000001852

        # 使用示例账户查询
        ctyun-cli cda gateway count --account autotest0627@qq.com --region-id 81f7728662dd11ec810800155d307d5b
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询专线网关数量
    result = cda_client.count_gateways(account=account, region_id=region_id)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    count = result.get('data', {}).get('count', 0)

    if output_format == 'json':
        format_output({
            'count': count,
            'account': account,
            'regionId': region_id,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        click.echo(f"专线网关数量统计")
        click.echo("=" * 40)
        click.echo(f"账户: {account}")
        if region_id:
            click.echo(f"资源池ID: {region_id}")
        click.echo(f"网关总数: {count}")
        if result.get('endpoint'):
            click.echo(f"端点: {result.get('endpoint')}")


@gateway.command('physical-lines')
@click.option('--gateway-name', required=True, help='专线网关名称（必填）')
@click.option('--account', required=True, help='天翼云客户邮箱（必填）')
@click.option('--region-id', help='资源池ID（实际必填）')
@click.pass_context
@handle_error
def list_gateway_physical_lines(ctx, gateway_name: str, account: str, region_id: Optional[str]):
    """
    查询专线网关已绑定的物理专线

    示例：
        ctyun-cli cda gateway physical-lines --gateway-name my-gateway --account user@example.com --region-id 81f7728662dd11ec810800155d307d5b

        # 使用示例网关查询
        ctyun-cli cda gateway physical-lines --gateway-name nm8CTYUN14 --account autotest0627@qq.com --region-id 81f7728662dd11ec810800155d307d5b

        # 使用已知网关查询物理专线
        ctyun-cli cda gateway physical-lines --gateway-name 3WJNUZMA2W19EIATI0OX --account hxcloud@travelsky.com.cn --region-id 81f7728662dd11ec810800155d307d5b
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询专线网关已绑定的物理专线
    result = cda_client.list_gateway_physical_lines(gateway_name=gateway_name, account=account, region_id=region_id)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    physical_lines = result.get('data', {}).get('lineList', [])

    if output_format == 'json':
        format_output({
            'gateway_name': gateway_name,
            'account': account,
            'physical_lines': physical_lines,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        if physical_lines:
            # 格式化表格输出
            table_data = []
            headers = ['物理专线名称', '物理专线ID', '专线类型', '带宽', '状态', '接入点', '创建时间']

            for line in physical_lines:
                if not isinstance(line, dict):
                    continue

                table_data.append([
                    line.get('lineName', ''),
                    line.get('lineID', ''),  # 完整显示物理专线ID，不截断
                    line.get('lineType', ''),
                    line.get('bandwidth', ''),
                    line.get('lineStatus', ''),
                    line.get('accessPoint', ''),
                    line.get('createTime', '')
                ])

            from tabulate import tabulate
            click.echo(f"专线网关已绑定的物理专线 (网关: {gateway_name})")
            click.echo("=" * 120)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo(f"专线网关 '{gateway_name}' 没有找到已绑定的物理专线。")


@gateway.command('cloud-express')
@click.option('--gateway-name', required=True, help='专线网关名字（必填）')
@click.pass_context
@handle_error
def list_gateway_cloud_express(ctx, gateway_name: str):
    """
    专线网关绑定的云间高速查询

    查询专线网关已绑定云间高速信息。

    示例：
        # 查询专线网关绑定的云间高速
        ctyun-cli cda gateway cloud-express --gateway-name my-gateway
    """
    client = ctx.obj['client']
    cda_client = init_cda_client(client)
    output_format = ctx.obj.get('output', 'table')

    click.echo(f"正在查询专线网关 '{gateway_name}' 绑定的云间高速信息...")

    # 调用专线网关绑定的云间高速查询API
    result = cda_client.list_gateway_cloud_express(gateway_name)

    if result.get('statusCode') == 800:
        return_obj = result.get('returnObj', {})
        line_gateway_list = return_obj.get('lineGatewayList', [])

        if output_format == 'json':
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        elif output_format == 'yaml':
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        else:
            click.echo(f"\n专线网关 '{gateway_name}' 的云间高速信息:")
            click.echo("=" * 80)

            if line_gateway_list:
                click.echo("已绑定的云间高速信息:")
                for idx, item in enumerate(line_gateway_list, 1):
                    click.echo(f"  {idx}. {item}")
            else:
                click.echo("没有找到绑定的云间高速信息。")
    else:
        error_msg = result.get('description', result.get('message', '未知错误'))
        error_code = result.get('errorCode', '')
        click.echo(f"查询失败: {error_msg} (错误代码: {error_code})")


# ============ 物理专线相关命令 ============

@cda.group('physical-line')
def physical_line():
    """物理专线管理"""
    pass


@physical_line.command('list')
@click.option('--region-id', help='资源池ID')
@click.option('--page-no', default=1, type=int, help='页码，默认为1')
@click.option('--page-size', default=10, type=int, help='每页数量，默认为10')
@click.option('--line-type', help='专线类型(PON/IPRAN)')
@click.option('--account', help='天翼云客户邮箱')
@click.pass_context
@handle_error
def list_physical_lines(ctx, region_id: Optional[str], page_no: int, page_size: int,
                        line_type: Optional[str], account: Optional[str]):
    """
    查询物理专线列表

    示例：
        # 查询所有物理专线
        ctyun-cli cda physical-line list

        # 分页查询物理专线
        ctyun-cli cda physical-line list --page-no 1 --page-size 20

        # 按资源池和专线类型过滤
        ctyun-cli cda physical-line list --region-id 81f7728662dd11ec810800155d307d5b --line-type PON

        # 按账户查询
        ctyun-cli cda physical-line list --account user@example.com
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询物理专线列表
    result = cda_client.list_physical_lines(
        page_no=page_no,
        page_size=page_size,
        region_id=region_id,
        line_type=line_type,
        account=account
    )

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    physical_line_list = data.get('physicalLineList', [])
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)

    if output_format == 'json':
        output_data = {
            'totalCount': total_count,
            'currentCount': current_count,
            'physicalLineList': physical_line_list
        }
        format_output(output_data, output_format)
    else:
        if physical_line_list:
            # 格式化表格输出
            table_data = []
            headers = ['专线ID', '专线名称', '专线类型', '带宽(M)', 'IP版本', 'VLAN', '端口类型', '接入点', '专线网关']

            for line in physical_line_list:
                if not isinstance(line, dict):
                    continue

                table_data.append([
                    line.get('lineId', ''),  # 完整显示专线ID，不截断
                    line.get('lineName', ''),
                    line.get('lineType', ''),
                    str(line.get('bandwidth', 0)),
                    line.get('ipVersion', ''),
                    str(line.get('vlan', '')),
                    line.get('portType', ''),
                    line.get('accessPoint', ''),
                    line.get('vrfName', '')
                ])

            from tabulate import tabulate
            click.echo(f"物理专线列表 (总计: {total_count}条, 当前页: {current_count}条)")
            if region_id:
                click.echo(f"资源池ID: {region_id}")
            if line_type:
                click.echo(f"专线类型: {line_type}")
            if account:
                click.echo(f"账户: {account}")
            click.echo("=" * 100)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo("没有找到物理专线记录。")


@physical_line.command('count')
@click.option('--account', required=True, help='天翼云客户邮箱')
@click.option('--region-id', help='资源池ID（可选，但实际可能需要）')
@click.pass_context
@handle_error
def count_physical_lines(ctx, account: str, region_id: Optional[str]):
    """
    查询物理专线数量

    示例：
        ctyun-cli cda physical-line count --account user@example.com

        # 使用示例账户和区域ID查询
        ctyun-cli cda physical-line count --account autotest0627@qq.com --region-id 81f7728662dd11ec810800155d307d5b

        # 仅使用账户查询（可能失败）
        ctyun-cli cda physical-line count --account test@example.com
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询物理专线数量
    result = cda_client.count_physical_lines(account=account, region_id=region_id)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    count = result.get('data', {}).get('count', 0)

    if output_format == 'json':
        format_output({
            'count': count,
            'account': account,
            'regionId': region_id,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        click.echo(f"物理专线数量统计")
        click.echo("=" * 40)
        click.echo(f"账户: {account}")
        if region_id:
            click.echo(f"资源池ID: {region_id}")
        click.echo(f"专线总数: {count}")
        if result.get('endpoint'):
            click.echo(f"端点: {result.get('endpoint')}")


@physical_line.command('shared')
@click.option('--region-id', help='资源池ID')
@click.option('--page-no', default=1, type=int, help='页码，默认为1')
@click.option('--page-size', default=10, type=int, help='每页数量，默认为10')
@click.option('--line-type', help='专线类型(PON/IPRAN)')
@click.option('--line-code', help='电路代号')
@click.option('--account', help='天翼云客户邮箱')
@click.pass_context
@handle_error
def list_shared_physical_lines(ctx, region_id: Optional[str], page_no: int, page_size: int,
                              line_type: Optional[str], line_code: Optional[str], account: Optional[str]):
    """
    查询共享物理专线列表

    示例：
        # 查询所有共享物理专线
        ctyun-cli cda physical-line shared

        # 分页查询共享物理专线
        ctyun-cli cda physical-line shared --page-no 1 --page-size 20

        # 按专线类型过滤
        ctyun-cli cda physical-line shared --line-type PON

        # 按电路代号查询
        ctyun-cli cda physical-line shared --line-code ABC123

        # 按账户查询
        ctyun-cli cda physical-line shared --account user@example.com
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询共享物理专线列表
    result = cda_client.list_shared_physical_lines(
        page_no=page_no,
        page_size=page_size,
        region_id=region_id,
        line_type=line_type,
        line_code=line_code,
        account=account
    )

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    shared_line_list = data.get('physicalLineList', [])
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)

    if output_format == 'json':
        output_data = {
            'totalCount': total_count,
            'currentCount': current_count,
            'sharedPhysicalLineList': shared_line_list
        }
        format_output(output_data, output_format)
    else:
        if shared_line_list:
            # 格式化表格输出
            table_data = []
            headers = ['专线ID', '专线名称', '专线类型', '带宽(M)', 'IP版本', 'VLAN', '端口类型', '接入点', '专线网关']

            for line in shared_line_list:
                if not isinstance(line, dict):
                    continue

                table_data.append([
                    line.get('lineId', ''),  # 完整显示专线ID，不截断
                    line.get('lineName', ''),
                    line.get('lineType', ''),
                    str(line.get('bandwidth', 0)),
                    line.get('ipVersion', ''),
                    str(line.get('vlan', '')),
                    line.get('portType', ''),
                    line.get('accessPoint', ''),
                    line.get('vrfName', '')
                ])

            from tabulate import tabulate
            click.echo(f"共享物理专线列表 (总计: {total_count}条, 当前页: {current_count}条)")
            if region_id:
                click.echo(f"资源池ID: {region_id}")
            if line_type:
                click.echo(f"专线类型: {line_type}")
            if line_code:
                click.echo(f"电路代号: {line_code}")
            if account:
                click.echo(f"账户: {account}")
            click.echo("=" * 100)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo("没有找到共享物理专线记录。")


@physical_line.command('access-points')
@click.option('--line-name', required=True, help='物理专线名称')
@click.option('--account', required=True, help='天翼云客户邮箱')
@click.option('--region-id', help='资源池ID（实际必填）')
@click.pass_context
@handle_error
def list_access_points(ctx, line_name: str, account: str, region_id: Optional[str]):
    """
    查询物理专线接入点

    示例：
        # 查询指定物理专线的接入点
        ctyun-cli cda physical-line access-points --line-name my-line --account user@example.com --region-id 200000001852

        # 使用示例参数查询
        ctyun-cli cda physical-line access-points --line-name "autotest0627@qq.com内蒙演示环境-1" --account autotest0627@qq.com --region-id 81f7728662dd11ec810800155d307d5b
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询物理专线接入点
    result = cda_client.list_access_points(line_name=line_name, account=account, region_id=region_id)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    access_point = result.get('data', {}).get('accessPoint', '')

    if output_format == 'json':
        format_output({
            'lineName': line_name,
            'account': account,
            'regionId': region_id,
            'accessPoint': access_point
        }, output_format)
    else:
        click.echo(f"物理专线接入点信息")
        click.echo("=" * 40)
        click.echo(f"专线名称: {line_name}")
        click.echo(f"账户: {account}")
        if region_id:
            click.echo(f"资源池ID: {region_id}")
        click.echo(f"接入点: {access_point if access_point else '未找到接入点信息'}")


# ============ VPC相关命令 ============

@cda.group('vpc')
def vpc():
    """VPC管理"""
    pass


@vpc.command('list')
@click.option('--gateway-name', required=True, help='专线网关名称')
@click.option('--account', required=True, help='天翼云客户邮箱')
@click.pass_context
@handle_error
def list_vpcs(ctx, gateway_name: str, account: str):
    """
    查询专线网关下的VPC列表

    示例：
        # 查询专线网关下的所有VPC
        ctyun-cli cda vpc list --gateway-name my-gateway --account user@example.com

        # 使用专线网关名称查询VPC
        ctyun-cli cda vpc list --gateway-name nm8CTYUN12 --account gmm-cdatest@qq.com
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询VPC列表
    result = cda_client.list_vpcs(gateway_name=gateway_name, account=account)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    vpc_list = result.get('data', {}).get('vpcList', [])

    if output_format == 'json':
        format_output(vpc_list, output_format)
    else:
        if vpc_list:
            # 格式化表格输出
            table_data = []
            headers = ['VPC ID', 'VPC名称', 'VPC网段', 'VPC子网', 'IP版本', '虚拟带宽', '资源池ID']

            for vpc in vpc_list:
                if not isinstance(vpc, dict):
                    continue

                table_data.append([
                    vpc.get('vpcId', ''),
                    vpc.get('vpcName', ''),
                    vpc.get('vpcNetworkSegment', ''),
                    vpc.get('vpcSubnet', ''),
                    vpc.get('ipVersion', ''),
                    str(vpc.get('virtualBandwidth', 0)),
                    vpc.get('resourcePool', '')
                ])

            from tabulate import tabulate
            click.echo(f"VPC列表 (专线网关: {gateway_name})")
            click.echo("=" * 80)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo("没有找到VPC记录。")


@vpc.command('count')
@click.option('--gateway-name', required=True, help='专线网关名称')
@click.option('--account', required=True, help='天翼云客户邮箱')
@click.pass_context
@handle_error
def count_vpcs(ctx, gateway_name: str, account: str):
    """
    查询专线网关下的VPC数量

    示例：
        ctyun-cli cda vpc count --gateway-name my-gateway --account user@example.com

        # 使用专线网关名称查询VPC数量
        ctyun-cli cda vpc count --gateway-name nm8CTYUN12 --account gmm-cdatest@qq.com
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询VPC数量
    result = cda_client.count_vpcs(gateway_name=gateway_name, account=account)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    count = result.get('data', {}).get('count', 0)

    if output_format == 'json':
        format_output({'count': count, 'gateway_name': gateway_name}, output_format)
    else:
        click.echo(f"VPC数量统计 (专线网关: {gateway_name})")
        click.echo("=" * 40)
        click.echo(f"VPC总数: {count}")


@vpc.command('info')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--gateway-name', help='专线网关名称（可选）')
@click.pass_context
@handle_error
def get_vpc_info(ctx, vpc_id: str, gateway_name: Optional[str]):
    """
    获取指定VPC的详细信息和能访问该VPC的物理专线信息

    示例：
        # 查询VPC详细信息
        ctyun-cli cda vpc info --vpc-id vpc-j1fz2xdyw5

        # 使用专线网关名称查询VPC详情
        ctyun-cli cda vpc info --vpc-id vpc-j1fz2xdyw5 --gateway-name linecnp30pyrj0006
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询VPC详细信息
    result = cda_client.get_vpc_info(vpc_id=vpc_id, gateway_name=gateway_name)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    vpc_info_list = result.get('data', {}).get('info', [])

    if output_format == 'json':
        format_output(vpc_info_list, output_format)
    else:
        if vpc_info_list:
            # 格式化输出VPC详细信息
            for idx, vpc_data in enumerate(vpc_info_list, 1):
                if not isinstance(vpc_data, dict):
                    continue

                vpc_info = vpc_data.get('vpc-info', {})
                line_info = vpc_data.get('line-info', [])
                cda_id = vpc_data.get('cda-id', '')

                click.echo(f"VPC详细信息 #{idx}")
                click.echo("=" * 60)
                click.echo(f"VPC ID: {vpc_info.get('id', '')}")
                click.echo(f"专线ID: {cda_id}")
                click.echo(f"IP版本: {vpc_info.get('ip-version', '')}")
                click.echo(f"虚拟带宽: {vpc_info.get('bandwidth', '')}")
                click.echo(f"设备IP: {vpc_info.get('device-ip', '')}")
                click.echo(f"本地CIDR: {', '.join(vpc_info.get('local-cidr', [])) if isinstance(vpc_info.get('local-cidr'), list) else vpc_info.get('local-cidr', '')}")
                click.echo(f"本地CIDR IPv6: {', '.join(vpc_info.get('local-cidr-ipv6', []))}")

                # 显示物理专线信息
                if line_info:
                    click.echo(f"\n物理专线信息 (共{len(line_info)}条):")
                    click.echo("-" * 40)
                    for line in line_info:
                        if not isinstance(line, dict):
                            continue
                        click.echo(f"  专线ID: {line.get('id', '')}")
                        click.echo(f"  链路类型: {line.get('link-type', '')}")
                        click.echo(f"  带宽: {line.get('rate', '')}Mbps")
                        click.echo(f"  VLAN: {line.get('vlan', '')}")
                        click.echo(f"  接口名称: {line.get('interface-name', '')}")
                        click.echo(f"  接口类型: {line.get('interface-type', '')}")
                        click.echo(f"  IP版本: {line.get('ip-version', '')}")
                        click.echo(f"  本地网关IP: {line.get('local-gateway-ip', '')}")
                        click.echo(f"  远程网关IP: {line.get('remote-gateway-ip', '')}")
                        click.echo("  " + "-" * 30)

                click.echo("\n" + "=" * 60 + "\n")
        else:
            click.echo("没有找到VPC详细信息。")


@vpc.command('info')
@click.option('--vpc-id', required=True, help='VPC ID（必填）')
@click.option('--gateway-name', help='专线网关名字（可选）')
@click.pass_context
@handle_error
def get_vpc_info(ctx, vpc_id: str, gateway_name: Optional[str]):
    """
    云专线VPC详情查询

    获取指定VPC的详细信息和能访问该VPC的物理专线信息。

    示例：
        # 查询VPC详细信息
        ctyun-cli cda vpc info --vpc-id vpc-j1fz2xdyw5

        # 查询指定专线网关下的VPC信息
        ctyun-cli cda vpc info --vpc-id vpc-j1fz2xdyw5 --gateway-name linecnp30pyrj0006
    """
    client = ctx.obj['client']
    cda_client = init_cda_client(client)
    output_format = ctx.obj.get('output', 'table')

    click.echo(f"正在查询VPC '{vpc_id}' 的详细信息...")

    # 调用VPC详情查询API
    result = cda_client.get_vpc_info(vpc_id, gateway_name)

    if result.get('statusCode') == 800:
        return_obj = result.get('returnObj', {})
        info_list = return_obj.get('info', [])

        if output_format == 'json':
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        elif output_format == 'yaml':
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        else:
            click.echo(f"\nVPC '{vpc_id}' 的详细信息:")
            click.echo("=" * 100)

            if info_list:
                for idx, vpc_info in enumerate(info_list, 1):
                    click.echo(f"\n【专线网关 {idx}】: {vpc_info.get('cda-id', 'N/A')}")
                    click.echo("-" * 80)

                    # VPC信息
                    vpc_data = vpc_info.get('vpc-info', {})
                    if vpc_data:
                        click.echo("📍 VPC基本信息:")
                        vpc_headers = ['配置项', '值']
                        vpc_table_data = [
                            ['VPC ID', vpc_data.get('id', 'N/A')],
                            ['CDA ID', vpc_data.get('cda-id', 'N/A')],
                            ['设备IP', vpc_data.get('device-ip', 'N/A')],
                            ['IP版本', vpc_data.get('ip-version', 'N/A')],
                            ['带宽', vpc_data.get('bandwidth', 'N/A') + ' Mbps' if vpc_data.get('bandwidth') else 'N/A'],
                            ['SW VTEP IP', vpc_data.get('sw-vtep-ip', 'N/A')],
                            ['DST VTEP IP', vpc_data.get('dst-vtep-ip', 'N/A')],
                            ['Guest Overlay Router', vpc_data.get('guest-overlay-router', 'N/A')],
                            ['CNP网关IPv6', vpc_data.get('cnp-gateway-ipv6', 'N/A')],
                            ['CNP连接IPv6前缀', vpc_data.get('cnp-connect-ipv6-prefix', 'N/A')]
                        ]

                        # 本地CIDR信息
                        local_cidr = vpc_data.get('local-cidr')
                        local_cidr_ipv6 = vpc_data.get('local-cidr-ipv6', [])
                        if local_cidr:
                            vpc_table_data.append(['本地CIDR', local_cidr])
                        if local_cidr_ipv6:
                            vpc_table_data.append(['本地CIDR IPv6', ', '.join(local_cidr_ipv6)])

                        vpc_table = tabulate(vpc_table_data, vpc_headers, tablefmt='grid')
                        click.echo(vpc_table)

                    # 物理专线信息
                    line_info_list = vpc_info.get('line-info', [])
                    if line_info_list:
                        click.echo(f"\n🔗 物理专线信息 ({len(line_info_list)}条):")
                        line_headers = ['配置项', '值']

                        for line_idx, line_data in enumerate(line_info_list, 1):
                            click.echo(f"\n  专线 {line_idx}:")
                            line_table_data = [
                                ['专线ID', line_data.get('id', 'N/A')],
                                ['CDA ID', line_data.get('cda-id', 'N/A')],
                                ['设备IP', line_data.get('device-ip', 'N/A')],
                                ['层级', line_data.get('layer', 'N/A')],
                                ['接口名称', line_data.get('interface-name', 'N/A')],
                                ['接口类型', line_data.get('interface-type', 'N/A')],
                                ['链路类型', line_data.get('link-type', 'N/A')],
                                ['VLAN', line_data.get('vlan', 'N/A')],
                                ['速率', f"{line_data.get('rate', 0)} Mbps"],
                                ['IP版本', line_data.get('ip-version', 'N/A')],
                                ['本地网关IPv6', line_data.get('local-gateway-ipv6', 'N/A')],
                                ['远程网关IPv6', line_data.get('remote-gateway-ipv6', 'N/A')]
                            ]

                            # 本地和远程网关IP
                            local_gw_ip = line_data.get('local-gateway-ip')
                            remote_gw_ip = line_data.get('remote-gateway-ip')
                            if local_gw_ip:
                                line_table_data.append(['本地网关IP', local_gw_ip])
                            if remote_gw_ip:
                                line_table_data.append(['远程网关IP', remote_gw_ip])

                            line_table = tabulate(line_table_data, line_headers, tablefmt='grid')
                            click.echo(f"    {line_table}")
            else:
                click.echo("没有找到VPC详细信息。")
    else:
        error_msg = result.get('description', result.get('message', '未知错误'))
        error_code = result.get('errorCode', '')
        click.echo(f"查询失败: {error_msg} (错误代码: {error_code})")


# ============ 静态路由相关命令 ============

@cda.group('static-route')
def static_route():
    """静态路由管理"""
    pass


@static_route.command('list')
@click.option('--gateway-name', required=True, help='专线网关名称')
@click.option('--account', required=True, help='天翼云客户邮箱')
@click.pass_context
@handle_error
def list_static_routes(ctx, gateway_name: str, account: str):
    """
    查询专线网关下的静态路由列表

    示例：
        # 查询专线网关下的所有静态路由
        ctyun-cli cda static-route list --gateway-name nm8CTYUN14 --account autotest0627@qq.com

        # 使用已知网关查询静态路由
        ctyun-cli cda static-route list --gateway-name 3WJNUZMA2W19EIATI0OX --account hxcloud@travelsky.com.cn
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询静态路由列表
    result = cda_client.list_static_routes(gateway_name=gateway_name, account=account)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    static_routes = result.get('data', {}).get('staticRouteList', [])

    if output_format == 'json':
        format_output(static_routes, output_format)
    else:
        if static_routes:
            # 格式化表格输出
            table_data = []
            headers = ['专线网关', 'IP版本', '目的地址', '下一跳IP', '优先级', 'Track', '静态路由ID']

            for route in static_routes:
                if not isinstance(route, dict):
                    continue

                # 处理目的地址列表
                dst_cidr = ', '.join(route.get('dstCidr', []))
                dst_cidr_v6 = ', '.join(route.get('dstCidrV6', []))
                dst_all = dst_cidr
                if dst_cidr_v6:
                    dst_all += f" (IPv6: {dst_cidr_v6})"

                # 处理下一跳列表
                next_hops = route.get('nextHop', [])
                next_hop_info = []
                for nh in next_hops:
                    if isinstance(nh, dict):
                        nh_info = f"{nh.get('remoteGatewayIp', '')}"
                        if nh.get('priority') is not None:
                            nh_info += f" (优先级: {nh.get('priority')})"
                        if nh.get('track') is not None:
                            nh_info += f" (Track: {nh.get('track')})"
                        next_hop_info.append(nh_info)

                table_data.append([
                    route.get('gatewayName', ''),
                    route.get('ipVersion', ''),
                    dst_all,
                    ', '.join(next_hop_info),
                    next_hops[0].get('priority') if next_hops else '',
                    next_hops[0].get('track') if next_hops else '',
                    route.get('SRID', '')  # 完整显示静态路由ID，不截断
                ])

            from tabulate import tabulate
            click.echo(f"静态路由列表 (专线网关: {gateway_name})")
            click.echo("=" * 120)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo(f"专线网关 '{gateway_name}' 没有找到静态路由配置。")


# ============ BGP路由相关命令 ============

@cda.group('bgp-route')
def bgp_route():
    """BGP路由管理"""
    pass


@bgp_route.command('list')
@click.option('--gateway-name', required=True, help='专线网关名称（必填）')
@click.option('--account', required=True, help='天翼云客户邮箱（必填）')
@click.pass_context
@handle_error
def list_bgp_routes(ctx, gateway_name: str, account: str):
    """
    查询专线网关下的BGP动态路由

    示例：
        # 查询专线网关下的所有BGP路由
        ctyun-cli cda bgp-route list --gateway-name nm8CTYUN14 --account autotest0627@qq.com

        # 使用已知网关查询BGP路由
        ctyun-cli cda bgp-route list --gateway-name 3WJNUZMA2W19EIATI0OX --account hxcloud@travelsky.com.cn
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询BGP路由列表
    result = cda_client.list_bgp_routes(gateway_name=gateway_name, account=account)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    bgp_routes = result.get('data', {}).get('BGPRouteList', [])

    if output_format == 'json':
        format_output({
            'gateway_name': gateway_name,
            'account': account,
            'bgp_routes': bgp_routes,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        if bgp_routes:
            # 格式化表格输出
            table_data = []
            headers = ['专线网关', 'IP版本', 'BGP ID', '客户侧子网(IPv4)', '客户侧子网(IPv6)', '多路径(IPv4)', '多路径(IPv6)', 'BGP邻居数']

            for route in bgp_routes:
                if not isinstance(route, dict):
                    continue

                # 处理客户侧子网列表
                network_cidr = ', '.join(route.get('networkCidr', []))
                network_cidr_v6 = ', '.join(route.get('networkCidrV6', []))

                # 处理多路径信息
                multi_path = '是' if route.get('multiPath', False) else '否'
                multi_path_ipv6 = '是' if route.get('multiPathIpv6', False) else '否'

                # 计算BGP邻居数量
                bgp_ipv4_count = len(route.get('BGPList', []))
                bgp_ipv6_count = len(route.get('BGPIpv6List', []))
                total_neighbors = bgp_ipv4_count + bgp_ipv6_count

                table_data.append([
                    route.get('gatewayName', ''),
                    route.get('ipVersion', ''),
                    route.get('BGPID', ''),  # 完整显示BGP ID，不截断
                    network_cidr,
                    network_cidr_v6,
                    multi_path,
                    multi_path_ipv6,
                    str(total_neighbors)
                ])

            from tabulate import tabulate
            click.echo(f"BGP路由列表 (专线网关: {gateway_name})")
            click.echo("=" * 140)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo(f"专线网关 '{gateway_name}' 没有找到BGP路由配置。")


# ============ 跨账号授权相关命令 ============

@cda.group('account-auth')
def account_auth():
    """跨账号授权管理"""
    pass


@account_auth.command('list')
@click.option('--region-id', required=True, help='资源池ID（必填）')
@click.option('--page-no', default=1, type=int, help='页码，默认为1')
@click.option('--page-size', default=10, type=int, help='每页数量，默认为10')
@click.option('--vpc-id', help='查询被授权：指定VPC ID，会带跨账号VPC子网信息')
@click.option('--auth-account-id', help='查询已授权：账号ID不传查询被授权：账号ID为自己账号ID')
@click.pass_context
@handle_error
def list_account_auths(ctx, region_id: str, page_no: int, page_size: int, vpc_id: Optional[str], auth_account_id: Optional[str]):
    """
    查询账户下已添加的跨账号授权网络实例

    示例：
        # 查询所有跨账号授权
        ctyun-cli cda account-auth list --region-id 81f7728662dd11ec810800155d307d5b

        # 分页查询跨账号授权
        ctyun-cli cda account-auth list --region-id 81f7728662dd11ec810800155d307d5b --page-no 1 --page-size 20

        # 查询指定VPC的授权
        ctyun-cli cda account-auth list --region-id 81f7728662dd11ec810800155d307d5b --vpc-id vpc-12345678

        # 查询指定账号的授权
        ctyun-cli cda account-auth list --region-id 81f7728662dd11ec810800155d307d5b --auth-account-id account-12345678
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询跨账号授权列表
    result = cda_client.list_account_authorizations(
        region_id=region_id,
        page_no=page_no,
        page_size=page_size,
        vpc_id=vpc_id,
        auth_account_id=auth_account_id
    )

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    account_auths = data.get('accountAuthList', [])
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)

    if output_format == 'json':
        format_output({
            'region_id': region_id,
            'total_count': total_count,
            'current_count': current_count,
            'page_no': page_no,
            'page_size': page_size,
            'vpc_id': vpc_id,
            'auth_account_id': auth_account_id,
            'account_auths': account_auths,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        if account_auths:
            # 格式化表格输出
            table_data = []
            headers = ['授权ID', '账号ID', '账号邮箱', 'VPC ID', 'VPC名称', 'VRF名称', '被授权账号ID', '被授权账号邮箱']

            for auth in account_auths:
                if not isinstance(auth, dict):
                    continue

                table_data.append([
                    auth.get('fuid', ''),  # 完整显示授权ID，不截断
                    auth.get('accountId', ''),
                    auth.get('account', ''),
                    auth.get('vpcId', ''),
                    auth.get('vpcName', ''),
                    auth.get('vrfName', ''),
                    auth.get('authorizedAccountId', ''),
                    auth.get('authorizedAccount', '')
                ])

            from tabulate import tabulate
            click.echo(f"跨账号授权列表 (资源池: {region_id})")
            click.echo("=" * 120)
            click.echo(f"总计: {total_count}个, 当前页: {current_count}个")
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo(f"资源池 '{region_id}' 没有找到跨账号授权配置。")


@account_auth.command('stats')
@click.option('--region-id', help='资源池ID（实际API需要，虽然文档未说明）')
@click.pass_context
@handle_error
def stats_account_auths(ctx, region_id: Optional[str]):
    """
    统计账号下已授权的VPC及授权给专线网关数量

    示例：
        # 使用当前配置的region
        ctyun-cli cda account-auth stats

        # 指定region
        ctyun-cli cda account-auth stats --region-id 81f7728662dd11ec810800155d307d5b

        # 使用华北2区域
        ctyun-cli cda account-auth stats --region-id 200000001852
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 如果没有指定region_id，使用客户端的默认region
    if not region_id:
        # 从客户端获取当前region
        region_id = getattr(client, 'region', '200000001852')  # 默认使用华北2

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API统计跨账号授权
    result = cda_client.get_account_authorization_statistics(region_id=region_id)

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    statistics = data.get('statistics', [])

    if output_format == 'json':
        format_output({
            'statistics': statistics,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        if statistics:
            # 格式化表格输出
            table_data = []
            headers = ['VPC ID', '授权数量']

            for stat in statistics:
                if not isinstance(stat, dict):
                    continue

                table_data.append([
                    stat.get('vpcID', ''),
                    str(stat.get('count', 0))
                ])

            from tabulate import tabulate
            click.echo(f"跨账号授权统计")
            click.echo("=" * 40)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)

            # 显示总计信息
            total_vpcs = len(statistics)
            total_auths = sum(stat.get('count', 0) for stat in statistics if isinstance(stat, dict))
            click.echo(f"\n总计: {total_vpcs}个VPC, {total_auths}个授权")
        else:
            click.echo("没有找到跨账号授权统计数据。")


# ============ 健康检查相关命令 ============

@cda.group('health-check')
def health_check():
    """健康检查和链路探测管理"""
    pass


@health_check.command('config')
@click.option('--gateway-name', required=True, help='专线网关名称（必填）')
@click.option('--vpc-id', required=True, help='VPC ID（必填）')
@click.option('--vpc-name', required=True, help='VPC名称（必填）')
@click.pass_context
@handle_error
def get_health_check_config(ctx, gateway_name: str, vpc_id: str, vpc_name: str):
    """
    专线网关查询健康检查设置项

    示例：
        # 查询专线网关的健康检查配置
        ctyun-cli cda health-check config --gateway-name nm8CTYUN14 --vpc-id vpc-a6zxrnx7j5 --vpc-name vpc-for-api-cda-test01

        # 使用已知的网关查询
        ctyun-cli cda health-check config --gateway-name 3WJNUZMA2W19EIATI0OX --vpc-id vpc-12345678 --vpc-name test-vpc
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询健康检查配置
    result = cda_client.get_health_check_config(
        gateway_name=gateway_name,
        vpc_id=vpc_id,
        vpc_name=vpc_name
    )

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    settings = data.get('settingItem', [])

    if output_format == 'json':
        format_output({
            'gateway_name': gateway_name,
            'vpc_id': vpc_id,
            'vpc_name': vpc_name,
            'settings': settings,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        if settings:
            # 格式化表格输出
            table_data = []
            headers = ['VRF名称', 'VPC ID', 'VPC名称', 'VPC子网', '源IP', '目的IP', '检测间隔(秒)', '重试次数', '自动路由切换']

            for setting in settings:
                if not isinstance(setting, dict):
                    continue

                table_data.append([
                    setting.get('vrfName', ''),
                    setting.get('vpcId', ''),
                    setting.get('vpcName', ''),
                    setting.get('vpcSubnet', ''),
                    setting.get('srcIP', ''),
                    setting.get('dstIP', ''),
                    str(setting.get('interval', 0)),
                    str(setting.get('ntimest', 0)),
                    '是' if setting.get('autoRouteSwitching', False) else '否'
                ])

            from tabulate import tabulate
            click.echo(f"健康检查配置 (网关: {gateway_name}, VPC: {vpc_name})")
            click.echo("=" * 140)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)
        else:
            click.echo(f"专线网关 '{gateway_name}' 的VPC '{vpc_name}' 没有找到健康检查配置。")


@health_check.command('status')
@click.option('--gateway-name', required=True, help='专线网关名称（必填）')
@click.option('--vpc-id', required=True, help='VPC ID（必填）')
@click.option('--region-id', required=True, help='资源池ID（必填）')
@click.option('--resource-pool', required=True, help='资源池ID（必填）')
@click.pass_context
@handle_error
def get_health_check_status(ctx, gateway_name: str, vpc_id: str, region_id: str, resource_pool: str):
    """
    健康检查查询检查结果

    示例：
        # 查询专线网关的健康检查状态
        ctyun-cli cda health-check status --gateway-name nm8CTYUN14 --vpc-id vpc-a6zxrnx7j5 --region-id 81f7728662dd11ec810800155d307d5b --resource-pool 81f7728662dd11ec810800155d307d5b

        # 使用已知的网关查询
        ctyun-cli cda health-check status --gateway-name 3WJNUZMA2W19EIATI0OX --vpc-id vpc-12345678 --region-id 81f7728662dd11ec810800155d307d5b --resource-pool 81f7728662dd11ec810800155d307d5b
    """
    from cda import init_cda_client

    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')

    # 初始化CDA客户端
    cda_client = init_cda_client(client)

    # 调用API查询健康检查状态
    result = cda_client.get_health_check_status(
        region_id=region_id,
        resource_pool=resource_pool,
        gateway_name=gateway_name,
        vpc_id=vpc_id
    )

    if not result.get('success'):
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    data = result.get('data', {})
    status_list = data.get('statusList', [])

    if output_format == 'json':
        format_output({
            'region_id': region_id,
            'resource_pool': resource_pool,
            'gateway_name': gateway_name,
            'vpc_id': vpc_id,
            'status_list': status_list,
            'endpoint': result.get('endpoint', 'N/A')
        }, output_format)
    else:
        if status_list:
            # 格式化表格输出
            table_data = []
            headers = ['VRF名称', 'VPC ID', '状态', '天翼云账号ID']

            for status in status_list:
                if not isinstance(status, dict):
                    continue

                table_data.append([
                    status.get('vrfName', ''),
                    status.get('vpcId', ''),
                    status.get('status', ''),
                    status.get('ctUserId', '')
                ])

            from tabulate import tabulate
            click.echo(f"健康检查状态 (网关: {gateway_name}, VPC: {vpc_id})")
            click.echo("=" * 120)
            table = tabulate(table_data, headers, tablefmt='grid')
            click.echo(table)

            # 显示资源池信息
            click.echo(f"资源池ID: {resource_pool}")
            click.echo(f"区域ID: {region_id}")
        else:
            click.echo(f"专线网关 '{gateway_name}' 的VPC '{vpc_id}' 没有找到健康检查状态信息。")


@health_check.command('link-probe')
@click.option('--gateway-name', required=True, help='专线网关名字（必填）')
@click.pass_context
@handle_error
def query_link_probe(ctx, gateway_name: str):
    """
    云专线链路探测查询

    展示指定专线网关下的所有Ping测历史数据。

    示例：
        # 查询专线网关的链路探测历史
        ctyun-cli cda health-check link-probe --gateway-name linecnp30pyrj0006
    """
    client = ctx.obj['client']
    cda_client = init_cda_client(client)
    output_format = ctx.obj.get('output', 'table')

    click.echo(f"正在查询专线网关 '{gateway_name}' 的链路探测历史数据...")

    # 调用链路探测查询API
    result = cda_client.query_link_probe(gateway_name)

    if result.get('statusCode') == 800:
        return_obj = result.get('returnObj', {})
        error_code = return_obj.get('errorCode')
        probe_list = return_obj.get('result', [])

        if error_code == '204' or not probe_list:
            # 没有找到数据
            click.echo(f"专线网关 '{gateway_name}' 没有找到链路探测历史数据。")
        else:
            # 显示链路探测历史数据

            if output_format == 'json':
                click.echo(json.dumps(result, ensure_ascii=False, indent=2))
            elif output_format == 'yaml':
                click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
            else:
                click.echo(f"\n专线网关 '{gateway_name}' 的链路探测历史数据:")
                click.echo("-" * 120)

                if probe_list:
                    headers = ['时间戳', '源IP', '目的IP', '丢包率', '往返时延(ms)', '设备IP', 'CDA ID', '错误信息']
                    table_data = []

                    for probe in probe_list:
                        table_data.append([
                            probe.get('timestamp', ''),
                            probe.get('src-ip', ''),
                            probe.get('dst-ip', ''),
                            probe.get('loss-rate', ''),
                            probe.get('round-trip', ''),
                            probe.get('device-ip', ''),
                            probe.get('cda-id', ''),
                            probe.get('error-msg', '')
                        ])

                    table = tabulate(table_data, headers, tablefmt='grid')
                    click.echo(table)
                else:
                    click.echo("没有找到链路探测记录。")
    else:
        error_msg = result.get('description', result.get('message', '未知错误'))
        error_code = result.get('errorCode', '')
        click.echo(f"查询失败: {error_msg} (错误代码: {error_code})")


# ============ 专线交换机相关命令 ============

@cda.command('switches')
@click.option('--switch-id', help='交换机ID（可选）')
@click.option('--resource-pool', help='资源池ID（可选）')
@click.option('--hostname', help='交换机hostname（可选）')
@click.option('--name', help='交换机name（可选）')
@click.option('--ip', help='交换机IP（可选）')
@click.pass_context
@handle_error
def list_switches(ctx, switch_id: Optional[str], resource_pool: Optional[str],
                 hostname: Optional[str], name: Optional[str], ip: Optional[str]):
    """
    专线交换机查询

    查询已创建的云专线交换机。

    示例：
        # 查询所有专线交换机
        ctyun-cli cda switches

        # 根据资源池查询专线交换机
        ctyun-cli cda switches --resource-pool 11f77286624311ec810r50155d307d67

        # 根据交换机ID查询
        ctyun-cli cda switches --switch-id 55KNQ8PD235KFU84YT

        # 根据IP地址查询
        ctyun-cli cda switches --ip 10.246.247.150
    """
    client = ctx.obj['client']
    cda_client = init_cda_client(client)
    output_format = ctx.obj.get('output', 'table')

    click.echo("正在查询专线交换机...")

    # 调用专线交换机查询API
    result = cda_client.list_switches(switch_id, resource_pool, hostname, name, ip)

    if result.get('statusCode') == 800:
        return_obj = result.get('returnObj', {})
        switches_list = return_obj.get('result', [])

        if output_format == 'json':
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        elif output_format == 'yaml':
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        else:
            click.echo(f"\n专线交换机列表:")
            click.echo("=" * 120)

            if switches_list:
                headers = ['交换机ID', '名称', '厂商', '设备型号', 'IP地址', '主机名', '资源池', '接入点', 'AS号', '登录端口', 'VTEP IP', 'VTEP VLAN']
                table_data = []

                for switch in switches_list:
                    table_data.append([
                        switch.get('switchId', 'N/A'),
                        switch.get('switchName', switch.get('name', 'N/A')),
                        switch.get('factory', 'N/A'),
                        switch.get('deviceModel', 'N/A'),
                        switch.get('ip', 'N/A'),
                        switch.get('hostname', 'N/A'),
                        f"{switch.get('resourceName', 'N/A')} ({switch.get('resourcePool', 'N/A')})",
                        switch.get('accessPoint', 'N/A'),
                        str(switch.get('as', 'N/A')),
                        switch.get('loginPort', 'N/A'),
                        switch.get('vtepIp', 'N/A'),
                        switch.get('vtepVlan', 'N/A')
                    ])

                table = tabulate(table_data, headers, tablefmt='grid')
                click.echo(table)

                # 显示详细信息
                click.echo(f"\n总计找到 {len(switches_list)} 台交换机")

                # 如果有查询条件，显示查询条件
                conditions = []
                if switch_id: conditions.append(f"交换机ID: {switch_id}")
                if resource_pool: conditions.append(f"资源池: {resource_pool}")
                if hostname: conditions.append(f"主机名: {hostname}")
                if name: conditions.append(f"名称: {name}")
                if ip: conditions.append(f"IP地址: {ip}")

                if conditions:
                    click.echo(f"查询条件: {', '.join(conditions)}")
            else:
                click.echo("没有找到匹配的专线交换机。")
    else:
        error_msg = result.get('description', result.get('message', '未知错误'))
        error_code = result.get('errorCode', '')
        click.echo(f"查询失败: {error_msg} (错误代码: {error_code})")