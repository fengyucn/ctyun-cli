"""
Redis分布式缓存服务CLI命令
提供Redis实例可用区查询等命令行功能
"""

import click
import json
import sys
from typing import Optional

from .client import RedisClient


def validate_credentials(func):
    """验证认证信息的装饰器"""
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()

        # 首先尝试从客户端对象获取凭证
        client = ctx.obj.get('client')
        if client and hasattr(client, 'access_key') and hasattr(client, 'secret_key'):
            access_key = client.access_key
            secret_key = client.secret_key
        else:
            # 如果没有客户端对象，尝试从上下文直接获取
            access_key = ctx.obj.get('access_key')
            secret_key = ctx.obj.get('secret_key')

        if not access_key or not secret_key:
            click.echo("❌ 错误: 未配置Access Key或Secret Key", err=True)
            click.echo("请使用 --access-key 和 --secret-key 参数，或通过 'ctyun-cli configure' 配置", err=True)
            sys.exit(1)

        return func(*args, **kwargs)
    return wrapper


@click.group(name='redis')
def redis_group():
    """Redis分布式缓存服务管理"""
    pass


@redis_group.command('zones')
@click.option('--region-id', '-r', default="200000001852", help='区域ID (默认: 200000001852)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def get_zones(ctx, region_id: str, output_format: str, timeout: int):
    """
    查询Redis实例可用区信息

    示例:
        ctyun redis zones
        ctyun redis zones --region-id 200000001852 --format json
        ctyun redis zones -r 200000001852 -f summary -t 60
    """
    from redis.client import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)

    click.echo(f"🔍 正在查询区域 {region_id} 的Redis可用区...")

    try:
        if output_format == 'summary':
            result = redis_client.get_zones_summary(region_id)
            _display_summary(result)
        else:
            result = redis_client.get_zones(region_id)

            if output_format == 'json':
                _display_json(result)
            else:
                _display_table(result, region_id)

    except Exception as e:
        click.echo(f"❌ 查询过程中发生异常: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('zones-multi')
@click.option('--regions', '-R', help='多个区域ID，用逗号分隔 (例如: 200000001852,200000001853)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def get_zones_multi(ctx, regions: Optional[str], output_format: str, timeout: int):
    """
    查询多个区域的Redis实例可用区信息

    示例:
        ctyun redis zones-multi --regions 200000001852,200000001853
        ctyun redis zones-multi -R 200000001852 -f json
    """
    # 获取凭证（validate_credentials装饰器已验证）
    from redis.client import RedisClient

    client = ctx.obj['client']

    # 默认查询主要区域
    if not regions:
        region_list = ["200000001852"]
    else:
        region_list = [r.strip() for r in regions.split(',') if r.strip()]

    click.echo(f"🚀 开始查询 {len(region_list)} 个区域的Redis可用区...")

    all_results = {}

    for i, region_id in enumerate(region_list, 1):
        click.echo(f"\n[{i}/{len(region_list)}] 查询区域: {region_id}")

        try:
            redis_client = RedisClient(client)
            redis_client.set_timeout(timeout)

            result = redis_client.get_zones_summary(region_id)
            all_results[region_id] = result

            if result['success']:
                click.echo(f"✅ 查询成功! 找到 {result['zones_count']} 个可用区")
            else:
                click.echo(f"❌ 查询失败: {result['message']}")

        except Exception as e:
            click.echo(f"❌ 查询异常: {str(e)}")
            all_results[region_id] = {
                'success': False,
                'message': f"查询异常: {str(e)}",
                'zones_count': 0,
                'zones': []
            }

    # 显示结果
    if output_format == 'json':
        _display_multi_json(all_results)
    else:
        _display_multi_summary(all_results)


def _display_table(result: dict, region_id: str):
    """以表格形式显示可用区信息"""
    click.echo("\n" + "="*80)
    click.echo(f"📍 Redis实例可用区查询结果 (区域: {region_id})")
    click.echo("="*80)

    if not result:
        click.echo("❌ 查询失败: 无响应数据")
        return

    if result.get("error"):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        if result.get('status_code'):
            click.echo(f"   HTTP状态码: {result['status_code']}")
        return

    if result.get("statusCode") == 800:
        # 成功响应，从returnObj.zoneList中获取数据
        return_obj = result.get("returnObj", {})
        zone_list_data = return_obj.get("zoneList", [])

        click.echo(f"📊 查询成功! 共找到 {len(zone_list_data)} 个可用区\n")

        if zone_list_data:
            click.echo("📍 可用区详细信息:")
            click.echo("-" * 80)
            click.echo(f"{'序号':<4} {'可用区ID':<35} {'可用区名称':<25} {'状态':<10}")
            click.echo("-" * 80)

            for i, zone_info in enumerate(zone_list_data, 1):
                if isinstance(zone_info, dict):
                    zone_id = zone_info.get("name", "N/A")
                    zone_name = zone_info.get("azDisplayName", "N/A")
                    zone_status = "available"  # Redis可用区通常都是可用的
                else:
                    zone_id = str(zone_info)
                    zone_name = "N/A"
                    zone_status = "N/A"

                # 截断过长的字段以适应表格
                zone_id_display = zone_id[:32] + "..." if len(zone_id) > 35 else zone_id
                zone_name_display = zone_name[:22] + "..." if len(zone_name) > 25 else zone_name

                click.echo(f"{i:<4} {zone_id_display:<35} {zone_name_display:<25} {zone_status:<10}")
        else:
            click.echo("ℹ️  该区域暂无可用的Redis实例可用区")
    else:
        error_msg = result.get("message", "未知错误")
        error_code = result.get("statusCode", "N/A")
        click.echo(f"❌ API查询失败 (错误码: {error_code}): {error_msg}")


def _display_json(result: dict):
    """以JSON格式显示结果"""
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


def _display_summary(result: dict):
    """显示摘要信息"""
    click.echo("\n" + "="*60)
    click.echo("📋 Redis实例可用区查询摘要")
    click.echo("="*60)

    click.echo(f"🏷️  区域ID: {result['region_id']}")
    click.echo(f"✅ 查询状态: {'成功' if result['success'] else '失败'}")
    click.echo(f"📢 结果消息: {result['message']}")

    if result['success']:
        click.echo(f"📈 可用区数量: {result['zones_count']}")

        if result['zones']:
            click.echo(f"\n📍 可用区列表:")
            for i, zone in enumerate(result['zones'], 1):
                zone_id = zone.get('zone_id', 'N/A')
                zone_name = zone.get('zone_name', 'N/A')
                zone_status = zone.get('zone_status', 'N/A')
                click.echo(f"   {i}. {zone_id}")
                click.echo(f"      名称: {zone_name}")
                click.echo(f"      状态: {zone_status}")
    else:
        if 'error_details' in result:
            click.echo(f"\n🔍 错误详情: {result['error_details']}")


def _display_multi_json(all_results: dict):
    """以JSON格式显示多区域查询结果"""
    click.echo(json.dumps(all_results, indent=2, ensure_ascii=False))


def _display_multi_summary(all_results: dict):
    """显示多区域查询摘要"""
    click.echo("\n" + "="*80)
    click.echo("📍 多区域Redis实例可用区查询结果汇总")
    click.echo("="*80)

    success_count = sum(1 for r in all_results.values() if r['success'])
    total_count = len(all_results)
    total_zones = sum(r['zones_count'] for r in all_results.values())

    click.echo(f"📊 查询统计: 成功 {success_count}/{total_count} 个区域")
    click.echo(f"📈 总可用区数量: {total_zones}")

    for region_id, result in all_results.items():
        status_icon = "✅" if result['success'] else "❌"
        click.echo(f"\n{status_icon} 区域: {region_id}")
        click.echo(f"   状态: {'成功' if result['success'] else '失败'}")
        click.echo(f"   消息: {result['message']}")

        if result['success']:
            click.echo(f"   可用区数量: {result['zones_count']}")


# ========== 查询类命令 ==========

@redis_group.command('list')
@click.option('--region-id', '-r', default=None, help='区域ID (默认使用配置中的区域)')
@click.option('--name', '-n', help='实例名称，支持模糊查询')
# status参数在新API中不支持，已移除
@click.option('--page', '-p', default=1, help='页码，默认1')
@click.option('--size', '--page-size', default=20, help='每页数量，默认20，最大100')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def list_instances(ctx, region_id: str, name: str, page: int, size: int, output_format: str, timeout: int):
    """
    查询Redis实例列表

    示例:
        ctyun redis list                          # 列出所有实例
        ctyun redis list --name prod              # 模糊查询名称包含prod的实例
        ctyun redis list --status Running         # 只列出运行中的实例
        ctyun redis list --page 2 --size 10       # 第2页，每页10条
        ctyun redis list -f json                   # JSON格式输出
    """
    from redis.client import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)

    try:
        click.echo("📋 正在查询Redis实例列表...")

        result = redis_client.describe_instances(
            region_id=region_id or "200000001852",  # 使用默认区域ID
            instance_name=name,
            page_num=page,
            page_size=size
        )

        if result and result.get('returnObj'):
            # 新API使用rows而不是instances，使用total而不是totalCount
            instances = result['returnObj'].get('rows', [])
            total_count = result['returnObj'].get('total', 0)
            page_num = page  # 新API不返回页码信息
            page_size = size

            if output_format == 'json':
                click.echo(json.dumps(result, indent=2, ensure_ascii=False))

            elif output_format == 'table':
                if instances:
                    click.echo(f"\n{'='*80}")
                    click.echo(f"📋 Redis实例列表 (第{page_num}页，共{total_count}个实例)")
                    click.echo(f"{'='*80}")

                    # 表头
                    headers = ['序号', '实例ID', '实例名称', '状态', '版本', '类型', '规格', '创建时间']
                    click.echo(f"{'序号':<5} {'实例ID':<30} {'实例名称':<20} {'状态':<12} {'版本':<8} {'类型':<8} {'规格':<15} {'创建时间':<20}")
                    click.echo("-" * 120)

                    # 数据行 - 适配新API的字段名
                    for i, instance in enumerate(instances, 1):
                        instance_id = instance.get('prodInstId', 'N/A')[:28]
                        instance_name = instance.get('instanceName', 'N/A')[:18]
                        status_ = instance.get('statusName', 'N/A')  # 新API使用statusName
                        version = instance.get('engineVersion', 'N/A')
                        arch_type = instance.get('archTypeName', 'N/A')  # 新API使用archTypeName
                        capacity = instance.get('capacity', 'N/A')  # 新API使用capacity
                        create_time = instance.get('createTime', 'N/A')[:18]

                        click.echo(f"{i:<5} {instance_id:<30} {instance_name:<20} {status_:<12} {version:<8} {arch_type:<8} {capacity:<15} {create_time:<20}")

                else:
                    click.echo("📭 未找到符合条件的Redis实例")

            elif output_format == 'summary':
                click.echo(f"\n{'='*60}")
                click.echo(f"📋 Redis实例列表摘要")
                click.echo(f"{'='*60}")
                click.echo(f"📊 总实例数: {total_count}")
                click.echo(f"📄 当前页: 第{page_num}页 (每页{page_size}条)")
                click.echo(f"📋 显示实例: {len(instances)}个")

                if instances:
                    # 按状态统计 - 使用新API的statusName字段
                    status_count = {}
                    for instance in instances:
                        status_ = instance.get('statusName', 'Unknown')
                        status_count[status_] = status_count.get(status_, 0) + 1

                    click.echo(f"\n📈 状态分布:")
                    for status_, count in sorted(status_count.items()):
                        emoji = {"Running": "🟢", "Stopped": "🔴", "Creating": "🟡", "Error": "❌"}.get(status_, "⚪")
                        click.echo(f"   {emoji} {status_}: {count}个")

                    click.echo(f"\n📝 实例详情:")
                    for i, instance in enumerate(instances[:5], 1):  # 只显示前5个
                        instance_name = instance.get('instanceName', 'N/A')
                        instance_id = instance.get('prodInstId', 'N/A')[:20]
                        status_ = instance.get('statusName', 'N/A')
                        version = instance.get('engineVersion', 'N/A')
                        capacity = instance.get('capacity', 'N/A')  # 新API使用capacity

                        emoji = {"Running": "🟢", "Stopped": "🔴", "Creating": "🟡", "Error": "❌"}.get(status_, "⚪")
                        click.echo(f"   {i}. {emoji} {instance_name} ({instance_id})")
                        click.echo(f"      状态: {status_} | 版本: {version} | 容量: {capacity}GB")

                    if len(instances) > 5:
                        click.echo(f"   ... 还有 {len(instances) - 5} 个实例未显示")
                else:
                    click.echo("📭 未找到符合条件的Redis实例")

        else:
            click.echo("❌ 查询Redis实例列表失败")
            if result:
                click.echo(f"错误信息: {result}")

    except Exception as e:
        click.echo(f"❌ 查询异常: {str(e)}")
        import traceback
        click.echo("详细错误信息:")
        click.echo(traceback.format_exc())


@redis_group.command('describe')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_instance(ctx, instance_id: str, output_format: str, timeout: int):
    """
    查询Redis实例基础详情

    示例:
        ctyun redis describe --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis describe -i xxx --format json
        ctyun redis describe -i xxx -f table -t 60
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)

    click.echo(f"🔍 正在查询Redis实例详情: {instance_id}")

    try:
        result = redis_client.describe_instances_overview(instance_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_instance_overview_table(result, instance_id)
        else:
            _display_instance_overview_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询实例详情失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('config')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--param-name', '-p', help='查询特定参数名称')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_config(ctx, instance_id: str, param_name: str, output_format: str, timeout: int):
    """
    查询Redis实例配置参数

    示例:
        ctyun redis config --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis config -i xxx --param-name maxmemory-policy
        ctyun redis config -i xxx -f json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    param_desc = f" (参数: {param_name})" if param_name else ""
    click.echo(f"🔧 正在查询Redis实例配置{param_desc}: {instance_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.describe_instance_config(instance_id, param_name)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_config_table(result, instance_id, param_name)
        else:
            _display_config_summary(result, instance_id, param_name)

    except Exception as e:
        click.echo(f"❌ 查询实例配置失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('monitor-items')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_monitor_items(ctx, instance_id: str, output_format: str, timeout: int):
    """
    查询Redis实例监控指标列表

    示例:
        ctyun redis monitor-items --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis monitor-items -i xxx -f json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    click.echo(f"📊 正在查询Redis监控指标列表: {instance_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.describe_history_monitor_items(instance_id)

        if output_format == 'json':
            _display_json(result)
        else:
            _display_monitor_items_table(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询监控指标列表失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('monitor-history')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--metric', '-m', required=True,
              type=click.Choice(['memory_fragmentation', 'memory_usage', 'cpu_util', 'connections', 'hit_rate']),
              help='监控指标名称')
@click.option('--start-time', '-s', help='开始时间 (格式: 2025-11-21T09:26:08Z)')
@click.option('--end-time', '-e', help='结束时间 (格式: 2025-11-25T09:26:08Z)')
@click.option('--hours', '-h', type=int, help='查询最近N小时的数据')
@click.option('--days', '-d', type=int, help='查询最近N天的数据')
@click.option('--period', type=int, default=300, help='数据聚合周期(秒，默认300)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_monitor_history(ctx, instance_id: str, metric: str, start_time: str, end_time: str,
                            hours: int, days: int, period: int, output_format: str, timeout: int):
    """
    查询Redis实例监控历史数据

    示例:
        ctyun redis monitor-history --instance-id xxx --metric memory_fragmentation --days 7
        ctyun redis monitor-history -i xxx -m memory_usage -h 24
        ctyun redis monitor-history -i xxx -m cpu_util -s "2025-11-21T09:26:08Z" -e "2025-11-25T09:26:08Z"
        ctyun redis monitor-history -i xxx -m memory_fragmentation --format json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    # 时间处理
    if not start_time or not end_time:
        import datetime
        now = datetime.datetime.utcnow()

        if hours:
            start_time_dt = now - datetime.timedelta(hours=hours)
            end_time_dt = now
        elif days:
            start_time_dt = now - datetime.timedelta(days=days)
            end_time_dt = now
        else:
            start_time_dt = now - datetime.timedelta(hours=24)  # 默认24小时
            end_time_dt = now

        start_time = start_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = end_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    click.echo(f"📈 正在查询Redis监控历史数据: {instance_id}")
    click.echo(f"   指标: {metric}")
    click.echo(f"   时间范围: {start_time} 至 {end_time}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.describe_instance_history_monitor_values(
            instance_id, metric, start_time, end_time, period
        )

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_monitor_history_table(result, instance_id, metric)
        else:
            _display_monitor_history_summary(result, instance_id, metric)

    except Exception as e:
        click.echo(f"❌ 查询监控历史数据失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('diagnose')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--node-name', '-n', help='节点名称 (可选)')
@click.option('--wait', '-w', is_flag=True, help='等待诊断完成并显示结果')
@click.option('--wait-timeout', type=int, default=120, help='等待诊断完成的超时时间(秒)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def diagnose_instance(ctx, instance_id: str, node_name: str, wait: bool, wait_timeout: int,
                      output_format: str, timeout: int):
    """
    执行Redis实例诊断分析

    示例:
        ctyun redis diagnose --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis diagnose -i xxx --node-name redis_6379_node --wait
        ctyun redis diagnose -i xxx --wait --format json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    node_desc = f" (节点: {node_name})" if node_name else ""
    click.echo(f"🔍 正在启动Redis实例诊断{node_desc}: {instance_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        # 启动诊断任务
        result = redis_client.do_analysis_instance_tasks(instance_id, node_name)

        if result.get("error"):
            click.echo(f"❌ 启动诊断失败: {result.get('message')}", err=True)
            sys.exit(1)

        if result.get("statusCode") == 800:
            task_id = result.get("returnObj", {}).get("taskId")
            click.echo(f"✅ 诊断任务启动成功")
            click.echo(f"📋 任务ID: {task_id}")

            if wait:
                click.echo(f"⏳ 等待诊断完成...")
                import time

                # 等待诊断完成
                start_time = time.time()
                while time.time() - start_time < wait_timeout:
                    time.sleep(5)

                    report_result = redis_client.query_analysis_instance_tasks_info(instance_id, task_id)

                    if report_result.get("statusCode") == 800:
                        return_obj = report_result.get("returnObj", {})
                        if return_obj.get("map"):
                            click.echo(f"✅ 诊断完成!")
                            _display_diagnosis_report(report_result, instance_id, output_format)
                            break
                    elif report_result.get("error"):
                        click.echo(f"❌ 查询诊断结果失败: {report_result.get('message')}", err=True)
                        break
                else:
                    click.echo(f"⏰ 诊断等待超时 ({wait_timeout}秒)")
                    click.echo(f"💡 请使用以下命令手动查询结果:")
                    click.echo(f"   ctyun redis diagnosis-report --instance-id {instance_id} --task-id {task_id}")
        else:
            click.echo(f"❌ 启动诊断失败: {result.get('message')}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ 诊断过程异常: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('diagnosis-report')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--task-id', '-t', required=True, help='诊断任务ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def query_diagnosis_report(ctx, instance_id: str, task_id: str, output_format: str, timeout: int):
    """
    查询Redis实例诊断分析报告详情

    示例:
        ctyun redis diagnosis-report --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c --task-id 20241125001
        ctyun redis diagnosis-report -i xxx -t xxx --format json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    click.echo(f"📋 正在查询Redis诊断报告: {instance_id}")
    click.echo(f"📋 任务ID: {task_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.query_analysis_instance_tasks_info(instance_id, task_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_diagnosis_report(result, instance_id, output_format)
        else:
            _display_diagnosis_report(result, instance_id, 'summary')

    except Exception as e:
        click.echo(f"❌ 查询诊断报告失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('clients')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--node-id', '-n', help='节点ID (可选)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def get_clients(ctx, instance_id: str, node_id: str, output_format: str, timeout: int):
    """
    查询Redis实例客户端会话列表

    示例:
        ctyun redis clients --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis clients -i xxx --node-id node-1
        ctyun redis clients -i xxx --format json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    node_desc = f" (节点: {node_id})" if node_id else ""
    click.echo(f"👥 正在查询Redis客户端会话{node_desc}: {instance_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.get_client_ip_info(instance_id, node_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_clients_table(result, instance_id, node_id)
        else:
            _display_clients_summary(result, instance_id, node_id)

    except Exception as e:
        click.echo(f"❌ 查询客户端会话失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('version')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_version(ctx, instance_id: str, output_format: str, timeout: int):
    """
    查询Redis实例版本信息

    示例:
        ctyun redis version --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis version -i xxx --format json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    click.echo(f"🔢 正在查询Redis实例版本信息: {instance_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.describe_instance_version(instance_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_version_table(result, instance_id)
        else:
            _display_version_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询版本信息失败: {str(e)}", err=True)
        sys.exit(1)


@redis_group.command('network')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_network(ctx, instance_id: str, output_format: str, timeout: int):
    """
    查询Redis实例网络信息

    示例:
        ctyun redis network --instance-id 0d200ac9745c4a0ea7e77ecd3d02f21c
        ctyun redis network -i xxx --format json
    """
    # 获取凭证
    from redis.client import RedisClient

    client = ctx.obj['client']

    click.echo(f"🌐 正在查询Redis实例网络信息: {instance_id}")

    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    try:
        result = redis_client.describe_db_instance_net_info(instance_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_network_table(result, instance_id)
        else:
            _display_network_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询网络信息失败: {str(e)}", err=True)
        sys.exit(1)


# ========== 查询类命令显示函数 ==========

def _display_instance_overview_table(result: dict, instance_id: str):
    """以表格形式显示实例详情"""
    click.echo("\n" + "="*80)
    click.echo(f"📍 Redis实例详情查询结果 (实例: {instance_id})")
    click.echo("="*80)

    if not result:
        click.echo("❌ 查询失败: 无响应数据")
        return

    if result.get("error"):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        click.echo(f"✅ 查询成功!\n")

        # 基本信息
        click.echo("📋 基本信息:")
        click.echo("-" * 50)
        basic_info = [
            ("实例ID", return_obj.get("prodInstId", "N/A")),
            ("实例名称", return_obj.get("instanceName", "N/A")),
            ("实例类型", return_obj("instanceType", "N/A")),
            ("实例状态", return_obj.get("instanceStatus", "N/A")),
            ("创建时间", return_obj.get("createTime", "N/A")),
        ]

        for key, value in basic_info:
            click.echo(f"{key:<12}: {value}")

        # 配置信息
        click.echo(f"\n⚙️ 配置信息:")
        click.echo("-" * 50)
        config_info = [
            ("容量(GB)", return_obj.get("capacityMB", 0) // 1024),
            ("分片数", return_obj.get("shardCount", "N/A")),
            ("副本数", return_obj("copiesCount", "N/A")),
            ("Redis版本", return_obj.get("engineVersion", "N/A")),
            ("端口", return_obj.get("port", "N/A")),
        ]

        for key, value in config_info:
            click.echo(f"{key:<12}: {value}")

        # 网络信息
        click.echo(f"\n🌐 网络信息:")
        click.echo("-" * 50)
        net_info = return_obj.get("network", {})
        if net_info:
            click.echo(f"VPC ID: {net_info.get('vpcId', 'N/A')}")
            click.echo(f"子网ID: {net_info.get('subnetId', 'N/A')}")
            click.echo(f"内网IP: {net_info.get('innerIp', 'N/A')}")
            click.echo(f"外网IP: {net_info.get('publicIp', 'N/A')}")

    else:
        click.echo(f"❌ API查询失败: {result.get('message', '未知错误')}")


def _display_instance_overview_summary(result: dict, instance_id: str):
    """显示实例详情摘要"""
    click.echo("\n" + "="*60)
    click.echo(f"📋 Redis实例详情摘要 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        click.echo(f"✅ 查询状态: 成功")
        click.echo(f"🏷️  实例名称: {return_obj.get('instanceName', 'N/A')}")
        click.echo(f"⚡ 实例状态: {return_obj.get('instanceStatus', 'N/A')}")
        click.echo(f"🔢 Redis版本: {return_obj.get('engineVersion', 'N/A')}")
        click.echo(f"💾 容量: {return_obj.get('capacityMB', 0) // 1024}GB")
        click.echo(f"🔌 端口: {return_obj.get('port', 'N/A')}")
        click.echo(f"🕐 创建时间: {return_obj.get('createTime', 'N/A')}")
    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")


def _display_config_table(result: dict, instance_id: str, param_name: str = None):
    """以表格形式显示配置信息"""
    title = f"Redis实例配置参数" + (f" (参数: {param_name})" if param_name else "")
    click.echo(f"\n📋 {title}")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        config_list = return_obj.get("configList", [])

        if param_name:
            # 显示单个参数
            for config in config_list:
                if config.get("paramName") == param_name:
                    click.echo(f"参数名称: {config.get('paramName')}")
                    click.echo(f"当前值: {config.get('currentValue', 'N/A')}")
                    click.echo(f"默认值: {config.get('defaultValue', 'N/A')}")
                    click.echo(f"可修改: {'是' if config.get('isModifiable') else '否'}")
                    click.echo(f"需要重启: {'是' if config.get('needRestart') else '否'}")
                    break
        else:
            # 显示所有参数
            click.echo(f"{'参数名称':<30} {'当前值':<20} {'可修改':<8} {'需要重启':<8}")
            click.echo("-" * 80)

            for config in config_list:
                param_name = config.get("paramName", "N/A")[:28]
                if len(config.get("paramName", "")) > 28:
                    param_name = config.get("paramName", "")[:25] + "..."

                current_value = str(config.get("currentValue", "N/A"))[:18]
                if len(str(config.get("currentValue", ""))) > 18:
                    current_value = str(config.get("currentValue", ""))[:15] + "..."

                click.echo(f"{param_name:<30} {current_value:<20} {'是' if config.get('isModifiable') else '否':<8} {'是' if config.get('needRestart') else '否':<8}")
    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")


def _display_config_summary(result: dict, instance_id: str, param_name: str = None):
    """显示配置摘要"""
    title = f"Redis实例配置摘要" + (f" (参数: {param_name})" if param_name else "")
    click.echo(f"\n{title}")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        config_list = return_obj.get("configList", [])

        if param_name:
            # 显示单个参数
            for config in config_list:
                if config.get("paramName") == param_name:
                    click.echo(f"🔧 参数名称: {config.get('paramName')}")
                    click.echo(f"📊 当前值: {config.get('currentValue', 'N/A')}")
                    click.echo(f"📝 默认值: {config.get('defaultValue', 'N/A')}")
                    click.echo(f"🔒 可修改: {'✅' if config.get('isModifiable') else '❌'}")
                    click.echo(f"🔄 需要重启: {'⚠️' if config.get('needRestart') else '✅'}")
                    break
        else:
            click.echo(f"📊 配置参数总数: {len(config_list)}")
            modifiable_count = sum(1 for config in config_list if config.get('isModifiable'))
            click.echo(f"🔧 可修改参数: {modifiable_count}")

            # 显示重要参数
            important_params = ['maxmemory', 'maxmemory-policy', 'timeout', 'save', 'appendonly']
            click.echo(f"\n🎯 重要参数:")
            for param in important_params:
                for config in config_list:
                    if config.get("paramName") == param:
                        click.echo(f"  {param}: {config.get('currentValue', 'N/A')}")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")


def _display_monitor_items_table(result: dict, instance_id: str):
    """以表格形式显示监控指标列表"""
    click.echo(f"\n📊 Redis实例监控指标列表 (实例: {instance_id})")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        items = return_obj.get("monitorItems", [])

        click.echo(f"📈 监控指标总数: {len(items)}")
        click.echo("\n" + "-"*80)
        click.echo(f"{'指标名称':<40} {'指标类型':<15} {'单位':<10} {'描述':<20}")
        click.echo("-" * 80)

        for item in items:
            metric_name = item.get("metricName", "N/A")[:38]
            if len(item.get("metricName", "")) > 38:
                metric_name = item.get("metricName", "")[:35] + "..."

            metric_type = item.get("metricType", "N/A")
            unit = item.get("unit", "N/A")
            description = item.get("description", "N/A")[:18]
            if len(item.get("description", "")) > 18:
                description = item.get("description", "")[:15] + "..."

            click.echo(f"{metric_name:<40} {metric_type:<15} {unit:<10} {description:<20}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")


def _display_monitor_history_table(result: dict, instance_id: str, metric: str):
    """以表格形式显示监控历史数据"""
    click.echo(f"\n📈 Redis监控历史数据 (实例: {instance_id}, 指标: {metric})")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        data_points = return_obj.get("dataPoints", [])

        click.echo(f"📊 数据点数量: {len(data_points)}")
        if data_points:
            click.echo(f"⏰ 时间范围: {data_points[0].get('timestamp', 'N/A')} 至 {data_points[-1].get('timestamp', 'N/A')}")
            click.echo(f"📈 平均值: {sum(dp.get('value', 0) for dp in data_points) / len(data_points):.2f}")
            click.echo(f"📊 最大值: {max(dp.get('value', 0) for dp in data_points):.2f}")
            click.echo(f"📊 最小值: {min(dp.get('value', 0) for dp in data_points):.2f}")

            click.echo("\n" + "-" * 80)
            click.echo(f"{'时间戳':<20} {'数值':<12} {'状态':<10}")
            click.echo("-" * 80)

            for dp in data_points[-10:]:  # 只显示最近10个数据点
                timestamp = dp.get("timestamp", "N/A")
                value = dp.get("value", "N/A")
                status = dp.get("status", "N/A")
                click.echo(f"{timestamp:<20} {value:<12} {status:<10}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")


def _display_monitor_history_summary(result: dict, instance_id: str, metric: str):
    """显示监控历史数据摘要"""
    click.echo(f"\n📈 Redis监控历史数据摘要 (实例: {instance_id}, 指标: {metric})")
    click.echo("="*70)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        data_points = return_obj.get("dataPoints", [])

        if data_points:
            click.echo(f"✅ 查询状态: 成功")
            click.echo(f"📊 数据点数量: {len(data_points)}")
            click.echo(f"📈 平均值: {sum(dp.get('value', 0) for dp in data_points) / len(data_points):.4f}")
            click.echo(f"📊 最大值: {max(dp.get('value', 0) for dp in data_points):.4f}")
            click.echo(f"📊 最小值: {min(dp.get('value', 0) for dp in data_points):.4f}")
            click.echo(f"⏰ 时间跨度: {data_points[0].get('timestamp', 'N/A')} 至 {data_points[-1].get('timestamp', 'N/A')}")
        else:
            click.echo(f"⚠️ 查询成功: 无数据点")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")


def _display_diagnosis_report(result: dict, instance_id: str, output_format: str = 'summary'):
    """显示诊断报告"""
    click.echo(f"\n🔍 Redis诊断分析报告 (实例: {instance_id})")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo("❌ 查询失败: 无响应数据")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        nodes = return_obj.get("map", {})

        click.echo(f"✅ 诊断完成: {return_obj.get('writeable', 'N/A')}")
        click.echo(f"🔗 集群状态: {'同步' if return_obj.get('redisSync') else '不同步'}")

        if output_format == 'summary':
            for node_name, node_data in nodes.items():
                click.echo(f"\n🖥️ 节点: {node_name}")

                # 内存相关指标 (重点)
                mem_fragmentation = node_data.get("memFragmentationRate", 0)
                memory_usage = node_data.get("usedMemoryRate", 0)
                memory_flag = "✅" if node_data.get("memoryflag") else "❌"
                frag_flag = "✅" if node_data.get("frageflag") else "❌"

                click.echo(f"   💾 内存使用率: {memory_usage:.1%} {memory_flag}")
                click.echo(f"   🔧 内存碎片率: {mem_fragmentation:.2%} {frag_flag}")

                # 其他指标
                cpu_rate = node_data.get("cpuRate", 0)
                hit_rate = node_data.get("keyspaceHitsRate", 0)
                connections = node_data.get("clientConnectionnums", 0)

                click.echo(f"   ⚡ CPU使用率: {cpu_rate:.1%}")
                click.echo(f"   🎯 缓存命中率: {hit_rate:.1%}")
                click.echo(f"   👥 连接数: {connections}")

                # 状态指示
                alive = "🟢" if node_data.get("alive") else "🔴"
                role = node_data.get("role", "N/A")
                az_name = node_data.get("azName", "N/A")

                click.echo(f"   {alive} 节点状态: {role} ({az_name})")

        elif output_format == 'table':
            click.echo("\n" + "-"*100)
            click.echo(f"{'节点名称':<20} {'状态':<6} {'内存碎片率':<12} {'内存使用率':<10} {'CPU使用率':<10} {'命中率':<10} {'连接数':<8}")
            click.echo("-" * 100)

            for node_name, node_data in nodes.items():
                alive = "运行" if node_data.get("alive") else "宕机"
                role = node_data.get("role", "N/A")
                mem_frag = f"{node_data.get('memFragmentationRate', 0):.2f}%"
                mem_usage = f"{node_data.get('usedMemoryRate', 0):.1%}"
                cpu_rate = f"{node_data.get('cpuRate', 0):.1%}"
                hit_rate = f"{node_data.get('keyspaceHitsRate', 0):.1%}"
                connections = node_data.get("clientConnectionnums", 0)

                click.echo(f"{node_name[:18]:<20} {alive:<6} {role:<6} {mem_frag:<12} {mem_usage:<10} {cpu_rate:<10} {hit_rate:<10} {connections:<8}")

    else:
        click.echo(f"❌ 诊断查询失败: {result.get('message', '未知错误')}")


def _display_clients_table(result: dict, instance_id: str, node_id: str = None):
    """以表格形式显示客户端会话"""
    title = f"Redis客户端会话列表 (实例: {instance_id}"
    if node_id:
        title += f", 节点: {node_id}"
    click.echo(f"\n{title}")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        clients = return_obj.get("clientInfoList", [])

        click.echo(f"👥 客户端连接总数: {len(clients)}")

        if clients:
            click.echo("\n" + "-"*100)
            click.echo(f"{'客户端IP:IP:端口':<25} {'连接时间':<20} {'空闲时间':<10} {'用户名':<15} {'状态':<8}")
            click.echo("-" * 100)

            for client in clients:
                ip_port = f"{client.get('clientIp', 'N/A')}:{client.get('clientPort', 'N/A')}"
                connect_time = client.get('connectTime', 'N/A')
                idle_time = f"{client.get('idleTime', 0)}s"
                username = client.get('username', 'N/A')
                status = "连接中" if client.get("connected") else "已断开"

                click.echo(f"{ip_port:<25} {connect_time:<20} {idle_time:<10} {username:<15} {status:<8}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")


def _display_clients_summary(result: dict, instance_id: str, node_id: str = None):
    """显示客户端会话摘要"""
    title = f"Redis客户端会话摘要 (实例: {instance_id}"
    if node_id:
        title += f", 节点: {node_id}"
    click.echo(f"\n{title}")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        clients = return_obj.get("clientInfoList", [])

        click.echo(f"✅ 查询状态: 成功")
        click.echo(f"👥 当前连接数: {len(clients)}")

        if clients:
            # IP统计
            ip_stats = {}
            for client in clients:
                ip = client.get('clientIp', 'N/A')
                ip_stats[ip] = ip_stats.get(ip, 0) + 1

            click.echo(f"🌐 独立IP数: {len(ip_stats)}")

            # 连接时间统计
            long_connections = sum(1 for client in clients if client.get('idleTime', 0) > 300)
            click.echo(f"⏰ 长时间连接数(>5分钟): {long_connections}")

            # 最新连接
            if clients:
                latest_client = clients[0]
                click.echo(f"🕐 最新连接: {latest_client.get('clientIp')}:{latest_client.get('clientPort')}")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")


def _display_version_table(result: dict, instance_id: str):
    """以表格形式显示版本信息"""
    click.echo(f"\n🔢 Redis实例版本信息 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        click.echo("📊 版本详情:")
        click.echo("-" * 40)
        version_info = [
            ("Redis引擎版本", return_obj.get("engineVersion", "N/A")),
            ("代理组件版本", return_obj.get("proxyVersion", "N/A")),
            ("升级状态", return_obj.get("upgradeStatus", "N/A")),
            ("可升级", return_obj.get("canUpgrade", "N/A")),
            ("当前版本号", return_obj.get("currentVersion", "N/A")),
            ("目标版本号", return_obj.get("targetVersion", "N/A")),
        ]

        for key, value in version_info:
            click.echo(f"{key:<12}: {value}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")


def _display_version_summary(result: dict, instance_id: str):
    """显示版本信息摘要"""
    click.echo(f"\n🔢 Redis实例版本信息摘要 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        click.echo(f"✅ 查询状态: 成功")
        click.echo(f"🔢 Redis版本: {return_obj.get('engineVersion', 'N/A')}")
        click.echo(f"🤖 代理版本: {return_obj.get('proxyVersion', 'N/A')}")
        click.echo(f"🔄 升级状态: {return_obj.get('upgradeStatus', 'N/A')}")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")


def _display_network_table(result: dict, instance_id: str):
    """以表格形式显示网络信息"""
    click.echo(f"\n🌐 Redis实例网络信息 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        click.echo("🌐 网络配置:")
        click.echo("-" * 40)
        network_info = [
            ("VPC ID", return_obj.get("vpcId", "N/A")),
            ("子网ID", return_obj.get("subnetId", "N/A")),
            ("安全组", return_obj.get("securityGroupId", "N/A")),
            ("可用区", return_obj.get("availableZoneName", "N/A")),
        ]

        for key, value in network_info:
            click.echo(f"{key:<12}: {value}")

        click.echo("\n🔗 IP地址:")
        click.echo("-" * 40)
        ip_info = [
            ("内网IP", return_obj.get("innerIp", "N/A")),
            ("外网IP", return_obj.get("publicIp", "N/A")),
            ("端口号", return_obj.get("port", "N/A")),
            ("协议类型", return_obj.get("protocol", "N/A")),
        ]

        for key, value in ip_info:
            click.echo(f"{key:<12}: {value}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")


def _display_network_summary(result: dict, instance_id: str):
    """显示网络信息摘要"""
    click.echo(f"\n🌐 Redis实例网络信息摘要 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        click.echo(f"✅ 查询状态: 成功")
        click.echo(f"🌐 VPC ID: {return_obj.get('vpcId', 'N/A')}")
        click.echo(f"🔗 内网IP: {return_obj.get('innerIp', 'N/A')}")
        click.echo(f"🌐 外网IP: {return_obj.get('publicIp', 'N/A')}")
        click.echo(f"🔌 端口号: {return_obj.get('port', 'N/A')}")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")