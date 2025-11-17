"""
云服务器(ECS)命令行接口
"""

import click
from typing import List, Optional
# 直接定义装饰器，避免循环导入
from src.ecs.client import ECSClient
from src.utils.helpers import ValidationUtils, OutputFormatter


def handle_error(func):
    """
    错误处理装饰器
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from client import CTYUNAPIError
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
        # 表格格式
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            table = OutputFormatter.format_table(data, headers)
            click.echo(table)
        elif isinstance(data, dict):
            # 单个对象，转换为表格
            headers = ['字段', '值']
            table_data = []
            for key, value in data.items():
                table_data.append([key, value])
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


@click.group()
def ecs():
    """云服务器(ECS)管理"""
    pass




@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=20, type=int, help='每页数量')
@click.option('--az-name', help='可用区名称')
@click.option('--state', help='云主机状态')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list(ctx, region_id: str, page: int, page_size: int, az_name: Optional[str], 
         state: Optional[str], output: Optional[str]):
    """列出云主机实例"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_instances(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            az_name=az_name,
            state=state
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        instances = return_obj.get('results', [])
        is_mock = result.get('_mock', False)
        
        if output and output in ['json', 'yaml']:
            format_output(instances, output)
        else:
            if instances:
                from tabulate import tabulate
                
                table_data = []
                headers = ['实例ID', '实例名称', '状态', '可用区', '私网IP', '公网IP', '到期时间']
                
                for instance in instances:
                    private_ips = instance.get('privateIP', [])
                    eip_addresses = instance.get('eipAddress', [])
                    
                    table_data.append([
                        instance.get('instanceID', '')[:20],
                        instance.get('displayName', instance.get('instanceName', '')),
                        instance.get('instanceStatusStr', instance.get('instanceStatus', '')),
                        instance.get('azName', ''),
                        private_ips[0] if private_ips else '',
                        eip_addresses[0] if eip_addresses else '',
                        instance.get('expireTime', '')
                    ])
                
                total_count = return_obj.get('totalCount', 0)
                current_count = return_obj.get('currentCount', len(instances))
                
                click.echo(f"云主机列表 (总计: {total_count} 台, 当前页: {current_count} 台)")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo()
                
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
            else:
                click.echo("没有找到云主机实例")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.argument('instance_id')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def details(ctx, instance_id: str, output: Optional[str]):
    """查询云主机详情"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_instance(instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        instance = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(instance, output)
        else:
            if instance:
                click.echo(f"云主机详情: {instance_id}")
                click.echo("=" * 80)
                click.echo(f"实例ID: {instance.get('instanceID', '')}")
                click.echo(f"实例名称: {instance.get('displayName', instance.get('instanceName', ''))}")
                click.echo(f"状态: {instance.get('instanceStatusStr', instance.get('instanceStatus', ''))}")
                click.echo(f"区域: {instance.get('regionID', '')}")
                click.echo(f"可用区: {instance.get('azName', '')}")
                click.echo(f"规格: {instance.get('flavorName', '')}")
                click.echo(f"镜像: {instance.get('imageName', '')}")
                click.echo(f"VPC: {instance.get('vpcName', instance.get('vpcID', ''))}")
                click.echo(f"子网: {instance.get('subnetName', instance.get('subnetID', ''))}")
                
                private_ips = instance.get('privateIP', [])
                if private_ips:
                    click.echo(f"私网IP: {', '.join(private_ips)}")
                
                eip_addresses = instance.get('eipAddress', [])
                if eip_addresses:
                    click.echo(f"公网IP: {', '.join(eip_addresses)}")
                
                click.echo(f"创建时间: {instance.get('createTime', '')}")
                click.echo(f"到期时间: {instance.get('expireTime', '')}")
            else:
                click.echo("未找到云主机信息")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.argument('region_id')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def resources(ctx, region_id: str, output: Optional[str]):
    """查询用户资源"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_customer_resources(region_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        resources = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(resources, output)
        else:
            if resources:
                click.echo(f"用户资源概览 (区域: {region_id})")
                click.echo("=" * 80)
                for key, value in resources.items():
                    click.echo(f"{key}: {value}")
            else:
                click.echo("未找到资源信息")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


