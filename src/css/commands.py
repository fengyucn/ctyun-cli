"""
云搜索服务(CSS)命令行接口
"""

import click
import json
import sys
from typing import Optional

from .client import CSSClient


# CSS实例状态映射
_INSTANCE_STATE_MAP = {
    1: "创建中", 2: "运行中", 3: "处理中", 4: "释放中",
    5: "已销毁", 6: "异常", 7: "处理中(重启)", 8: "处理中(扩容)",
    10: "已冻结", 11: "处理中(重置密码)", 12: "处理中(配置变更)",
    13: "处理中(升配)", 14: "处理中(磁盘扩容)", 15: "处理中(开启备份)",
    16: "处理中(加装Logstash)", 17: "处理中(Logstash退订)",
    18: "处理中(开通云日志)", 19: "处理中(关闭云日志)",
}

_LOGSTASH_STATE_MAP = {
    1: "创建中", 2: "运行中", 4: "释放中", 5: "已销毁",
    6: "异常", 7: "处理中(重启)", 8: "处理中(扩容)",
    10: "已冻结", 13: "处理中(升配)", 14: "处理中(磁盘扩容)",
    18: "处理中(开通云日志)", 19: "处理中(关闭云日志)",
}


@click.group()
def css():
    """云搜索服务(CSS)管理"""
    pass


