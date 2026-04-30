"""
翼MapReduce(EMR)命令行接口
"""

import click
import json
import sys
import time
from typing import Optional

from .client import EMRClient


# 集群状态映射
_CLUSTER_STATE_MAP = {
    1: "启动中", 2: "运行中", 3: "异常终止", 4: "释放中",
    5: "已终止", 10: "已冻结",
}

_CLUSTER_TYPE_MAP = {
    1: "数据湖", 2: "数据分析", 3: "数据服务", 4: "云搜索", 5: "自定义", 6: "实时数据流",
}

_NODE_STATE_MAP = {
    1: "启动中", 2: "正在关机", 4: "已删除", 8: "运行中", 9: "已关机",
}


@click.group()
def emr():
    """翼MapReduce(EMR)管理"""
    pass


# ========== 集群列表/详情命令 ==========

@emr.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--name', '-n', help='集群名称')
@click.option('--state', '-s', type=int, help='集群状态码 (1:启动中 2:运行中 3:异常终止 ...)')
@click.option('--type', '-t', type=int, help='集群类型码 (1:数据湖 2:数据分析 3:数据服务 4:云搜索 6:实时数据流)')
@click.option('--page', '-p', default=1, help='页码，默认1')
@click.option('--size', default=10, help='每页大小，默认10')
@click.option('--v2', is_flag=True, help='使用V2 API')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', default=30, help='请求超时时间(秒)')
@click.pass_context
def list_clusters(ctx, region_id: str, name: str, state: int, type: int,
                  page: int, size: int, v2: bool, output_format: str, timeout: int):
    """
    查询EMR集群列表

    示例:
        ctyun emr list --region-id xxx
        ctyun emr list -r xxx --name test --state 2 --v2
    """
    client = ctx.obj['client']
    emr_client = EMRClient(client)
    emr_client.set_timeout(timeout)

    click.echo(f"📋 正在查询EMR集群列表{'(V2)' if v2 else '(V1)'}...")

    try:
        if v2:
            result = emr_client.select_cluster_page_v2(
                region_id=region_id, page_index=page, page_size=size,
                cluster_name=name, cluster_state_code=state, cluster_type_code=type
            )
        else:
            result = emr_client.select_cluster_detail_pages(
                region_id=region_id, page_index=page, page_size=size,
                cluster_name=name, cluster_state_code=state, cluster_type_code=type
            )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_clusters_table(result)
        else:
            _display_clusters_summary(result)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_clusters_table(result: dict):
    """以表格形式显示集群列表"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    records = return_obj.get("records", [])
    total = return_obj.get("total", 0)

    click.echo(f"\n📊 EMR集群列表 (共{total}条)")
    click.echo("=" * 125)

    if not records:
        click.echo("📭 未找到集群")
        return

    click.echo(f"{'集群ID':<36} {'名称':<22} {'状态':<10} {'类型':<10} {'版本':<14} {'付费':<8} {'创建时间':<20}")
    click.echo("-" * 125)

    for inst in records:
        inst_id = inst.get("id", "N/A")[:34]
        name = inst.get("clusterName", "N/A")[:20]
        state = inst.get("clusterState", "N/A")[:8]
        type_name = inst.get("clusterType", "N/A")[:8]
        version = inst.get("clusterTypeVersion", "N/A")[:12]
        pay = inst.get("payType", "N/A")[:6]
        create_time = inst.get("clusterCreateTime", "N/A")
        click.echo(f"{inst_id:<36} {name:<22} {state:<10} {type_name:<10} {version:<14} {pay:<8} {create_time:<20}")


def _display_clusters_summary(result: dict):
    """显示集群列表摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    records = return_obj.get("records", [])
    total = return_obj.get("total", 0)

    click.echo(f"\n📊 EMR集群列表摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📋 总集群数: {total}")
    click.echo(f"📄 当前显示: {len(records)}个")

    if records:
        click.echo(f"\n🏷️ 集群列表:")
        for i, inst in enumerate(records, 1):
            state = inst.get("clusterState", "N/A")
            name = inst.get("clusterName", "N/A")
            inst_id = inst.get("id", "N/A")
            type_name = inst.get("clusterType", "N/A")
            version = inst.get("clusterTypeVersion", "N/A")

            emoji = "🟢" if state == "运行中" else "🔴" if state in ["已终止", "异常终止"] else "🟡"
            click.echo(f"   {i}. {emoji} {name}")
            click.echo(f"      ID: {inst_id}")
            click.echo(f"      状态: {state} | 类型: {type_name} | 版本: {version}")


