"""
云电脑(CloudPC)命令行接口
"""

import click
import json
import sys
from typing import Optional

from .client import CloudPCClient


# 通用状态映射
_DESKTOP_STATUS_MAP = {
    'STOPPED': '已关机', 'RUNNING': '运行中', 'REBOOT': '重启中',
    'BUILD': '创建中', 'REBUILD': '重装中', 'DELETED': '已删除',
    'STOPPING': '关机中', 'STARTING': '开机中', 'SUSPEND': '已休眠',
    'SUSPENDING': '休眠中', 'RESUMING': '唤醒中',
}


@click.group()
def cloudpc():
    """云电脑(CloudPC)管理"""
    pass


# ========== 服务状态 ==========

@cloudpc.command('service-status')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'summary']),
              default='summary', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def service_status(ctx, region_id, output_format, timeout):
    """查询云电脑服务开通状态"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)

    click.echo(f"🔍 正在查询云电脑服务状态: {region_id}")

    try:
        result = pc.check_service_status(region_id)

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if result.get("statusCode") != 800:
                click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
                return
            return_obj = result.get("returnObj", {})
            status = return_obj.get("status", "N/A")
            status_text = {"Unactivated": "未开通", "Activating": "开通中", "Activated": "已开通"}.get(status, status)
            emoji = {"Unactivated": "⚪", "Activating": "🟡", "Activated": "🟢"}.get(status, "⚪")
            click.echo(f"\n📋 云电脑服务状态")
            click.echo("=" * 40)
            click.echo(f"{emoji} 状态: {status_text} ({status})")

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


# ========== 桌面列表 ==========

@cloudpc.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--desktop-oid', help='桌面OID')
@click.option('--nickname', help='桌面别名')
@click.option('--status', help='状态过滤 (RUNNING/STOPPED/REBOOT/BUILD等)')
@click.option('--vpc-oid', help='VPC OID')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=10, help='每页大小')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def list_desktops(ctx, region_id, desktop_oid, nickname, status,
                  vpc_oid, page, size, output_format, timeout):
    """查询云电脑列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)

    click.echo(f"📋 正在查询云电脑列表...")

    try:
        result = pc.describe_desktops(
            region_id=region_id, desktop_oid=desktop_oid,
            nickname=nickname, status=status, vpc_oid=vpc_oid,
            page_num=page, page_size=size
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_desktops_table(result)
        else:
            _display_desktops_summary(result)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_desktops_table(result):
    """以表格显示桌面列表"""
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)

    click.echo(f"\n📊 云电脑列表 (共{total}条)")
    click.echo("=" * 130)
    if not data:
        click.echo("📭 未找到云电脑")
        return

    click.echo(f"{'桌面OID':<36} {'名称':<18} {'状态':<10} {'规格':<12} {'CPU':<6} {'内存':<6} {'系统盘':<8} {'VPC':<14} {'用户':<12} {'创建时间':<18}")
    click.echo("-" * 130)

    for d in data:
        oid = d.get("desktopOid", "N/A")[:34]
        name = d.get("nickname", d.get("desktopName", "N/A"))[:16]
        status = _DESKTOP_STATUS_MAP.get(d.get("status", ""), d.get("status", "N/A"))[:8]
        flavor = d.get("flavorType", "N/A")[:10]
        cpu = str(d.get("cpu", "N/A"))
        mem = str(d.get("memory", "N/A"))
        sys_disk = str(d.get("sysDisk", "N/A"))
        vpc = d.get("vpcName", "N/A")[:12]
        user = d.get("userName", "N/A")[:10]
        create = d.get("createTime", "N/A")[:16]
        click.echo(f"{oid:<36} {name:<18} {status:<10} {flavor:<12} {cpu:<6} {mem:<6} {sys_disk:<8} {vpc:<14} {user:<12} {create:<18}")


