"""物理机(DPS)命令行接口"""

import click
import sys
from typing import Optional
from utils import OutputFormatter


@click.group()
def dps():
    """物理机(DPS)管理"""
    pass


def _output(ctx, result: dict, output: Optional[str]):
    fmt = output or ctx.obj.get('output', 'table')
    if fmt == 'json':
        click.echo(OutputFormatter.format_json(result))
    elif fmt == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
    return fmt


# ==================== 查询操作系统列表 ====================

@dps.command('list-os')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--page-no', type=int, default=None, help='页码，默认1')
@click.option('--page-size', type=int, default=None, help='每页数量，默认50，最大1000')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_os(ctx, region_id: str, az_name: str,
            page_no: Optional[int], page_size: Optional[int], output: Optional[str]):
    """查询操作系统列表"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.list_os(
        region_id=region_id, az_name=az_name, page_no=page_no, page_size=page_size
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    return_obj = result.get('returnObj', {})
    results = return_obj.get('results', [])
    click.echo(f"操作系统列表 (共 {return_obj.get('totalCount', 0)} 个，当前 {return_obj.get('currentCount', 0)} 个)")
    if results:
        table_data = []
        for r in results:
            table_data.append({
                'UUID': r.get('uuid', ''),
                '中文名': r.get('nameZh', ''),
                '平台': r.get('platform', ''),
                '版本': r.get('version', ''),
                '类型': r.get('osType', ''),
                '架构': r.get('architecture', ''),
                '位数': r.get('bits', ''),
                '管理员': r.get('superUser', ''),
            })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 物理机元数据查询 ====================

@dps.command('metadata')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--instance-uuid', required=True, help='实例UUID')
@click.option('--metadata-key', default=None, help='元数据键值，缺省则查询全部')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def metadata(ctx, region_id: str, az_name: str, instance_uuid: str,
             metadata_key: Optional[str], output: Optional[str]):
    """物理机元数据查询"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.list_metadata(
        region_id=region_id, az_name=az_name, instance_uuid=instance_uuid,
        metadata_key=metadata_key
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    metadata_dict = result.get('returnObj', {}).get('metadata', {})
    if metadata_dict:
        click.echo(f"物理机 {instance_uuid} 元数据:")
        for key, val in metadata_dict.items():
            click.echo(f"  {key}: {val}")
    else:
        click.echo("该物理机未设置元数据")


# ==================== 物理机查询网卡信息 ====================

@dps.command('interfaces')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--instance-uuid', required=True, help='实例UUID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def interfaces(ctx, region_id: str, az_name: str, instance_uuid: str, output: Optional[str]):
    """物理机查询网卡信息"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.list_interfaces(
        region_id=region_id, az_name=az_name, instance_uuid=instance_uuid
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    interfaces_list = result.get('returnObj', [])
    click.echo(f"物理机 {instance_uuid} 网卡信息 (共 {len(interfaces_list)} 个)")
    if interfaces_list:
        table_data = []
        for nic in interfaces_list:
            sg_names = ','.join(sg.get('securityGroupName', '') for sg in nic.get('securityGroups', []))
            table_data.append({
                '网卡UUID': nic.get('interfaceUUID', '')[:20],
                '主网卡': '✓' if nic.get('master') else '',
                'IPv4': nic.get('ipv4', ''),
                'IPv4网关': nic.get('ipv4Gateway', ''),
                'IPv6': nic.get('ipv6', ''),
                '子网UUID': nic.get('subnetUUID', '')[:20],
                'VPC': nic.get('vpcUUID', '')[:20],
                '安全组': sg_names,
            })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 物理机查询挂载卷ID列表信息 ====================

@dps.command('volumes')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--instance-uuid', required=True, help='实例UUID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def volumes(ctx, region_id: str, az_name: str, instance_uuid: str, output: Optional[str]):
    """物理机查询挂载卷ID列表信息"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.list_attached_volume_ids(
        region_id=region_id, az_name=az_name, instance_uuid=instance_uuid
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    vol_ids = result.get('returnObj', {}).get('attachedVolumes', [])
    click.echo(f"物理机 {instance_uuid} 挂载卷 (共 {len(vol_ids)} 个)")
    for vid in vol_ids:
        click.echo(f"  {vid}")


# ==================== 查询物理机所使用镜像的信息 ====================

