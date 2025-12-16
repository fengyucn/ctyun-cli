"""
Redis分布式缓存服务CLI命令
提供Redis实例可用区查询等命令行功能
"""

import click
import json
import sys
from typing import Optional

from redis import RedisClient


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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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
                        instance_id = instance.get('prodInstId', 'N/A')  # 保留完整的实例ID
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
                        instance_id = instance.get('prodInstId', 'N/A')  # 保留完整的实例ID
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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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
    from redis import RedisClient

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


@redis_group.command('create-instance')
@click.option('--instance-name', '-n', required=True, help='实例名称 (必需，长度4~40个字符，大小写字母开头，只能包含字母、数字、分隔符(-)，字母或数字结尾)')
@click.option('--password', '-p', required=True, help='访问密码 (必需，长度8-26字符，必须包含大写字母、小写字母、数字、特殊字符(@%^*_+!$-=.)中的三种类型)')

# 计费相关参数
@click.option('--charge-type', type=click.Choice(['PrePaid', 'PostPaid']), default='PostPaid', help='计费模式 (默认: PostPaid按需计费，PrePaid包年包月)')
@click.option('--period', type=int, help='购买时长月数，包年包月时必需，取值：1~6,12,24,36')
@click.option('--auto-pay/--no-auto-pay', default=False, help='是否自动付费 (仅包周期实例有效，默认: 否)')
@click.option('--size', type=int, default=1, help='购买数量 (默认: 1，取值范围：1~100)')
@click.option('--auto-renew/--no-auto-renew', default=False, help='是否启用自动续订 (默认: 否)')
@click.option('--auto-renew-period', type=int, help='自动续期购买时长月数，启用自动续费时必需，取值：1~6,12,24,36')

# 实例配置参数
@click.option('--version', '-v', type=click.Choice(['BASIC', 'PLUS', 'Classic']), default='BASIC', help='版本类型 (默认: BASIC基础版，PLUS增强版，Classic经典版白名单)')
@click.option('--edition', '-e', required=True, help='实例类型 (必需，如StandardSingle单机版，ClusterSingle集群单机版等，详见产品规格)')
@click.option('--engine-version', required=True, type=click.Choice(['5.0', '6.0', '7.0', '2.8', '4.0']), help='Redis引擎版本号 (必需，BASIC支持5.0/6.0/7.0，PLUS支持6.0/7.0，Classic支持2.8/4.0/5.0)')
@click.option('--zone-name', '-z', required=True, help='主可用区名称 (必需，如cn-huabei2-tj-1a-public-ctcloud)')
@click.option('--secondary-zone-name', help='备可用区名称 (双/多副本建议填写)')
@click.option('--host-type', type=click.Choice(['S', 'C', 'M', 'HS', 'HC', 'KS', 'KC']), help='主机类型 (S通用型，C计算增强型，M内存型，HS海光通用，HC海光计算，KS鲲鹏通用，KC鲲鹏计算)')
@click.option('--shard-mem-size', type=int, help='分片规格GB，BASIC版本支持1,2,4,8,16,32,64；PLUS版本支持8,16,32,64')
@click.option('--shard-count', type=int, help='分片数，Cluster类型必需，取值3~256')
@click.option('--capacity', type=int, help='存储容量GB，仅Classic版本需要填写')
@click.option('--copies-count', type=int, default=2, help='副本数，默认2，取值2~10')
@click.option('--data-disk-type', type=click.Choice(['SSD', 'SAS']), default='SSD', help='磁盘类型 (默认: SSD超高IO，可选SAS高IO)')

# 网络配置参数
@click.option('--vpc-id', required=True, help='虚拟私有云ID (必需)')
@click.option('--subnet-id', required=True, help='所在子网ID (必需)')
@click.option('--secgroups', required=True, help='安全组ID (必需，多个用逗号分隔)')
@click.option('--cache-server-port', type=int, default=6379, help='实例端口 (默认: 6379)')

# 企业项目参数
@click.option('--project-id', default='0', help='企业项目ID (默认: 0)')
@click.option('--region-id', '-r', help='资源池ID (必需，可通过查询可用资源池接口获取)')