# 保留旧的命令以兼容
@ecs.command()
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=20, type=int, help='每页数量')
@click.option('--status', help='实例状态过滤 (running/stopped/starting/stopping)')
@click.option('--instance-type', help='实例规格过滤')
@click.pass_context
@handle_error
def list_old(ctx, page: int, page_size: int, status: Optional[str], instance_type: Optional[str]):
    """列出云服务器实例(旧版，已废弃)"""
    # 模拟数据，因为还没有真实的API连接
    mock_instances = [
        {
            'instanceId': 'i-12345678',
            'instanceName': 'web-server-01',
            'status': 'running',
            'instanceType': 's6.small',
            'publicIp': '123.456.78.90',
            'privateIp': '10.0.1.100',
            'createTime': '2024-01-15 10:30:00'
        },
        {
            'instanceId': 'i-87654321',
            'instanceName': 'database-server-01',
            'status': 'running',
            'instanceType': 's6.medium',
            'publicIp': '123.456.78.91',
            'privateIp': '10.0.1.101',
            'createTime': '2024-01-14 15:45:00'
        },
        {
            'instanceId': 'i-11223344',
            'instanceName': 'test-server-01',
            'status': 'stopped',
            'instanceType': 's6.large',
            'publicIp': None,
            'privateIp': '10.0.1.102',
            'createTime': '2024-01-10 09:20:00'
        }
    ]

    # 应用过滤条件
    filtered_instances = mock_instances
    if status:
        filtered_instances = [inst for inst in filtered_instances if inst['status'] == status]
    if instance_type:
        filtered_instances = [inst for inst in filtered_instances if inst['instanceType'] == instance_type]

    # 应用分页
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_instances = filtered_instances[start_idx:end_idx]

    format_output(paginated_instances, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.pass_context
@handle_error
def show(ctx, instance_id: str):
    """显示云服务器实例详情"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    instance = ecs_client.get_instance(instance_id)
    format_output(instance, ctx.obj['output'])


@ecs.command()
@click.option('--name', required=True, help='实例名称')
@click.option('--instance-type', required=True, help='实例规格')
@click.option('--image-id', required=True, help='镜像ID')
@click.option('--system-disk-type', default='SSD', help='系统盘类型')
@click.option('--system-disk-size', default=40, type=int, help='系统盘大小(GB)')
@click.option('--vpc-id', help='VPC ID')
@click.option('--subnet-id', help='子网ID')
@click.option('--security-group-ids', help='安全组ID列表，逗号分隔')
@click.option('--key-name', help='密钥对名称')
@click.option('--password', help='登录密码')
@click.option('--count', default=1, type=int, help='创建数量')
@click.pass_context
@handle_error
def create(ctx, name: str, instance_type: str, image_id: str,
          system_disk_type: str, system_disk_size: int,
          vpc_id: Optional[str], subnet_id: Optional[str],
          security_group_ids: Optional[str], key_name: Optional[str],
          password: Optional[str], count: int):
    """创建云服务器实例"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    # 验证实例规格
    if not ValidationUtils.is_valid_instance_type(instance_type):
        click.echo(f"错误: 无效的实例规格 '{instance_type}'", err=True)
        return

    # 处理安全组ID列表
    sg_ids = None
    if security_group_ids:
        sg_ids = [sg_id.strip() for sg_id in security_group_ids.split(',') if sg_id.strip()]

    result = ecs_client.create_instance(
        name=name,
        instance_type=instance_type,
        image_id=image_id,
        system_disk_type=system_disk_type,
        system_disk_size=system_disk_size,
        vpc_id=vpc_id,
        subnet_id=subnet_id,
        security_group_ids=sg_ids,
        key_name=key_name,
        password=password,
        count=count
    )

    OutputFormatter.color_print("✓ 云服务器实例创建成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.option('--force', is_flag=True, help='强制启动')
@click.pass_context
@handle_error
def start(ctx, instance_id: str, force: bool):
    """启动云服务器实例"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.start_instance(instance_id)
    OutputFormatter.color_print(f"✓ 云服务器实例 {instance_id} 启动成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.option('--force', is_flag=True, help='强制停止')
@click.pass_context
@handle_error
def stop(ctx, instance_id: str, force: bool):
    """停止云服务器实例"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.stop_instance(instance_id, force=force)
    OutputFormatter.color_print(f"✓ 云服务器实例 {instance_id} 停止成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.option('--force', is_flag=True, help='强制重启')
@click.pass_context
@handle_error
def reboot(ctx, instance_id: str, force: bool):
    """重启云服务器实例"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.reboot_instance(instance_id, force=force)
    OutputFormatter.color_print(f"✓ 云服务器实例 {instance_id} 重启成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.option('--delete-disk/--keep-disk', default=True, help='是否同时删除数据盘')
@click.option('--confirm', is_flag=True, help='确认删除')
@click.pass_context
@handle_error
def delete(ctx, instance_id: str, delete_disk: bool, confirm: bool):
    """删除云服务器实例"""
    if not confirm:
        click.echo(f"确定要删除云服务器实例 {instance_id} 吗？")
        click.echo("此操作不可逆，请使用 --confirm 参数确认删除")
        return

    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.delete_instance(instance_id, delete_disk=delete_disk)
    OutputFormatter.color_print(f"✓ 云服务器实例 {instance_id} 删除成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.argument('instance_type')
@click.pass_context
@handle_error
def resize(ctx, instance_id: str, instance_type: str):
    """调整云服务器实例规格"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    # 验证实例规格
    if not ValidationUtils.is_valid_instance_type(instance_type):
        click.echo(f"错误: 无效的实例规格 '{instance_type}'", err=True)
        return

    result = ecs_client.resize_instance(instance_id, instance_type)
    OutputFormatter.color_print(f"✓ 云服务器实例 {instance_id} 规格调整成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.option('--type', 'image_type', default='public',
              type=click.Choice(['public', 'private', 'shared']),
              help='镜像类型')
@click.option('--os-type', help='操作系统类型过滤')
@click.pass_context
@handle_error
def images(ctx, image_type: str, os_type: Optional[str]):
    """列出可用的镜像"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.list_images(image_type=image_type, os_type=os_type)
    format_output(result.get('images', []), ctx.obj['output'])


@ecs.command()
@click.pass_context
@handle_error
def instance_types(ctx):
    """列出可用的实例规格"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.list_instance_types()
    format_output(result.get('instanceTypes', []), ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.pass_context
@handle_error
def console(ctx, instance_id: str):
    """获取云服务器实例控制台URL"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.get_instance_console(instance_id)
    console_url = result.get('consoleUrl')
    if console_url:
        click.echo(f"控制台URL: {console_url}")
    else:
        click.echo("无法获取控制台URL")
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.option('--name', required=True, help='镜像名称')
@click.option('--description', help='镜像描述')
@click.pass_context
@handle_error
def create_image(ctx, instance_id: str, name: str, description: Optional[str]):
    """创建云服务器实例镜像"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.create_instance_image(instance_id, name, description)
    OutputFormatter.color_print(f"✓ 镜像 {name} 创建成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_ids', nargs=-1, required=True)
@click.option('--force', is_flag=True, help='强制启动')
@click.pass_context
@handle_error
def batch_start(ctx, instance_ids: List[str], force: bool):
    """批量启动云服务器实例"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.batch_start_instances(list(instance_ids))
    OutputFormatter.color_print(f"✓ 批量启动 {len(instance_ids)} 个云服务器实例成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_ids', nargs=-1, required=True)
@click.option('--force', is_flag=True, help='强制停止')
@click.pass_context
@handle_error
def batch_stop(ctx, instance_ids: List[str], force: bool):
    """批量停止云服务器实例"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.batch_stop_instances(list(instance_ids), force=force)
    OutputFormatter.color_print(f"✓ 批量停止 {len(instance_ids)} 个云服务器实例成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_ids', nargs=-1, required=True)
@click.option('--delete-disk/--keep-disk', default=True, help='是否同时删除数据盘')
@click.option('--confirm', is_flag=True, help='确认删除')
@click.pass_context
@handle_error
def batch_delete(ctx, instance_ids: List[str], delete_disk: bool, confirm: bool):
    """批量删除云服务器实例"""
    if not confirm:
        click.echo(f"确定要删除以下 {len(instance_ids)} 个云服务器实例吗？")
        for instance_id in instance_ids:
            click.echo(f"  - {instance_id}")
        click.echo("此操作不可逆，请使用 --confirm 参数确认删除")
        return

    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.batch_delete_instances(list(instance_ids), delete_disk=delete_disk)
    OutputFormatter.color_print(f"✓ 批量删除 {len(instance_ids)} 个云服务器实例成功", 'green')
    format_output(result, ctx.obj['output'])


@ecs.command()
@click.argument('instance_id')
@click.argument('metric_name')
@click.argument('start_time')
@click.argument('end_time')
@click.option('--period', default=300, type=int, help='统计周期(秒)')
@click.pass_context
@handle_error
def monitoring(ctx, instance_id: str, metric_name: str, start_time: str, end_time: str, period: int):
    """获取云服务器实例监控数据"""
    client = ctx.obj['client']
    ecs_client = ECSClient(client)

    result = ecs_client.get_instance_monitoring(
        instance_id=instance_id,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time,
        period=period
    )
    format_output(result, ctx.obj['output'])