def _display_desktops_summary(result):
    """显示桌面列表摘要"""
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)

    click.echo(f"\n📊 云电脑列表摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📋 总数: {total}")
    click.echo(f"📄 当前显示: {len(data)}")

    if data:
        status_cnt = {}
        for d in data:
            s = _DESKTOP_STATUS_MAP.get(d.get("status", ""), d.get("status", "未知"))
            status_cnt[s] = status_cnt.get(s, 0) + 1
        if status_cnt:
            click.echo(f"\n📈 状态分布:")
            for s, c in sorted(status_cnt.items()):
                click.echo(f"   {s}: {c}")

        click.echo(f"\n🏷️ 桌面列表:")
        for i, d in enumerate(data, 1):
            oid = d.get("desktopOid", "N/A")
            name = d.get("nickname", d.get("desktopName", "N/A"))
            status = _DESKTOP_STATUS_MAP.get(d.get("status", ""), d.get("status", "N/A"))
            emoji = "🟢" if d.get("status") == "RUNNING" else "🔴" if d.get("status") in ("STOPPED", "DELETED") else "🟡"
            click.echo(f"   {i}. {emoji} {name}")
            click.echo(f"      OID: {oid} | 状态: {status}")


# ========== ECS型云电脑 ==========

@cloudpc.command('ecs-list')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--desktop-oid', help='桌面OID')
@click.option('--nickname', help='桌面别名')
@click.option('--status', help='状态过滤')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=10, help='每页大小')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def ecs_list(ctx, region_id, desktop_oid, nickname, status,
             page, size, output_format, timeout):
    """查询弹性云电脑(ECS型)列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)

    click.echo(f"📋 正在查询ECS型云电脑列表...")

    try:
        result = pc.describe_ecs(
            region_id=region_id, desktop_oid=desktop_oid,
            nickname=nickname, status=status,
            page_num=page, page_size=size
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_ecs_table(result)
        else:
            _display_ecs_summary(result)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_ecs_table(result):
    """以表格显示ECS型云电脑列表"""
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n📊 ECS型云电脑列表 (共{total}条)")
    click.echo("=" * 130)
    if not data:
        click.echo("📭 未找到")
        return
    click.echo(f"{'桌面OID':<36} {'名称':<18} {'状态':<10} {'CPU':<6} {'内存':<6} {'系统盘':<8} {'VPC':<14} {'用户':<12} {'创建时间':<18}")
    click.echo("-" * 130)
    for d in data:
        oid = d.get("desktopOid", "N/A")[:34]
        name = d.get("nickname", d.get("desktopName", "N/A"))[:16]
        status = _DESKTOP_STATUS_MAP.get(d.get("status", ""), d.get("status", "N/A"))[:8]
        cpu = str(d.get("cpu", "N/A"))
        mem = str(d.get("memory", "N/A"))
        sys_disk = str(d.get("sysDisk", "N/A"))
        vpc = d.get("vpcName", "N/A")[:12]
        user = d.get("userName", "N/A")[:10]
        create = d.get("createTime", "N/A")[:16]
        click.echo(f"{oid:<36} {name:<18} {status:<10} {cpu:<6} {mem:<6} {sys_disk:<8} {vpc:<14} {user:<12} {create:<18}")


def _display_ecs_summary(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n📊 ECS型云电脑摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功 | 📋 总数: {total} | 📄 当前: {len(data)}")
    if data:
        for i, d in enumerate(data, 1):
            oid = d.get("desktopOid", "N/A")
            name = d.get("nickname", d.get("desktopName", "N/A"))
            status = _DESKTOP_STATUS_MAP.get(d.get("status", ""), d.get("status", "N/A"))
            emoji = "🟢" if d.get("status") == "RUNNING" else "🔴"
            click.echo(f"   {i}. {emoji} {name} ({oid}) - {status}")


# ========== 镜像 ==========

@cloudpc.command('images')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--os-type', help='操作系统类型')
@click.option('--flavor-type', help='规格类型')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=20, help='每页大小')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def images(ctx, region_id, os_type, flavor_type, page, size, output_format, timeout):
    """查询可用镜像列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)
    click.echo(f"📋 正在查询可用镜像...")
    try:
        result = pc.describe_available_images(
            region_id=region_id, os_type=os_type,
            flavor_type=flavor_type, page_num=page, page_size=size
        )
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_images_table(result)
        else:
            _display_images_summary(result)
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_images_table(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n📸 可用镜像 (共{total}条)")
    click.echo("=" * 100)
    if not data:
        click.echo("📭 无镜像")
        return
    click.echo(f"{'镜像OID':<36} {'名称':<30} {'操作系统':<16} {'系统盘':<8}")
    click.echo("-" * 100)
    for img in data:
        oid = img.get("imageOid", "N/A")[:34]
        name = img.get("imageName", "N/A")[:28]
        os_name = img.get("osName", "N/A")[:14]
        disk = str(img.get("sysDisk", "N/A"))
        click.echo(f"{oid:<36} {name:<30} {os_name:<16} {disk:<8}")


def _display_images_summary(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n📸 可用镜像摘要")
    click.echo("=" * 50)
    click.echo(f"✅ 查询成功 | 📋 总数: {total}")


# ========== 云硬盘 ==========

@cloudpc.command('volumes')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--desktop-oid', help='桌面OID')
@click.option('--disk-type', help='磁盘类型')
@click.option('--status', help='状态')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=20, help='每页大小')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def volumes(ctx, region_id, desktop_oid, disk_type, status,
            page, size, output_format, timeout):
    """查询云硬盘列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)
    click.echo(f"📋 正在查询云硬盘...")
    try:
        result = pc.describe_cloud_volumes(
            region_id=region_id, desktop_oid=desktop_oid,
            disk_type=disk_type, status=status,
            page_num=page, page_size=size
        )
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_volumes_table(result)
        else:
            _display_volumes_summary(result)
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_volumes_table(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n💾 云硬盘列表 (共{total}条)")
    click.echo("=" * 110)
    if not data:
        click.echo("📭 无云硬盘")
        return
    click.echo(f"{'卷OID':<36} {'名称':<20} {'大小':<8} {'类型':<12} {'系统盘':<8} {'状态':<10} {'桌面OID':<36}")
    click.echo("-" * 110)
    for v in data:
        oid = v.get("volumeOid", "N/A")[:34]
        name = v.get("volumeName", "N/A")[:18]
        size = str(v.get("volumeSize", "N/A"))
        dtype = v.get("diskType", "N/A")[:10]
        sys = "是" if v.get("forSysDisk") else "否"
        status = v.get("status", "N/A")[:8]
        doid = v.get("desktopOid", "")[:34]
        click.echo(f"{oid:<36} {name:<20} {size:<8} {dtype:<12} {sys:<8} {status:<10} {doid:<36}")


def _display_volumes_summary(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n💾 云硬盘摘要")
    click.echo("=" * 50)
    click.echo(f"✅ 查询成功 | 📋 总数: {total}")
    total_size = sum(int(v.get("volumeSize", 0) or 0) for v in data)
    click.echo(f"💿 总容量: {total_size}GB")


# ========== 网络 ==========

@cloudpc.command('vpcs')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--vpc-oid', help='VPC OID')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=20, help='每页大小')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def vpcs(ctx, region_id, vpc_oid, page, size, output_format, timeout):
    """查询VPC列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)
    click.echo(f"📋 正在查询VPC列表...")
    try:
        result = pc.describe_vpcs(region_id=region_id, vpc_oid=vpc_oid, page_num=page, page_size=size)
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_vpcs_table(result)
        else:
            _display_vpcs_summary(result)
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_vpcs_table(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n🌐 VPC列表 (共{total}条)")
    click.echo("=" * 100)
    if not data:
        click.echo("📭 无VPC")
        return
    click.echo(f"{'VPC OID':<36} {'名称':<20} {'CIDR':<20} {'状态':<10}")
    click.echo("-" * 100)
    for v in data:
        oid = v.get("vpcOid", "N/A")[:34]
        name = v.get("vpcName", "N/A")[:18]
        cidr = v.get("cidr", "N/A")[:18]
        status = v.get("status", "N/A")[:8]
        click.echo(f"{oid:<36} {name:<20} {cidr:<20} {status:<10}")


def _display_vpcs_summary(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n🌐 VPC摘要")
    click.echo("=" * 50)
    click.echo(f"✅ 查询成功 | 📋 总数: {total}")


@cloudpc.command('subnets')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--vpc-oid', required=True, help='VPC OID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=20, help='每页大小')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def subnets(ctx, region_id, vpc_oid, page, size, output_format, timeout):
    """查询子网列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)
    click.echo(f"📋 正在查询子网列表...")
    try:
        result = pc.describe_subnets(region_id=region_id, vpc_oid=vpc_oid, page_num=page, page_size=size)
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_subnets_table(result, vpc_oid)
        else:
            _display_subnets_summary(result, vpc_oid)
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_subnets_table(result, vpc_oid):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n🌐 子网列表 (VPC: {vpc_oid}, 共{total}条)")
    click.echo("=" * 120)
    if not data:
        click.echo("📭 无子网")
        return
    click.echo(f"{'子网OID':<36} {'名称':<18} {'CIDR':<20} {'网关':<16} {'可用IP':<8} {'状态':<10}")
    click.echo("-" * 120)
    for s in data:
        oid = s.get("subnetOid", "N/A")[:34]
        name = s.get("subnetName", "N/A")[:16]
        cidr = s.get("cidr", "N/A")[:18]
        gw = s.get("gatewayIp", "N/A")[:14]
        avail = str(s.get("availableIpCount", "N/A"))
        status = s.get("status", "N/A")[:8]
        click.echo(f"{oid:<36} {name:<18} {cidr:<20} {gw:<16} {avail:<8} {status:<10}")


def _display_subnets_summary(result, vpc_oid):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n🌐 子网摘要 (VPC: {vpc_oid})")
    click.echo("=" * 50)
    click.echo(f"✅ 查询成功 | 📋 总数: {total}")
    if data:
        total_avail = sum(int(s.get("availableIpCount", 0) or 0) for s in data)
        click.echo(f"🔢 可用IP总数: {total_avail}")


# ========== 用户与部门 ==========

@cloudpc.command('users')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--org-oid', help='部门OID')
@click.option('--user-name', help='用户名')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=20, help='每页大小')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def users(ctx, region_id, org_oid, user_name, page, size, output_format, timeout):
    """查询用户列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)
    click.echo(f"📋 正在查询用户列表...")
    try:
        result = pc.describe_users(region_id=region_id, org_oid=org_oid, user_name=user_name, page_num=page, page_size=size)
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_users_table(result)
        else:
            _display_users_summary(result)
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_users_table(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n👤 用户列表 (共{total}条)")
    click.echo("=" * 110)
    if not data:
        click.echo("📭 无用户")
        return
    click.echo(f"{'用户OID':<36} {'登录账号':<20} {'用户名':<16} {'邮箱':<22} {'桌面数':<8} {'状态':<8}")
    click.echo("-" * 110)
    for u in data:
        oid = u.get("pubUserOid", "N/A")[:34]
        account = u.get("loginAccount", "N/A")[:18]
        uname = u.get("userName", "N/A")[:14]
        email = u.get("email", "N/A")[:20]
        dnum = str(u.get("desktopNums", "N/A"))
        lock = u.get("lockStatus", "")
        status_text = "🔒锁定" if lock else "正常"
        click.echo(f"{oid:<36} {account:<20} {uname:<16} {email:<22} {dnum:<8} {status_text:<8}")


def _display_users_summary(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n👤 用户摘要")
    click.echo("=" * 50)
    click.echo(f"✅ 查询成功 | 📋 总数: {total}")
    locked = sum(1 for u in data if u.get("lockStatus"))
    click.echo(f"🔒 锁定: {locked}")


@cloudpc.command('orgs')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--parent-org-oid', help='父部门OID')
@click.option('--org-name', help='部门名称')
@click.option('--page', '-p', default=1, help='页码')
@click.option('--size', default=20, help='每页大小')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def orgs(ctx, region_id, parent_org_oid, org_name, page, size, output_format, timeout):
    """查询部门列表"""
    client = ctx.obj['client']
    pc = CloudPCClient(client)
    pc.set_timeout(timeout)
    click.echo(f"📋 正在查询部门列表...")
    try:
        result = pc.describe_organizations(region_id=region_id, parent_org_oid=parent_org_oid, org_name=org_name, page_num=page, page_size=size)
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_orgs_table(result)
        else:
            _display_orgs_summary(result)
    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_orgs_table(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n🏢 部门列表 (共{total}条)")
    click.echo("=" * 90)
    if not data:
        click.echo("📭 无部门")
        return
    click.echo(f"{'部门OID':<36} {'名称':<20} {'描述':<30}")
    click.echo("-" * 90)
    for o in data:
        oid = o.get("orgOid", "N/A")[:34]
        name = o.get("orgName", "N/A")[:18]
        desc = o.get("description", "")[:28]
        click.echo(f"{oid:<36} {name:<20} {desc:<28}")


def _display_orgs_summary(result):
    if result.get("statusCode") != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return
    return_obj = result.get("returnObj", {})
    data = return_obj.get("list", [])
    total = return_obj.get("total", 0)
    click.echo(f"\n🏢 部门摘要")
    click.echo("=" * 50)
    click.echo(f"✅ 查询成功 | 📋 总数: {total}")