# 输出和控制参数
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=60, help='请求超时时间(秒，默认60)')
@click.option('--check-resources', is_flag=True, help='创建前检查可用规格')
@click.option('--dry-run', is_flag=True, help='预览模式，只验证参数不实际创建')
@click.pass_context
@validate_credentials
def create_instance(ctx, instance_name: str, password: str, charge_type: str, period: int,
                   auto_pay: bool, size: int, auto_renew: bool, auto_renew_period: int,
                   version: str, edition: str, engine_version: str, zone_name: str,
                   secondary_zone_name: str, host_type: str, shard_mem_size: int,
                   shard_count: int, capacity: int, copies_count: int, data_disk_type: str,
                   vpc_id: str, subnet_id: str, secgroups: str, cache_server_port: int,
                   project_id: str, region_id: str, output_format: str, timeout: int,
                   check_resources: bool, dry_run: bool):
    """
    创建Redis分布式缓存实例 - 支持完整的25+API参数

    基础示例:
        # 创建基础版Redis实例 (按需付费)
        ctyun redis create-instance \\
            --region-id 200000001852 \\
            --instance-name my-redis \\
            --edition StandardSingle \\
            --engine-version 6.0 \\
            --shard-mem-size 4 \\
            --zone-name cn-huabei2-tj-1a-public-ctcloud \\
            --vpc-id vpc-grqvu4741a \\
            --subnet-id subnet-gr36jdeyt0 \\
            --secgroups sg-ufrtt04xq1 \\
            --password Test@123456

        # 创建增强版实例 (包年包月)
        ctyun redis create-instance \\
            --region-id 200000001852 \\
            -n prod-redis -e ClusterSingle -v 7.0 \\
            --shard-mem-size 16 --shard-count 3 \\
            -z cn-huabei2-tj-1a-public-ctcloud \\
            --vpc-id vpc-grqvu4741a --subnet-id subnet-gr36jdeyt0 \\
            --secgroups sg-ufrtt04xq1 \\
            -p Test@123456 --charge-type PrePaid --period 3 --auto-pay

        # 创建双副本高可用实例
        ctyun redis create-instance \\
            --region-id 200000001852 \\
            --instance-name ha-redis \\
            --edition StandardDual \\
            --version PLUS --engine-version 6.0 \\
            --shard-mem-size 8 --copies-count 2 \\
            --zone-name cn-huabei2-tj-1a-public-ctcloud \\
            --secondary-zone-name cn-huabei2-tj-2a-public-ctcloud \\
            --vpc-id vpc-grqvu4741a --subnet-id subnet-gr36jdeyt0 \\
            --secgroups sg-ufrtt04xq1 \\
            --password Test@123456 --host-type S --data-disk-type SSD

    参数说明:
        计费相关:
            --charge-type: PrePaid包年包月 / PostPaid按需计费 (默认)
            --period: 包年包月时长(1~6,12,24,36月)
            --auto-pay: 是否自动付费 (仅包周期有效)
            --size: 购买数量 (1~100)
            --auto-renew: 是否自动续订
            --auto-renew-period: 自动续费时长 (1~6,12,24,36月)

        实例配置:
            --version: BASIC基础版 / PLUS增强版 / Classic经典版(白名单)
            --edition: 实例类型 (StandardSingle, StandardDual, ClusterSingle等)
            --engine-version: Redis版本 (BASIC:5.0/6.0/7.0, PLUS:6.0/7.0, Classic:2.8/4.0/5.0)
            --zone-name: 主可用区名称 (必需)
            --secondary-zone-name: 备可用区名称 (高可用建议)
            --host-type: 主机类型 (S通用/C计算/M内存/HS海光/HC海光计算/KS鲲鹏通用/KC鲲鹏计算)
            --shard-mem-size: 分片规格GB (BASIC:1,2,4,8,16,32,64; PLUS:8,16,32,64)
            --shard-count: 分片数 (Cluster类型必需，3~256)
            --capacity: 存储容量GB (仅Classic版本需要)
            --copies-count: 副本数 (默认2，取值2~10)
            --data-disk-type: SSD超高IO / SAS高IO (默认SSD)

        资源池配置:
            --region-id: 资源池ID (必需，常用: 200000001852 华北2)

        网络配置:
            --vpc-id: 虚拟私有云ID (必需)
            --subnet-id: 子网ID (必需)
            --secgroups: 安全组ID (必需，多个用逗号分隔)
            --cache-server-port: 实例端口 (默认6379)

        企业项目:
            --project-id: 企业项目ID (默认0)

    注意事项:
        1. --region-id是必需参数，指定资源池ID，常用值: 200000001852 (华北2)
        2. 经典版(Classic)属于白名单功能，默认不开放，建议优先使用基础版和增强版
        3. 实例名称长度4~40字符，大小写字母开头，只能包含字母、数字、分隔符(-)，字母或数字结尾
        4. 密码长度8-26字符，必须包含大写字母、小写字母、数字、特殊字符(@%^*_+!$-=.)中的三种类型
        5. 包年包月模式必须指定charge-type为PrePaid和period参数
        6. 启用自动续费时必须指定auto-renew-period参数
        7. 使用--check-resources参数可以在创建前检查资源可用性
        8. 使用--dry-run参数可以验证参数正确性而不实际创建实例
    """
    import re
    from redis import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    # ========== 参数验证 ==========
    click.echo("🔍 开始参数验证...")

    # 验证资源池ID
    if not region_id:
        click.echo("❌ 错误: region-id是必需参数", err=True)
        click.echo("💡 获取region-id方法:", err=True)
        click.echo("   1. 查看附录文档: 分布式缓存服务Redis资源池", err=True)
        click.echo("   2. 调用查询可用资源池接口获取resPoolCode字段", err=True)
        click.echo("   3. 常用region-id: 200000001852 (华北2)", err=True)
        sys.exit(1)

    # 验证实例名称
    if not (4 <= len(instance_name) <= 40):
        click.echo("❌ 错误: 实例名称长度必须为4~40个字符", err=True)
        sys.exit(1)

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$', instance_name):
        click.echo("❌ 错误: 实例名称格式不正确，必须大小写字母开头，只能包含字母、数字、分隔符(-)，字母或数字结尾", err=True)
        sys.exit(1)

    # 验证密码复杂度
    def validate_password_complexity(pwd):
        has_upper = bool(re.search(r'[A-Z]', pwd))
        has_lower = bool(re.search(r'[a-z]', pwd))
        has_digit = bool(re.search(r'\d', pwd))
        has_special = bool(re.search(r'[@%^*_+!$=\-.]', pwd))

        return sum([has_upper, has_lower, has_digit, has_special]) >= 3

    if not (8 <= len(password) <= 26):
        click.echo("❌ 错误: 密码长度必须为8-26个字符", err=True)
        sys.exit(1)

    if not validate_password_complexity(password):
        click.echo("❌ 错误: 密码必须包含大写字母、小写字母、数字、特殊字符(@%^*_+!$-=.)中的三种类型", err=True)
        sys.exit(1)

    # 验证版本和引擎版本兼容性
    if version == 'BASIC' and engine_version not in ['5.0', '6.0', '7.0']:
        click.echo("❌ 错误: BASIC版本仅支持Redis版本 5.0, 6.0, 7.0", err=True)
        sys.exit(1)

    if version == 'PLUS' and engine_version not in ['6.0', '7.0']:
        click.echo("❌ 错误: PLUS版本仅支持Redis版本 6.0, 7.0", err=True)
        sys.exit(1)

    if version == 'Classic' and engine_version not in ['2.8', '4.0', '5.0']:
        click.echo("❌ 错误: Classic版本仅支持Redis版本 2.8, 4.0, 5.0", err=True)
        sys.exit(1)

    # 验证分片规格
    if version == 'BASIC':
        if shard_mem_size and shard_mem_size not in [1, 2, 4, 8, 16, 32, 64]:
            click.echo("❌ 错误: BASIC版本分片规格仅支持 1,2,4,8,16,32,64 GB", err=True)
            sys.exit(1)
    elif version == 'PLUS':
        if shard_mem_size and shard_mem_size not in [8, 16, 32, 64]:
            click.echo("❌ 错误: PLUS版本分片规格仅支持 8,16,32,64 GB", err=True)
            sys.exit(1)

    # 验证包年包月参数
    if charge_type == 'PrePaid' and not period:
        click.echo("❌ 错误: 包年包月模式必须指定购买时长(--period)", err=True)
        sys.exit(1)

    if period and not (1 <= period <= 36 or period in [12, 24, 36]):
        click.echo("❌ 错误: 购买时长取值为 1~6,12,24,36 月", err=True)
        sys.exit(1)

    # 验证自动续费参数
    if auto_renew and not auto_renew_period:
        click.echo("❌ 错误: 启用自动续费必须指定自动续费时长(--auto-renew-period)", err=True)
        sys.exit(1)

    if auto_renew_period and not (1 <= auto_renew_period <= 36 or auto_renew_period in [12, 24, 36]):
        click.echo("❌ 错误: 自动续费时长取值为 1~6,12,24,36 月", err=True)
        sys.exit(1)

    # 验证分片数
    if shard_count and not (3 <= shard_count <= 256):
        click.echo("❌ 错误: 分片数取值范围为3~256", err=True)
        sys.exit(1)

    # 验证副本数
    if copies_count and not (2 <= copies_count <= 10):
        click.echo("❌ 错误: 副本数取值范围为2~10", err=True)
        sys.exit(1)

    # 验证购买数量
    if size and not (1 <= size <= 100):
        click.echo("❌ 错误: 购买数量取值范围为1~100", err=True)
        sys.exit(1)

    # 验证端口范围
    if cache_server_port and not (1024 <= cache_server_port <= 65535):
        click.echo("❌ 错误: 端口取值范围为1024~65535", err=True)
        sys.exit(1)

    # 验证Classic版本必须参数
    if version == 'Classic' and not capacity:
        click.echo("❌ 错误: Classic版本必须指定存储容量(--capacity)", err=True)
        sys.exit(1)

    click.echo("✅ 参数验证通过!")

    # ========== 预览模式 ==========
    if dry_run:
        click.echo("\n🔍 预览模式 - 参数配置如下:")
        click.echo("="*60)
        click.echo(f"资源池ID: {region_id}")
        click.echo(f"实例名称: {instance_name}")
        click.echo(f"版本类型: {version} - {engine_version}")
        click.echo(f"实例类型: {edition}")
        click.echo(f"主可用区: {zone_name}")
        if secondary_zone_name:
            click.echo(f"备可用区: {secondary_zone_name}")
        click.echo(f"主机类型: {host_type or '默认'}")

        if version != 'Classic':
            click.echo(f"分片规格: {shard_mem_size}GB" if shard_mem_size else "未指定")
            if shard_count:
                click.echo(f"分片数量: {shard_count}")
        else:
            click.echo(f"存储容量: {capacity}GB")

        click.echo(f"副本数量: {copies_count}")
        click.echo(f"磁盘类型: {data_disk_type}")
        click.echo(f"计费模式: {charge_type}")
        if charge_type == 'PrePaid':
            click.echo(f"购买时长: {period}个月")
            click.echo(f"自动付费: {'是' if auto_pay else '否'}")
        click.echo(f"购买数量: {size}")
        if auto_renew:
            click.echo(f"自动续费: 是 ({auto_renew_period}个月)")

        click.echo(f"\n网络配置:")
        click.echo(f"  VPC ID: {vpc_id}")
        click.echo(f"  子网ID: {subnet_id}")
        click.echo(f"  安全组: {secgroups}")
        click.echo(f"  端口: {cache_server_port}")
        click.echo(f"企业项目ID: {project_id}")
        click.echo("="*60)
        click.echo("🔍 预览模式完成，未实际创建实例")
        return

    # ========== 创建前检查可用规格 ==========
    if check_resources:
        click.echo(f"🔍 检查可用规格: {version}-{engine_version}")
        try:
            resource_result = redis_client.describe_available_resources("200000001852", edition, engine_version)

            if resource_result and resource_result.get("statusCode") == 800:
                click.echo("✅ 可用规格检查通过")
            else:
                click.echo("❌ 可用规格检查失败")
                if resource_result:
                    click.echo(f"错误: {resource_result.get('message', '未知错误')}")
                if not click.confirm("是否继续创建实例？"):
                    click.echo("用户取消创建")
                    sys.exit(0)
        except Exception as e:
            click.echo(f"⚠️ 规格检查异常: {str(e)}")
            if not click.confirm("规格检查失败，是否继续创建？"):
                click.echo("用户取消创建")
                sys.exit(0)

    # ========== 构建API请求参数 ==========
    request_params = {
        # 计费相关
        'chargeType': charge_type,
        'size': size,

        # 实例配置
        'version': version,
        'edition': edition,
        'engineVersion': engine_version,
        'zoneName': zone_name,
        'copiesCount': copies_count,
        'dataDiskType': data_disk_type,

        # 网络配置
        'vpcId': vpc_id,
        'subnetId': subnet_id,
        'secgroups': secgroups,
        'cacheServerPort': cache_server_port,

        # 实例信息
        'instanceName': instance_name,
        'password': password,

        # 企业项目
        'projectID': project_id,

        # 资源池ID (header参数)
        'regionId': region_id,
    }

    # 可选参数
    if charge_type == 'PrePaid':
        if period:
            request_params['period'] = period
        request_params['autoPay'] = auto_pay
        if auto_renew:
            request_params['autoRenew'] = auto_renew
            request_params['autoRenewPeriod'] = str(auto_renew_period)

    if secondary_zone_name:
        request_params['secondaryZoneName'] = secondary_zone_name

    if host_type:
        request_params['hostType'] = host_type

    if version != 'Classic' and shard_mem_size:
        request_params['shardMemSize'] = str(shard_mem_size)

    if shard_count:
        request_params['shardCount'] = shard_count

    if version == 'Classic' and capacity:
        request_params['capacity'] = str(capacity)

    # ========== 显示创建信息 ==========
    click.echo(f"\n🚀 开始创建Redis实例: {instance_name}")
    click.echo(f"   版本: {version} - Redis {engine_version}")
    click.echo(f"   类型: {edition}")
    if version != 'Classic':
        click.echo(f"   规格: {shard_mem_size}GB" if shard_mem_size else "默认规格")
        if shard_count:
            click.echo(f"   分片: {shard_count}个")
    else:
        click.echo(f"   容量: {capacity}GB")
    click.echo(f"   副本: {copies_count}个")
    click.echo(f"   可用区: {zone_name}")
    if secondary_zone_name:
        click.echo(f"   备可用区: {secondary_zone_name}")
    click.echo(f"   主机类型: {host_type or '默认'}")
    click.echo(f"   磁盘类型: {data_disk_type}")
    click.echo(f"   计费: {charge_type}")
    if charge_type == 'PrePaid':
        click.echo(f"   时长: {period}个月, 自动付费: {'是' if auto_pay else '否'}")
    click.echo(f"   数量: {size}个")
    if auto_renew:
        click.echo(f"   自动续费: {auto_renew_period}个月")
    click.echo(f"   网络: VPC={vpc_id}, 子网={subnet_id}")
    click.echo(f"   安全组: {secgroups}")
    click.echo(f"   端口: {cache_server_port}")
    click.echo(f"   项目: {project_id}")

    # ========== 发送API请求 ==========
    try:
        result = redis_client.create_instance_v2(**request_params)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_create_instance_table(result, instance_name)
        else:
            _display_create_instance_summary(result, instance_name)

        # 如果创建成功，显示后续操作提示
        if result and result.get("statusCode") == 800:
            return_obj = result.get("returnObj", {})
            instance_id = return_obj.get("newOrderId")  # 注意：新API返回的是订单ID
            order_no = return_obj.get("newOrderNo")
            total_price = return_obj.get("totalPrice", 0)

            click.echo(f"\n💡 Redis实例创建订单提交成功!")
            click.echo(f"📋 订单ID: {instance_id}")
            click.echo(f"📋 订单号: {order_no}")
            if total_price > 0:
                click.echo(f"💰 总价: ¥{total_price}")
            click.echo(f"🕐 实例创建是异步过程，通常需要几分钟时间完成")
            click.echo(f"\n🔗 后续操作:")
            click.echo(f"   查看实例列表: ctyun redis list")
            click.echo(f"   查看订单详情: 请登录天翼云控制台查看订单状态")
            click.echo(f"   查看实例状态: ctyun redis list --name {instance_name}")
        else:
            click.echo(f"❌ 创建失败: {result.get('message', '未知错误')}", err=True)
            if result.get('error'):
                click.echo(f"错误码: {result.get('error')}", err=True)

    except Exception as e:
        click.echo(f"❌ 创建Redis实例失败: {str(e)}", err=True)
        import traceback
        click.echo("详细错误信息:")
        click.echo(traceback.format_exc())
        sys.exit(1)


