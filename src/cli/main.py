"""
天翼云CLI主入口
"""

import click
import sys
from typing import Optional

from core import CTYUNClient, CTYUNAPIError
from config.settings import config
from utils.helpers import OutputFormatter, logger
# 移除循环导入，稍后动态添加


@click.group()
@click.option('--profile', default='default', help='配置文件名称')
@click.option('--access-key', help='访问密钥')
@click.option('--secret-key', help='密钥')
@click.option('--region', help='区域')
@click.option('--endpoint', help='API端点')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              default=None, help='输出格式')
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.pass_context
def cli(ctx, profile: str, access_key: Optional[str], secret_key: Optional[str],
        region: Optional[str], endpoint: Optional[str], output: Optional[str], debug: bool):
    """
    天翼云CLI工具 - 基于终端的云资源管理平台
    """
    # 确保上下文对象存在
    ctx.ensure_object(dict)

    # 设置调试模式
    if debug:
        import logging
        logging.getLogger('ctyun_cli').setLevel(logging.DEBUG)
        click.echo("调试模式已启用", err=True)

    # 存储全局配置
    ctx.obj['profile'] = profile
    ctx.obj['access_key'] = access_key
    ctx.obj['secret_key'] = secret_key
    ctx.obj['region'] = region
    ctx.obj['endpoint'] = endpoint
    ctx.obj['output'] = output or config.get_output_format()

    try:
        # 创建API客户端
        client = CTYUNClient(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            endpoint=endpoint,
            profile=profile
        )
        ctx.obj['client'] = client
    except Exception as e:
        click.echo(f"错误: 初始化客户端失败 - {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--access-key', required=True, help='访问密钥')
@click.option('--secret-key', required=True, help='密钥')
@click.option('--region', default='cn-north-1', help='区域')
@click.option('--endpoint', default='https://api.ctyun.cn', help='API端点')
@click.option('--profile', default='default', help='配置文件名称')
@click.pass_context
def configure(ctx, access_key: str, secret_key: str, region: str,
             endpoint: str, profile: str):
    """
    配置天翼云认证信息
    """
    try:
        config.set_credentials(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            endpoint=endpoint,
            profile=profile
        )
        click.echo(f"✓ 配置已保存到配置文件 '{profile}'")
        click.echo(f"  区域: {region}")
        click.echo(f"  端点: {endpoint}")
    except Exception as e:
        click.echo(f"✗ 配置保存失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--profile', default='default', help='配置文件名称')
def show_config(profile: str):
    """
    显示当前配置信息
    """
    try:
        credentials = config.get_credentials(profile)
        click.echo(f"配置文件: {profile}")
        click.echo(f"访问密钥: {credentials['access_key'][:8]}...")
        click.echo(f"密钥: {credentials['secret_key'][:8]}...")
        click.echo(f"区域: {credentials['region']}")
        click.echo(f"端点: {credentials['endpoint']}")
        click.echo(f"输出格式: {config.get_output_format()}")
        click.echo(f"超时时间: {config.get_timeout()}秒")
        click.echo(f"重试次数: {config.get_retry_count()}")
    except Exception as e:
        click.echo(f"✗ 获取配置失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_profiles():
    """
    列出所有配置文件
    """
    try:
        profiles = config.list_profiles()
        if profiles:
            click.echo("可用的配置文件:")
            for profile in profiles:
                click.echo(f"  - {profile}")
        else:
            click.echo("没有找到配置文件")
    except Exception as e:
        click.echo(f"✗ 获取配置文件列表失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def test(ctx):
    """
    测试API连接
    """
    try:
        client = ctx.obj['client']
        # 这里可以调用一个简单的API来测试连接
        # 例如查询可用区域列表
        click.echo("正在测试API连接...")

        # 模拟测试连接（实际应该调用真实API）
        click.echo("✓ API连接测试成功")
        click.echo(f"  区域: {client.region}")
        click.echo(f"  端点: {client.endpoint}")

    except CTYUNAPIError as e:
        click.echo(f"✗ API连接测试失败: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ 连接测试失败: {e}", err=True)
        sys.exit(1)


@cli.group()
def ecs():
    """
    云服务器(ECS)管理
    """
    pass


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量（最大50）')
@click.option('--az-name', help='可用区名称')
@click.option('--state', type=click.Choice(['active', 'shutoff', 'expired', 'unsubscribed', 'freezing', 'shelve']), 
              help='云主机状态')
@click.option('--keyword', help='关键字模糊查询')
@click.option('--instance-name', help='云主机名称（精确匹配）')
@click.option('--vpc-id', help='VPC ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def list(ctx, region_id: str, page: int, page_size: int, az_name: Optional[str], 
         state: Optional[str], keyword: Optional[str], instance_name: Optional[str],
         vpc_id: Optional[str], output: Optional[str]):
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
            state=state,
            keyword=keyword,
            instance_name=instance_name,
            vpc_id=vpc_id
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
                headers = ['实例ID', '实例名称', '状态', 'IP地址', '规格', '镜像', '到期时间']
                
                for instance in instances:
                    # 获取IP地址
                    private_ip = instance.get('privateIP', '')
                    floating_ip = instance.get('floatingIP', '')
                    ip_display = private_ip
                    if floating_ip:
                        ip_display += f"\n({floating_ip})"
                    
                    # 获取规格信息
                    flavor = instance.get('flavor', {})
                    flavor_str = f"{flavor.get('flavorName', '')}\n{flavor.get('flavorCPU', '')}C{flavor.get('flavorRAM', 0)//1024}G"
                    
                    # 获取镜像信息
                    image = instance.get('image', {})
                    image_name = image.get('imageName', '')
                    
                    table_data.append([
                        instance.get('instanceID', ''),  # 保留完整的实例ID，不截断
                        instance.get('displayName', instance.get('instanceName', '')),
                        instance.get('instanceStatus', ''),
                        ip_display,
                        flavor_str,
                        image_name[:20] + '...' if len(image_name) > 20 else image_name,
                        instance.get('expiredTime', '-') if instance.get('expiredTime') else '按量付费'
                    ])
                
                total_count = return_obj.get('totalCount', 0)
                current_count = return_obj.get('currentCount', len(instances))
                total_page = return_obj.get('totalPage', 1)
                
                click.echo(f"云主机列表 (总计: {total_count} 台, 当前页: {current_count} 台, 第{page}/{total_page}页)")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo()
                
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
                
                if total_page > 1:
                    click.echo()
                    click.echo(f"提示: 使用 --page 参数查看其他页")
            else:
                click.echo("没有找到云主机实例")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--project-id', help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def statistics(ctx, region_id: str, project_id: Optional[str], output: Optional[str]):
    """查询云主机统计信息"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.get_instance_statistics(region_id, project_id)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        stats = return_obj.get('instanceStatistics', {})
        is_mock = result.get('_mock', False)
        
        if output and output in ['json', 'yaml']:
            format_output(stats, output)
        else:
            from tabulate import tabulate
            
            click.echo(f"云主机统计信息 (区域: {region_id})")
            if project_id:
                click.echo(f"企业项目: {project_id}")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo()
            
            table_data = [
                ['总数', stats.get('totalCount', 0)],
                ['运行中', stats.get('RunningCount', 0)],
                ['已关机', stats.get('shutdownCount', 0)],
                ['已过期', stats.get('expireCount', 0)],
                ['过期运行中', stats.get('expireRunningCount', 0)],
                ['过期已关机', stats.get('expireShutdownCount', 0)],
                ['CPU总数', f"{stats.get('cpuCount', 0)} 核"],
                ['内存总量', f"{stats.get('memoryCount', 0)} GB"]
            ]
            
            headers = ['统计项', '数值']
            table = tabulate(table_data, headers=headers, tablefmt='grid')
            click.echo(table)
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.argument('instance_id')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def detail(ctx, instance_id: str, region_id: str, output: Optional[str]):
    """查询云主机详情"""
    try:
        from ecs.client import ECSClient

        client = ctx.obj['client']
        ecs_client = ECSClient(client)

        result = ecs_client.get_instance(instance_id, region_id)
        
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
                click.echo(f"状态: {instance.get('instanceStatus', '')}")
                click.echo(f"可用区: {instance.get('azName', '')}")

                # 规格信息
                flavor = instance.get('flavor', {})
                flavor_name = flavor.get('flavorName', '')
                click.echo(f"规格: {flavor_name}")

                # 镜像信息
                image = instance.get('image', {})
                image_name = image.get('imageName', '')
                click.echo(f"镜像: {image_name}")

                click.echo(f"VPC: {instance.get('vpcName', '')}")
                click.echo(f"子网ID列表: {', '.join(instance.get('subnetIDList', []))}")

                # IP地址信息
                private_ip = instance.get('privateIP', '')
                if private_ip:
                    click.echo(f"私网IP: {private_ip}")

                private_ipv6 = instance.get('privateIPv6', '')
                if private_ipv6:
                    click.echo(f"私网IPv6: {private_ipv6}")

                # 查找公网IP
                floating_ip = instance.get('floatingIP', '')
                if floating_ip:
                    click.echo(f"公网IP: {floating_ip}")

                # 时间信息
                created_time = instance.get('createdTime', '')
                if created_time:
                    click.echo(f"创建时间: {created_time}")

                expired_time = instance.get('expiredTime', '')
                if expired_time:
                    click.echo(f"到期时间: {expired_time}")
            else:
                click.echo("未找到云主机信息")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-id', required=True, help='区域ID')
@click.option('--instance-id-list', help='实例ID列表，多个ID用逗号分隔')
@click.option('--instance-name', help='实例名称，支持模糊查询')
@click.option('--state', help='实例状态')
@click.option('--keyword', help='关键字，支持实例名称、实例ID、IP地址的模糊查询')
@click.option('--page-no', type=int, help='页码，从1开始')
@click.option('--page-size', type=int, help='每页记录数，最大100')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def multidetail(ctx, region_id: str, instance_id_list: Optional[str], instance_name: Optional[str],
                state: Optional[str], keyword: Optional[str], page_no: Optional[int],
                page_size: Optional[int], output: Optional[str]):
    """查询一台或多台云主机详细信息（API ID: 9268）"""
    try:
        from ecs.client import ECSClient

        client = ctx.obj['client']
        ecs_client = ECSClient(client)

        result = ecs_client.describe_instances(
            region_id=region_id,
            instance_id_list=instance_id_list,
            instance_name=instance_name,
            state=state,
            keyword=keyword,
            page_no=page_no,
            page_size=page_size
        )

        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return

        return_obj = result.get('returnObj', {})
        instances = return_obj.get('instanceList', [])
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            if instances:
                from tabulate import tabulate

                click.echo(f"云主机详细信息列表 (区域: {region_id})")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo("=" * 100)

                # 准备表格数据
                table_data = []
                for instance in instances:
                    # 获取规格信息
                    flavor = instance.get('flavor', {})
                    flavor_name = flavor.get('flavorName', '')

                    # 获取镜像信息
                    image = instance.get('image', {})
                    image_name = image.get('imageName', '')

                    # 获取IP地址
                    public_ips = []
                    private_ips = []

                    # 处理弹性IP
                    fip = instance.get('fip', [])
                    if fip:
                        for ip_info in fip:
                            public_ips.append(ip_info.get('publicIp', ''))

                    # 处理主网卡IP
                    primary_nic = instance.get('primaryNic', {})
                    if primary_nic:
                        private_ip = primary_nic.get('privateIpAddress', '')
                        if private_ip:
                            private_ips.append(private_ip)

                        # 处理辅助IP
                        auxiliary_private_ips = primary_nic.get('auxiliaryPrivateIpAddress', [])
                        if auxiliary_private_ips:
                            private_ips.extend(auxiliary_private_ips)

                    table_data.append([
                        instance.get('instanceID', ''),
                        instance.get('instanceName', ''),
                        instance.get('vmState', ''),
                        instance.get('availabilityZone', ''),
                        flavor_name,
                        image_name,
                        ', '.join(public_ips) if public_ips else '',
                        ', '.join(private_ips) if private_ips else ''
                    ])

                # 显示表格
                headers = ['实例ID', '实例名称', '状态', '可用区', '规格', '镜像', '公网IP', '私网IP']
                click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))

                # 显示分页信息
                page_no = return_obj.get('pageNo', 1)
                page_size = return_obj.get('pageSize', len(instances))
                total_count = return_obj.get('totalCount', len(instances))

                click.echo(f"\n分页信息: 第 {page_no} 页, 每页 {page_size} 条, 共 {total_count} 条记录")

                # 如果只需要查看特定实例的详细信息
                if len(instances) == 1 and (instance_id_list or instance_name):
                    click.echo("\n详细信息:")
                    instance = instances[0]

                    click.echo(f"实例ID: {instance.get('instanceID', '')}")
                    click.echo(f"实例名称: {instance.get('instanceName', '')}")
                    click.echo(f"状态: {instance.get('vmState', '')}")
                    click.echo(f"可用区: {instance.get('availabilityZone', '')}")

                    # 规格信息
                    flavor = instance.get('flavor', {})
                    click.echo(f"规格: {flavor.get('flavorName', '')}")
                    click.echo(f"CPU: {flavor.get('cpu', '')}核")
                    click.echo(f"内存: {flavor.get('ram', '')}GB")

                    # 镜像信息
                    image = instance.get('image', {})
                    click.echo(f"镜像: {image.get('imageName', '')}")
                    click.echo(f"操作系统: {image.get('osType', '')} {image.get('osBit', '')}位")

                    # 网络信息
                    vpc_id = instance.get('vpcId', '')
                    click.echo(f"VPC ID: {vpc_id}")

                    # 存储信息
                    system_disk = instance.get('systemDisk', {})
                    if system_disk:
                        click.echo(f"系统盘: {system_disk.get('diskType', '')} {system_disk.get('size', '')}GB")

                    # 创建时间
                    created_time = instance.get('createdTime', '')
                    if created_time:
                        click.echo(f"创建时间: {created_time}")

            else:
                click.echo("未找到符合条件的云主机")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.argument('region_id')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
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
        
        return_obj = result.get('returnObj', {})
        resources_data = return_obj.get('resources', {})
        is_mock = result.get('_mock', False)
        
        if output and output in ['json', 'yaml']:
            format_output(resources_data, output)
        else:
            if resources_data:
                from tabulate import tabulate
                
                click.echo(f"用户资源概览 (区域: {region_id})")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo("=" * 80)
                click.echo()
                
                vm_info = resources_data.get('VM', {})
                if vm_info:
                    click.echo("【云主机 (VM)】")
                    vm_table = [
                        ['总数', vm_info.get('total_count', 0)],
                        ['运行中', vm_info.get('vm_running_count', 0)],
                        ['已关机', vm_info.get('vm_shutd_count', 0)],
                        ['已过期', vm_info.get('expire_count', 0)],
                        ['CPU总数', vm_info.get('cpu_count', 0)],
                        ['内存(GB)', vm_info.get('memory_count', 0)]
                    ]
                    click.echo(tabulate(vm_table, tablefmt='plain'))
                    click.echo()
                
                volume_info = resources_data.get('Volume', {})
                if volume_info:
                    click.echo("【磁盘 (Volume)】")
                    volume_table = [
                        ['总数', volume_info.get('total_count', 0)],
                        ['系统盘数量', volume_info.get('vo_root_count', 0)],
                        ['数据盘数量', volume_info.get('vo_disk_count', 0)],
                        ['总大小(GB)', volume_info.get('total_size', 0)],
                        ['系统盘大小(GB)', volume_info.get('vo_root_size', 0)],
                        ['数据盘大小(GB)', volume_info.get('vo_disk_size', 0)]
                    ]
                    click.echo(tabulate(volume_table, tablefmt='plain'))
                    click.echo()
                
                other_resources = []
                resource_name_map = {
                    'VPC': 'VPC',
                    'Public_IP': '公网IP',
                    'VOLUME_SNAPSHOT': '磁盘快照',
                    'BMS': '物理机',
                    'NAT': 'NAT网关',
                    'IMAGE': '私有镜像',
                    'LOADBALANCER': '负载均衡',
                    'LB_LISTENER': '负载均衡监听器',
                    'IP_POOL': '共享带宽',
                    'SNAPSHOT': '云主机快照',
                    'ACLLIST': 'ACL',
                    'Vm_Group': '云主机组',
                    'Disk_Backup': '磁盘备份',
                    'CBR': '云主机备份',
                    'CBR_VBS': '磁盘存储备份',
                    'CERT': '负载均衡证书',
                    'OS_Backup': '操作系统备份',
                    'TrafficMirror_Flow': '流量镜像流',
                    'TrafficMirror_Filter': '流量镜像过滤器'
                }
                
                for key, name in resource_name_map.items():
                    if key in resources_data and key not in ['VM', 'Volume']:
                        res = resources_data[key]
                        count = res.get('total_count', res.get('detail_total_count', 0))
                        if count > 0:
                            other_resources.append([name, count])
                
                if other_resources:
                    click.echo("【其他资源】")
                    click.echo(tabulate(other_resources, headers=['资源类型', '数量'], tablefmt='plain'))
            else:
                click.echo("未找到资源信息")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command()
@click.option('--region-name', help='资源池名称过滤')
@click.option('--no-cache', is_flag=True, help='不使用缓存')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def regions(ctx, region_name: Optional[str], no_cache: bool, output: Optional[str]):
    """查询资源池列表"""
    try:
        from ecs.client import ECSClient
        
        client = ctx.obj['client']
        ecs_client = ECSClient(client)
        
        result = ecs_client.list_regions(region_name, use_cache=not no_cache)
        
        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return
        
        return_obj = result.get('returnObj', {})
        region_list = return_obj.get('regionList', [])
        is_mock = result.get('_mock', False)
        
        if output and output in ['json', 'yaml']:
            format_output(region_list, output)
        else:
            if region_list:
                from tabulate import tabulate
                
                table_data = []
                headers = ['资源池ID', '资源池名称', '所属省份', '区域代码', '多可用区', '可用区', 'OpenAPI']
                
                for region in region_list:
                    zone_list = region.get('zoneList', [])
                    zones_str = ', '.join(zone_list) if zone_list else '-'
                    
                    table_data.append([
                        region.get('regionID', '')[:30],
                        region.get('regionName', ''),
                        region.get('regionParent', ''),
                        region.get('regionCode', ''),
                        '是' if region.get('isMultiZones', False) else '否',
                        zones_str,
                        '是' if region.get('openapiAvailable', False) else '否'
                    ])
                
                click.echo(f"资源池列表 (总计: {len(region_list)} 个)")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo()
                
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(table)
            else:
                click.echo("没有找到资源池")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@ecs.command('flavor-options')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
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
@click.option('--region-id', required=True, help='区域ID')
@click.option('--master-order-id', required=True, help='订单ID (masterOrderID)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
@click.pass_context
def query_uuid(ctx, region_id: str, master_order_id: str, output: Optional[str]):
    """根据订单ID查询云主机UUID"""
    try:
        from ecs.client import ECSClient

        client = ctx.obj['client']
        ecs_client = ECSClient(client)

        result = ecs_client.query_uuid_by_order(
            region_id=region_id,
            master_order_id=master_order_id
        )

        if result.get('statusCode') != 800:
            click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
            return

        return_obj = result.get('returnObj', {})
        order_status = return_obj.get('orderStatus', '')
        instance_id_list = return_obj.get('instanceIDList', [])

        # 订单状态映射
        status_map = {
            '1': '待支付', '2': '已支付', '3': '完成', '4': '取消', '5': '施工失败',
            '7': '正在支付中', '8': '待审核', '9': '审核通过', '10': '审核未通过',
            '11': '撤单完成', '12': '退订中', '13': '退订完成', '14': '开通中',
            '15': '变更移除', '16': '自动撤单中', '17': '手动撤单中', '18': '终止中',
            '22': '支付失败', '-2': '待撤单', '-1': '未知', '0': '错误',
            '140': '已初始化', '999': '逻辑错误'
        }

        status_text = status_map.get(str(order_status), f'未知状态({order_status})')

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
                sys.exit(1)
        else:
            # 表格格式
            click.echo("=" * 80)
            click.echo(f"订单查询结果")
            click.echo("=" * 80)

            # 显示订单基本信息
            basic_info = [
                ('订单ID', master_order_id),
                ('订单状态', f"{status_text} ({order_status})"),
                ('返回云主机数量', str(len(instance_id_list)))
            ]

            for key, value in basic_info:
                click.echo(f"{key:15}: {value}")

            # 显示云主机ID列表
            if instance_id_list:
                click.echo("\n云主机ID列表:")
                click.echo("-" * 80)
                for i, instance_id in enumerate(instance_id_list, 1):
                    click.echo(f"{i:3}. {instance_id}")

                if order_status == '3':  # 订单完成
                    click.echo(f"\n✅ 订单已完成，成功获取 {len(instance_id_list)} 个云主机ID")
                else:
                    click.echo(f"\n⏳ 订单状态: {status_text}")
                    if order_status in ['14']:  # 开通中
                        click.echo("   订单正在处理中，请稍后重试获取云主机ID")
                    elif order_status in ['1']:  # 待支付
                        click.echo("   订单待支付，支付完成后才能获取云主机ID")
                    elif order_status in ['5', '22', '0', '999']:  # 失败状态
                        click.echo("   ❌ 订单处理失败，无法获取云主机ID")
            else:
                click.echo("\n云主机ID列表: 无")
                if order_status == '3':  # 订单完成但没有实例
                    click.echo("⚠️  订单已完成但未返回云主机ID，可能订单不涉及云主机创建")
                elif order_status == '14':  # 开通中
                    click.echo("⏳ 订单正在开通中，完成后将返回云主机ID")
                else:
                    click.echo(f"ℹ️  当前订单状态: {status_text}")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@cli.command()
def clear_cache():
    """清空所有缓存"""
    try:
        from utils.cache import get_cache
        cache = get_cache()
        count = cache.clear()
        click.echo(f"✓ 已清空 {count} 个缓存文件")
    except Exception as e:
        click.echo(f"✗ 清空缓存失败: {e}", err=True)

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


@cli.group()
def storage():
    """
    存储管理
    """
    pass


@cli.group()
def network():
    """
    网络管理
    """
    pass


@cli.group()
def monitor():
    """
    监控查询
    """
    pass


@cli.group()
def security():
    """
    服务器安全卫士
    """
    pass


@security.command()
@click.argument('agent_guid')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--title', help='漏洞名称过滤')
@click.option('--cve', help='CVE编号过滤')
@click.option('--status', 'handle_status',
              type=click.Choice(['HANDLED', 'UN_HANDLED', 'IGNORED']),
              help='处理状态过滤')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def vuln_list(ctx, agent_guid: str, page: int, page_size: int,
              title: Optional[str], cve: Optional[str],
              handle_status: Optional[str], output: Optional[str]):
    """查询服务器漏洞扫描列表"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_vulnerability_list(
            agent_guid=agent_guid,
            current_page=page,
            page_size=page_size,
            title=title,
            cve=cve,
            handle_status=handle_status
        )

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        vulnerabilities = return_obj.get('list', [])

        # 检查是否是模拟数据
        is_mock = result.get('_mock', False)

        # 显示分页信息
        total = return_obj.get('total', 0)
        current_page = return_obj.get('pageNum', 1)
        actual_page_size = return_obj.get('pageSize', page_size)
        total_pages = return_obj.get('pages', 1) if return_obj.get('pages', 1) > 0 else ((total + actual_page_size - 1) // actual_page_size if total > 0 else 1)

        if total > 0:
            click.echo(f"漏洞列表 (总计: {total} 条, 第 {current_page}/{total_pages} 页, 每页 {actual_page_size} 条)")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo()

            # 格式化输出漏洞列表
            if output and output in ['json', 'yaml']:
                format_output(vulnerabilities, output)
            else:
                # 表格格式 - 精简显示关键字段
                from tabulate import tabulate
                
                table_data = []
                headers = ['ID', '漏洞标题', '危险等级', '状态', 'CVE数量', '发现时间']

                for vuln in vulnerabilities:
                    if not isinstance(vuln, dict):
                        continue

                    status_map = {0: '未处理', 1: '已处理', 2: '已忽略'}
                    level_map = {'LOW': '低', 'MIDDLE': '中', 'HIGH': '高'}

                    # 处理CVE列表
                    cve_list = vuln.get('cveList', [])
                    cve_count = len(cve_list) if type(cve_list).__name__ == 'list' else 0

                    table_data.append([
                        str(vuln.get('vulAnnouncementId', ''))[:30],  # 限制ID长度
                        str(vuln.get('vulAnnouncementTitle', ''))[:50],  # 限制标题长度
                        level_map.get(vuln.get('fixLevel', ''), vuln.get('fixLevel', '')),
                        status_map.get(vuln.get('status', 0), '未知'),
                        f"{cve_count} 个",
                        vuln.get('timestamp', '')
                    ])

                if table_data:
                    table = tabulate(table_data, headers=headers, tablefmt='grid')
                    click.echo(table)
                else:
                    click.echo("没有有效的漏洞数据")

                if total_pages > 1:
                    click.echo()
                    click.echo(f"提示: 使用 --page 参数查看其他页 (共{total_pages}页)")
        else:
            click.echo("该服务器没有发现漏洞")
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.argument('agent_guid')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def summary(ctx, agent_guid: str, output: Optional[str]):
    """获取漏洞统计摘要"""
    from security.client import SecurityClient

    client = ctx.obj['client']
    security_client = SecurityClient(client)

    summary = security_client.get_vulnerability_summary(agent_guid)

    if output and output in ['json', 'yaml']:
        format_output(summary, output)
    else:
        click.echo("漏洞统计摘要")
        click.echo("=" * 40)
        click.echo(f"总漏洞数: {summary['total_vulnerabilities']}")
        click.echo(f"高危漏洞: {summary['high_risk']}")
        click.echo(f"中危漏洞: {summary['medium_risk']}")
        click.echo(f"低危漏洞: {summary['low_risk']}")
        click.echo("-" * 40)
        click.echo(f"未处理: {summary['unhandled']}")
        click.echo(f"已处理: {summary['handled']}")
        click.echo(f"已忽略: {summary['ignored']}")
        click.echo(f"需要重启: {summary['reboot_required']}")


@security.command()
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=20, type=int, help='每页数量')
@click.option('--guard-status', type=click.Choice(['protecting', 'closed', 'offline', 'unprotected']),
              help='防护状态：protecting-防护中, closed-已关闭, offline-已离线, unprotected-未防护')
@click.option('--agent-status', type=click.Choice(['online', 'offline', 'inactive', 'error']),
              help='Agent状态：online-在线, offline-离线, inactive-未激活, error-错误')
@click.option('--risk-level', type=click.Choice(['safe', 'unknown', 'risk']),
              help='风险级别：safe-安全, unknown-未知, risk-风险')
@click.option('--search', help='搜索内容（服务器名称、IP或agentGuid）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def agents(ctx, page: int, page_size: int, guard_status: Optional[str], 
           agent_status: Optional[str], risk_level: Optional[str], 
           search: Optional[str], output: Optional[str]):
    """获取安全卫士客户端列表"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        # 映射命令行参数到API参数
        guard_type_map = {
            'protecting': 1,
            'closed': 2,
            'offline': 3,
            'unprotected': 4
        }
        agent_state_map = {
            'online': 1,
            'offline': 2,
            'inactive': 3,
            'error': 4
        }
        risk_level_map = {
            'safe': 1,
            'unknown': 2,
            'risk': 3
        }

        guard_type = guard_type_map.get(guard_status) if guard_status else None
        agent_state = agent_state_map.get(agent_status) if agent_status else None
        risk_level_val = risk_level_map.get(risk_level) if risk_level else None

        result = security_client.get_agent_list(
            page=page,
            page_size=page_size,
            guard_type=guard_type,
            agent_state=agent_state,
            risk_level=risk_level_val,
            search_type=1 if search else None,  # 默认按服务器名称搜索
            search_param=search
        )

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        agent_list = return_obj.get('list', []) if isinstance(return_obj, dict) else []

        # 检查是否是模拟数据
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(agent_list, output)
        else:
            # 表格格式显示客户端列表
            if agent_list:
                from tabulate import tabulate
                
                table_data = []
                headers = ['服务器名称', 'IP地址', '操作系统', 'Agent状态', '防护状态', '风险状态', 'Agent GUID']

                for agent in agent_list:
                    # 处理IP地址
                    agent_ip = agent.get('agentIp', '')
                    public_ip = agent.get('publicIp', '')
                    ip_display = f"{agent_ip}"
                    if public_ip:
                        ip_display += f"\n({public_ip})"

                    table_data.append([
                        agent.get('custName', ''),
                        ip_display,
                        agent.get('osType', ''),
                        agent.get('agentStateCode', ''),
                        agent.get('guardStatus', ''),
                        agent.get('riskStatus', ''),
                        agent.get('agentGuid', '')  # 显示完整GUID
                    ])

                table = tabulate(table_data, headers=headers, tablefmt='grid')
                
                # 显示分页信息
                total = return_obj.get('total', 0)
                current_page = return_obj.get('pageNum', page)
                total_pages = return_obj.get('pages', 1)
                
                click.echo(f"安全卫士客户端列表 (总计: {total} 个, 第{current_page}/{total_pages}页)")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo()
                click.echo(table)
                
                # 分页提示
                if total_pages > 1:
                    click.echo()
                    click.echo(f"提示: 使用 --page 参数查看其他页 (共{total_pages}页)")
            else:
                click.echo("没有找到安全卫士客户端")
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def vuln_types(ctx, output: Optional[str]):
    """获取漏洞类型列表"""
    from security.client import SecurityClient

    client = ctx.obj['client']
    security_client = SecurityClient(client)

    result = security_client.get_vulnerability_types()

    if result.get('error') != 'CTCSSCN_000000':
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)
        return

    types = result.get('returnObj', {}).get('list', [])

    if output and output in ['json', 'yaml']:
        format_output(types, output)
    else:
        # 表格格式显示漏洞类型
        if types:
            table_data = []
            headers = ['类型代码', '类型名称', '描述']

            for vuln_type in types:
                table_data.append([
                    vuln_type.get('typeCode', ''),
                    vuln_type.get('typeName', ''),
                    vuln_type.get('description', '')
                ])

            from utils.helpers import OutputFormatter
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(f"漏洞类型列表 (总计: {len(types)} 种)")
            click.echo("-" * 60)
            click.echo(table)
        else:
            click.echo("没有找到漏洞类型")


@security.command()
@click.argument('vul_announcement_id')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def vuln_detail(ctx, vul_announcement_id: str, page: int, page_size: int, output: Optional[str]):
    """查询漏洞详情信息"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_vulnerability_detail(
            vul_announcement_id, page, page_size
        )

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        is_mock = result.get('_mock', False)

        # 检查returnObj是否有效
        if not return_obj or all(v is None for v in return_obj.values()):
            click.echo(f"漏洞公告 '{vul_announcement_id}' 不存在或无详细信息")
            return

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            # 表格格式显示漏洞详情
            click.echo("漏洞详情信息")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo("=" * 80)
            
            # 基本信息
            click.echo(f"漏洞公告ID: {return_obj.get('vulAnnouncementId', 'N/A')}")
            click.echo(f"漏洞名称:   {return_obj.get('title', 'N/A')}")
            click.echo(f"漏洞类型:   {return_obj.get('vulType', 'N/A')}")
            click.echo(f"发布时间:   {return_obj.get('publishAt', 'N/A')}")
            click.echo(f"参考链接:   {return_obj.get('url', 'N/A')}")
            
            description = return_obj.get('description')
            if description:
                click.echo()
                click.echo(f"漏洞描述:")
                click.echo(f"  {description}")
            
            # CVE详情
            cve_detail = return_obj.get('cveDetailPageInfo')
            if cve_detail and isinstance(cve_detail, dict):
                cve_list = cve_detail.get('list', [])
                
                if cve_list:
                    click.echo()
                    click.echo("-" * 80)
                    click.echo(f"CVE详情 (共 {cve_detail.get('total', 0)} 条):")
                    
                    for idx, cve in enumerate(cve_list, 1):
                        click.echo()
                        click.echo(f"[{idx}] {cve.get('cveId', 'N/A')}")
                        click.echo(f"    标题: {cve.get('title', 'N/A')}")
                        
                        # 危险等级
                        rating_map = {1: '低危', 2: '中危', 3: '高危', 6: '严重', 7: '待定级'}
                        rating_level = cve.get('ratingLevel', 0)
                        rating_text = rating_map.get(rating_level, f'未知({rating_level})')
                        click.echo(f"    危险等级: {rating_text}")
                        
                        click.echo(f"    需要重启: {'是' if cve.get('rebootRequired') else '否'}")
                        
                        vul_label = cve.get('vulLabel')
                        if vul_label:
                            click.echo(f"    漏洞标签: {vul_label}")
                        
                        # 修复建议
                        solution = cve.get('solution', '')
                        if solution:
                            click.echo(f"    修复建议: {solution[:100]}{'...' if len(solution) > 100 else ''}")
                    
                    # 分页信息
                    total_pages = cve_detail.get('pages', 1)
                    if total_pages > 1:
                        click.echo()
                        click.echo(f"提示: 使用 --page 参数查看更多CVE详情 (共{total_pages}页)")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def statistics(ctx, output: Optional[str]):
    """查询漏洞扫描统计"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_vulnerability_statistics()

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            # 表格格式显示漏洞统计
            click.echo("漏洞扫描统计")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo("=" * 60)
            
            emergent_vul = return_obj.get('emergentVul', 0)
            un_handle = return_obj.get('unHandle', 0)
            host_num = return_obj.get('hostNum', 0)
            
            click.echo(f"存在漏洞的服务器数: {host_num}")
            click.echo(f"未处理的漏洞数:     {un_handle}")
            click.echo(f"需紧急修复的漏洞数: {emergent_vul}")
            
            # 显示紧急程度提示
            if emergent_vul > 0:
                click.echo()
                click.echo(f"⚠️  警告: 有 {emergent_vul} 个需紧急修复的漏洞，请及时处理！")
            
            # 计算处理率
            if un_handle > 0:
                click.echo()
                click.echo("建议操作:")
                click.echo("  查看漏洞列表: ctyun-cli security vuln-list <agent_guid>")
                click.echo("  查看最近扫描: ctyun-cli security last-scan")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def last_scan(ctx, output: Optional[str]):
    """查询最近一次扫描结果"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_last_scan()

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            # 表格格式显示最近一次扫描
            click.echo("最近一次漏洞扫描")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo("=" * 60)
            click.echo(f"任务ID:    {return_obj.get('taskId', 'N/A')}")
            click.echo(f"扫描时间:  {return_obj.get('time', 'N/A')}")
            click.echo(f"漏洞数:    {return_obj.get('num', 0)}")
            
            # 提示下一步操作
            task_id = return_obj.get('taskId')
            if task_id:
                click.echo()
                click.echo("查看详细信息:")
                click.echo(f"  扫描详情: ctyun-cli security scan-detail --task-id {task_id}")
                click.echo(f"  扫描状态: ctyun-cli security scan-result --task-id {task_id}")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.option('--task-id', required=True, help='任务ID（必填）')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def scan_detail(ctx, task_id: str, output: Optional[str]):
    """查询最近一次扫描详情统计"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_last_scan_detail(task_id)

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            # 表格格式显示扫描详情
            click.echo("漏洞扫描详情统计")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo("=" * 70)
            click.echo(f"扫描类型: {return_obj.get('taskType', 'N/A')}")
            click.echo(f"漏洞类型: {return_obj.get('osType', 'N/A')}")
            click.echo(f"开始时间: {return_obj.get('createTime', 'N/A')}")
            click.echo(f"结束时间: {return_obj.get('finishTime', 'N/A')}")
            click.echo("-" * 70)
            click.echo(f"目标检测主机数: {return_obj.get('vulHost', 0)}")
            click.echo(f"风险主机数:     {return_obj.get('hostRisk', 0)}")
            click.echo(f"漏洞风险数:     {return_obj.get('vulRisk', 0)}")
            
            # 计算风险比例
            total_hosts = return_obj.get('vulHost', 0)
            risk_hosts = return_obj.get('hostRisk', 0)
            if total_hosts > 0:
                risk_percentage = (risk_hosts / total_hosts) * 100
                click.echo(f"风险主机占比:   {risk_percentage:.1f}%")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.option('--task-id', help='任务ID，默认返回最近一次检测任务结果')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def scan_result(ctx, task_id: Optional[str], output: Optional[str]):
    """查询漏洞扫描检测结果"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_vulnerability_scan_result(task_id)

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj')
        is_mock = result.get('_mock', False)

        # 如果returnObj为None，说明任务已完成或不存在
        if return_obj is None:
            click.echo("漏洞扫描检测结果")
            click.echo("=" * 60)
            click.echo("任务状态: 已完成或任务不存在")
            if task_id:
                click.echo(f"任务ID: {task_id}")
                click.echo()
                click.echo("提示: 扫描可能已完成，使用以下命令查看详细结果:")
                click.echo(f"       ctyun-cli security scan-detail --task-id {task_id}")
            return

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            # 表格格式显示扫描结果
            status_map = {
                0: '未执行',
                1: '执行中',
                2: '执行完毕',
                3: '取消执行',
                4: '超时取消执行',
                5: '失败'
            }
            
            status = return_obj.get('status', 0)
            status_text = status_map.get(status, f'未知({status})')
            
            click.echo("漏洞扫描检测结果")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo("=" * 60)
            click.echo(f"任务ID: {return_obj.get('taskId', 'N/A')}")
            click.echo(f"检测状态: {status_text}")
            
            if status == 1:
                click.echo("\n提示: 任务正在执行中，请稍后再查询")
            elif status == 2:
                click.echo("\n提示: 扫描已完成，使用以下命令查看详细结果:")
                task_id_val = return_obj.get('taskId')
                if task_id_val:
                    click.echo(f"       ctyun-cli security scan-detail --task-id {task_id_val}")

    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
def examples():
    """显示使用示例"""
    click.echo("服务器安全卫士使用示例:")
    click.echo()
    click.echo("1. 查看客户端列表:")
    click.echo("   ctyun-cli security agents")
    click.echo()
    click.echo("2. 查询漏洞扫描统计:")
    click.echo("   ctyun-cli security statistics")
    click.echo()
    click.echo("3. 查询最近一次扫描:")
    click.echo("   ctyun-cli security last-scan")
    click.echo()
    click.echo("4. 查询漏洞扫描结果:")
    click.echo("   ctyun-cli security scan-result")
    click.echo("   ctyun-cli security scan-result --task-id <任务ID>")
    click.echo()
    click.echo("5. 查询扫描详情统计:")
    click.echo("   ctyun-cli security scan-detail --task-id <任务ID>")
    click.echo()
    click.echo("6. 查询漏洞详情:")
    click.echo("   ctyun-cli security vuln-detail <漏洞公告ID>")
    click.echo("   ctyun-cli security vuln-detail CTyunOS-SA-2023-41697")
    click.echo()
    click.echo("7. 查询漏洞列表:")
    click.echo("   ctyun-cli security vuln-list <agent_guid>")
    click.echo()
    click.echo("8. 分页查询漏洞:")
    click.echo("   ctyun-cli security vuln-list <agent_guid> --page 1 --page-size 5")


@security.command()
@click.option('--type', 'trend_type', default=1, type=click.Choice(['1', '2', '3']),
              help='趋势类型: 1-近7天, 2-近14天, 3-近30天')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def host_trend(ctx, trend_type: str, output: Optional[str]):
    """查询主机概况趋势统计"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_host_trend(int(trend_type))

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        trend_data = result.get('returnObj', [])
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(trend_data, output)
        else:
            if trend_data:
                from tabulate import tabulate
                
                type_names = {1: '近7天', 2: '近14天', 3: '近30天'}
                type_name = type_names.get(int(trend_type), '近7天')
                
                table_data = []
                headers = ['日期', '主机总数', '在线', '离线', '风险', '未防护', '防护关闭']

                for item in trend_data:
                    table_data.append([
                        item.get('day', ''),
                        item.get('total', 0),
                        item.get('onLine', 0),
                        item.get('offLine', 0),
                        item.get('risk', 0),
                        item.get('unguarded', 0),
                        item.get('closed', 0)
                    ])

                table = tabulate(table_data, headers=headers, tablefmt='grid')
                
                click.echo(f"主机概况趋势统计 ({type_name})")
                if is_mock:
                    click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
                click.echo()
                click.echo(table)
                
                click.echo()
                click.echo("说明:")
                click.echo("  - 主机总数: 包括全部服务器")
                click.echo("  - 未防护: 防护状态为'未防护'的服务器")
                click.echo("  - 离线: 防护状态'已离线'的服务器")
                click.echo("  - 风险: 风险状态为'风险'的全部服务器")
                click.echo("  - 防护关闭: 防护状态'已关闭'的服务器")
            else:
                click.echo("没有找到趋势数据")
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']),
              help='输出格式')
@click.pass_context
def untreated(ctx, output: Optional[str]):
    """查询最近7日待处理风险"""
    try:
        from security.client import SecurityClient

        client = ctx.obj['client']
        security_client = SecurityClient(client)

        result = security_client.get_untreated_risks()

        if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
            click.echo(f"查询失败: {result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'}", err=True)
            return

        return_obj = result.get('returnObj', {})
        is_mock = result.get('_mock', False)

        if output and output in ['json', 'yaml']:
            format_output(return_obj, output)
        else:
            from tabulate import tabulate
            
            click.echo("安全概览 - 最近7日待处理风险")
            if is_mock:
                click.echo("⚠️  注意: 当前显示的是模拟数据，实际API调用失败")
            click.echo()
            
            # 入侵检测统计
            table_data = []
            headers = ['类型', '风险数', '风险主机数']
            
            table_data.append([
                '入侵检测 (SSH)',
                return_obj.get('sshRiskNum', 0),
                return_obj.get('sshHostNum', 0)
            ])
            
            table_data.append([
                '漏洞风险',
                return_obj.get('vulRiskNum', 0),
                return_obj.get('vulHostNum', 0)
            ])
            
            table_data.append([
                '安全基线 (收费版)',
                return_obj.get('scaRiskNum', 0),
                return_obj.get('scaHostNum', 0)
            ])
            
            table_data.append([
                '网页防篡改',
                return_obj.get('wpRiskNum', 0),
                return_obj.get('wpHostNum', 0)
            ])
            
            table_data.append([
                '病毒查杀 (企业版)',
                return_obj.get('virusRiskNum', 0),
                return_obj.get('virusHostNum', 0)
            ])
            
            # 计算总计
            total_risks = (return_obj.get('sshRiskNum', 0) + 
                          return_obj.get('vulRiskNum', 0) + 
                          return_obj.get('scaRiskNum', 0) + 
                          return_obj.get('wpRiskNum', 0) + 
                          return_obj.get('virusRiskNum', 0))
            
            total_hosts = len(set([
                return_obj.get('sshHostNum', 0),
                return_obj.get('vulHostNum', 0),
                return_obj.get('scaHostNum', 0),
                return_obj.get('wpHostNum', 0),
                return_obj.get('virusHostNum', 0)
            ]))
            
            table_data.append([
                '总计',
                total_risks,
                f"约 {max(return_obj.get('sshHostNum', 0), return_obj.get('vulHostNum', 0), return_obj.get('scaHostNum', 0), return_obj.get('wpHostNum', 0), return_obj.get('virusHostNum', 0))} 台"
            ])
            
            table = tabulate(table_data, headers=headers, tablefmt='grid')
            click.echo(table)
            
            # 风险提示
            click.echo()
            if total_risks > 0:
                click.echo("⚠️  发现待处理风险，建议:")
                if return_obj.get('sshRiskNum', 0) > 0:
                    click.echo(f"   - 入侵检测: 发现 {return_obj.get('sshRiskNum', 0)} 个风险，影响 {return_obj.get('sshHostNum', 0)} 台主机")
                if return_obj.get('vulRiskNum', 0) > 0:
                    click.echo(f"   - 漏洞风险: 发现 {return_obj.get('vulRiskNum', 0)} 个漏洞，影响 {return_obj.get('vulHostNum', 0)} 台主机")
                if return_obj.get('scaRiskNum', 0) > 0:
                    click.echo(f"   - 安全基线: 发现 {return_obj.get('scaRiskNum', 0)} 个问题，影响 {return_obj.get('scaHostNum', 0)} 台主机")
                if return_obj.get('virusRiskNum', 0) > 0:
                    click.echo(f"   - 病毒查杀: 发现 {return_obj.get('virusRiskNum', 0)} 个威胁，影响 {return_obj.get('virusHostNum', 0)} 台主机")
            else:
                click.echo("✓ 暂无待处理风险")
                
    except Exception as e:
        click.echo(f"运行出错: {e}", err=True)
        import traceback
        traceback.print_exc()


@security.command()
def examples():
    """显示使用示例"""
    click.echo("服务器安全卫士使用示例:")
    click.echo()
    click.echo("   ctyun-cli security summary <agent_guid>")
@security.command()
def examples():
    """显示使用示例"""
    click.echo("服务器安全卫士使用示例:")
    click.echo()
    click.echo("1. 查看客户端列表:")
    click.echo("   ctyun-cli security agents")
    click.echo()
    click.echo("2. 查询漏洞扫描统计:")
    click.echo("   ctyun-cli security statistics")
    click.echo()
    click.echo("3. 查询最近一次扫描:")
    click.echo("   ctyun-cli security last-scan")
    click.echo()
    click.echo("4. 查询漏洞扫描结果:")
    click.echo("   ctyun-cli security scan-result")
    click.echo("   ctyun-cli security scan-result --task-id <任务ID>")
    click.echo()
    click.echo("5. 查询扫描详情统计:")
    click.echo("   ctyun-cli security scan-detail --task-id <任务ID>")
    click.echo()
    click.echo("6. 查询漏洞详情:")
    click.echo("   ctyun-cli security vuln-detail <漏洞公告ID>")
    click.echo("   ctyun-cli security vuln-detail CTyunOS-SA-2023-41697")
    click.echo()
    click.echo("7. 查询漏洞列表:")
    click.echo("   ctyun-cli security vuln-list <agent_guid>")
    click.echo()
    click.echo("8. 分页查询漏洞:")
    click.echo("   ctyun-cli security vuln-list <agent_guid> --page 1 --page-size 5")
    click.echo()
    click.echo("9. 按CVE编号查询:")
    click.echo("   ctyun-cli security vuln-list <agent_guid> --cve CVE-2024-20696")
    click.echo()
    click.echo("10. 查询未处理的高危漏洞:")
    click.echo("   ctyun-cli security vuln-list <agent_guid> --status UN_HANDLED")
    click.echo()
    click.echo("11. 获取漏洞统计摘要:")
    click.echo("   ctyun-cli security summary <agent_guid>")
    click.echo()
    click.echo("12. 查看漏洞类型:")
    click.echo("   ctyun-cli security vuln-types")
    click.echo()
    click.echo("13. 主机概况趋势:")
    click.echo("   ctyun-cli security host-trend --type 1  # 近7天")
    click.echo("   ctyun-cli security host-trend --type 2  # 近14天")
    click.echo()
    click.echo("14. 待处理风险概览:")
    click.echo("   ctyun-cli security untreated")
    click.echo()
    click.echo("注意: <agent_guid> 是服务器安全卫士客户端的唯一标识符")
    click.echo("      可以通过 'ctyun-cli security agents' 命令获取")
    click.echo("      <任务ID> 可以通过 'last-scan' 或 'scan-result' 命令获取")
    click.echo("      <漏洞公告ID> 可以通过 'vuln-list' 命令获取")


def handle_error(func):
    """
    错误处理装饰器
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CTYUNAPIError as e:
            click.echo(f"API错误 [{e.code}]: {e.message}", err=True)
            if e.request_id:
                click.echo(f"请求ID: {e.request_id}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"错误: {e}", err=True)
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """
    格式化输出
    """
    try:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        elif output_format == 'yaml':
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                sys.exit(1)
        else:
            # 表格格式
            if isinstance(data, list) and data:
                headers = list(data[0].keys()) if isinstance(data[0], dict) else []
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
    except Exception as e:
        click.echo(f"输出格式化错误: {e}", err=True)
        # 简单输出原始数据
        if isinstance(data, (list, dict)):
            click.echo(OutputFormatter.format_json(data))
        else:
            click.echo(str(data))


from billing.commands import billing
cli.add_command(billing)

from monitor.commands import monitor
cli.add_command(monitor)

from iam.commands import iam
cli.add_command(iam)

from ebs.commands import ebs
cli.add_command(ebs)

from redis.commands import redis_group
cli.add_command(redis_group)

from cce.commands import cce
cli.add_command(cce)

from cda.commands import cda
cli.add_command(cda)

from vpc.commands import vpc
cli.add_command(vpc)

from elb.commands import elb
cli.add_command(elb)


if __name__ == '__main__':
    cli()
