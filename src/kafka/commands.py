"""
分布式消息服务(Kafka)命令行接口
"""

import click
import json
import sys
from typing import Optional

from .client import KafkaClient


# Kafka实例状态映射
_INSTANCE_STATUS_MAP = {
    1: "运行中", 2: "已过期", 3: "已注销", 4: "变更中",
    5: "已退订", 6: "开通中", 7: "已取消", 8: "已停止",
    9: "弹性IP处理中", 10: "重启中", 11: "重启失败",
    12: "升级中", 13: "已欠费", 101: "开通失败",
}


@click.group()
def kafka():
    """分布式消息服务Kafka管理"""
    pass


@kafka.command('list')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--instance-id', '-i', help='实例ID')
@click.option('--name', '-n', help='实例名称')
@click.option('--exact-match', is_flag=True, help='精确匹配实例名称')
@click.option('--status', type=int, help='实例状态 (1:运行中 2:已过期 3:已注销 ...)')
@click.option('--project-id', help='企业项目ID')
@click.option('--page', '-p', default=1, help='页码，默认1')
@click.option('--size', '-s', default=10, help='每页大小，默认10')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def list_instances(ctx, region_id: str, instance_id: str, name: str,
                   exact_match: bool, status: int, project_id: str,
                   page: int, size: int, output_format: str, timeout: int):
    """
    查询Kafka实例列表

    示例:
        ctyun kafka list --region-id bb9fdb42056f11eda1610242ac110002
        ctyun kafka list -r xxx --name test --exact-match
        ctyun kafka list -r xxx --status 1 --page 1 --size 20
    """
    client = ctx.obj['client']
    kafka_client = KafkaClient(client)
    kafka_client.set_timeout(timeout)

    click.echo(f"📋 正在查询Kafka实例列表...")

    try:
        result = kafka_client.inst_query(
            region_id=region_id,
            prod_inst_id=instance_id,
            name=name,
            exact_match_name=exact_match,
            status=status,
            outer_project_id=project_id,
            page_num=page,
            page_size=size
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
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", [])
    total = return_obj.get("total", 0)
    page_num = return_obj.get("pageNum", 1)
    page_size = return_obj.get("pageSize", 10)

    click.echo(f"\n📊 Kafka实例列表 (共{total}条，第{page_num}页，每页{page_size}条)")
    click.echo("=" * 130)

    if not data:
        click.echo("📭 未找到实例")
        return

    click.echo(f"{'实例ID':<36} {'名称':<20} {'状态':<10} {'引擎':<8} {'版本':<8} {'规格':<22} {'VPC':<15} {'创建时间':<20}")
    click.echo("-" * 130)

    for inst in data:
        inst_id = inst.get("prodInstId", "N/A")[:34]
        name = inst.get("instanceName", "N/A")[:18]
        status = inst.get("status", 0)
        status_name = _INSTANCE_STATUS_MAP.get(status, f"未知({status})")
        engine = inst.get("mqEngineType", "N/A")
        version = inst.get("version", "N/A")[:6]
        spec = inst.get("specifications", "N/A")[:20]
        vpc = inst.get("network", "N/A")[:13]
        create_time = inst.get("createTime", "N/A")[:18]

        click.echo(f"{inst_id:<36} {name:<20} {status_name:<10} {engine:<8} {version:<8} {spec:<22} {vpc:<15} {create_time:<20}")


def _display_instances_summary(result: dict):
    """显示实例列表摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", [])
    total = return_obj.get("total", 0)

    click.echo(f"\n📊 Kafka实例列表摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📋 总实例数: {total}")
    click.echo(f"📄 当前显示: {len(data)}个")

    if data:
        click.echo(f"\n🏷️ 实例列表:")
        for i, inst in enumerate(data, 1):
            status = inst.get("status", 0)
            status_name = _INSTANCE_STATUS_MAP.get(status, f"未知({status})")
            name = inst.get("instanceName", "N/A")
            inst_id = inst.get("prodInstId", "N/A")
            engine = inst.get("mqEngineType", "N/A")
            version = inst.get("version", "N/A")
            spec = inst.get("specifications", "N/A")

            emoji = "🟢" if status == 1 else "🔴" if status in [2, 3, 5, 7, 8] else "🟡"
            click.echo(f"   {i}. {emoji} {name}")
            click.echo(f"      ID: {inst_id}")
            click.echo(f"      状态: {status_name} | 引擎: {engine} {version} | 规格: {spec}")


@kafka.command('node-status')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--instance-id', '-i', required=True, help='实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def node_status(ctx, region_id: str, instance_id: str, output_format: str, timeout: int):
    """
    查看Kafka实例节点状态

    示例:
        ctyun kafka node-status --region-id xxx --instance-id xxx
    """
    client = ctx.obj['client']
    kafka_client = KafkaClient(client)
    kafka_client.set_timeout(timeout)

    click.echo(f"🔍 正在查看实例节点状态: {instance_id}")

    try:
        result = kafka_client.node_status(region_id=region_id, prod_inst_id=instance_id)

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_node_status_table(result, instance_id)
        else:
            _display_node_status_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_node_status_table(result: dict, instance_id: str):
    """以表格形式显示节点状态"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", [])

    click.echo(f"\n🔍 Kafka实例节点状态 (实例: {instance_id})")
    click.echo("=" * 50)

    if not data:
        click.echo("📭 无节点信息")
        return

    click.echo(f"{'节点IP':<20} {'状态':<10}")
    click.echo("-" * 50)

    for node in data:
        ip = node.get("ip", "N/A")
        status = node.get("status", False)
        status_text = "✅ 正常" if status else "❌ 异常"
        click.echo(f"{ip:<20} {status_text:<10}")