@redis_group.command('check-resources')
@click.option('--region-id', '-r', default="200000001852", help='区域ID (默认: 200000001852)')
@click.option('--edition', '-e', required=True,
              type=click.Choice(['Basic', 'Enhance', 'Classic']),
              help='实例版本类型 (必需): Basic(基础版), Enhance(增强版), Classic(经典版)')
@click.option('--version', '-v', required=True, help='Redis版本号 (必需，如: 5.0)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def check_available_resources(ctx, region_id: str, edition: str, version: str,
                             output_format: str, timeout: int):
    """
    查询Redis实例可创建规格

    示例:
        ctyun redis check-resources --edition Basic --version 5.0
        ctyun redis check-resources -e Enhance -v 6.0 --format json
        ctyun redis check-resources -e Classic -v 5.0 -f table
    """
    from redis import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    click.echo(f"🔍 查询Redis可创建规格: {edition}-{version}")

    try:
        result = redis_client.describe_available_resources(region_id, edition, version)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_resources_table(result, region_id, edition, version)
        else:
            _display_resources_summary(result, region_id, edition, version)

    except Exception as e:
        click.echo(f"❌ 查询可用规格失败: {str(e)}", err=True)
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
    from redis import RedisClient

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
            ("实例类型", return_obj.get("instanceType", "N/A")),
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
            ("副本数", return_obj.get("copiesCount", "N/A")),
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