@dps.command('image')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--instance-uuid', required=True, help='实例UUID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def image(ctx, region_id: str, az_name: str, instance_uuid: str, output: Optional[str]):
    """查询物理机所使用镜像的信息"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.get_instance_image(
        region_id=region_id, az_name=az_name, instance_uuid=instance_uuid
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    results = result.get('returnObj', {}).get('results', [])
    click.echo(f"物理机 {instance_uuid} 镜像信息 (共 {len(results)} 个)")
    if results:
        table_data = []
        for img in results:
            os_info = img.get('os', {})
            table_data.append({
                '镜像UUID': img.get('imageUUID', '')[:20],
                '名称': img.get('nameZh', ''),
                '版本': img.get('version', ''),
                '类型': img.get('imageType', ''),
                '格式': img.get('format', ''),
                '布局': img.get('layoutType', ''),
                '状态': img.get('status', ''),
                '共享': '是' if img.get('isShared') else '否',
                'OS': os_info.get('platform', ''),
                'OS版本': os_info.get('version', ''),
                '架构': os_info.get('architecture', ''),
            })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 物理机查询库存 ====================

@dps.command('stock')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--device-type', default=None, help='物理机套餐类型，如physical.t3.large')
@click.option('--count', type=int, default=None, help='所需库存数(正整数)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def stock(ctx, region_id: str, az_name: str, device_type: Optional[str],
          count: Optional[int], output: Optional[str]):
    """物理机查询库存"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.get_device_stock(
        region_id=region_id, az_name=az_name, device_type=device_type, count=count
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    return_obj = result.get('returnObj', {})
    results = return_obj.get('results', [])
    click.echo(f"物理机库存 (共 {return_obj.get('totalCount', 0)} 个套餐)")
    if results:
        table_data = []
        for r in results:
            stocks = r.get('stocks', [])
            for stock_item in stocks:
                table_data.append({
                    '套餐': stock_item.get('deviceType', ''),
                    '可用数量': stock_item.get('available', 0),
                    '库存充足': '✓' if stock_item.get('success') else '✗',
                })
            if not stocks:
                table_data.append({
                    '套餐': device_type or '-',
                    '可用数量': r.get('available', 0),
                    '库存充足': '✓' if r.get('success') else '✗',
                })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 查询单台物理机 ====================