@css.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--type', '-t', type=click.Choice(['1', '2']), help='实例类型 (1:OpenSearch 2:Elasticsearch)')
@click.option('--name', '-n', help='实例名称')
@click.option('--project-id', help='企业项目ID')
@click.option('--status', '-s', multiple=True, type=int, help='实例状态 (可多次指定)')
@click.option('--page', '-p', default=1, help='页码，默认1')
@click.option('--size', default=10, help='每页大小，默认10')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def list_instances(ctx, region_id: str, type: str, name: str, project_id: str,
                   status: tuple, page: int, size: int, output_format: str, timeout: int):
    """
    查询CSS实例列表

    示例:
        ctyun css list --region-id xxx --type 1
        ctyun css list -r xxx --name test --status 2 --status 6
    """
    client = ctx.obj['client']
    css_client = CSSClient(client)
    css_client.set_timeout(timeout)

    click.echo(f"📋 正在查询CSS实例列表...")

    try:
        result = css_client.select_instance_page(
            region_id=region_id,
            page_index=page,
            page_size=size,
            cluster_name=name,
            cluster_type=int(type) if type else None,
            project_id=project_id,
            cluster_state_list=list(status) if status else None
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_instances_table(result)
        else:
            _display_instances_summary(result)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_instances_table(result: dict):
    """以表格形式显示实例列表"""
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
    page_index = return_obj.get("pageIndex", 1)
    page_size = return_obj.get("pageSize", 10)

    click.echo(f"\n📊 CSS实例列表 (共{total}条，第{page_index}页，每页{page_size}条)")
    click.echo("=" * 125)

    if not records:
        click.echo("📭 未找到实例")
        return

    click.echo(f"{'实例ID':<38} {'名称':<20} {'状态':<12} {'类型':<14} {'版本':<8} {'付费':<8} {'创建时间':<20}")
    click.echo("-" * 125)

    for inst in records:
        inst_id = inst.get("clusterId", "N/A")[:36]
        name = inst.get("clusterName", "N/A")[:18]
        state_type = inst.get("clusterStateType", 0)
        state = _INSTANCE_STATE_MAP.get(state_type, f"未知({state_type})")
        type_name = inst.get("clusterTypeName", "N/A")[:12]
        version = inst.get("clusterTypeVersion", "N/A")[:6]
        pay = inst.get("payType", "N/A")[:6]
        create_time = inst.get("createTime", "N/A")
        click.echo(f"{inst_id:<38} {name:<20} {state:<12} {type_name:<14} {version:<8} {pay:<8} {create_time:<20}")


def _display_instances_summary(result: dict):
    """显示实例列表摘要"""
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

    click.echo(f"\n📊 CSS实例列表摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📋 总实例数: {total}")
    click.echo(f"📄 当前显示: {len(records)}个")

    if records:
        click.echo(f"\n🏷️ 实例列表:")
        for i, inst in enumerate(records, 1):
            state_type = inst.get("clusterStateType", 0)
            state = _INSTANCE_STATE_MAP.get(state_type, f"未知({state_type})")
            name = inst.get("clusterName", "N/A")
            inst_id = inst.get("clusterId", "N/A")
            type_name = inst.get("clusterTypeName", "N/A")
            version = inst.get("clusterTypeVersion", "N/A")
            storage = inst.get("storageUsage", "N/A")

            emoji = "🟢" if state_type == 2 else "🔴" if state_type in [5, 6] else "🟡"
            click.echo(f"   {i}. {emoji} {name}")
            click.echo(f"      ID: {inst_id}")
            click.echo(f"      状态: {state} | 类型: {type_name} {version} | 存储: {storage}")


@css.command('describe')
@click.option('--cluster-id', '-i', required=True, help='实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def describe_instance(ctx, cluster_id: str, output_format: str, timeout: int):
    """
    查询CSS实例详情

    示例:
        ctyun css describe --cluster-id OpenSearch-xxx
    """
    client = ctx.obj['client']
    css_client = CSSClient(client)
    css_client.set_timeout(timeout)

    click.echo(f"🔍 正在查询CSS实例详情: {cluster_id}")

    try:
        result = css_client.get_cluster_by_id(cluster_id)

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_instance_detail_table(result, cluster_id)
        else:
            _display_instance_detail_summary(result, cluster_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_instance_detail_table(result: dict, cluster_id: str):
    """以表格形式显示实例详情"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    inst = result.get("returnObj", {})

    click.echo(f"\n📍 CSS实例详情 (实例: {cluster_id})")
    click.echo("=" * 60)

    click.echo("\n📋 基本信息:")
    click.echo("-" * 55)
    basic = [
        ("实例名称", inst.get("clusterName", "N/A")),
        ("健康状态", inst.get("state", "N/A")),
        ("类型", f"{inst.get('clusterTypeName', 'N/A')} ({inst.get('clusterTypeVersion', 'N/A')})"),
        ("付费类型", inst.get("payType", "N/A")),
        ("资源池", inst.get("regionName", "N/A")),
        ("可用区", inst.get("azName", "N/A")),
        ("VPC", inst.get("vpcName", "N/A")),
        ("子网", inst.get("subnetName", "N/A")),
        ("安全组", inst.get("securityGroupnName", "N/A")),
    ]
    for k, v in basic:
        click.echo(f"  {k:<12}: {v}")

    click.echo("\n⚙️ 规格信息:")
    click.echo("-" * 55)
    spec = [
        ("CPU", f"{inst.get('cpuNum', 'N/A')}核"),
        ("内存", f"{inst.get('memory', 'N/A')}GB"),
        ("主机数", inst.get("hostNum", "N/A")),
        ("磁盘", f"{inst.get('diskVolumn', 'N/A')}GB"),
        ("CPU架构", inst.get("cpuInfo", "N/A")),
    ]
    for k, v in spec:
        click.echo(f"  {k:<12}: {v}")

    # 节点信息
    for node_type, key, label in [
        ("路由节点", "routerHostInfo", "routerHostInfo"),
        ("数据节点", "dataHostInfos", "dataHostInfos"),
        ("专属Master", "exclusiveMasterHostInfos", "exclusiveMasterHostInfos"),
        ("协调节点", "coordinateHostInfos", "coordinateHostInfos"),
        ("冷数据节点", "coldHostInfos", "coldHostInfos"),
    ]:
        nodes = inst.get(key, [])
        if nodes:
            click.echo(f"\n🔗 {node_type}:")
            click.echo("-" * 55)
            if isinstance(nodes, dict):
                nodes = [nodes]
            for node in nodes:
                ip = node.get("hostIp", "N/A")
                state = node.get("state", "N/A")
                cpu = node.get("cpuNum", "N/A")
                mem = node.get("memory", "N/A")
                disk = node.get("diskVolumn", "N/A")
                click.echo(f"  {ip} ({state}) - {cpu}核/{mem}GB/{disk}GB")


def _display_instance_detail_summary(result: dict, cluster_id: str):
    """显示实例详情摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != 200 and status_code != "200":
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    inst = result.get("returnObj", {})

    click.echo(f"\n📍 CSS实例详情摘要 (实例: {cluster_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"🏷️  名称: {inst.get('clusterName', 'N/A')}")
    click.echo(f"💚 健康状态: {inst.get('state', 'N/A')}")
    click.echo(f"🔧 类型: {inst.get('clusterTypeName', 'N/A')} {inst.get('clusterTypeVersion', 'N/A')}")
    click.echo(f"💰 付费: {inst.get('payType', 'N/A')}")
    click.echo(f"🌐 VPC: {inst.get('vpcName', 'N/A')}")
    click.echo(f"⚙️ 规格: {inst.get('cpuNum', 'N/A')}核/{inst.get('memory', 'N/A')}GB/{inst.get('hostNum', 'N/A')}主机/{inst.get('diskVolumn', 'N/A')}GB磁盘")


@css.command('logstash-list')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--name', '-n', help='实例名称')
@click.option('--project-id', help='企业项目ID')
@click.option('--status', '-s', multiple=True, type=int, help='实例状态 (可多次指定)')
@click.option('--page', '-p', default=1, help='页码，默认1')
@click.option('--size', default=10, help='每页大小，默认10')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def list_logstash(ctx, region_id: str, name: str, project_id: str,
                  status: tuple, page: int, size: int, output_format: str, timeout: int):
    """
    查询CSS Logstash实例列表

    示例:
        ctyun css logstash-list --region-id xxx
        ctyun css logstash-list -r xxx --name test --status 2
    """
    client = ctx.obj['client']
    css_client = CSSClient(client)
    css_client.set_timeout(timeout)

    click.echo(f"📋 正在查询CSS Logstash实例列表...")

    try:
        result = css_client.select_logstash_page(
            region_id=region_id,
            page_index=page,
            page_size=size,
            cluster_name=name,
            project_id=project_id,
            cluster_state_list=list(status) if status else None
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_logstash_table(result)
        else:
            _display_logstash_summary(result)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_logstash_table(result: dict):
    """以表格形式显示Logstash实例列表"""
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

    click.echo(f"\n📊 CSS Logstash实例列表 (共{total}条)")
    click.echo("=" * 120)

    if not records:
        click.echo("📭 未找到实例")
        return

    click.echo(f"{'实例ID':<38} {'名称':<20} {'状态':<12} {'版本':<10} {'管道':<8} {'节点':<6} {'付费':<8} {'关联实例':<20}")
    click.echo("-" * 120)

    for inst in records:
        inst_id = inst.get("clusterId", "N/A")[:36]
        name = inst.get("clusterName", "N/A")[:18]
        state_type = inst.get("clusterStateType", 0)
        state = _LOGSTASH_STATE_MAP.get(state_type, f"未知({state_type})")
        version = inst.get("clusterTypeVersion", "N/A")[:8]
        pipe = f"{inst.get('runningPipeNum', 0)}/{inst.get('pipeNum', 0)}"
        node = inst.get("nodeNum", "N/A")
        pay = inst.get("payType", "N/A")[:6]
        related = inst.get("relatedClusterName", "N/A")[:18]
        click.echo(f"{inst_id:<38} {name:<20} {state:<12} {version:<10} {pipe:<8} {node:<6} {pay:<8} {related:<20}")


def _display_logstash_summary(result: dict):
    """显示Logstash实例列表摘要"""
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

    click.echo(f"\n📊 CSS Logstash实例列表摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📋 总实例数: {total}")
    click.echo(f"📄 当前显示: {len(records)}个")

    if records:
        click.echo(f"\n🏷️ 实例列表:")
        for i, inst in enumerate(records, 1):
            state_type = inst.get("clusterStateType", 0)
            state = _LOGSTASH_STATE_MAP.get(state_type, f"未知({state_type})")
            name = inst.get("clusterName", "N/A")
            inst_id = inst.get("clusterId", "N/A")
            version = inst.get("clusterTypeVersion", "N/A")
            pipe = f"{inst.get('runningPipeNum', 0)}/{inst.get('pipeNum', 0)}"
            related = inst.get("relatedClusterName", "N/A")

            emoji = "🟢" if state_type == 2 else "🔴" if state_type in [5, 6] else "🟡"
            click.echo(f"   {i}. {emoji} {name}")
            click.echo(f"      ID: {inst_id}")
            click.echo(f"      状态: {state} | 版本: {version} | 管道: {pipe}")
            if related and related != "N/A":
                click.echo(f"      关联实例: {related}")