def _display_create_instance_table(result: dict, instance_name: str):
    """以表格形式显示创建实例结果"""
    click.echo(f"\n🚀 Redis实例创建结果 ({instance_name})")
    click.echo("="*80)

    if not result:
        click.echo("❌ 创建失败: 无响应数据")
        return

    if result.get("error"):
        click.echo(f"❌ 创建失败: {result.get('message', '未知错误')}")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        click.echo(f"✅ 创建成功!\n")

        # 基本信息
        click.echo("📋 创建结果:")
        click.echo("-" * 50)
        basic_info = [
            ("实例ID", return_obj.get("instanceId", "N/A")),
            ("实例名称", return_obj.get("instanceName", "N/A")),
            ("订单ID", return_obj.get("orderId", "N/A")),
            ("创建时间", return_obj.get("createTime", "N/A")),
        ]

        for key, value in basic_info:
            click.echo(f"{key:<12}: {value}")

        # 计费信息
        charge_info = return_obj.get("chargeInfo", {})
        if charge_info:
            click.echo(f"\n💰 计费信息:")
            click.echo("-" * 50)
            charge_fields = [
                ("计费模式", charge_info.get("chargeMode", "N/A")),
                ("创建时间", charge_info.get("createTime", "N/A")),
            ]

            for key, value in charge_fields:
                click.echo(f"{key:<12}: {value}")

    else:
        error_msg = result.get("message", "未知错误")
        error_code = result.get("statusCode", "N/A")
        click.echo(f"❌ 创建失败 (错误码: {error_code}): {error_msg}")


