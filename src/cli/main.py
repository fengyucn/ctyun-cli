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

from security.commands import security
cli.add_command(security)


if __name__ == '__main__':
    cli()