def _display_node_status_summary(result: dict, instance_id: str):
    """显示节点状态摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", [])

    click.echo(f"\n🔍 Kafka实例节点状态摘要 (实例: {instance_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📊 节点总数: {len(data)}")

    normal = sum(1 for n in data if n.get("status"))
    abnormal = len(data) - normal

    click.echo(f"🟢 正常节点: {normal}")
    click.echo(f"🔴 异常节点: {abnormal}")

    if data:
        click.echo(f"\n📍 节点详情:")
        for node in data:
            ip = node.get("ip", "N/A")
            status = node.get("status", False)
            emoji = "🟢" if status else "🔴"
            click.echo(f"   {emoji} {ip} ({'正常' if status else '异常'})")


@kafka.command('floating-ips')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--page', '-p', default=1, help='页码，默认1')
@click.option('--size', '-s', default=10, help='每页大小，默认10')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def floating_ips(ctx, region_id: str, page: int, size: int,
                 output_format: str, timeout: int):
    """
    查询Kafka可绑定的弹性IP列表

    示例:
        ctyun kafka floating-ips --region-id xxx
        ctyun kafka floating-ips -r xxx --page 1 --size 20
    """
    client = ctx.obj['client']
    kafka_client = KafkaClient(client)
    kafka_client.set_timeout(timeout)

    click.echo(f"🌐 正在查询弹性IP列表...")

    try:
        result = kafka_client.page_query_floatingips(
            region_id=region_id, page_num=page, page_size=size
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_floating_ips_table(result)
        else:
            _display_floating_ips_summary(result)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_floating_ips_table(result: dict):
    """以表格形式显示弹性IP列表"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", {})
    total = data.get("total", 0)
    pages = data.get("pages", 1)
    ip_list = data.get("list", [])

    click.echo(f"\n🌐 弹性IP列表 (共{total}条，{pages}页)")
    click.echo("=" * 80)

    if not ip_list:
        click.echo("📭 未找到弹性IP")
        return

    click.echo(f"{'UUID':<25} {'IP地址':<18} {'状态':<10} {'创建时间':<20}")
    click.echo("-" * 80)

    for ip in ip_list:
        uuid = ip.get("fipUuid", "N/A")[:23]
        address = ip.get("floatingIpAddress", "N/A")
        status = ip.get("status", 0)
        status_text = "可用" if status == 1 else "不可用"
        create_date = ip.get("createDate", "N/A")
        click.echo(f"{uuid:<25} {address:<18} {status_text:<10} {create_date:<20}")