def _display_create_instance_summary(result: dict, instance_name: str):
    """显示创建实例摘要"""
    click.echo(f"\n🚀 Redis实例创建摘要 ({instance_name})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 创建状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        click.echo(f"✅ 创建状态: 成功")
        click.echo(f"🏷️  实例ID: {return_obj.get('instanceId', 'N/A')}")
        click.echo(f"📋 订单ID: {return_obj.get('orderId', 'N/A')}")

        charge_info = return_obj.get("chargeInfo", {})
        if charge_info:
            click.echo(f"💰 计费模式: {charge_info.get('chargeMode', 'N/A')}")
        click.echo(f"🕐 创建时间: {return_obj.get('createTime', 'N/A')}")
    else:
        click.echo(f"❌ 创建状态: 失败 - {result.get('message', '未知错误')}")


def _display_resources_table(result: dict, region_id: str, edition: str, version: str):
    """以表格形式显示可用规格"""
    click.echo(f"\n📊 Redis可创建规格查询结果 (区域: {region_id}, 版本: {edition}-{version})")
    click.echo("="*100)

    if not result:
        click.echo("❌ 查询失败: 无响应数据")
        return

    if result.get("error"):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        click.echo(f"✅ 查询成功!\n")

        # 主机类型
        host_types = return_obj.get("hostTypes", [])
        if host_types:
            click.echo("🖥️ 主机类型:")
            click.echo("-" * 80)
            click.echo(f"{'主机类型':<20} {'CPU核数':<8} {'内存GB':<8} {'磁盘类型':<12} {'可用':<6}")
            click.echo("-" * 80)

            for host_type in host_types:
                name = host_type.get("hostTypeName", "N/A")[:18]
                cpu = host_type.get("cpu", "N/A")
                memory = host_type.get("memory", "N/A")
                disk_type = host_type.get("diskType", "N/A")
                available = "是" if host_type.get("available") else "否"

                click.echo(f"{name:<20} {cpu:<8} {memory:<8} {disk_type:<12} {available:<6}")

        # 容量规格
        capacity_specs = return_obj.get("capacitySpecs", [])
        if capacity_specs:
            click.echo(f"\n💾 容量规格:")
            click.echo("-" * 70)
            click.echo(f"{'容量GB':<8} {'最小分片':<10} {'最大分片':<10} {'最小副本':<10} {'最大副本':<10} {'可用':<6}")
            click.echo("-" * 70)

            for spec in capacity_specs:
                capacity = spec.get("capacity", "N/A")
                min_shard = spec.get("minShardCount", "N/A")
                max_shard = spec.get("maxShardCount", "N/A")
                min_copies = spec.get("minCopiesCount", "N/A")
                max_copies = spec.get("maxCopiesCount", "N/A")
                available = "是" if spec.get("available") else "否"

                click.echo(f"{capacity:<8} {min_shard:<10} {max_shard:<10} {min_copies:<10} {max_copies:<10} {available:<6}")

        # 价格信息
        pricing_info = return_obj.get("pricingInfo", {})
        if pricing_info:
            pay_per_use = pricing_info.get("payPerUse", {})
            if pay_per_use:
                click.echo(f"\n💰 按需付费价格:")
                click.echo("-" * 50)
                prices = pay_per_use.get("prices", {})
                for capacity, price in prices.items():
                    click.echo(f"  {capacity}: ¥{price}/小时")

    else:
        error_msg = result.get("message", "未知错误")
        error_code = result.get("statusCode", "N/A")
        click.echo(f"❌ 查询失败 (错误码: {error_code}): {error_msg}")


def _display_resources_summary(result: dict, region_id: str, edition: str, version: str):
    """显示可用规格摘要"""
    click.echo(f"\n📊 Redis可创建规格摘要 (区域: {region_id}, 版本: {edition}-{version})")
    click.echo("="*70)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})
        click.echo(f"✅ 查询状态: 成功")

        # 主机类型统计
        host_types = return_obj.get("hostTypes", [])
        available_hosts = [ht for ht in host_types if ht.get("available")]
        click.echo(f"🖥️ 主机类型: {len(available_hosts)}/{len(host_types)} 种可用")

        # 容量规格统计
        capacity_specs = return_obj.get("capacitySpecs", [])
        available_capacities = [cs for cs in capacity_specs if cs.get("available")]
        capacities = [cs.get("capacity") for cs in available_capacities]

        if capacities:
            min_cap = min(capacities)
            max_cap = max(capacities)
            click.echo(f"💾 容量范围: {min_cap}GB - {max_cap}GB")
            click.echo(f"📊 可选容量: {', '.join(map(str, sorted(capacities)))}GB")

        # 分片和副本配置
        if available_capacities:
            max_shards = max(cs.get("maxShardCount", 1) for cs in available_capacities)
            max_copies = max(cs.get("maxCopiesCount", 1) for cs in available_capacities)
            click.echo(f"🔧 最大分片数: {max_shards}")
            click.echo(f"🔢 最大副本数: {max_copies}")

        # 价格信息
        pricing_info = return_obj.get("pricingInfo", {})
        if pricing_info.get("payPerUse"):
            prices = pricing_info["payPerUse"].get("prices", {})
            if prices:
                min_price = min(float(p) for p in prices.values())
                max_price = max(float(p) for p in prices.values())
                click.echo(f"💰 按需价格: ¥{min_price}/小时 - ¥{max_price}/小时")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")