@dps.command('describe')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--instance-uuid', required=True, help='实例UUID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def describe(ctx, region_id: str, az_name: str, instance_uuid: str, output: Optional[str]):
    """查询单台物理机详情"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.describe_instance(
        region_id=region_id, az_name=az_name, instance_uuid=instance_uuid
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    inst = result.get('returnObj', {})
    if not inst:
        click.echo("未找到该物理机")
        return

    flavor = inst.get('flavor', {})
    device_detail = inst.get('deviceDetail', {})
    click.echo(f"物理机详情: {inst.get('instanceName', '')} ({inst.get('instanceUUID', '')})")
    click.echo("=" * 70)
    click.echo(f"  {'状态':<12}: {inst.get('ebmState', '')}")
    click.echo(f"  {'展示名':<12}: {inst.get('displayName', '')}")
    click.echo(f"  {'描述':<12}: {inst.get('description', '') or '无'}")
    click.echo(f"  {'设备类型':<12}: {inst.get('deviceType', '')}")
    click.echo(f"  {'资源池':<12}: {inst.get('region', '')} ({inst.get('regionID', '')[:20]})")
    click.echo(f"  {'可用区':<12}: {inst.get('azName', '')}")
    click.echo(f"  {'镜像':<12}: {inst.get('imageName', '')} ({inst.get('imageID', '')[:20]})")
    click.echo(f"  {'OS':<12}: {inst.get('osTypeName', '')}")
    click.echo(f"  {'内网IP':<12}: {inst.get('privateIP', '')}")
    click.echo(f"  {'公网IP':<12}: {inst.get('publicIP', '') or '无'}")
    click.echo(f"  {'内网IPv6':<12}: {inst.get('privateIPv6', '') or '无'}")
    click.echo(f"  {'VPC':<12}: {inst.get('vpcName', '')} ({inst.get('vpcID', '')[:20]})")
    click.echo(f"  {'子网':<12}: {inst.get('subnetID', '')[:30]}")
    click.echo(f"  {'vCPU':<12}: {flavor.get('vcpus', '')}")
    click.echo(f"  {'内存(GB)':<12}: {flavor.get('memSize', '')}")
    click.echo(f"  {'网卡数':<12}: {flavor.get('nicAmount', '')}")
    click.echo(f"  {'NUMA':<12}: {flavor.get('numaNodeAmount', '')}")
    click.echo(f"  {'CPU':<12}: {device_detail.get('cpuManufacturer', '')} {device_detail.get('cpuModel', '')} ({device_detail.get('cpuFrequency', '')}GHz)")
    click.echo(f"  {'设备型号':<12}: {device_detail.get('deviceModel', '')}")
    click.echo(f"  {'弹性裸金属':<12}: {'是' if device_detail.get('smartNicExist') else '否'}")
    click.echo(f"  {'支持云盘':<12}: {'是' if device_detail.get('supportCloud') else '否'}")
    click.echo(f"  {'系统盘':<12}: {device_detail.get('systemVolumeDescription', '')}")
    click.echo(f"  {'数据盘':<12}: {device_detail.get('dataVolumeDescription', '') or '无'}")
    attached = inst.get('attachedVolumes', [])
    click.echo(f"  {'挂载卷':<12}: {len(attached)}个 {', '.join(attached) if attached else '无'}")
    click.echo(f"  {'付费方式':<12}: {'按量' if inst.get('onDemand') else '包周期'}")
    click.echo(f"  {'冻结':<12}: {'是' if inst.get('freezing') else '否'}")
    click.echo(f"  {'到期':<12}: {'是' if inst.get('expired') else '否'}")
    click.echo(f"  {'创建时间':<12}: {inst.get('createTime', '')}")
    click.echo(f"  {'到期时间':<12}: {inst.get('expiredTime', '')}")
    click.echo(f"  {'企业项目':<12}: {inst.get('projectID', '')}")


# ==================== 批量查询物理机 ====================

@dps.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--az-name', required=True, help='可用区名称(单可用区填default)')
@click.option('--instance-name', default=None, help='实例名称')
@click.option('--ip', default=None, help='公网IP地址')
@click.option('--vpc-id', default=None, help='VPC ID')
@click.option('--subnet-id', default=None, help='子网UUID')
@click.option('--device-type', default=None, help='物理机套餐类型')
@click.option('--status', default=None,
              help='实例状态: CREATING/STARTING/RUNNING/STOPPING/RESTARTING/ERROR等')
@click.option('--query-content', default=None, help='模糊查询(instanceName/内网IP/displayName)')
@click.option('--instance-uuid', default=None, help='单个实例UUID')
@click.option('--page-no', type=int, default=None, help='页码，默认1')
@click.option('--page-size', type=int, default=None, help='每页数量，默认10，最大1000')
@click.option('--project-id', default=None, help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None, help='输出格式')
@click.pass_context
def list_instances(ctx, region_id: str, az_name: str,
                   instance_name: Optional[str], ip: Optional[str],
                   vpc_id: Optional[str], subnet_id: Optional[str],
                   device_type: Optional[str], status: Optional[str],
                   query_content: Optional[str], instance_uuid: Optional[str],
                   page_no: Optional[int], page_size: Optional[int],
                   project_id: Optional[str], output: Optional[str]):
    """批量查询物理机列表"""
    from dps.client import DPSClient

    client = ctx.obj['client']
    dps_client = DPSClient(client)

    result = dps_client.list_instances(
        region_id=region_id, az_name=az_name,
        instance_name=instance_name, ip=ip, vpc_id=vpc_id, subnet_id=subnet_id,
        device_type=device_type, status=status, query_content=query_content,
        instance_uuid=instance_uuid, page_no=page_no, page_size=page_size,
        project_id=project_id
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    return_obj = result.get('returnObj', {})
    results = return_obj.get('results', [])
    click.echo(f"物理机列表 (共 {return_obj.get('totalCount', 0)} 个，当前 {return_obj.get('currentCount', 0)} 个)")
    if results:
        table_data = []
        for inst in results:
            flavor = inst.get('flavor', {})
            table_data.append({
                '实例UUID': inst.get('instanceUUID', '')[:20],
                '名称': inst.get('instanceName', ''),
                '设备类型': inst.get('deviceType', ''),
                '状态': inst.get('ebmState', ''),
                '内网IP': inst.get('privateIP', ''),
                '公网IP': inst.get('publicIP', '') or '无',
                'vCPU': flavor.get('vcpus', ''),
                '内存': flavor.get('memSize', ''),
                '镜像': inst.get('imageName', ''),
                '付费': '按量' if inst.get('onDemand') else '包周期',
                '到期时间': inst.get('expiredTime', ''),
            })
        click.echo(OutputFormatter.format_table(table_data))