def _display_floating_ips_summary(result: dict):
    """显示弹性IP列表摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", {})
    total = data.get("total", 0)
    ip_list = data.get("list", [])

    click.echo(f"\n🌐 弹性IP列表摘要")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📋 总记录数: {total}")

    available = sum(1 for ip in ip_list if ip.get("status") == 1)
    click.echo(f"🟢 可用: {available}")
    click.echo(f"🔴 不可用: {len(ip_list) - available}")

    if ip_list:
        click.echo(f"\n📍 IP列表:")
        for ip in ip_list:
            address = ip.get("floatingIpAddress", "N/A")
            uuid = ip.get("fipUuid", "N/A")
            status = ip.get("status", 0)
            emoji = "🟢" if status == 1 else "🔴"
            click.echo(f"   {emoji} {address} ({uuid})")


@kafka.command('config')
@click.option('--region-id', '-r', required=True, help='资源池ID (必需)')
@click.option('--instance-id', '-i', required=True, help='实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
def instance_config(ctx, region_id: str, instance_id: str,
                    output_format: str, timeout: int):
    """
    获取Kafka实例配置

    示例:
        ctyun kafka config --region-id xxx --instance-id xxx
    """
    client = ctx.obj['client']
    kafka_client = KafkaClient(client)
    kafka_client.set_timeout(timeout)

    click.echo(f"⚙️ 正在获取实例配置: {instance_id}")

    try:
        result = kafka_client.get_instance_config(
            region_id=region_id, prod_inst_id=instance_id
        )

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'table':
            _display_config_table(result, instance_id)
        else:
            _display_config_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询失败: {str(e)}", err=True)
        sys.exit(1)


def _display_config_table(result: dict, instance_id: str):
    """以表格形式显示实例配置"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", [])

    click.echo(f"\n⚙️ Kafka实例配置 (实例: {instance_id})")
    click.echo("=" * 110)

    if not data:
        click.echo("📭 无配置信息")
        return

    click.echo(f"{'配置名称':<35} {'当前值':<12} {'默认值':<12} {'类型':<10} {'配置类型':<10} {'有效值':<15}")
    click.echo("-" * 110)

    for cfg in data:
        name = cfg.get("name", "N/A")[:33]
        value = str(cfg.get("value", "N/A"))[:10]
        default = str(cfg.get("default_value", "N/A"))[:10]
        var_type = cfg.get("varType", "N/A")[:8]
        config_type = cfg.get("config_type", "N/A")[:8]
        valid = cfg.get("valid_values", "N/A")[:13]
        click.echo(f"{name:<35} {value:<12} {default:<12} {var_type:<10} {config_type:<10} {valid:<15}")


def _display_config_summary(result: dict, instance_id: str):
    """显示实例配置摘要"""
    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    status_code = result.get("statusCode")
    if status_code != "800" and status_code != 800:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    return_obj = result.get("returnObj", {})
    data = return_obj.get("data", [])

    click.echo(f"\n⚙️ Kafka实例配置摘要 (实例: {instance_id})")
    click.echo("=" * 60)
    click.echo(f"✅ 查询成功")
    click.echo(f"📊 配置项总数: {len(data)}")

    static_count = sum(1 for c in data if c.get("config_type") == "static")
    dynamic_count = sum(1 for c in data if c.get("config_type") == "dynamic")
    click.echo(f"🔒 静态配置(需重启): {static_count}")
    click.echo(f"🔄 动态配置(无需重启): {dynamic_count}")

    if data:
        click.echo(f"\n📋 重要配置:")
        important_keys = ['log.retention.hours', 'num.partitions', 'default.replication.factor']
        for cfg in data:
            if cfg.get("name") in important_keys:
                name = cfg.get("name", "N/A")
                value = cfg.get("value", "N/A")
                desc = cfg.get("desc", "")[:30]
                click.echo(f"   • {name}: {value} ({desc})")
