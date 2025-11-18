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


@ecs.command('flavor-options')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def flavor_options(ctx, output: Optional[str]):
    """查询云主机规格可售地域总览查询条件范围"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_flavor_options()
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        is_mock = result.get('_mock', False)
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo("云主机规格查询条件范围")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo("=" * 80)
            
            if return_obj.get('flavorNameScope'):
                click.echo(f"\n规格名称范围: {', '.join(return_obj.get('flavorNameScope', []))}")
            
            if return_obj.get('flavorCPUScope'):
                click.echo(f"vCPU范围: {', '.join(return_obj.get('flavorCPUScope', []))}")
            
            if return_obj.get('flavorRAMScope'):
                click.echo(f"内存范围(GB): {', '.join(return_obj.get('flavorRAMScope', []))}")
            
            if return_obj.get('flavorFamilyScope'):
                click.echo(f"规格族范围: {', '.join(return_obj.get('flavorFamilyScope', []))}")
            
            if return_obj.get('gpuConfigScope'):
                click.echo(f"GPU配置范围: {', '.join(return_obj.get('gpuConfigScope', []))}")
            
            if return_obj.get('localDiskConfigScope'):
                click.echo(f"本地盘配置范围: {', '.join(return_obj.get('localDiskConfigScope', []))}")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_auto_renew_config(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询包周期云主机自动续订配置"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_auto_renew_config(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo("云主机自动续订配置")
            click.echo("=" * 80)
            click.echo(f"云主机ID: {return_obj.get('instanceID', 'N/A')}")
            
            auto_renew_status = return_obj.get('autoRenewStatus', '0')
            status_text = '自动续费' if auto_renew_status == '1' else '不续费'
            click.echo(f"续订状态: {status_text}")
            
            if auto_renew_status == '1':
                cycle_type = return_obj.get('autoRenewCycleType', '')
                cycle_type_text = '按年' if cycle_type == 'YEAR' else '按月' if cycle_type == 'MONTH' else cycle_type
                click.echo(f"续订周期类型: {cycle_type_text}")
                click.echo(f"订购时长: {return_obj.get('autoRenewCycleCount', 'N/A')}")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()

@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_dns_record(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询云主机的内网DNS记录"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_dns_record(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo("云主机内网DNS记录")
            click.echo("=" * 80)
            click.echo(f"云主机ID: {return_obj.get('instanceID', 'N/A')}")
            
            dns_records = return_obj.get('privateDnsRecordList', [])
            if dns_records:
                click.echo(f"\nDNS记录数量: {len(dns_records)}")
                for idx, record in enumerate(dns_records, 1):
                    click.echo(f"\n记录 {idx}:")
                    click.echo(f"  域名选项: {record.get('dnsOption', 'N/A')}")
                    click.echo(f"  域名类型: {record.get('dnsType', 'N/A')}")
                    click.echo(f"  域名: {record.get('dnsName', 'N/A')}")
                    click.echo(f"  内网IP: {record.get('privateIP', 'N/A')}")
            else:
                click.echo("\n无DNS记录")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--project-id', help='企业项目ID')
@click.option('--instance-id', help='云主机ID')
@click.option('--snapshot-status', help='快照状态（pending/available/restoring/error）')
@click.option('--snapshot-id', help='快照ID')
@click.option('--snapshot-name', help='快照名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_snapshots(ctx, region_id: str, page: int, page_size: int, 
                   project_id: Optional[str], instance_id: Optional[str],
                   snapshot_status: Optional[str], snapshot_id: Optional[str],
                   snapshot_name: Optional[str], output: Optional[str]):
    """查询云主机快照列表"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_snapshots(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            project_id=project_id,
            instance_id=instance_id,
            snapshot_status=snapshot_status,
            snapshot_id=snapshot_id,
            snapshot_name=snapshot_name
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            results = return_obj.get('results', [])
            click.echo(f"云主机快照列表 (共 {return_obj.get('totalCount', 0)} 个)")
            click.echo("=" * 120)
            
            if results:
                for idx, snapshot in enumerate(results, 1):
                    click.echo(f"\n快照 {idx}:")
                    click.echo(f"  快照ID: {snapshot.get('snapshotID', 'N/A')}")
                    click.echo(f"  快照名称: {snapshot.get('snapshotName', 'N/A')}")
                    click.echo(f"  云主机ID: {snapshot.get('instanceID', 'N/A')}")
                    click.echo(f"  云主机名称: {snapshot.get('instanceName', 'N/A')}")
                    click.echo(f"  快照状态: {snapshot.get('snapshotStatus', 'N/A')}")
                    click.echo(f"  云主机状态: {snapshot.get('instanceStatus', 'N/A')}")
                    click.echo(f"  可用区: {snapshot.get('azName', 'N/A')}")
                    click.echo(f"  CPU核数: {snapshot.get('cpu', 'N/A')}")
                    click.echo(f"  内存(MB): {snapshot.get('memory', 'N/A')}")
                    click.echo(f"  创建时间: {snapshot.get('createdTime', 'N/A')}")
                    click.echo(f"  更新时间: {snapshot.get('updatedTime', 'N/A')}")
                    
                    members = snapshot.get('members', [])
                    if members:
                        click.echo(f"  云硬盘快照:")
                        for disk in members:
                            click.echo(f"    - 磁盘ID: {disk.get('diskID', 'N/A')}, "
                                     f"类型: {disk.get('diskType', 'N/A')}, "
                                     f"大小: {disk.get('diskSize', 'N/A')}GB, "
                                     f"启动盘: {'是' if disk.get('isBootable') else '否'}, "
                                     f"快照状态: {disk.get('diskSnapshotStatus', 'N/A')}")
                
                click.echo(f"\n当前页: {page}/{return_obj.get('totalPage', 1)}")
            else:
                click.echo("\n无快照数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--snapshot-id', required=True, help='快照ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_snapshot_details(ctx, region_id: str, snapshot_id: str, output: Optional[str]):
    """查询云主机快照详情"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_snapshot_details(region_id=region_id, snapshot_id=snapshot_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        results = return_obj.get('results', [])
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            if results:
                snapshot = results[0]
                click.echo("云主机快照详情")
                click.echo("=" * 120)
                click.echo(f"快照ID: {snapshot.get('snapshotID', 'N/A')}")
                click.echo(f"快照名称: {snapshot.get('snapshotName', 'N/A')}")
                click.echo(f"快照描述: {snapshot.get('snapshotDescription', 'N/A')}")
                click.echo(f"快照状态: {snapshot.get('snapshotStatus', 'N/A')}")
                click.echo(f"\n云主机信息:")
                click.echo(f"  云主机ID: {snapshot.get('instanceID', 'N/A')}")
                click.echo(f"  云主机名称: {snapshot.get('instanceName', 'N/A')}")
                click.echo(f"  云主机状态: {snapshot.get('instanceStatus', 'N/A')}")
                click.echo(f"  可用区: {snapshot.get('azName', 'N/A')}")
                click.echo(f"  CPU核数: {snapshot.get('cpu', 'N/A')}")
                click.echo(f"  内存(MB): {snapshot.get('memory', 'N/A')}")
                click.echo(f"  规格ID: {snapshot.get('flavorID', 'N/A')}")
                click.echo(f"  镜像ID: {snapshot.get('imageID', 'N/A')}")
                click.echo(f"\n其他信息:")
                click.echo(f"  企业项目ID: {snapshot.get('projectID', 'N/A')}")
                click.echo(f"  创建时间: {snapshot.get('createdTime', 'N/A')}")
                click.echo(f"  更新时间: {snapshot.get('updatedTime', 'N/A')}")
                
                members = snapshot.get('members', [])
                if members:
                    click.echo(f"\n云硬盘快照 ({len(members)}个):")
                    for idx, disk in enumerate(members, 1):
                        click.echo(f"\n  磁盘 {idx}:")
                        click.echo(f"    磁盘ID: {disk.get('diskID', 'N/A')}")
                        click.echo(f"    磁盘名称: {disk.get('diskName', 'N/A')}")
                        click.echo(f"    磁盘类型: {disk.get('diskType', 'N/A')}")
                        click.echo(f"    磁盘大小: {disk.get('diskSize', 'N/A')}GB")
                        click.echo(f"    启动盘: {'是' if disk.get('isBootable') else '否'}")
                        click.echo(f"    加密: {'是' if disk.get('isEncrypt') else '否'}")
                        click.echo(f"    快照ID: {disk.get('diskSnapshotID', 'N/A')}")
                        click.echo(f"    快照状态: {disk.get('diskSnapshotStatus', 'N/A')}")
            else:
                click.echo("未找到快照详情")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--project-id', help='企业项目ID')
@click.option('--keypair-name', help='密钥对名称')
@click.option('--query-content', help='模糊查询内容')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_keypairs(ctx, region_id: str, page: int, page_size: int, 
                  project_id: Optional[str], keypair_name: Optional[str],
                  query_content: Optional[str], output: Optional[str]):
    """查询一个或多个密钥对"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_keypairs(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            project_id=project_id,
            keypair_name=keypair_name,
            query_content=query_content
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            results = return_obj.get('results', [])
            click.echo(f"密钥对列表 (共 {return_obj.get('totalCount', 0)} 个)")
            click.echo("=" * 120)
            
            if results:
                for idx, keypair in enumerate(results, 1):
                    click.echo(f"\n密钥对 {idx}:")
                    click.echo(f"  密钥对ID: {keypair.get('keyPairID', 'N/A')}")
                    click.echo(f"  密钥对名称: {keypair.get('keyPairName', 'N/A')}")
                    click.echo(f"  指纹: {keypair.get('fingerPrint', 'N/A')}")
                    click.echo(f"  绑定实例数: {keypair.get('bindInstanceNum', 0)}")
                    click.echo(f"  企业项目ID: {keypair.get('projectID', 'N/A')}")
                    
                    desc = keypair.get('keyPairDescription', '')
                    if desc:
                        click.echo(f"  描述: {desc}")
                    
                    labels = keypair.get('labelList', [])
                    if labels:
                        click.echo(f"  标签:")
                        for label in labels:
                            click.echo(f"    - {label.get('labelKey', 'N/A')}: {label.get('labelValue', 'N/A')}")
                
                click.echo(f"\n当前页记录数: {return_obj.get('currentCount', 0)}")
            else:
                click.echo("\n无密钥对数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--job-ids', required=True, help='异步任务ID列表，以英文逗号分隔')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_jobs(ctx, region_id: str, job_ids: str, output: Optional[str]):
    """查询多个异步任务的结果"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_jobs(region_id=region_id, job_ids=job_ids)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            job_list = return_obj.get('jobList', [])
            click.echo(f"异步任务查询结果 (共 {len(job_list)} 个)")
            click.echo("=" * 80)
            
            if job_list:
                status_map = {
                    0: '执行中',
                    1: '执行成功',
                    2: '执行失败'
                }
                
                for idx, job in enumerate(job_list, 1):
                    job_status = job.get('jobStatus', -1)
                    status_text = status_map.get(job_status, '未知状态')
                    click.echo(f"\n任务 {idx}:")
                    click.echo(f"  任务ID: {job.get('jobID', 'N/A')}")
                    click.echo(f"  任务状态: {status_text} ({job_status})")
            else:
                click.echo("\n无任务数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--job-id', required=True, help='异步任务ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_async_result(ctx, region_id: str, job_id: str, output: Optional[str]):
    """查询一个异步任务的结果"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_async_result(region_id=region_id, job_id=job_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            status_map = {
                0: '执行中',
                1: '执行成功',
                2: '执行失败'
            }
            
            job_status = return_obj.get('jobStatus', -1)
            status_text = status_map.get(job_status, '未知状态')
            
            click.echo("异步任务查询结果")
            click.echo("=" * 80)
            click.echo(f"任务ID: {job_id}")
            click.echo(f"任务状态: {status_text} ({job_status})")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--project-id', help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_volume_statistics(ctx, region_id: str, project_id: Optional[str], output: Optional[str]):
    """查询用户云硬盘统计信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_volume_statistics(region_id=region_id, project_id=project_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        stats = return_obj.get('volumeStatistics', {})
        
        if output and output in ['json', 'yaml']:
            format_output(stats, output)
        else:
            click.echo("云硬盘统计信息")
            click.echo("=" * 80)
            click.echo(f"云硬盘总数: {stats.get('totalCount', 0)}")
            click.echo(f"  系统盘数量: {stats.get('rootDiskCount', 0)}")
            click.echo(f"  数据盘数量: {stats.get('dataDiskCount', 0)}")
            click.echo(f"\n云硬盘总大小: {stats.get('totalSize', 0)} GB")
            click.echo(f"  系统盘大小: {stats.get('rootDiskSize', 0)} GB")
            click.echo(f"  数据盘大小: {stats.get('dataDiskSize', 0)} GB")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_fixed_ip_list(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询云主机的固定IP"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_fixed_ip_list(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        fixed_ips = return_obj.get('fixedIPList', [])
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo("云主机固定IP")
            click.echo("=" * 80)
            click.echo(f"云主机ID: {instance_id}")
            
            if fixed_ips:
                click.echo(f"\n固定IP列表 ({len(fixed_ips)}个):")
                for idx, ip in enumerate(fixed_ips, 1):
                    click.echo(f"  {idx}. {ip}")
            else:
                click.echo("\n无固定IP")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--policy-id', help='备份策略ID')
@click.option('--policy-name', help='备份策略名称')
@click.option('--project-id', help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_backup_policies(ctx, region_id: str, page: int, page_size: int,
                         policy_id: Optional[str], policy_name: Optional[str],
                         project_id: Optional[str], output: Optional[str]):
    """查询云主机备份策略列表"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_backup_policies(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            policy_id=policy_id,
            policy_name=policy_name,
            project_id=project_id
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            policies = return_obj.get('policyList', [])
            click.echo(f"云主机备份策略列表 (共 {return_obj.get('totalCount', 0)} 个)")
            click.echo("=" * 120)
            
            if policies:
                for idx, policy in enumerate(policies, 1):
                    click.echo(f"\n策略 {idx}:")
                    click.echo(f"  策略ID: {policy.get('policyID', 'N/A')}")
                    click.echo(f"  策略名称: {policy.get('policyName', 'N/A')}")
                    click.echo(f"  状态: {'启用' if policy.get('status') == 1 else '停用'}")
                    click.echo(f"  资源池ID: {policy.get('regionID', 'N/A')}")
                    click.echo(f"  企业项目ID: {policy.get('projectID', 'N/A')}")
                    
                    cycle_type = policy.get('cycleType', '')
                    if cycle_type == 'day':
                        click.echo(f"  备份周期: 每 {policy.get('cycleDay', 'N/A')} 天")
                    elif cycle_type == 'week':
                        click.echo(f"  备份周期: 每周 {policy.get('cycleWeek', 'N/A')}")
                    
                    click.echo(f"  备份时间: {policy.get('time', 'N/A')} 点")
                    
                    retention_type = policy.get('retentionType', '')
                    if retention_type == 'num':
                        click.echo(f"  保留策略: 保留 {policy.get('retentionNum', 'N/A')} 个备份")
                    elif retention_type == 'date':
                        click.echo(f"  保留策略: 保留 {policy.get('retentionDay', 'N/A')} 天")
                    elif retention_type == 'all':
                        click.echo(f"  保留策略: 永久保留")
                    
                    click.echo(f"  绑定云主机数: {policy.get('resourceCount', 0)}")
                    
                    repos = policy.get('repositoryList', [])
                    if repos:
                        click.echo(f"  备份库:")
                        for repo in repos:
                            click.echo(f"    - {repo.get('repositoryName', 'N/A')} ({repo.get('repositoryID', 'N/A')})")
                
                click.echo(f"\n当前页: {return_obj.get('currentPage', 1)}/{return_obj.get('totalPage', 1)}")
            else:
                click.echo("\n无备份策略数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-backup-id', required=True, help='云主机备份ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_backup_status(ctx, region_id: str, instance_backup_id: str, output: Optional[str]):
    """查询云主机备份状态"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_backup_status(region_id=region_id, instance_backup_id=instance_backup_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            status = return_obj.get('instanceBackupStatus', 'N/A')
            status_map = {
                'CREATING': '创建中',
                'ACTIVE': '可用',
                'MERGING_BACKUP': '合并中',
                'RESTORING': '恢复中',
                'DELETING': '删除中',
                'FROZEN': '已冻结',
                'ERROR': '错误'
            }
            status_text = status_map.get(status, status)
            
            click.echo("云主机备份状态")
            click.echo("=" * 80)
            click.echo(f"备份ID: {instance_backup_id}")
            click.echo(f"备份状态: {status_text} ({status})")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--disk-id', required=True, help='磁盘ID')
@click.option('--region-id', help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_volume_info(ctx, disk_id: str, region_id: Optional[str], output: Optional[str]):
    """云硬盘信息查询（基于磁盘ID）"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_volume_info(disk_id=disk_id, region_id=region_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo("云硬盘信息")
            click.echo("=" * 120)
            click.echo(f"磁盘ID: {return_obj.get('diskID', 'N/A')}")
            click.echo(f"磁盘名称: {return_obj.get('diskName', 'N/A')}")
            click.echo(f"磁盘大小: {return_obj.get('diskSize', 'N/A')} GB")
            
            disk_type = return_obj.get('diskType', 'N/A')
            disk_type_map = {
                'SATA': '普通IO',
                'SAS': '高IO',
                'SSD': '超高IO',
                'FAST-SSD': '极速型SSD',
                'XSSD-0': 'X系列云硬盘-0',
                'XSSD-1': 'X系列云硬盘-1',
                'XSSD-2': 'X系列云硬盘-2'
            }
            disk_type_text = disk_type_map.get(disk_type, disk_type)
            click.echo(f"磁盘类型: {disk_type_text} ({disk_type})")
            
            disk_mode = return_obj.get('diskMode', 'N/A')
            disk_mode_map = {
                'VBD': '虚拟块存储设备',
                'ISCSI': '小型计算机系统接口',
                'FCSAN': '光纤通道协议的SAN网络'
            }
            disk_mode_text = disk_mode_map.get(disk_mode, disk_mode)
            click.echo(f"磁盘模式: {disk_mode_text} ({disk_mode})")
            
            click.echo(f"磁盘状态: {return_obj.get('diskStatus', 'N/A')}")
            click.echo(f"资源池ID: {return_obj.get('regionID', 'N/A')}")
            click.echo(f"可用区: {return_obj.get('azName', 'N/A')}")
            
            import datetime
            create_time = return_obj.get('createTime')
            if create_time:
                dt = datetime.datetime.fromtimestamp(create_time / 1000)
                click.echo(f"创建时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            update_time = return_obj.get('updateTime')
            if update_time:
                dt = datetime.datetime.fromtimestamp(update_time / 1000)
                click.echo(f"更新时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            expire_time = return_obj.get('expireTime')
            if expire_time:
                dt = datetime.datetime.fromtimestamp(expire_time / 1000)
                click.echo(f"过期时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            click.echo(f"是否系统盘: {'是' if return_obj.get('isSystemVolume') else '否'}")
            click.echo(f"是否成套资源: {'是' if return_obj.get('isPackaged') else '否'}")
            click.echo(f"是否共享云硬盘: {'是' if return_obj.get('multiAttach') else '否'}")
            click.echo(f"是否加密盘: {'是' if return_obj.get('isEncrypt') else '否'}")
            
            if return_obj.get('isEncrypt'):
                click.echo(f"加密盘密钥UUID: {return_obj.get('kmsUUID', 'N/A')}")
            
            click.echo(f"是否按需订购: {'是' if return_obj.get('onDemand') else '否'}")
            
            if not return_obj.get('onDemand'):
                cycle_type_map = {'month': '月', 'year': '年', 'MONTH': '月', 'YEAR': '年'}
                cycle_type = return_obj.get('cycleType', 'N/A')
                cycle_type_text = cycle_type_map.get(cycle_type, cycle_type)
                click.echo(f"订购周期类型: {cycle_type_text}")
                click.echo(f"订购周期数: {return_obj.get('cycleCount', 'N/A')}")
            
            click.echo(f"是否冻结: {'是' if return_obj.get('diskFreeze') else '否'}")
            click.echo(f"企业项目ID: {return_obj.get('projectID', 'N/A')}")
            
            if return_obj.get('provisionedIops'):
                click.echo(f"预配置IOPS: {return_obj.get('provisionedIops')}")
            
            if return_obj.get('volumeSource'):
                click.echo(f"源快照ID: {return_obj.get('volumeSource')}")
            
            if return_obj.get('snapshotPolicyID'):
                click.echo(f"绑定快照策略ID: {return_obj.get('snapshotPolicyID')}")
            
            if return_obj.get('instanceID'):
                click.echo(f"\n挂载信息:")
                click.echo(f"  绑定云主机ID: {return_obj.get('instanceID', 'N/A')}")
                click.echo(f"  绑定云主机名称: {return_obj.get('instanceName', 'N/A')}")
                click.echo(f"  云主机状态: {return_obj.get('instanceStatus', 'N/A')}")
            
            attachments = return_obj.get('attachments', [])
            if attachments:
                click.echo(f"\n挂载详情 (共{len(attachments)}个):")
                for idx, att in enumerate(attachments, 1):
                    click.echo(f"  挂载 #{idx}")
                    click.echo(f"    云主机ID: {att.get('instanceID', 'N/A')}")
                    click.echo(f"    挂载ID: {att.get('attachmentID', 'N/A')}")
                    click.echo(f"    挂载设备名: {att.get('device', 'N/A')}")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--policy-id', required=True, help='云主机备份策略ID')
@click.option('--instance-name', help='云主机名称，模糊过滤')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_backup_policy_instances(ctx, region_id: str, policy_id: str, instance_name: Optional[str], page: int, page_size: int, output: Optional[str]):
    """查询云主机备份策略绑定云主机信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_backup_policy_instances(
            region_id=region_id,
            policy_id=policy_id,
            instance_name=instance_name,
            page_no=page,
            page_size=page_size
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            instances = return_obj.get('instancePolicies', [])
            
            if instances:
                click.echo(f"备份策略绑定云主机列表 (备份策略ID: {policy_id})")
                click.echo("=" * 120)
                
                for idx, instance in enumerate(instances, 1):
                    click.echo(f"\n云主机 #{idx}")
                    click.echo(f"  云主机ID: {instance.get('instanceID', 'N/A')}")
                    click.echo(f"  云主机名称: {instance.get('instanceName', 'N/A')}")
                    click.echo(f"  显示名称: {instance.get('displayName', 'N/A')}")
                    
                    status = instance.get('status', 'N/A')
                    status_map = {
                        'ACTIVE': '运行中',
                        'SHUTOFF': '已关机',
                        'backingup': '备份中',
                        'creating': '创建中',
                        'expired': '已到期',
                        'freezing': '已冻结',
                        'rebuild': '重装',
                        'restarting': '重启中',
                        'running': '运行中',
                        'starting': '开机中',
                        'stopped': '已关机',
                        'stopping': '关机中',
                        'error': '错误',
                        'snapshotting': '快照创建中',
                        'unsubscribed': '包周期已退订',
                        'unsubscribing': '包周期退订中'
                    }
                    status_text = status_map.get(status, status)
                    click.echo(f"  状态: {status_text} ({status})")
                    
                    click.echo(f"  资源池ID: {instance.get('regionID', 'N/A')}")
                    click.echo(f"  创建时间: {instance.get('createTime', 'N/A')}")
                    click.echo(f"  更新时间: {instance.get('updateTime', 'N/A')}")
                    
                    volumes = instance.get('attachedVolumes', [])
                    if volumes:
                        click.echo(f"  关联云硬盘数量: {len(volumes)}")
                        click.echo(f"  云硬盘ID列表:")
                        for vol_id in volumes:
                            click.echo(f"    - {vol_id}")
                    else:
                        click.echo(f"  关联云硬盘数量: 0")
                
                click.echo(f"\n当前页: {return_obj.get('currentPage', 1)}/{return_obj.get('totalPage', 1)}")
                click.echo(f"总记录数: {return_obj.get('totalCount', 0)}")
            else:
                click.echo("\n该备份策略未绑定任何云主机")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_volumes(ctx, region_id: str, instance_id: str, page: int, page_size: int, output: Optional[str]):
    """查询云主机的云硬盘列表"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_volumes(
            region_id=region_id,
            instance_id=instance_id,
            page_no=page,
            page_size=page_size
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            results = return_obj.get('results', [])
            click.echo(f"云主机云硬盘列表 (共 {return_obj.get('totalCount', 0)} 个)")
            click.echo("=" * 120)
            click.echo(f"云主机ID: {instance_id}")
            
            if results:
                for idx, volume in enumerate(results, 1):
                    click.echo(f"\n云硬盘 {idx}:")
                    click.echo(f"  云硬盘ID: {volume.get('diskID', 'N/A')}")
                    click.echo(f"  用途分类: {volume.get('diskType', 'N/A')}")
                    click.echo(f"  云硬盘类型: {volume.get('diskDataType', 'N/A')}")
                    click.echo(f"  云硬盘属性: {volume.get('diskMode', 'N/A')}")
                    click.echo(f"  容量大小: {volume.get('diskSize', 'N/A')} GB")
                    click.echo(f"  是否加密: {'是' if volume.get('isEncrypt') else '否'}")
                
                click.echo(f"\n当前页: {page}/{return_obj.get('totalPage', 1)}")
            else:
                click.echo("\n无云硬盘数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_affinity_group_details(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询云主机所在云主机组"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_affinity_group_details(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo("云主机所在云主机组")
            click.echo("=" * 80)
            click.echo(f"云主机ID: {instance_id}")
            
            if return_obj:
                click.echo(f"\n云主机组ID: {return_obj.get('affinityGroupID', 'N/A')}")
                click.echo(f"云主机组名称: {return_obj.get('affinityGroupName', 'N/A')}")
                click.echo(f"策略类型: {return_obj.get('policyTypeName', 'N/A')}")
            else:
                click.echo("\n该云主机未加入任何云主机组")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_regions_details(ctx, output: Optional[str]):
    """查询账户启用的资源池信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_regions_details()
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        regions = return_obj.get('regionList', [])
        
        if output and output in ['json', 'yaml']:
            format_output(regions, output)
        else:
            click.echo(f"账户启用的资源池 (共 {len(regions)} 个)")
            click.echo("=" * 100)
            
            if regions:
                for idx, region in enumerate(regions, 1):
                    click.echo(f"\n资源池 {idx}:")
                    click.echo(f"  资源池ID: {region.get('regionID', 'N/A')}")
                    click.echo(f"  资源池UUID: {region.get('regionUUID', 'N/A')}")
                    click.echo(f"  资源池名称: {region.get('regionName', 'N/A')}")
            else:
                click.echo("\n无资源池数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_availability_zones_details(ctx, region_id: str, output: Optional[str]):
    """查询账户资源池中可用区信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_availability_zones_details(region_id=region_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        az_list = return_obj.get('azList', [])
        
        if output and output in ['json', 'yaml']:
            format_output(az_list, output)
        else:
            click.echo(f"资源池可用区列表 (共 {len(az_list)} 个)")
            click.echo("=" * 80)
            click.echo(f"资源池ID: {region_id}")
            
            if az_list:
                for idx, az in enumerate(az_list, 1):
                    click.echo(f"\n可用区 {idx}:")
                    click.echo(f"  可用区ID: {az.get('azID', 'N/A')}")
                    click.echo(f"  可用区名称: {az.get('azName', 'N/A')}")
            else:
                click.echo("\n无可用区数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--az-name', help='可用区名称')
@click.option('--instance-id-list', help='云主机ID列表，多台使用英文逗号分割')
@click.option('--project-id', help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_instance_status(ctx, region_id: str, page: int, page_size: int,
                         az_name: Optional[str], instance_id_list: Optional[str],
                         project_id: Optional[str], output: Optional[str]):
    """获取多台云主机的状态信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_instance_status(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            az_name=az_name,
            instance_id_list=instance_id_list,
            project_id=project_id
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            status_list = return_obj.get('statusList', [])
            click.echo(f"云主机状态列表 (共 {return_obj.get('totalCount', 0)} 个)")
            click.echo("=" * 100)
            
            if status_list:
                status_map = {
                    'backingup': '备份中',
                    'creating': '创建中',
                    'expired': '已到期',
                    'freezing': '已冻结',
                    'rebuild': '重装',
                    'restarting': '重启中',
                    'running': '运行中',
                    'starting': '开机中',
                    'stopped': '已关机',
                    'stopping': '关机中',
                    'error': '错误',
                    'snapshotting': '快照创建中',
                    'unsubscribed': '包周期已退订',
                    'unsubscribing': '包周期退订中'
                }
                
                for idx, instance in enumerate(status_list, 1):
                    status = instance.get('instanceStatus', 'N/A')
                    status_text = status_map.get(status, status)
                    click.echo(f"\n{idx}. 云主机ID: {instance.get('instanceID', 'N/A')}")
                    click.echo(f"   状态: {status_text} ({status})")
                
                click.echo(f"\n当前页: {page}/{return_obj.get('totalPage', 1)}")
            else:
                click.echo("\n无云主机状态数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--master-order-id', required=True, help='订单ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_uuid_by_order(ctx, master_order_id: str, output: Optional[str]):
    """根据masterOrderID查询云主机ID"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_uuid_by_order(master_order_id=master_order_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            order_status_map = {
                '1': '待支付', '2': '已支付', '3': '完成', '4': '取消',
                '5': '施工失败', '7': '正在支付中', '8': '待审核',
                '9': '审核通过', '10': '审核未通过', '11': '撤单完成',
                '12': '退订中', '13': '退订完成', '14': '开通中',
                '15': '变更移除', '16': '自动撤单中', '17': '手动撤单中',
                '18': '终止中', '22': '支付失败', '-2': '待撤单',
                '-1': '未知', '0': '错误', '140': '已初始化', '999': '逻辑错误'
            }
            
            order_status = return_obj.get('orderStatus', '-1')
            status_text = order_status_map.get(order_status, '未知状态')
            instance_ids = return_obj.get('instanceIDList', [])
            
            click.echo("订单查询结果")
            click.echo("=" * 80)
            click.echo(f"订单ID: {master_order_id}")
            click.echo(f"订单状态: {status_text} ({order_status})")
            
            if instance_ids:
                click.echo(f"\n云主机ID列表 ({len(instance_ids)}个):")
                for idx, instance_id in enumerate(instance_ids, 1):
                    click.echo(f"  {idx}. {instance_id}")
            else:
                click.echo("\n暂无云主机ID（订单可能还在创建中）")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--affinity-group-id', help='云主机组ID')
@click.option('--query-content', help='模糊匹配查询内容')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_affinity_groups(ctx, region_id: str, page: int, page_size: int,
                         affinity_group_id: Optional[str], query_content: Optional[str],
                         output: Optional[str]):
    """查询云主机组列表或者详情"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_affinity_groups(
            region_id=region_id,
            page_no=page,
            page_size=page_size,
            affinity_group_id=affinity_group_id,
            query_content=query_content
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            results = return_obj.get('results', [])
            click.echo(f"云主机组列表 (共 {return_obj.get('totalCount', 0)} 个)")
            click.echo("=" * 100)
            
            if results:
                policy_type_map = {
                    0: '强制反亲和',
                    1: '强制亲和',
                    2: '软反亲和',
                    3: '软亲和'
                }
                
                for idx, group in enumerate(results, 1):
                    click.echo(f"\n云主机组 {idx}:")
                    click.echo(f"  云主机组ID: {group.get('affinityGroupID', 'N/A')}")
                    click.echo(f"  云主机组名称: {group.get('affinityGroupName', 'N/A')}")
                    
                    policy = group.get('affinityGroupPolicy', {})
                    if policy:
                        policy_type = policy.get('policyType', -1)
                        policy_type_text = policy_type_map.get(policy_type, '未知')
                        click.echo(f"  策略类型: {policy_type_text} ({policy.get('policyTypeName', 'N/A')})")
                    
                    click.echo(f"  创建时间: {group.get('createdTime', 'N/A')}")
                    click.echo(f"  更新时间: {group.get('updatedTime', 'N/A')}")
                    click.echo(f"  是否删除: {'是' if group.get('deleted') else '否'}")
                
                click.echo(f"\n当前页: {page}/{return_obj.get('totalPage', 1)}")
            else:
                click.echo("\n无云主机组数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--snapshot-id', required=True, help='云主机快照ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_snapshot_status(ctx, region_id: str, snapshot_id: str, output: Optional[str]):
    """查询云主机快照状态"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_snapshot_status(region_id=region_id, snapshot_id=snapshot_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            snapshot_status = return_obj.get('snapshotStatus', 'N/A')
            status_desc = {
                'pending': '创建中',
                'available': '可用',
                'restoring': '恢复中',
                'error': '错误'
            }
            
            click.echo(f"快照状态信息")
            click.echo("=" * 80)
            click.echo(f"  快照ID: {snapshot_id}")
            click.echo(f"  状态: {snapshot_status} ({status_desc.get(snapshot_status, snapshot_status)})")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_snapshot_count(ctx, region_id: str, output: Optional[str]):
    """查询云主机快照个数统计"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_snapshot_count(region_id=region_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            total_count = return_obj.get('totalCount', 0)
            available_count = return_obj.get('availableCount', 0)
            creating_count = return_obj.get('creatingCount', 0)
            error_count = return_obj.get('errorCount', 0)
            
            click.echo(f"快照统计信息")
            click.echo("=" * 80)
            click.echo(f"  总数: {total_count}")
            click.echo(f"  可用: {available_count}")
            click.echo(f"  创建中: {creating_count}")
            click.echo(f"  错误: {error_count}")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', help='可用区名称')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def list_flavor_families(ctx, region_id: str, az_name: Optional[str], output: Optional[str]):
    """查询云主机规格族列表"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_flavor_families(region_id=region_id, az_name=az_name)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        flavor_families = return_obj.get('flavorFamilyList', [])
        
        if output and output in ['json', 'yaml']:
            format_output(flavor_families, output)
        else:
            click.echo(f"云主机规格族列表 (共 {len(flavor_families)} 个)")
            click.echo("=" * 80)
            
            if flavor_families:
                for idx, family in enumerate(flavor_families, 1):
                    click.echo(f"  {idx}. {family}")
            else:
                click.echo("\n无规格族数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--flavor-names', help='云主机规格名称列表，逗号分隔')
@click.option('--flavor-families', help='云主机规格族列表，逗号分隔')
@click.option('--flavor-cpus', help='云主机规格vcpu个数列表，逗号分隔')
@click.option('--flavor-rams', help='云主机规格内存大小列表，逗号分隔')
@click.option('--local-disk-sizes', help='本地盘容量配置列表，逗号分隔')
@click.option('--gpu-configs', help='GPU配置列表，逗号分隔')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页记录数（最大50）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_flavor_available_regions(ctx, flavor_names: Optional[str], flavor_families: Optional[str],
                                   flavor_cpus: Optional[str], flavor_rams: Optional[str],
                                   local_disk_sizes: Optional[str], gpu_configs: Optional[str],
                                   page: int, page_size: int, output: Optional[str]):
    """查询云主机规格可售地域总览"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        # 解析参数列表
        flavor_name_list = flavor_names.split(',') if flavor_names else None
        flavor_family_list = flavor_families.split(',') if flavor_families else None
        flavor_cpu_list = [int(cpu) for cpu in flavor_cpus.split(',')] if flavor_cpus else None
        flavor_ram_list = [int(ram) for ram in flavor_rams.split(',')] if flavor_rams else None
        local_disk_size_list = local_disk_sizes.split(',') if local_disk_sizes else None
        gpu_config_list = gpu_configs.split(',') if gpu_configs else None
        
        result = ecs_client.query_flavor_available_regions(
            flavor_name_list=flavor_name_list,
            flavor_family_list=flavor_family_list,
            flavor_cpu_list=flavor_cpu_list,
            flavor_ram_list=flavor_ram_list,
            local_disk_size_list=local_disk_size_list,
            gpu_config_list=gpu_config_list,
            page_no=page,
            page_size=page_size
        )
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            total_count = return_obj.get('totalCount', 0)
            current_count = return_obj.get('currentCount', 0)
            total_page = return_obj.get('totalPage', 1)
            resource_list = return_obj.get('availableStatusResourceList', []) or return_obj.get('AvailableStatusResourceList', [])
            
            click.echo(f"云主机规格可售地域总览 (共 {total_count} 条记录)")
            click.echo("=" * 120)
            
            if resource_list:
                for idx, resource in enumerate(resource_list, 1):
                    click.echo(f"\n规格 {idx}:")
                    click.echo(f"  规格名称: {resource.get('flavorName', 'N/A')}")
                    click.echo(f"  规格族: {resource.get('flavorFamily', 'N/A')}")
                    click.echo(f"  vCPU: {resource.get('flavorCPU', 'N/A')}")
                    click.echo(f"  内存(GB): {resource.get('flavorRAM', 'N/A')}")
                    
                    if resource.get('gpuConfig'):
                        click.echo(f"  GPU配置: {resource.get('gpuConfig')}")
                    if resource.get('localDiskConfig'):
                        click.echo(f"  本地盘配置: {resource.get('localDiskConfig')}")
                    
                    region_list = resource.get('availableStatusRegionList', []) or resource.get('AvailableStatusRegionList', [])
                    if region_list:
                        click.echo(f"  可售地域:")
                        for region in region_list:
                            available_status = "✓ 可用" if region.get('available') else "✗ 售罄"
                            click.echo(f"    - {region.get('regionName', 'N/A')} ({region.get('azName', 'N/A')}) - {available_status}")
                
                click.echo(f"\n当前页: {page}/{total_page}, 本页记录: {current_count}")
            else:
                click.echo("\n无规格数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_flavor_query_options(ctx, output: Optional[str]):
    """查询云主机规格可售地域总览查询条件范围"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_flavor_query_options()
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            click.echo(f"云主机规格查询条件范围")
            click.echo("=" * 80)
            
            flavor_names = return_obj.get('flavorNameScope', [])
            if flavor_names:
                click.echo(f"\n规格名称: {', '.join(flavor_names[:10])}")
                if len(flavor_names) > 10:
                    click.echo(f"  ... 等共 {len(flavor_names)} 个规格")
            
            flavor_families = return_obj.get('flavorFamilyScope', [])
            if flavor_families:
                click.echo(f"\n规格族: {', '.join(flavor_families)}")
            
            flavor_cpus = return_obj.get('flavorCPUScope', [])
            if flavor_cpus:
                click.echo(f"\nvCPU: {', '.join(flavor_cpus)}")
            
            flavor_rams = return_obj.get('flavorRAMScope', [])
            if flavor_rams:
                click.echo(f"\n内存(GB): {', '.join(flavor_rams)}")
            
            gpu_configs = return_obj.get('gpuConfigScope', [])
            if gpu_configs:
                click.echo(f"\nGPU配置: {', '.join(gpu_configs)}")
            
            local_disk_configs = return_obj.get('localDiskConfigScope', [])
            if local_disk_configs:
                click.echo(f"\n本地盘配置: {', '.join(local_disk_configs)}")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_cold_resize_flavors(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询云主机支持的冷变配规格信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_cold_resize_flavors(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        flavor_list = return_obj.get('flavorList', [])
        
        if output and output in ['json', 'yaml']:
            format_output(flavor_list, output)
        else:
            click.echo(f"云主机支持的冷变配规格列表 (共 {len(flavor_list)} 个)")
            click.echo("=" * 120)
            
            if flavor_list:
                for idx, flavor in enumerate(flavor_list, 1):
                    click.echo(f"\n规格 {idx}:")
                    click.echo(f"  规格名称: {flavor.get('flavorName', 'N/A')}")
                    click.echo(f"  规格ID: {flavor.get('flavorID', 'N/A')}")
                    click.echo(f"  vCPU: {flavor.get('flavorCPU', 'N/A')} 核")
                    click.echo(f"  内存: {flavor.get('flavorRAM', 'N/A')} GB")
                    click.echo(f"  规格系列: {flavor.get('flavorSeriesName', flavor.get('flavorSeries', 'N/A'))}")
                    click.echo(f"  规格类型: {flavor.get('flavorType', 'N/A')}")
                    click.echo(f"  CPU架构: {flavor.get('cpuInfo', 'N/A')}")
                    click.echo(f"  基准带宽: {flavor.get('baseBandwidth', 'N/A')} Gbps")
                    click.echo(f"  带宽: {flavor.get('bandwidth', 'N/A')} Gbps")
                    click.echo(f"  网卡多队列: {flavor.get('nicMultiQueue', 'N/A')}")
                    
                    if flavor.get('gpuType'):
                        click.echo(f"  GPU类型: {flavor.get('gpuType', 'N/A')}")
                        click.echo(f"  GPU厂商: {flavor.get('gpuVendor', 'N/A')}")
                        click.echo(f"  GPU数量: {flavor.get('gpuCount', 'N/A')}")
                        click.echo(f"  显存大小: {flavor.get('videoMemSize', 'N/A')} GB")
                    
                    available = flavor.get('available', False)
                    click.echo(f"  可用状态: {'✓ 可用' if available else '✗ 售罄'}")
                    
                    az_list = flavor.get('azList', [])
                    if az_list:
                        click.echo(f"  可用区: {', '.join(az_list)}")
            else:
                click.echo("\n无冷变配规格数据")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def query_hot_resize_flavors(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询云主机支持的热变配规格信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.query_hot_resize_flavors(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        flavor_list = return_obj.get('flavorList', [])
        
        if output and output in ['json', 'yaml']:
            format_output(flavor_list, output)
        else:
            click.echo(f"云主机支持的热变配规格列表 (共 {len(flavor_list)} 个)")
            click.echo("=" * 120)
            
            if flavor_list:
                for idx, flavor in enumerate(flavor_list, 1):
                    click.echo(f"\n规格 {idx}:")
                    click.echo(f"  规格名称: {flavor.get('flavorName', 'N/A')}")
                    click.echo(f"  规格ID: {flavor.get('flavorID', 'N/A')}")
                    click.echo(f"  vCPU: {flavor.get('flavorCPU', 'N/A')} 核")
                    click.echo(f"  内存: {flavor.get('flavorRAM', 'N/A')} GB")
                    click.echo(f"  规格系列: {flavor.get('flavorSeries', 'N/A')}")
                    click.echo(f"  规格类型: {flavor.get('flavorType', 'N/A')}")
                    click.echo(f"  CPU架构: {flavor.get('cpuInfo', 'N/A')}")
                    click.echo(f"  基准带宽: {flavor.get('baseBandwidth', 'N/A')} Gbps")
                    click.echo(f"  带宽: {flavor.get('bandwidth', 'N/A')} Gbps")
                    click.echo(f"  网卡多队列: {flavor.get('nicMultiQueue', 'N/A')}")
            else:
                click.echo("\n无热变配规格数据（可能该云主机不支持热变配）")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='云主机ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_vnc_details(ctx, region_id: str, instance_id: str, output: Optional[str]):
    """查询云主机的WEB管理终端地址"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_vnc_details(region_id=region_id, instance_id=instance_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        
        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            token_url = return_obj.get('token', 'N/A')
            
            click.echo(f"云主机WEB管理终端信息")
            click.echo("=" * 120)
            click.echo(f"  云主机ID: {instance_id}")
            click.echo(f"  VNC访问地址: {token_url}")
            
            if token_url.startswith('wss://'):
                click.echo(f"\n  说明: 这是多可用区WebSocket VNC地址")
                click.echo(f"  使用方法: 可使用noVNC等客户端访问")
            elif token_url.startswith('http'):
                click.echo(f"\n  说明: 这是单可用区HTTP VNC地址")
                click.echo(f"  使用方法: 可直接在浏览器中打开")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--project-id', help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
@handle_error
def get_instance_statistics(ctx, region_id: str, project_id: Optional[str], output: Optional[str]):
    """查询用户云主机统计信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_instance_statistics(region_id=region_id, project_id=project_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        stats = return_obj.get('instanceStatistics', {})
        
        if output and output in ['json', 'yaml']:
            format_output(stats, output)
        else:
            click.echo(f"云主机统计信息")
            click.echo("=" * 80)
            click.echo(f"  云主机总数: {stats.get('totalCount', 0)}")
            click.echo(f"  运行中: {stats.get('RunningCount', 0)}")
            click.echo(f"  已关机: {stats.get('shutdownCount', 0)}")
            click.echo(f"  过期总数: {stats.get('expireCount', 0)}")
            click.echo(f"    - 过期运行中: {stats.get('expireRunningCount', 0)}")
            click.echo(f"    - 过期已关机: {stats.get('expireShutdownCount', 0)}")
            click.echo(f"\n  资源统计:")
            click.echo(f"  CPU总数: {stats.get('cpuCount', 0)} 核")
            click.echo(f"  内存总量: {stats.get('memoryCount', 0)} GB")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()