@emr.command('describe')
@click.option('--cluster-id', '-i', required=True, help='集群ID (必需)')
@click.option('--v2', is_flag=True, help='使用V2 API')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式')
@click.option('--timeout', default=30, help='请求超时时间(秒)')
@click.pass_context
def describe_cluster(ctx, cluster_id: str, v2: bool, output_format: str, timeout: int):
    """
    查询EMR集群详情

    示例:
        ctyun emr describe --cluster-id xxx
        ctyun emr describe -i xxx --v2
    """
    client = ctx.obj['client']
    emr_client = EMRClient(client)
    emr_client.set_timeout(timeout)

    click.echo(f"🔍 正在查询EMR集群详情{'(V2)' if v2 else '(V1)'}: {cluster_id}")

    try:
        if v2:
            result = emr_client.get_cluster_by_id_v2(cluster_id)
        else:
            result = emr_client.get_cluster_detail_by_id(cluster_id)

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_cluster_detail_table(result, cluster_id)
        else:
            _display_cluster_detail_summary(result, cluster_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_cluster_detail_table(result: dict, cluster_id: str):
    """以表格形式显示集群详情"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    inst = result.get("returnObj", {})

    click.echo(f"\n📍 EMR集群详情 (集群: {cluster_id})")
    click.echo("=" * 60)

    click.echo("\n📋 基本信息:")
    click.echo("-" * 55)
    basic = [
        ("集群名称", inst.get("clusterName", "N/A")),
        ("集群状态", inst.get("clusterState", "N/A")),
        ("集群类型", inst.get("clusterType", "N/A")),
        ("产品版本", inst.get("clusterTypeVersion", "N/A")),
        ("付费类型", inst.get("payType", "N/A")),
        ("资源池", inst.get("regionName", "N/A")),
        ("可用区", inst.get("availableZoneName", "N/A")),
        ("VPC", inst.get("vpcId", "N/A")),
        ("子网", inst.get("subnetId", "N/A")),
        ("安全组", inst.get("securityGroupId", "N/A")),
    ]
    for k, v in basic:
        click.echo(f"  {k:<12}: {v}")

    click.echo("\n⚙️ 其他信息:")
    click.echo("-" * 55)
    click.echo(f"  登录方式: {inst.get('loginType', 'N/A')}")
    click.echo(f"  Manager版本: {inst.get('managerVersion', 'N/A')}")
    click.echo(f"  IPv6: {inst.get('enableIpv6', 'N/A')}")
    click.echo(f"  自动续订: {'是' if inst.get('autoRenewStatus') == 1 else '否'}")


def _display_cluster_detail_summary(result: dict, cluster_id: str):
    """显示集群详情摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    inst = result.get("returnObj", {})

    click.echo(f"\n📍 EMR集群详情摘要 (集群: {cluster_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"🏷️  名称: {inst.get('clusterName', 'N/A')}")
    click.echo(f"⚡ 状态: {inst.get('clusterState', 'N/A')}")
    click.echo(f"🔧 类型: {inst.get('clusterType', 'N/A')} ({inst.get('clusterTypeVersion', 'N/A')})")
    click.echo(f"💰 付费: {inst.get('payType', 'N/A')}")
    click.echo(f"🌐 资源池: {inst.get('regionName', 'N/A')}")
    click.echo(f"📦 组件: {inst.get('componentNameList', 'N/A')[:50]}")


# ========== 节点组命令 ==========

@emr.command('node-groups')
@click.option('--cluster-id', '-i', required=True, help='集群ID (必需)')
@click.option('--v2', is_flag=True, help='使用V2 API (默认V1)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', default=30, help='请求超时时间(秒)')
@click.pass_context
def node_groups(ctx, cluster_id: str, v2: bool, output_format: str, timeout: int):
    """
    查询EMR集群节点组信息

    示例:
        ctyun emr node-groups --cluster-id xxx
        ctyun emr node-groups -i xxx --v2
    """
    client = ctx.obj['client']
    emr_client = EMRClient(client)
    emr_client.set_timeout(timeout)

    click.echo(f"🔍 正在查询EMR节点组信息{'(V2)' if v2 else '(V1)'}: {cluster_id}")

    try:
        if v2:
            result = emr_client.get_node_group_by_cluster_id_v2(cluster_id)
        else:
            # V1没有单独的节点组查询API，使用节点组详情API
            result = emr_client.get_group_and_host_by_condition_v2(cluster_id)

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_node_groups_table(result, cluster_id)
        else:
            _display_node_groups_summary(result, cluster_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_node_groups_table(result: dict, cluster_id: str):
    """以表格形式显示节点组"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    # V2返回列表，V2节点组详情返回列表
    groups = return_obj if isinstance(return_obj, list) else return_obj.get("records", [])
    if not groups and isinstance(return_obj, dict):
        # 尝试从节点组详情API获取
        groups = [return_obj] if return_obj.get("id") else []

    click.echo(f"\n🔗 EMR节点组信息 (集群: {cluster_id})")
    click.echo("=" * 100)

    if not groups:
        click.echo("📭 未找到节点组")
        return

    click.echo(f"{'节点组ID':<20} {'类型':<12} {'名称':<12} {'主机数':<8} {'CPU':<6} {'内存':<6} {'规格':<20}")
    click.echo("-" * 100)

    for g in groups:
        gid = str(g.get("id", "N/A"))[:18]
        gtype = g.get("nodeGroupType", "N/A")[:10]
        gname = g.get("nodeGroupName", "N/A")[:10]
        host_num = g.get("hostNum", "N/A")
        cpu = g.get("cpuNum", "N/A")
        mem = g.get("memory", "N/A")
        spec = g.get("iaasVmSpecCode", "N/A")[:18]
        click.echo(f"{gid:<20} {gtype:<12} {gname:<12} {host_num:<8} {cpu:<6} {mem:<6} {spec:<20}")


def _display_node_groups_summary(result: dict, cluster_id: str):
    """显示节点组摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    groups = return_obj if isinstance(return_obj, list) else return_obj.get("records", [])
    if not groups and isinstance(return_obj, dict):
        groups = [return_obj] if return_obj.get("id") else []

    click.echo(f"\n🔗 EMR节点组摘要 (集群: {cluster_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📊 节点组数: {len(groups)}")

    total_hosts = sum(g.get("hostNum", 0) for g in groups)
    click.echo(f"🖥️  总主机数: {total_hosts}")

    if groups:
        click.echo(f"\n📍 节点组:")
        for g in groups:
            gtype = g.get("nodeGroupType", "N/A")
            gname = g.get("nodeGroupName", "N/A")
            host_num = g.get("hostNum", 0)
            cpu = g.get("cpuNum", "N/A")
            mem = g.get("memory", "N/A")
            spec = g.get("iaasVmSpecCode", "N/A")
            click.echo(f"   • {gtype} ({gname}): {host_num}主机, {cpu}核/{mem}GB, {spec}")


@emr.command('node-detail')
@click.option('--cluster-id', '-i', required=True, help='集群ID (必需)')
@click.option('--node-state', type=int, help='主机状态过滤 (1:启动中 2:正在关机 4:已删除 8:运行中 9:已关机)')
@click.option('--select-key', help='模糊查询 (节点名称/IP)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', default=30, help='请求超时时间(秒)')
@click.pass_context
def node_detail(ctx, cluster_id: str, node_state: int, select_key: str,
                output_format: str, timeout: int):
    """
    查询EMR集群节点组详情(V2)

    示例:
        ctyun emr node-detail --cluster-id xxx
        ctyun emr node-detail -i xxx --node-state 8
    """
    client = ctx.obj['client']
    emr_client = EMRClient(client)
    emr_client.set_timeout(timeout)

    click.echo(f"🔍 正在查询EMR节点详情: {cluster_id}")

    try:
        result = emr_client.get_group_and_host_by_condition_v2(
            cluster_id=cluster_id, node_state=node_state, select_key=select_key
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_node_detail_table(result, cluster_id)
        else:
            _display_node_detail_summary(result, cluster_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_node_detail_table(result: dict, cluster_id: str):
    """以表格形式显示节点详情"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    groups = return_obj if isinstance(return_obj, list) else [return_obj] if return_obj.get("id") else []

    click.echo(f"\n🖥️ EMR节点详情 (集群: {cluster_id})")
    click.echo("=" * 130)

    if not groups:
        click.echo("📭 未找到节点")
        return

    for g in groups:
        gtype = g.get("nodeGroupType", "N/A")
        gname = g.get("nodeGroupName", "N/A")
        click.echo(f"\n📌 节点组: {gtype} ({gname})")
        click.echo("-" * 130)

        hosts = g.get("clusterHostDtoList", [])
        if hosts:
            click.echo(f"{'主机名称':<22} {'管理IP':<16} {'内网IP':<16} {'公网IP':<16} {'状态':<8} {'角色':<20}")
            click.echo("-" * 130)
            for h in hosts:
                hostname = h.get("hostName", "N/A")[:20]
                manage_ip = h.get("manageIp", "N/A")[:14]
                service_ip = h.get("serviceIp", "N/A")[:14]
                public_ip = h.get("publicIp", "N/A")[:14]
                state_val = h.get("hostStateValue", "N/A")
                roles = ", ".join(h.get("deployRoleInstance", []))[:18]
                click.echo(f"{hostname:<22} {manage_ip:<16} {service_ip:<16} {public_ip:<16} {state_val:<8} {roles:<20}")
        else:
            click.echo("  📭 该节点组下无主机")


def _display_node_detail_summary(result: dict, cluster_id: str):
    """显示节点详情摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    groups = return_obj if isinstance(return_obj, list) else [return_obj] if return_obj.get("id") else []

    click.echo(f"\n🖥️ EMR节点详情摘要 (集群: {cluster_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")

    total_hosts = 0
    for g in groups:
        hosts = g.get("clusterHostDtoList", [])
        total_hosts += len(hosts)

    click.echo(f"📊 节点组数: {len(groups)}")
    click.echo(f"🖥️  总主机数: {total_hosts}")

    if groups:
        click.echo(f"\n📍 节点组:")
        for g in groups:
            gtype = g.get("nodeGroupType", "N/A")
            gname = g.get("nodeGroupName", "N/A")
            hosts = g.get("clusterHostDtoList", [])
            click.echo(f"   • {gtype} ({gname}): {len(hosts)}主机")
            for h in hosts:
                ip = h.get("serviceIp", "N/A")
                state = h.get("hostStateValue", "N/A")
                click.echo(f"      - {h.get('hostName', 'N/A')} ({ip}) - {state}")


# ========== 元数据命令 ==========

@emr.command('meta-overview')
@click.option('--cluster-id', '-i', required=True, help='集群ID (必需)')
@click.option('--timestamp', default=None, type=int, help='查询时间戳 (Unix秒，默认当前时间)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式')
@click.option('--timeout', default=30, help='请求超时时间(秒)')
@click.pass_context
def meta_overview(ctx, cluster_id: str, timestamp: int, output_format: str, timeout: int):
    """
    查询EMR集群Hive元数据概览

    示例:
        ctyun emr meta-overview --cluster-id xxx
    """
    client = ctx.obj['client']
    emr_client = EMRClient(client)
    emr_client.set_timeout(timeout)

    if timestamp is None:
        timestamp = int(time.time())

    click.echo(f"📊 正在查询EMR元数据概览: {cluster_id}")

    try:
        result = emr_client.meta_overview(cluster_id=cluster_id, timestamp=timestamp)

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_meta_overview_table(result, cluster_id)
        else:
            _display_meta_overview_summary(result, cluster_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_meta_overview_table(result: dict, cluster_id: str):
    """以表格形式显示元数据概览"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    obj = result.get("returnObj", {})

    click.echo(f"\n📊 EMR Hive元数据概览 (集群: {cluster_id})")
    click.echo("=" * 60)

    db_cnt = obj.get("databaseCnt", 0)
    table_cnt = obj.get("tableCnt", 0)
    storage = obj.get("storageCnt", 0)
    file_cnt = obj.get("fileCnt", 0)

    click.echo(f"  {'数据库总数':<15}: {db_cnt}")
    click.echo(f"  {'表总数':<15}: {table_cnt}")
    click.echo(f"  {'总存储量':<15}: {_format_bytes(storage)}")
    click.echo(f"  {'文件总数':<15}: {file_cnt}")

    user_metas = obj.get("userQuotaMetas", [])
    if user_metas:
        click.echo(f"\n👤 用户级存储统计:")
        click.echo("-" * 50)
        click.echo(f"{'用户':<20} {'存储量':<20}")
        click.echo("-" * 50)
        for um in user_metas:
            owner = um.get("owner", "N/A")[:18]
            storage_cnt = um.get("storageCnt", 0)
            click.echo(f"{owner:<20} {_format_bytes(storage_cnt):<20}")


def _display_meta_overview_summary(result: dict, cluster_id: str):
    """显示元数据概览摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    obj = result.get("returnObj", {})

    click.echo(f"\n📊 EMR Hive元数据概览摘要 (集群: {cluster_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📚 数据库总数: {obj.get('databaseCnt', 0)}")
    click.echo(f"📋 表总数: {obj.get('tableCnt', 0)}")
    click.echo(f"💾 总存储量: {_format_bytes(obj.get('storageCnt', 0))}")
    click.echo(f"📁 文件总数: {obj.get('fileCnt', 0)}")

    user_metas = obj.get("userQuotaMetas", [])
    if user_metas:
        click.echo(f"\n👤 用户级存储统计 ({len(user_metas)}个用户):")
        for um in user_metas:
            click.echo(f"   • {um.get('owner', 'N/A')}: {_format_bytes(um.get('storageCnt', 0))}")


@emr.command('meta-table')
@click.option('--cluster-id', '-i', required=True, help='集群ID (必需)')
@click.option('--database', '-d', required=True, help='Hive库名 (必需)')
@click.option('--table', '-t', required=True, help='Hive表名 (必需)')
@click.option('--timestamp', default=None, type=int, help='查询时间戳 (Unix秒，默认当前时间)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式')
@click.option('--timeout', default=30, help='请求超时时间(秒)')
@click.pass_context
def meta_table(ctx, cluster_id: str, database: str, table: str,
               timestamp: int, output_format: str, timeout: int):
    """
    查询EMR集群指定Hive表的元数据信息

    示例:
        ctyun emr meta-table --cluster-id xxx --database test_db --table test_table
    """
    client = ctx.obj['client']
    emr_client = EMRClient(client)
    emr_client.set_timeout(timeout)

    if timestamp is None:
        timestamp = int(time.time())

    click.echo(f"📋 正在查询表元数据: {database}.{table}")

    try:
        result = emr_client.meta_table_info(
            cluster_id=cluster_id, timestamp=timestamp,
            database_name=database, table_name=table
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_meta_table_table(result, database, table)
        else:
            _display_meta_table_summary(result, database, table)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_meta_table_table(result: dict, database: str, table: str):
    """以表格形式显示表元数据"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    obj = result.get("returnObj", {})

    click.echo(f"\n📋 Hive表元数据 (集群: {obj.get('clusterId', 'N/A')})")
    click.echo("=" * 60)

    click.echo(f"  {'数据库':<15}: {obj.get('databaseName', 'N/A')}")
    click.echo(f"  {'表名':<15}: {obj.get('tableName', 'N/A')}")
    click.echo(f"  {'存储路径':<15}: {obj.get('hivePath', 'N/A')}")
    click.echo(f"  {'文件数':<15}: {obj.get('fileCnt', 0)}")
    click.echo(f"  {'存储量':<15}: {_format_bytes(obj.get('storageCnt', 0))}")
    click.echo(f"  {'平均文件大小':<15}: {_format_bytes(obj.get('avgStorageCnt', 0))}")
    click.echo(f"  {'最后访问时间':<15}: {obj.get('lastAccessTime', 'N/A')}")
    click.echo(f"  {'外部表':<15}: {'是' if obj.get('isExternalTable') else '否'}")
    click.echo(f"  {'分区表':<15}: {'是' if obj.get('isPartitionTable') else '否'}")
    click.echo(f"  {'分区数':<15}: {obj.get('partitionCnt', 0)}")
    click.echo(f"  {'误删除':<15}: {'是' if obj.get('isMisDelete') else '否'}")

    # 分区统计
    ice_file = obj.get("iceFileCnt", 0)
    cold_file = obj.get("coldFileCnt", 0)
    empty_pt = obj.get("emptyFilePtCnt", 0)
    small_pt = obj.get("smallFilePtCnt", 0)

    if any([ice_file, cold_file, empty_pt, small_pt]):
        click.echo(f"\n📊 分区统计:")
        click.echo("-" * 50)
        if ice_file:
            click.echo(f"  冰分区文件: {ice_file} ({_format_bytes(obj.get('iceStorageCnt', 0))})")
        if cold_file:
            click.echo(f"  冷分区文件: {cold_file} ({_format_bytes(obj.get('coldStorageCnt', 0))})")
        if empty_pt:
            click.echo(f"  空白文件分区: {empty_pt} ({obj.get('emptyFilePtFileCnt', 0)}文件)")
        if small_pt:
            click.echo(f"  小文件分区: {small_pt} ({obj.get('smallFilePtFileCnt', 0)}文件)")


def _display_meta_table_summary(result: dict, database: str, table: str):
    """显示表元数据摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    obj = result.get("returnObj", {})

    click.echo(f"\n📋 Hive表元数据摘要 ({database}.{table})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📁 存储路径: {obj.get('hivePath', 'N/A')}")
    click.echo(f"📊 文件数: {obj.get('fileCnt', 0)} | 存储量: {_format_bytes(obj.get('storageCnt', 0))}")
    click.echo(f"📐 平均文件大小: {_format_bytes(obj.get('avgStorageCnt', 0))}")
    click.echo(f"⏰ 最后访问: {obj.get('lastAccessTime', 'N/A')}")
    click.echo(f"🔖 外部表: {'是' if obj.get('isExternalTable') else '否'} | 分区表: {'是' if obj.get('isPartitionTable') else '否'}")
    click.echo(f"📂 分区数: {obj.get('partitionCnt', 0)}")


def _format_bytes(size: int) -> str:
    """格式化字节大小"""
    if size is None or size == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} EB"
