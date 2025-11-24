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
    # 获取凭证（validate_credentials装饰器已验证）
    client = ctx.obj.get('client')
    if client and hasattr(client, 'access_key') and hasattr(client, 'secret_key'):
        access_key = client.access_key
        secret_key = client.secret_key
    else:
        access_key = ctx.obj.get('access_key')
        secret_key = ctx.obj.get('secret_key')

    click.echo(f"🔍 正在查询区域 {region_id} 的Redis可用区...")

    # 创建Redis客户端
    redis_client = RedisClient(access_key, secret_key, region_id)
    redis_client.set_timeout(timeout)

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
    client = ctx.obj.get('client')
    if client and hasattr(client, 'access_key') and hasattr(client, 'secret_key'):
        access_key = client.access_key
        secret_key = client.secret_key
    else:
        access_key = ctx.obj.get('access_key')
        secret_key = ctx.obj.get('secret_key')

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
            redis_client = RedisClient(access_key, secret_key, region_id)
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