@redis_group.command('engine-version')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--region-id', '-r', default=None, help='区域ID (默认使用配置中的区域)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_engine_version(ctx, instance_id: str, region_id: str, output_format: str, timeout: int):
    """
    查询Redis实例引擎版本信息

    示例:
        ctyun redis engine-version --instance-id b5fcacfc2e7069553759558b9a4eb27a
        ctyun redis engine-version -i xxx --region-id 200000001852
        ctyun redis engine-version -i xxx -f json
    """
    from redis import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    click.echo(f"🔍 正在查询Redis实例引擎版本信息: {instance_id}")
    if region_id:
        click.echo(f"📍 区域ID: {region_id}")

    try:
        result = redis_client.describe_engine_version(instance_id, region_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_engine_version_table(result, instance_id)
        else:
            _display_engine_version_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询引擎版本信息失败: {str(e)}", err=True)
        sys.exit(1)


def _display_engine_version_table(result: dict, instance_id: str):
    """以表格形式显示引擎版本信息"""
    click.echo(f"\n🔢 Redis实例引擎版本信息 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        click.echo("📊 引擎版本详情:")
        click.echo("-" * 40)
        version_info = [
            ("实例ID", return_obj.get("prodInstId", "N/A")),
            ("引擎大版本号", return_obj.get("versionNo", "N/A")),
            ("架构类型说明", return_obj.get("releaseNotes", "N/A")),
        ]

        for key, value in version_info:
            click.echo(f"{key:<12}: {value}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        if result.get("statusCode"):
            click.echo(f"错误码: {result.get('statusCode')}")


def _display_engine_version_summary(result: dict, instance_id: str):
    """显示引擎版本信息摘要"""
    click.echo(f"\n🔢 Redis实例引擎版本信息摘要 (实例: {instance_id})")
    click.echo("="*60)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        click.echo(f"✅ 查询状态: 成功")
        click.echo(f"🏷️  实例ID: {return_obj.get('prodInstId', 'N/A')}")
        click.echo(f"🔢 引擎版本: {return_obj.get('versionNo', 'N/A')}")
        click.echo(f"🏗️  架构类型: {return_obj.get('releaseNotes', 'N/A')}")

        # 添加版本特征说明
        version_no = return_obj.get('versionNo', '')
        if version_no:
            click.echo(f"📋 版本特征:")
            if version_no.startswith('6.'):
                click.echo(f"   • Redis 6.x - 支持多线程IO、ACL权限控制、客户端缓存等新特性")
            elif version_no.startswith('5.'):
                click.echo(f"   • Redis 5.x - 支持Stream数据结构、Lua脚本优化等")
            elif version_no.startswith('4.'):
                click.echo(f"   • Redis 4.x - 支持PSYNC 2.0、混合持久化等")
            elif version_no.startswith('2.8'):
                click.echo(f"   • Redis 2.8.x - 经典稳定版本，广泛用于生产环境")

        # 添加架构类型说明
        release_notes = return_obj.get('releaseNotes', '')
        if release_notes:
            click.echo(f"🏗️ 架构说明:")
            if 'Cluster' in release_notes:
                click.echo(f"   • 集群版 - 支持数据分片，高可用，水平扩展")
            elif '直连' in release_notes:
                click.echo(f"   • 直连模式 - 客户端直接连接到Redis节点")
            elif 'Proxy' in release_notes:
                click.echo(f"   • 代理模式 - 通过代理节点转发请求")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")
        if result.get("statusCode"):
            click.echo(f"错误码: {result.get('statusCode')}")


@redis_group.command('instance-version')
@click.option('--instance-id', '-i', required=True, help='Redis实例ID (必需)')
@click.option('--region-id', '-r', default=None, help='区域ID (默认使用配置中的区域)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='summary', help='输出格式 (table/json/summary)')
@click.option('--timeout', '-t', default=30, help='请求超时时间(秒)')
@click.pass_context
@validate_credentials
def describe_instance_version(ctx, instance_id: str, region_id: str, output_format: str, timeout: int):
    """
    查询Redis实例详细版本信息

    示例:
        ctyun redis instance-version --instance-id b5fcacfc2e7069553759558b9a4eb27a
        ctyun redis instance-version -i xxx --region-id 200000001852
        ctyun redis instance-version -i xxx -f json
    """
    from redis import RedisClient

    client = ctx.obj['client']
    redis_client = RedisClient(client)
    redis_client.set_timeout(timeout)

    click.echo(f"🔍 正在查询Redis实例详细版本信息: {instance_id}")
    if region_id:
        click.echo(f"📍 区域ID: {region_id}")

    try:
        result = redis_client.describe_instance_version(instance_id, region_id)

        if output_format == 'json':
            _display_json(result)
        elif output_format == 'table':
            _display_instance_version_table(result, instance_id)
        else:
            _display_instance_version_summary(result, instance_id)

    except Exception as e:
        click.echo(f"❌ 查询实例版本信息失败: {str(e)}", err=True)
        sys.exit(1)


def _display_instance_version_table(result: dict, instance_id: str):
    """以表格形式显示实例详细版本信息"""
    click.echo(f"\n🔢 Redis实例详细版本信息 (实例: {instance_id})")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo("❌ 查询失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        # 引擎大版本信息
        engine_major_info = return_obj.get("engineMajorVersionInfo", {})
        # 引擎小版本信息
        engine_minor_info = return_obj.get("engineMinorVersionInfo", {})
        # 代理版本信息
        proxy_info = return_obj.get("proxyVersionInfo", {})

        click.echo("📊 引擎大版本信息:")
        click.echo("-" * 40)
        engine_version_items = engine_major_info.get("engineVersionItems", [])
        upgradable_major_items = engine_major_info.get("upgradableEngineVersionItems", [])

        major_info = [
            ("当前大版本", engine_major_info.get("engineMajorVersion", "N/A")),
            ("可用大版本列表", ", ".join(engine_version_items) if engine_version_items else "N/A"),
            ("可升级大版本", ", ".join(upgradable_major_items) if upgradable_major_items else "无可升级版本"),
        ]

        for key, value in major_info:
            click.echo(f"{key:<16}: {value}")

        click.echo("\n📊 引擎小版本信息:")
        click.echo("-" * 40)
        upgradable_minor_items = engine_minor_info.get("upgradableEngineMinorVersionItems", [])

        minor_info = [
            ("当前小版本", engine_minor_info.get("engineMinorVersion", "N/A")),
            ("可升级小版本", ", ".join(upgradable_minor_items) if upgradable_minor_items else "无可升级版本"),
        ]

        for key, value in minor_info:
            click.echo(f"{key:<16}: {value}")

        click.echo("\n📊 代理版本信息:")
        click.echo("-" * 40)
        upgradable_proxy_items = proxy_info.get("upgradableProxyMinorVersions", [])

        proxy_version_info = [
            ("当前代理版本", proxy_info.get("proxyMinorVersion", "N/A")),
            ("可升级代理版本", ", ".join(upgradable_proxy_items) if upgradable_proxy_items else "无可升级版本"),
        ]

        for key, value in proxy_version_info:
            click.echo(f"{key:<16}: {value}")

    else:
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}")
        if result.get("statusCode"):
            click.echo(f"错误码: {result.get('statusCode')}")


def _display_instance_version_summary(result: dict, instance_id: str):
    """显示实例详细版本信息摘要"""
    click.echo(f"\n🔢 Redis实例详细版本信息摘要 (实例: {instance_id})")
    click.echo("="*80)

    if not result or result.get("error"):
        click.echo(f"❌ 查询状态: 失败")
        return

    if result.get("statusCode") == 800:
        return_obj = result.get("returnObj", {})

        # 引擎大版本信息
        engine_major_info = return_obj.get("engineMajorVersionInfo", {})
        # 引擎小版本信息
        engine_minor_info = return_obj.get("engineMinorVersionInfo", {})
        # 代理版本信息
        proxy_info = return_obj.get("proxyVersionInfo", {})

        click.echo(f"✅ 查询状态: 成功")
        click.echo(f"🏷️  实例ID: {instance_id}")

        # 引擎版本摘要
        major_version = engine_major_info.get("engineMajorVersion", "N/A")
        minor_version = engine_minor_info.get("engineMinorVersion", "N/A")
        proxy_version = proxy_info.get("proxyMinorVersion", "N/A")

        click.echo(f"🔢 引擎版本: {major_version} (小版本: {minor_version})")
        click.echo(f"🔗 代理版本: {proxy_version}")

        # 可升级信息
        upgradable_major = engine_major_info.get("upgradableEngineVersionItems", [])
        upgradable_minor = engine_minor_info.get("upgradableEngineMinorVersionItems", [])
        upgradable_proxy = proxy_info.get("upgradableProxyMinorVersions", [])

        if upgradable_major or upgradable_minor or upgradable_proxy:
            click.echo(f"🔄 可升级版本:")
            if upgradable_major:
                click.echo(f"   • 引擎大版本: {', '.join(upgradable_major)}")
            if upgradable_minor:
                click.echo(f"   • 引擎小版本: {', '.join(upgradable_minor)}")
            if upgradable_proxy:
                click.echo(f"   • 代理版本: {', '.join(upgradable_proxy)}")
        else:
            click.echo(f"✅ 版本状态: 已是最新版本")

        # 版本特性说明
        if major_version != "N/A":
            click.echo(f"📋 版本特性:")
            if major_version.startswith('7.'):
                click.echo(f"   • Redis 7.x - 最新稳定版本，性能和功能全面优化")
            elif major_version.startswith('6.'):
                click.echo(f"   • Redis 6.x - 支持多线程IO、ACL权限控制、客户端缓存等")
            elif major_version.startswith('5.'):
                click.echo(f"   • Redis 5.x - 支持Stream数据结构、Lua脚本优化等")
            elif major_version.startswith('4.'):
                click.echo(f"   • Redis 4.x - 支持PSYNC 2.0、混合持久化等")
            elif major_version.startswith('2.8'):
                click.echo(f"   • Redis 2.8.x - 经典稳定版本，广泛用于生产环境")

    else:
        click.echo(f"❌ 查询状态: 失败 - {result.get('message', '未知错误')}")
        if result.get("statusCode"):
            click.echo(f"错误码: {result.get('statusCode')}")
