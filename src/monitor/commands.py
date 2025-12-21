"""
云监控服务命令行接口
"""

import click
from typing import Optional, List
from datetime import datetime, timedelta
from core import CTYUNAPIError
from utils import OutputFormatter, logger
from monitor import MonitorClient


def handle_error(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CTYUNAPIError as e:
            click.echo(f"API错误 [{e.code}]: {e.message}", err=True)
            if e.request_id:
                click.echo(f"请求ID: {e.request_id}", err=True)
            import sys
            sys.exit(1)
        except Exception as e:
            click.echo(f"错误: {e}", err=True)
            import sys
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """格式化输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                table = OutputFormatter.format_table(data, headers)
                click.echo(table)
            else:
                click.echo(data)
        elif isinstance(data, dict):
            headers = ['字段', '值']
            table_data = []
            for key, value in data.items():
                table_data.append([key, value])
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


@click.group()
def monitor():
    """云监控服务管理"""
    pass


@monitor.command('custom-trend')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-item-id', required=True, help='自定义监控项ID')
@click.option('--start-time', type=int, help='查询起始时间戳（Unix时间戳，秒），默认为24小时前')
@click.option('--end-time', type=int, help='查询结束时间戳（Unix时间戳，秒），默认为当前时间')
@click.option('--period', default=300, type=int, help='聚合周期（秒），默认300秒（5分钟）')
@click.option('--dimension', multiple=True, help='维度过滤，格式：name=value1,value2（可多次指定）')
@click.pass_context
@handle_error
def custom_trend(ctx, region_id: str, custom_item_id: str,
                start_time: Optional[int], end_time: Optional[int],
                period: int, dimension: tuple):
    """
    查询自定义监控项的时序指标趋势监控数据
    
    示例：
        # 查询最近24小时的监控数据
        ctyun-cli monitor custom-trend \\
            --region-id 81f7728662dd11ec810800155d307d5b \\
            --custom-item-id 64ea1664-4347-558e-9bc6-651341c2fa15
        
        # 查询指定时间段和维度的监控数据
        ctyun-cli monitor custom-trend \\
            --region-id 81f7728662dd11ec810800155d307d5b \\
            --custom-item-id 64ea1664-4347-558e-9bc6-651341c2fa15 \\
            --start-time 1687158009 \\
            --end-time 1687158309 \\
            --dimension uuid=00350e57-67af-f1db-1fa5-20193d873f5d \\
            --dimension job=virtual_machine,bare_metal
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    
    dimensions = None
    if dimension:
        dimensions = []
        for dim in dimension:
            if '=' not in dim:
                click.echo(f"❌ 维度格式错误: {dim}，应为 name=value1,value2", err=True)
                import sys
                sys.exit(1)
            
            name, values = dim.split('=', 1)
            value_list = [v.strip() for v in values.split(',')]
            dimensions.append({
                'name': name.strip(),
                'value': value_list
            })
    
    result = monitor_client.query_custom_item_trendmetricdata(
        region_id=region_id,
        custom_item_id=custom_item_id,
        start_time=start_time,
        end_time=end_time,
        period=period,
        dimensions=dimensions
    )
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    results = data.get('result', [])
    
    if not results:
        click.echo("未找到监控数据")
        return
    
    if output_format in ['json', 'yaml']:
        format_output(results, output_format)
    else:
        for idx, item in enumerate(results, 1):
            click.echo(f"\n{'='*70}")
            click.echo(f"数据组 #{idx}")
            click.echo(f"{'='*70}")
            
            click.echo(f"资源池ID: {item.get('regionID', '')}")
            click.echo(f"监控项ID: {item.get('customItemID', '')}")
            
            dims = item.get('dimensions', [])
            if dims:
                click.echo("\n维度信息:")
                for dim in dims:
                    click.echo(f"  {dim.get('name', '')}: {dim.get('value', '')}")
            
            datapoints = item.get('data', [])
            if datapoints:
                click.echo(f"\n监控数据 (共 {len(datapoints)} 个数据点):")
                
                table_data = []
                headers = ['采样时间', '最大值', '最小值', '平均值', '方差']
                
                total_avg = 0
                total_max = 0
                total_min = float('inf')
                count = 0
                
                for dp in datapoints:
                    sampling_time = dp.get('samplingTime', 0)
                    if sampling_time:
                        try:
                            dt = datetime.fromtimestamp(sampling_time)
                            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            time_str = str(sampling_time)
                    else:
                        time_str = ''
                    
                    max_val = dp.get('max', 0)
                    min_val = dp.get('min', 0)
                    avg_val = dp.get('avg', 0)
                    variance = dp.get('variance', 0)
                    
                    total_avg += avg_val
                    if max_val > total_max:
                        total_max = max_val
                    if min_val < total_min:
                        total_min = min_val
                    count += 1
                    
                    table_data.append([
                        time_str,
                        f"{max_val:.4f}",
                        f"{min_val:.4f}",
                        f"{avg_val:.4f}",
                        f"{variance:.4f}"
                    ])
                
                table = OutputFormatter.format_table(table_data, headers)
                click.echo(table)
                
                if count > 0:
                    avg_overall = total_avg / count
                    click.echo(f"\n统计汇总:")
                    click.echo(f"  数据点数: {count}")
                    click.echo(f"  平均值: {avg_overall:.4f}")
                    click.echo(f"  最大值: {total_max:.4f}")
                    click.echo(f"  最小值: {total_min:.4f}")
        
        click.echo(f"\n{'='*70}")
        click.echo(f"共 {len(results)} 个数据组")




@click.option('--device-id', required=True, help='云专线设备ID')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--metric', 
              type=click.Choice(['network_incoming_bytes', 'network_outgoing_bytes', 'both']),
              default='both',
              help='监控指标（network_incoming_bytes: 流入流量, network_outgoing_bytes: 流出流量, both: 两者）')
@click.option('--start-time', help='开始时间（格式：2024-01-01T00:00:00Z），默认为24小时前')
@click.option('--end-time', help='结束时间（格式：2024-01-01T00:00:00Z），默认为当前时间')
@click.option('--period', default=300, type=int, help='统计周期（秒），默认300秒（5分钟）')
@click.pass_context
@handle_error
def dcaas_traffic(ctx, device_id: str, region_id: str, metric: str,
                 start_time: Optional[str], end_time: Optional[str], period: int):
    """
    查询云专线流量监控数据
    
    示例：
        # 查询最近24小时的流入和流出流量
        ctyun-cli monitor dcaas-traffic --device-id xxx --region-id xxx
        
        # 查询指定时间段的流入流量
        ctyun-cli monitor dcaas-traffic --device-id xxx --region-id xxx \\
            --metric network_incoming_bytes \\
            --start-time 2024-01-01T00:00:00Z \\
            --end-time 2024-01-02T00:00:00Z
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    
    metrics_to_query = []
    if metric == 'both':
        metrics_to_query = ['network_incoming_bytes', 'network_outgoing_bytes']
    else:
        metrics_to_query = [metric]
    
    all_results = {}
    
    for m in metrics_to_query:
        result = monitor_client.query_dcaas_traffic(
            device_id=device_id,
            region_id=region_id,
            start_time=start_time,
            end_time=end_time,
            period=period,
            metric=m
        )
        
        if not result.get('success'):
            click.echo(f"❌ 查询 {m} 失败: {result.get('message', '未知错误')}", err=True)
            continue
        
        all_results[m] = result.get('data', {})
    
    if not all_results:
        click.echo("❌ 没有成功查询到任何数据", err=True)
        import sys
        sys.exit(1)
    
    if output_format in ['json', 'yaml']:
        format_output(all_results, output_format)
    else:
        for metric_name, data in all_results.items():
            metric_display = '流入流量' if metric_name == 'network_incoming_bytes' else '流出流量'
            click.echo(f"\n{'='*60}")
            click.echo(f"监控指标: {metric_display} ({metric_name})")
            click.echo(f"{'='*60}")
            
            datapoints = data.get('datapoints', [])
            
            if not datapoints:
                click.echo("未找到监控数据")
                continue
            
            table_data = []
            headers = ['时间戳', '平均值(Bytes)', '最大值(Bytes)', '最小值(Bytes)']
            
            total_avg = 0
            total_max = 0
            count = 0
            
            for dp in datapoints:
                timestamp = dp.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        timestamp_str = timestamp
                else:
                    timestamp_str = ''
                
                avg_value = dp.get('average', 0)
                max_value = dp.get('max', 0)
                min_value = dp.get('min', 0)
                
                total_avg += avg_value
                if max_value > total_max:
                    total_max = max_value
                count += 1
                
                table_data.append([
                    timestamp_str,
                    f"{avg_value:,.2f}",
                    f"{max_value:,.2f}",
                    f"{min_value:,.2f}"
                ])
            
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
            
            if count > 0:
                avg_overall = total_avg / count
                click.echo(f"\n统计汇总:")
                click.echo(f"  数据点数: {count}")
                click.echo(f"  平均流量: {avg_overall:,.2f} Bytes ({avg_overall/1024/1024:,.2f} MB)")
                click.echo(f"  峰值流量: {total_max:,.2f} Bytes ({total_max/1024/1024:,.2f} MB)")



@monitor.command('cpu-top')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--number', default=3, type=int, help='选取TOP值的数量，默认为3')
@click.pass_context
@handle_error
def cpu_top(ctx, region_id: str, number: int):
    """
    查询云主机CPU使用率Top-N
    
    示例：
        # 查询CPU使用率Top 3
        ctyun-cli monitor cpu-top --region-id bb9fdb42056f11eda1610242ac110002
        
        # 查询CPU使用率Top 10
        ctyun-cli monitor cpu-top --region-id bb9fdb42056f11eda1610242ac110002 --number 10
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_cpu_top(region_id, number)

    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}", err=True)
        import sys
        sys.exit(1)

    data = result.get('data', {})
    # 检查 data 是否是列表（直接返回的CPU列表）
    if isinstance(data, list):
        cpu_list = data
    else:
        # 如果是字典，尝试获取 cpuList
        cpu_list = data.get('cpuList', [])

    if not cpu_list:
        click.echo("未找到云主机CPU数据")
        return
    
    if output_format in ['json', 'yaml']:
        format_output(cpu_list, output_format)
    else:
        click.echo(f"\n云主机CPU使用率 Top {number}")
        click.echo("=" * 80)
        
        table_data = []
        headers = ['排名', '设备ID', '设备名称', 'CPU使用率(%)']
        
        for idx, item in enumerate(cpu_list, 1):
            device_id = item.get('deviceID', '')
            device_name = item.get('name', '')
            cpu_value = item.get('value', '0')
            
            try:
                cpu_value_float = float(cpu_value)
                # 检查值是否已经是百分比格式（大于1则假设已经是百分比）
                if cpu_value_float > 1:
                    cpu_percent = cpu_value_float
                else:
                    cpu_percent = cpu_value_float * 100
                cpu_display = f"{cpu_percent:.2f}%"
            except:
                cpu_display = f"{cpu_value}%"
            
            table_data.append([
                f"#{idx}",
                device_id,
                device_name,
                cpu_display
            ])

        # 直接使用 tabulate 来格式化表格数据
        from tabulate import tabulate
        table = tabulate(table_data, headers=headers, tablefmt='grid')
        click.echo(table)
        
        if cpu_list:
            click.echo(f"\n共找到 {len(cpu_list)} 台云主机")
            try:
                cpu_values = []
                for item in cpu_list:
                    val = float(item.get('value', 0))
                    # 检查值是否已经是百分比格式
                    if val > 1:
                        cpu_values.append(val)
                    else:
                        cpu_values.append(val * 100)

                max_cpu = max(cpu_values)
                min_cpu = min(cpu_values)
                avg_cpu = sum(cpu_values) / len(cpu_values)
                
                click.echo(f"CPU使用率统计:")
                click.echo(f"  最高: {max_cpu:.2f}%")
                click.echo(f"  最低: {min_cpu:.2f}%")
                click.echo(f"  平均: {avg_cpu:.2f}%")
            except:
                pass


@monitor.command('mem-top')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--number', default=3, type=int, help='选取TOP值的数量，默认为3')
@click.pass_context
@handle_error
def mem_top(ctx, region_id: str, number: int):
    """
    查询云主机内存使用率Top-N
    
    示例：
        # 查询内存使用率Top 3
        ctyun-cli monitor mem-top --region-id bb9fdb42056f11eda1610242ac110002
        
        # 查询内存使用率Top 10
        ctyun-cli monitor mem-top --region-id bb9fdb42056f11eda1610242ac110002 --number 10
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_mem_top(region_id, number)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    # 检查 data 是否是列表（直接返回的内存列表）
    if isinstance(data, list):
        mem_list = data
    else:
        # 如果是字典，尝试获取 memList
        mem_list = data.get('memList', [])
    
    if not mem_list:
        click.echo("未找到云主机内存数据")
        return
    
    if output_format in ['json', 'yaml']:
        format_output(mem_list, output_format)
    else:
        click.echo(f"\n云主机内存使用率 Top {number}")
        click.echo("=" * 80)
        
        table_data = []
        headers = ['排名', '设备ID', '设备名称', '内存使用率(%)']
        
        for idx, item in enumerate(mem_list, 1):
            device_id = item.get('deviceID', '')
            device_name = item.get('name', '')
            mem_value = item.get('value', '0')
            
            try:
                mem_percent = float(mem_value)
                mem_display = f"{mem_percent:.2f}%"
            except:
                mem_display = mem_value
            
            table_data.append([
                f"#{idx}",
                device_id,
                device_name,
                mem_display
            ])

        # 直接使用 tabulate 来格式化表格数据
        from tabulate import tabulate
        table = tabulate(table_data, headers=headers, tablefmt='grid')
        click.echo(table)

        if mem_list:
            click.echo(f"\n共找到 {len(mem_list)} 台云主机")
            try:
                max_mem = max([float(item.get('value', 0)) for item in mem_list])
                min_mem = min([float(item.get('value', 0)) for item in mem_list])
                avg_mem = sum([float(item.get('value', 0)) for item in mem_list]) / len(mem_list)
                
                click.echo(f"内存使用率统计:")
                click.echo(f"  最高: {max_mem:.2f}%")
                click.echo(f"  最低: {min_mem:.2f}%")
                click.echo(f"  平均: {avg_mem:.2f}%")
            except:
                pass


@monitor.command('disk-top')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--number', default=3, type=int, help='选取TOP值的数量，默认为3')
@click.pass_context
@handle_error
def disk_top(ctx, region_id: str, number: int):
    """
    查询云主机磁盘使用率Top-N
    
    示例：
        # 查询磁盘使用率Top 3
        ctyun-cli monitor disk-top --region-id bb9fdb42056f11eda1610242ac110002
        
        # 查询磁盘使用率Top 10
        ctyun-cli monitor disk-top --region-id bb9fdb42056f11eda1610242ac110002 --number 10
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_disk_top(region_id, number)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    # 检查 data 是否是列表（直接返回的磁盘列表）
    if isinstance(data, list):
        disk_list = data
    else:
        # 如果是字典，尝试获取 diskList
        disk_list = data.get('diskList', [])
    
    if not disk_list:
        click.echo("未找到云主机磁盘数据")
        return
    
    if output_format in ['json', 'yaml']:
        format_output(disk_list, output_format)
    else:
        click.echo(f"\n云主机磁盘使用率 Top {number}")
        click.echo("=" * 80)
        
        table_data = []
        headers = ['排名', '设备ID', '设备名称', '磁盘使用率(%)']
        
        for idx, item in enumerate(disk_list, 1):
            device_id = item.get('deviceID', '')
            device_name = item.get('name', '')
            disk_value = item.get('value', '0')
            
            try:
                disk_percent = float(disk_value)
                disk_display = f"{disk_percent:.2f}%"
            except:
                disk_display = disk_value
            
            table_data.append([
                f"#{idx}",
                device_id,
                device_name,
                disk_display
            ])

        # 直接使用 tabulate 来格式化表格数据
        from tabulate import tabulate
        table = tabulate(table_data, headers=headers, tablefmt='grid')
        click.echo(table)

        if disk_list:
            click.echo(f"\n共找到 {len(disk_list)} 台云主机")
            try:
                max_disk = max([float(item.get('value', 0)) for item in disk_list])
                min_disk = min([float(item.get('value', 0)) for item in disk_list])
                avg_disk = sum([float(item.get('value', 0)) for item in disk_list]) / len(disk_list)
                
                click.echo(f"磁盘使用率统计:")
                click.echo(f"  最高: {max_disk:.2f}%")
                click.echo(f"  最低: {min_disk:.2f}%")
                click.echo(f"  平均: {avg_disk:.2f}%")
            except:
                pass


@monitor.command('query-items')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', help='服务（如：ecs）')
@click.option('--dimension', help='维度（如：ecs）')
@click.option('--item-type', type=click.Choice(['series', 'event']), help='监控项类型')
@click.option('--ignore-items', is_flag=True, help='不展示监控项详细信息')
@click.pass_context
@handle_error
def query_items(ctx, region_id: str, service: Optional[str], dimension: Optional[str],
               item_type: Optional[str], ignore_items: bool):
    """
    查询服务维度及监控项
    
    示例：
        # 查询所有服务和监控项
        ctyun-cli monitor query-items --region-id bb9fdb42056f11eda1610242ac110002
        
        # 查询指定服务（如ECS）的监控项
        ctyun-cli monitor query-items \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs
        
        # 只查询服务和维度信息，不显示监控项详情
        ctyun-cli monitor query-items \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --ignore-items
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_monitor_items(
        region_id=region_id,
        service=service,
        dimension=dimension,
        item_type=item_type,
        ignore_items=ignore_items
    )
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    services = data.get('data', [])
    
    if not services:
        click.echo("未找到监控项数据")
        return
    
    if output_format in ['json', 'yaml']:
        format_output(services, output_format)
    else:
        for svc in services:
            click.echo(f"\n{'='*80}")
            click.echo(f"服务: {svc.get('service', '')} - {svc.get('description', '')}")
            click.echo(f"监控项总数: {svc.get('serviceCount', 0)}")
            click.echo(f"{'='*80}")
            
            dimensions = svc.get('dimensions', [])
            for dim in dimensions:
                click.echo(f"\n  维度: {dim.get('dimension', '')} - {dim.get('description', '')}")
                click.echo(f"  监控项数量: {dim.get('dimensionCount', 0)}")
                
                if not ignore_items:
                    monitor_items = dim.get('monitorItems', [])
                    if monitor_items:
                        click.echo(f"\n  监控项列表:")
                        
                        table_data = []
                        headers = ['监控项Key', '名称', '单位', '周期(s)', '统计类型']
                        
                        try:
                            for item in monitor_items:
                                # 处理 item 可能是 dict 或其他类型
                                if isinstance(item, dict):
                                    name = item.get('name', '')
                                    metric_name = item.get('metricName', '')
                                    unit = item.get('unit', '')
                                    period = item.get('period', '')
                                    statistics = item.get('statistics', [])
                                    if isinstance(statistics, list):
                                        statistics = ', '.join(statistics)
                                    
                                    table_data.append([
                                        name,
                                        metric_name,
                                        unit,
                                        str(period),
                                        str(statistics)
                                    ])
                            
                            if table_data:
                                table = OutputFormatter.format_table(table_data, headers)
                                click.echo(f"\n{table}")
                        except Exception as e:
                            click.echo(f"错误: {str(e)}", err=True)
        
        click.echo(f"\n{'='*80}")
        click.echo(f"共找到 {len(services)} 个服务")


@monitor.command('query-sys-services')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
@handle_error
def query_sys_services(ctx, region_id: str):
    """
    查询系统看板支持的服务维度
    
    示例：
        # 查询支持的服务维度
        ctyun-cli monitor query-sys-services --region-id bb9fdb42056f11eda1610242ac110002
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_sys_services(region_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message', '未知错误')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    services = data.get('data', [])
    
    if not services:
        click.echo("未找到支持的服务维度")
        return
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(services))
        return
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(services, allow_unicode=True, default_flow_style=False))
            return
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    
    try:
        click.echo(f"\n系统看板支持的服务维度")
        click.echo("=" * 80)
        
        table_data = []
        headers = ['服务', '服务名称', '维度', '维度名称']
        
        for svc in services:
            if not isinstance(svc, dict):
                continue
                
            service_key = svc.get('service', '')
            service_name = svc.get('serviceName', '')
            
            dimensions = svc.get('dimensions', [])
            if dimensions and isinstance(dimensions, list):
                for idx, dim in enumerate(dimensions):
                    if not isinstance(dim, dict):
                        continue
                        
                    dim_key = dim.get('dimension', '')
                    dim_name = dim.get('dimensionName', '')
                    
                    if idx == 0:
                        table_data.append([service_key, service_name, dim_key, dim_name])
                    else:
                        table_data.append(['', '', dim_key, dim_name])
            else:
                table_data.append([service_key, service_name, '', ''])
        
        if not table_data:
            click.echo("未找到可显示的数据")
            return
        
        from tabulate import tabulate
        table = tabulate(table_data, headers=headers, tablefmt='grid')
        click.echo(f"\n{table}")
        
        click.echo(f"\n{'='*80}")
        total_dims = sum([len(svc.get('dimensions', [])) for svc in services if isinstance(svc, dict)])
        click.echo(f"共找到 {len(services)} 个服务，{total_dims} 个维度")
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)


@monitor.command('describe')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--board-id', required=True, help='监控看板ID')
@click.pass_context
@handle_error
def describe_board(ctx, region_id: str, board_id: str):
    """
    查看监控看板详细信息
    
    示例：
        # 查看指定看板详情
        ctyun-cli monitor describe \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --board-id 0bf803e8-5049-11ed-8fb7-005056897257
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.describe_monitor_board(region_id, board_id)
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        
        if error_code == 'MonitorBoardNotExist':
            click.echo(f"❌ 监控看板不存在: {error_msg}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    views = data.get('views', [])
    view_quota = data.get('viewQuota', 0)
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n监控看板详情")
        click.echo("=" * 60)
        click.echo(f"看板ID: {board_id}")
        click.echo(f"视图配额剩余: {view_quota}")
        click.echo(f"视图数量: {len(views)}")
        
        if views:
            click.echo(f"\n视图列表:")
            click.echo("-" * 60)
            
            for idx, view in enumerate(views, 1):
                if not isinstance(view, dict):
                    continue
                    
                view_id = view.get('viewID', '')
                name = view.get('name', '')
                service = view.get('service', '')
                dimension = view.get('dimension', '')
                view_type = view.get('viewType', '')
                order_index = view.get('orderIndex', 0)
                create_time = view.get('createTime', 0)
                update_time = view.get('updateTime', 0)
                
                # 格式化时间
                try:
                    from datetime import datetime
                    create_dt = datetime.fromtimestamp(create_time) if create_time else '未知'
                    update_dt = datetime.fromtimestamp(update_time) if update_time else '未知'
                except:
                    create_dt = '未知'
                    update_dt = '未知'
                
                click.echo(f"\n  视图 #{idx}")
                click.echo(f"    ID: {view_id}")
                click.echo(f"    名称: {name}")
                click.echo(f"    服务: {service}")
                click.echo(f"    维度: {dimension}")
                click.echo(f"    类型: {view_type}")
                click.echo(f"    排序: {order_index}")
                click.echo(f"    创建时间: {create_dt}")
                click.echo(f"    更新时间: {update_dt}")
                
                # 显示监控指标
                item_names = view.get('itemNameList', [])
                if item_names:
                    click.echo(f"    监控指标: {', '.join(item_names)}")
                
                # 显示资源实例
                resources = view.get('resources', [])
                if resources:
                    resource_list = []
                    for res in resources:
                        if isinstance(res, dict) and 'resource' in res:
                            resource_items = res['resource']
                            if isinstance(resource_items, list):
                                for item in resource_items:
                                    if isinstance(item, dict):
                                        key = item.get('key', '')
                                        value = item.get('value', '')
                                        resource_list.append(f"{key}={value}")
                    if resource_list:
                        click.echo(f"    资源实例: {', '.join(resource_list)}")
        
        click.echo(f"\n{'='*60}")


@monitor.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--board-type', type=click.Choice(['all', 'system', 'custom']), 
              help='看板类型（all/system/custom）')
@click.option('--name', help='名称模糊搜索')
@click.option('--service', help='服务（仅当boardType为system时有效）')
@click.option('--dimension', help='维度（仅当boardType为system时有效）')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=10, help='页大小，默认为10')
@click.pass_context
@handle_error
def list_boards(ctx, region_id: str, board_type: Optional[str], name: Optional[str],
               service: Optional[str], dimension: Optional[str], 
               page_no: int, page_size: int):
    """
    查询监控看板列表
    
    示例：
        # 查询所有看板
        ctyun-cli monitor list --region-id bb9fdb42056f11eda1610242ac110002
        
        # 查询系统默认看板
        ctyun-cli monitor list \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --board-type system
            
        # 模糊搜索看板名称
        ctyun-cli monitor list \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --name "看板"
            
        # 分页查询
        ctyun-cli monitor list \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --page-no 1 \
            --page-size 5
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.list_monitor_boards(
        region_id=region_id,
        board_type=board_type,
        name=name,
        service=service,
        dimension=dimension,
        page_no=page_no,
        page_size=page_size
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    board_list = data.get('boardList', [])
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)
    total_page = data.get('totalPage', 0)
    board_quota = data.get('boardQuota', 0)
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n监控看板列表")
        click.echo("=" * 80)
        click.echo(f"总记录数: {total_count}")
        click.echo(f"当前页记录数: {current_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"看板配额剩余: {board_quota}")
        
        if board_list:
            click.echo(f"\n看板详情:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['ID', '类型', '名称', '创建时间', '更新时间']
            
            for board in board_list:
                if not isinstance(board, dict):
                    continue
                    
                board_id = board.get('boardID', '')[:20] + '...' if len(board.get('boardID', '')) > 20 else board.get('boardID', '')
                board_type = board.get('type', '')
                name = board.get('name', '')
                create_time = board.get('createTime', 0)
                update_time = board.get('updateTime', 0)
                
                # 格式化时间
                try:
                    from datetime import datetime
                    create_dt = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
                    update_dt = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S') if update_time else '未知'
                except:
                    create_dt = '未知'
                    update_dt = '未知'
                
                table_data.append([
                    board_id,
                    board_type,
                    name,
                    create_dt,
                    update_dt
                ])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
        else:
            click.echo("\n未找到监控看板")
        
        click.echo(f"\n{'='*80}")


@monitor.command('describe-view')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--view-id', required=True, help='监控视图ID')
@click.pass_context
@handle_error
def describe_view(ctx, region_id: str, view_id: str):
    """
    查看监控视图详细信息
    
    示例：
        # 查看指定视图详情
        ctyun-cli monitor describe-view \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --view-id 0bf803e8-5049-11ed-8fb7-005056897257
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.describe_monitor_view(region_id, view_id)
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        
        if error_code == 'MonitorViewNotExist':
            click.echo(f"❌ 监控视图不存在: {error_msg}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n监控视图详情")
        click.echo("=" * 60)
        click.echo(f"视图ID: {view_id}")
        
        if isinstance(data, dict):
            name = data.get('name', '')
            service = data.get('service', '')
            dimension = data.get('dimension', '')
            view_type = data.get('viewType', '')
            order_index = data.get('orderIndex', 0)
            create_time = data.get('createTime', 0)
            update_time = data.get('updateTime', 0)
            
            # 格式化时间
            try:
                from datetime import datetime
                create_dt = datetime.fromtimestamp(create_time) if create_time else '未知'
                update_dt = datetime.fromtimestamp(update_time) if update_time else '未知'
            except:
                create_dt = '未知'
                update_dt = '未知'
            
            click.echo(f"名称: {name}")
            click.echo(f"服务: {service}")
            click.echo(f"维度: {dimension}")
            click.echo(f"类型: {view_type}")
            click.echo(f"排序: {order_index}")
            click.echo(f"创建时间: {create_dt}")
            click.echo(f"更新时间: {update_dt}")
            
            # 显示监控指标
            item_names = data.get('itemNameList', [])
            if item_names:
                click.echo(f"监控指标: {', '.join(item_names)}")
            
            # 显示同比环比配置
            compares = data.get('compares', [])
            if compares:
                click.echo(f"同比环比: {', '.join(compares)}")
            
            # 显示资源实例
            resources = data.get('resources', [])
            if resources:
                click.echo(f"\n资源实例:")
                for res in resources:
                    if isinstance(res, dict) and 'resource' in res:
                        resource_items = res['resource']
                        if isinstance(resource_items, list):
                            for item in resource_items:
                                if isinstance(item, dict):
                                    key = item.get('key', '')
                                    value = item.get('value', '')
                                    click.echo(f"  {key}: {value}")
            
            # 显示仪表盘配置
            gauge_pattern = data.get('gaugePattern', {})
            if gauge_pattern and isinstance(gauge_pattern, dict):
                click.echo(f"\n仪表盘配置:")
                min_val = gauge_pattern.get('minVal', 0)
                max_val = gauge_pattern.get('maxVal', 0)
                threshold = gauge_pattern.get('threshold', [])
                click.echo(f"  最小值: {min_val}")
                click.echo(f"  最大值: {max_val}")
                click.echo(f"  阈值: {threshold}")
        
        click.echo(f"\n{'='*60}")


@monitor.command('query-view-data')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--view-id', required=True, help='面板ID')
@click.option('--start-time', type=int, help='查询起始Unix时间戳')
@click.option('--end-time', type=int, help='查询结束Unix时间戳')
@click.option('--fun', type=click.Choice(['raw', 'avg', 'min', 'max', 'variance', 'sum']), 
              help='聚合类型')
@click.option('--period', type=int, help='聚合周期（秒）')
@click.pass_context
@handle_error
def query_view_data_cmd(ctx, region_id: str, view_id: str, start_time: Optional[int],
                       end_time: Optional[int], fun: Optional[str], period: Optional[int]):
    """
    查询监控视图数据
    
    示例：
        # 查询视图最近1小时的数据
        ctyun-cli monitor query-view-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --view-id fb33ae47-415f-4026-23ad-c8492a667e9c
            
        # 查询指定时间范围的数据
        ctyun-cli monitor query-view-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --view-id fb33ae47-415f-4026-23ad-c8492a667e9c \
            --start-time 1667815639 \
            --end-time 1667817639 \
            --fun avg \
            --period 300
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_view_data(
        region_id=region_id,
        view_id=view_id,
        start_time=start_time,
        end_time=end_time,
        fun=fun,
        period=period
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n监控视图数据查询")
        click.echo("=" * 60)
        click.echo(f"视图ID: {view_id}")
        
        if isinstance(data, dict):
            # 显示数据统计信息
            if 'metrics' in data:
                metrics = data['metrics']
                click.echo(f"\n指标数据:")
                if isinstance(metrics, list):
                    for metric in metrics:
                        if isinstance(metric, dict):
                            metric_name = metric.get('metricName', '')
                            datapoints = metric.get('datapoints', [])
                            click.echo(f"  {metric_name}: {len(datapoints)} 个数据点")
                            
                            # 显示前几个数据点
                            if datapoints:
                                click.echo(f"    前3个数据点:")
                                for i, dp in enumerate(datapoints[:3]):
                                    timestamp = dp.get('timestamp', '')
                                    value = dp.get('value', '')
                                    click.echo(f"      {timestamp}: {value}")
                                if len(datapoints) > 3:
                                    click.echo(f"      ... (还有 {len(datapoints) - 3} 个数据点)")
                else:
                    click.echo(f"  {metrics}")
            
            # 显示其他数据
            for key, value in data.items():
                if key != 'metrics':
                    click.echo(f"{key}: {value}")
        else:
            click.echo(f"数据: {data}")
        
        click.echo(f"\n{'='*60}")


@monitor.command('query-resource-groups')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--name', help='名称模糊搜索')
@click.option('--res-group-id', help='资源分组ID搜索')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=10, help='每页数量，默认10')
@click.pass_context
@handle_error
def query_resource_groups(ctx, region_id: str, name: Optional[str], res_group_id: Optional[str],
                         page_no: int, page_size: int):
    """
    查询资源分组列表
    
    示例：
        # 查询所有资源分组
        ctyun-cli monitor query-resource-groups \
            --region-id bb9fdb42056f11eda1610242ac110002
            
        # 模糊搜索分组名称
        ctyun-cli monitor query-resource-groups \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --name "test"
            
        # 查询指定分组ID
        ctyun-cli monitor query-resource-groups \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --res-group-id 95f7f0cb-b5d7-547e-8667-3fceeab177d5
            
        # 分页查询
        ctyun-cli monitor query-resource-groups \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --page-no 1 \
            --page-size 5
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_resource_groups(
        region_id=region_id,
        name=name,
        res_group_id=res_group_id,
        page_no=page_no,
        page_size=page_size
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    res_group_list = data.get('resGroupList', [])
    res_group_quota = data.get('resGroupQuota', 0)
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)
    total_page = data.get('totalPage', 0)
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n资源分组列表")
        click.echo("=" * 80)
        click.echo(f"总记录数: {total_count}")
        click.echo(f"当前页记录数: {current_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"资源分组配额剩余: {res_group_quota}")
        
        if res_group_list:
            click.echo(f"\n资源分组详情:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['ID', '名称', '创建方式', '描述', '创建时间', '更新时间']
            
            for group in res_group_list:
                if not isinstance(group, dict):
                    continue
                    
                group_id = group.get('resGroupID', '')[:20] + '...' if len(group.get('resGroupID', '')) > 20 else group.get('resGroupID', '')
                name = group.get('name', '')
                create_type = group.get('createType', '')
                desc = group.get('desc', '')
                create_time = group.get('createTime', 0)
                update_time = group.get('updateTime', 0)
                
                # 格式化时间
                try:
                    from datetime import datetime
                    create_dt = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
                    update_dt = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S') if update_time else '未知'
                except:
                    create_dt = '未知'
                    update_dt = '未知'
                
                table_data.append([
                    group_id,
                    name,
                    create_type,
                    desc[:20] + '...' if len(desc) > 20 else desc,
                    create_dt,
                    update_dt
                ])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
                
                # 显示资源数量统计
                resource_count = sum([len(group.get('resourceList', [])) for group in res_group_list if isinstance(group, dict)])
                click.echo(f"\n资源统计: 共 {len(res_group_list)} 个分组，{resource_count} 个资源")
        else:
            click.echo("\n未找到资源分组")
        
        click.echo(f"\n{'='*80}")


@monitor.command('describe-resource-group')
@click.option('--res-group-id', required=True, help='资源分组ID')
@click.option('--service', help='云监控服务')
@click.option('--dimension', help='云监控维度')
@click.option('--instance', help='对resource.value具体资源进行模糊查询')
@click.pass_context
@handle_error
def describe_resource_group(ctx, res_group_id: str, service: Optional[str], dimension: Optional[str],
                           instance: Optional[str]):
    """
    查询指定资源分组详情
    
    示例：
        # 查询资源分组详情
        ctyun-cli monitor describe-resource-group \
            --res-group-id 95f7f0cb-b5d7-547e-8667-3fceeab177d5
            
        # 查询资源分组详情并过滤服务
        ctyun-cli monitor describe-resource-group \
            --res-group-id 95f7f0cb-b5d7-547e-8667-3fceeab177d5 \
            --service ecs
            
        # 查询资源分组详情并过滤维度
        ctyun-cli monitor describe-resource-group \
            --res-group-id 95f7f0cb-b5d7-547e-8667-3fceeab177d5 \
            --dimension ecs
            
        # 查询资源分组详情并模糊搜索资源
        ctyun-cli monitor describe-resource-group \
            --res-group-id 95f7f0cb-b5d7-547e-8667-3fceeab177d5 \
            --instance 2e8ad126-3f08-11ed-95a4-acde48001122
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.describe_resource_group(
        res_group_id=res_group_id,
        service=service,
        dimension=dimension,
        instance=instance
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        # 特殊错误码处理
        if error_code == 'ResourceGroupNotExist':
            click.echo(f"❌ 资源分组不存在: {res_group_id}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n资源分组详情")
        click.echo("=" * 80)
        click.echo(f"资源分组ID: {data.get('resGroupID', '')}")
        click.echo(f"资源池ID: {data.get('regionID', '')}")
        click.echo(f"名称: {data.get('name', '')}")
        click.echo(f"描述: {data.get('desc', '')}")
        click.echo(f"创建方式: {data.get('createType', '')}")
        
        # 格式化时间
        try:
            from datetime import datetime
            create_time = data.get('createTime', 0)
            update_time = data.get('updateTime', 0)
            create_dt = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
            update_dt = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S') if update_time else '未知'
            click.echo(f"创建时间: {create_dt}")
            click.echo(f"更新时间: {update_dt}")
        except:
            click.echo(f"创建时间: {data.get('createTime', '未知')}")
            click.echo(f"更新时间: {data.get('updateTime', '未知')}")
        
        # 状态信息
        alarm_status_map = {0: '未配置告警规则', 1: '有告警规则但未告警', 2: '告警中'}
        alarm_status = data.get('alarmStatus', 0)
        click.echo(f"告警状态: {alarm_status_map.get(alarm_status, '未知')}")
        click.echo(f"告警资源总数: {data.get('totalAlarm', 0)}")
        click.echo(f"规则数: {data.get('totalRule', 0)}")
        click.echo(f"资源总数: {data.get('totalResource', 0)}")
        click.echo(f"资源类型数: {data.get('totalResourceType', 0)}")
        
        # 资源列表
        resource_list = data.get('resourceList', [])
        if resource_list:
            click.echo(f"\n资源列表:")
            click.echo("-" * 80)
            
            for resource_obj in resource_list:
                if not isinstance(resource_obj, dict):
                    continue
                    
                service_name = resource_obj.get('service', '')
                dimension_name = resource_obj.get('dimension', '')
                resources_total = resource_obj.get('resourcesTotal', 0)
                alarm_num = resource_obj.get('alarmNum', 0)
                
                click.echo(f"\n服务: {service_name}")
                click.echo(f"维度: {dimension_name}")
                click.echo(f"资源总数: {resources_total}")
                click.echo(f"告警中资源数: {alarm_num}")
                
                # 具体资源信息
                resources = resource_obj.get('resources', [])
                if resources:
                    click.echo(f"具体资源信息:")
                    for res in resources:
                        if not isinstance(res, dict):
                            continue
                            
                        status = res.get('status', 0)
                        status_text = '告警' if status == 1 else '正常'
                        click.echo(f"  状态: {status_text}")
                        
                        resource_items = res.get('resource', [])
                        if resource_items:
                            for item in resource_items:
                                if not isinstance(item, dict):
                                    continue

@monitor.command('query-latest-metric-data')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', required=True, help='云监控服务')
@click.option('--dimension', required=True, help='云监控维度')
@click.option('--item-name-list', required=True, multiple=True, help='待查监控项名称，可多次指定')
@click.option('--dimension-name', required=True, help='设备标签键')
@click.option('--dimension-value', required=True, multiple=True, help='设备标签值，可多次指定')
@click.pass_context
@handle_error
def query_latest_metric_data(ctx, region_id: str, service: str, dimension: str,
                           item_name_list: List[str], dimension_name: str, dimension_value: List[str]):
    """
    查询指定设备的实时监控数据
    
    示例：
        # 查询单个云主机的CPU和磁盘使用率
        ctyun-cli monitor query-latest-metric-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --item-name-list cpu_util \
            --item-name-list disk_util \
            --dimension-name uuid \
            --dimension-value 000f0322-1f4d-8cc8-bb2e-1c30fb751aa5
            
        # 查询多个云主机的CPU使用率
        ctyun-cli monitor query-latest-metric-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --item-name-list cpu_util \
            --dimension-name uuid \
            --dimension-value 000f0322-1f4d-8cc8-bb2e-1c30fb751aa5 \
            --dimension-value 00229aa9-ce6b-b46f-4b7d-df61f48a5903
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    # 构造dimensions参数
    dimensions = [{
        'name': dimension_name,
        'value': list(dimension_value)
    }]
    
    # 转换item_name_list为列表
    item_names = list(item_name_list)
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_latest_metric_data(
        region_id=region_id,
        service=service,
        dimension=dimension,
        item_name_list=item_names,
        dimensions=dimensions
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n实时监控数据")
        click.echo("=" * 80)
        
        item_list = data.get('itemList', [])
        if item_list:
            click.echo(f"监控项数据:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['监控项名称', '描述', '单位', '值', '时间戳', '设备标签']
            
            for item in item_list:
                if not isinstance(item, dict):
                    continue
                    
                item_name = item.get('itemName', '')
                item_desc = item.get('itemDesc', '')
                item_unit = item.get('itemUnit', '')
                item_value = item.get('value', '')
                timestamp = item.get('timestamp', 0)
                
                # 格式化时间
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else '未知'
                except:
                    dt = '未知'
                
                # 设备标签
                dimensions = item.get('dimensions', [])
                dim_str = ''
                if dimensions:
                    dim_parts = []
                    for dim in dimensions:
                        if isinstance(dim, dict):
                            name = dim.get('name', '')
                            value = dim.get('value', '')
                            dim_parts.append(f"{name}={value}")
                    dim_str = ', '.join(dim_parts)
                
                # 格式化监控值，保留2位小数
                if isinstance(item_value, (int, float)):
                    formatted_value = f"{item_value:.2f}"
                else:
                    formatted_value = str(item_value)
                
                table_data.append([
                    item_name,
                    item_desc,
                    item_unit,
                    formatted_value,
                    dt,
                    dim_str
                ])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
        else:
            click.echo(f"未找到监控数据")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-history-metric-data')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', required=True, help='云监控服务')
@click.option('--dimension', required=True, help='云监控维度')
@click.option('--item-name-list', required=True, multiple=True, help='待查监控项名称，可多次指定')
@click.option('--start-time', required=True, type=int, help='查询起始Unix时间戳，秒级')
@click.option('--end-time', required=True, type=int, help='查询结束Unix时间戳，秒级')
@click.option('--dimension-name', required=True, help='设备标签键')
@click.option('--dimension-value', required=True, multiple=True, help='设备标签值，可多次指定')
@click.option('--fun', default='avg', help='聚合类型，默认值为avg，取值范围:raw、avg、min、max、variance、sum')
@click.option('--period', type=int, help='聚合周期，单位：秒，默认300，需不小于60，推荐使用60的整倍数。当fun为raw时本参数无效。')
@click.pass_context
@handle_error
def query_history_metric_data(ctx, region_id: str, service: str, dimension: str,
                           item_name_list: List[str], start_time: int, end_time: int,
                           dimension_name: str, dimension_value: List[str],
                           fun: str, period: Optional[int]):
    """
    查询指定时间段内的设备时序指标监控数据
    
    示例：
        # 查询最近1小时的CPU使用率数据
        ctyun-cli monitor query-history-metric-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --item-name-list cpu_util \
            --start-time 1665305264 \
            --end-time 1665391665 \
            --dimension-name uuid \
            --dimension-value 000f0322-1f4d-8cc8-bb2e-1c30fb751aa5
            
        # 查询最近24小时的CPU和磁盘使用率数据，使用最大值聚合
        ctyun-cli monitor query-history-metric-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --item-name-list cpu_util \
            --item-name-list disk_util \
            --start-time 1665305264 \
            --end-time 1665391665 \
            --fun max \
            --period 3600 \
            --dimension-name uuid \
            --dimension-value 000f0322-1f4d-8cc8-bb2e-1c30fb751aa5
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    # 构造dimensions参数
    dimensions = [{
        'name': dimension_name,
        'value': list(dimension_value)
    }]
    
    # 转换item_name_list为列表
    item_names = list(item_name_list)
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_history_metric_data(
        region_id=region_id,
        service=service,
        dimension=dimension,
        item_name_list=item_names,
        start_time=start_time,
        end_time=end_time,
        dimensions=dimensions,
        fun=fun,
        period=period
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n历史监控数据")
        click.echo("=" * 80)
        
        item_list = data.get('itemList', [])
        if item_list:
            click.echo(f"监控项数据:")
            click.echo("-" * 80)
            
            # 按设备分组显示数据
            device_data = {}
            for item in item_list:
                if not isinstance(item, dict):
                    continue
                    
                # 获取设备标签作为分组键
                dimensions = item.get('dimensions', [])
                device_key = 'unknown'
                if dimensions:
                    dim_parts = []
                    for dim in dimensions:
                        if isinstance(dim, dict):
                            name = dim.get('name', '')
                            value = dim.get('value', '')
                            dim_parts.append(f"{name}={value}")
                    device_key = ', '.join(dim_parts)
                
                if device_key not in device_data:
                    device_data[device_key] = []
                device_data[device_key].append(item)
            
            # 显示每个设备的数据
            for device_key, items in device_data.items():
                click.echo(f"\n设备: {device_key}")
                click.echo("-" * 40)
                
                for item in items:
                    item_name = item.get('itemName', '')
                    item_desc = item.get('itemDesc', '')
                    item_unit = item.get('itemUnit', '')
                    
                    click.echo(f"\n{item_desc} ({item_name}) [{item_unit}]:")
                    
                    # 显示数据点
                    item_data = item.get('itemData', [])
                    if item_data:
                        table_data = []
                        headers = ['时间戳', '值']
                        
                        for data_point in item_data:
                            if not isinstance(data_point, dict):
                                continue
                                
                            value = data_point.get('value', '')
                            timestamp = data_point.get('timestamp', 0)
                            
                            # 格式化时间
                            try:
                                from datetime import datetime
                                dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else '未知'
                            except:
                                dt = '未知'
                            
                            table_data.append([dt, str(value)])
                        
                        if table_data:
                            from tabulate import tabulate
                            table = tabulate(table_data, headers=headers, tablefmt='grid')
                            click.echo(f"{table}")
                    else:
                        click.echo("  无数据")
        else:
            click.echo(f"未找到监控数据")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-event-services')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', help='服务')
@click.option('--monitor-type', help='监控类型，如果为event则表示事件类型')
@click.pass_context
@handle_error
def query_event_services(ctx, region_id: str, service: Optional[str], monitor_type: Optional[str]):
    """
    获取资源池下服务维度信息（事件监控）
    
    示例：
        # 查询所有事件服务维度信息
        ctyun-cli monitor query-event-services \
            --region-id bb9fdb42056f11eda1610242ac110002
            
        # 查询指定服务的维度信息
        ctyun-cli monitor query-event-services \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs
            
        # 查询事件类型的服务维度信息
        ctyun-cli monitor query-event-services \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --monitor-type event
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_event_services(
        region_id=region_id,
        service=service,
        monitor_type=monitor_type
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n事件服务维度信息")
        click.echo("=" * 80)
        
        services = data.get('services', [])
        if services:
            click.echo(f"服务列表:")
            click.echo("-" * 80)
            
            for service_obj in services:
                if not isinstance(service_obj, dict):
                    continue
                    
                service_name = service_obj.get('service', '')
                description = service_obj.get('description', '')
                
                click.echo(f"\n服务: {service_name} ({description})")
                
                # 显示维度信息
                dimensions = service_obj.get('dimensions', [])
                if dimensions:
                    click.echo(f"  维度列表:")
                    
                    table_data = []
                    headers = ['维度', '描述']
                    
                    for dim in dimensions:
                        if not isinstance(dim, dict):
                            continue
                        
                        dimension = dim.get('dimension', '')
                        dim_desc = dim.get('description', '')
                        table_data.append([dimension, dim_desc])
                    
                    if table_data:
                        from tabulate import tabulate
                        table = tabulate(table_data, headers=headers, tablefmt='simple')
                        for line in table.split('\n'):
                            click.echo(f"    {line}")
                else:
                    click.echo(f"  维度列表: 无")
            
            click.echo(f"\n总计: {len(services)} 个服务")
        else:
            click.echo(f"未找到服务信息")
        
        click.echo(f"\n{'='*80}")


@monitor.command('count-event-data')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--event-name', required=True, help='事件指标')
@click.option('--service', required=True, help='服务')
@click.option('--dimension', required=True, help='维度')
@click.option('--start-time', required=True, type=int, help='查询起始时间戳')
@click.option('--end-time', required=True, type=int, help='查询截止时间戳')
@click.option('--period', required=True, type=int, help='统计周期（秒）')
@click.option('--res-group-id', help='资源分组ID')
@click.pass_context
@handle_error
def count_event_data(ctx, region_id: str, event_name: str, service: str, dimension: str,
                    start_time: int, end_time: int, period: int, res_group_id: Optional[str]):
    """
    根据指定时间段统计指定事件发生情况
    
    示例：
        # 统计最近1小时的迁移事件
        ctyun-cli monitor count-event-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --event-name migration_event_start \
            --service ecs \
            --dimension ecs \
            --start-time 1647424360 \
            --end-time 1647424660 \
            --period 300
            
        # 统计资源分组的事件
        ctyun-cli monitor count-event-data \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --event-name migration_event_start \
            --service ecs \
            --dimension ecs \
            --start-time 1647424360 \
            --end-time 1647424660 \
            --period 300 \
            --res-group-id 9cb2b330-1dd8-5ec4-9c6d-b07fe65a9aca
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.count_event_data(
        region_id=region_id,
        event_name=event_name,
        service=service,
        dimension=dimension,
        start_time=start_time,
        end_time=end_time,
        period=period,
        res_group_id=res_group_id
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        # 特殊错误码处理
        if error_code == 'DimensionNotSupport':
            click.echo(f"❌ 该维度的事件暂不支持: {dimension}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n事件数据统计")
        click.echo("=" * 80)
        click.echo(f"事件名称: {event_name}")
        click.echo(f"服务: {service}")
        click.echo(f"维度: {dimension}")
        click.echo(f"统计周期: {period}秒")
        
        # 格式化时间
        try:
            from datetime import datetime
            start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            click.echo(f"时间范围: {start_dt} ~ {end_dt}")
        except:
            click.echo(f"时间范围: {start_time} ~ {end_time}")
        
        event_data = data.get('data', [])
        if event_data:
            click.echo(f"\n统计数据:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['采样时间', '事件数量']
            
            total_count = 0
            for item in event_data:
                if not isinstance(item, dict):
                    continue
                    
                sampling_time = item.get('samplingTime', 0)
                value = item.get('value', 0)
                total_count += value
                
                # 格式化时间
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(sampling_time).strftime('%Y-%m-%d %H:%M:%S') if sampling_time else '未知'
                except:
                    dt = '未知'
                
                table_data.append([dt, value])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
                click.echo(f"\n总事件数: {total_count}")
                click.echo(f"数据点数: {len(event_data)}")
        else:
            click.echo(f"\n未找到统计数据")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-event-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', required=True, help='服务')
@click.option('--dimension', required=True, help='维度')
@click.option('--start-time', required=True, type=int, help='查询起始时间戳')
@click.option('--end-time', required=True, type=int, help='查询截止时间戳')
@click.option('--event-name-list', multiple=True, help='事件指标列表，可多次指定')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=20, help='页大小，默认为20')
@click.option('--res-group-id', help='资源分组ID')
@click.pass_context
@handle_error
def query_event_list(ctx, region_id: str, service: str, dimension: str,
                    start_time: int, end_time: int, event_name_list: List[str],
                    page_no: int, page_size: int, res_group_id: Optional[str]):
    """
    根据指定时间段查询事件发生情况
    
    示例：
        # 查询所有事件
        ctyun-cli monitor query-event-list \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --start-time 1647424360 \
            --end-time 1647424660
            
        # 查询指定事件
        ctyun-cli monitor query-event-list \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --start-time 1647424360 \
            --end-time 1647424660 \
            --event-name-list migration_event_start \
            --event-name-list migration_event_complete
            
        # 分页查询
        ctyun-cli monitor query-event-list \
            --region-id bb9fdb42056f11eda1610242ac110002 \
            --service ecs \
            --dimension ecs \
            --start-time 1647424360 \
            --end-time 1647424660 \
            --page-no 1 \
            --page-size 10
    """
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    # 转换event_name_list为列表
    event_names = list(event_name_list) if event_name_list else None
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_event_list(
        region_id=region_id,
        service=service,
        dimension=dimension,
        start_time=start_time,
        end_time=end_time,
        event_name_list=event_names,
        page_no=page_no,
        page_size=page_size,
        res_group_id=res_group_id
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        # 特殊错误码处理
        if error_code == 'DimensionNotSupport':
            click.echo(f"❌ 该维度的事件暂不支持: {dimension}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n事件列表")
        click.echo("=" * 80)
        
        total_count = data.get('totalCount', 0)
        total_page = data.get('totalPage', 0)
        current_count = data.get('currentCount', 0)
        
        click.echo(f"总记录数: {total_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"当前页记录数: {current_count}")
        
        # 格式化时间
        try:
            from datetime import datetime
            start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            click.echo(f"时间范围: {start_dt} ~ {end_dt}")
        except:
            click.echo(f"时间范围: {start_time} ~ {end_time}")
        
        event_list = data.get('eventList', [])
        if event_list:
            click.echo(f"\n事件详情:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['事件名称', '描述', '最后发生时间', '事件数量']
            
            for event in event_list:
                if not isinstance(event, dict):
                    continue
                    
                event_name = event.get('eventName', '')
                description = event.get('description', '')
                event_time = event.get('eventTime', 0)
                event_count = event.get('eventCount', 0)
                
                # 格式化时间
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(event_time).strftime('%Y-%m-%d %H:%M:%S') if event_time else '未知'
                except:
                    dt = '未知'
                
                table_data.append([event_name, description, dt, event_count])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
        else:
            click.echo(f"\n未找到事件")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-event-detail')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--event-name', required=True, help='事件指标名称')
@click.option('--service', required=True, help='服务')
@click.option('--dimension', required=True, help='维度')
@click.option('--start-time', required=True, type=int, help='查询起始时间戳')
@click.option('--end-time', required=True, type=int, help='查询截止时间戳')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=20, help='页大小，默认为20')
@click.option('--res-group-id', help='资源分组ID')
@click.pass_context
@handle_error
def query_event_detail(ctx, region_id: str, event_name: str, service: str, 
                      dimension: str, start_time: int, end_time: int,
                      page_no: int, page_size: int, res_group_id: Optional[str]):
    """查询事件详情"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_event_detail(
        region_id=region_id,
        event_name=event_name,
        service=service,
        dimension=dimension,
        start_time=start_time,
        end_time=end_time,
        page_no=page_no,
        page_size=page_size,
        res_group_id=res_group_id
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        # 特殊错误码处理
        if error_code == 'DimensionNotSupport':
            click.echo(f"❌ 该维度的事件暂不支持: {dimension}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n事件详情")
        click.echo("=" * 80)
        
        total_count = data.get('totalCount', 0)
        total_page = data.get('totalPage', 0)
        current_count = data.get('currentCount', 0)
        
        click.echo(f"总记录数: {total_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"当前页记录数: {current_count}")
        
        # 格式化时间
        try:
            from datetime import datetime
            start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            click.echo(f"时间范围: {start_dt} ~ {end_dt}")
        except:
            click.echo(f"时间范围: {start_time} ~ {end_time}")
        
        click.echo(f"事件名称: {event_name}")
        
        event_details = data.get('eventDetail', [])
        if event_details:
            click.echo(f"\n事件详细列表:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['设备ID', '设备名称', '事件发生时间']
            
            for detail in event_details:
                if not isinstance(detail, dict):
                    continue
                    
                device_uuid = detail.get('deviceUUID', '')
                device_name = detail.get('deviceName', '')
                device_time = detail.get('deviceTime', 0)
                
                # 格式化时间
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(device_time).strftime('%Y-%m-%d %H:%M:%S') if device_time else '未知'
                except:
                    dt = '未知'
                
                table_data.append([device_uuid, device_name, dt])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
        else:
            click.echo(f"\n未找到事件详情")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-events')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', required=True, help='服务')
@click.option('--dimension', required=True, help='维度')
@click.pass_context
@handle_error
def query_events(ctx, region_id: str, service: str, dimension: str):
    """查询事件"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_events(
        region_id=region_id,
        service=service,
        dimension=dimension
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n事件列表")
        click.echo("=" * 80)
        
        events = data.get('events', [])
        if events:
            table_data = []
            headers = ['事件指标', '事件描述']
            
            for event in events:
                if not isinstance(event, dict):
                    continue
                    
                event_name = event.get('eventName', '')
                description = event.get('description', '')
                
                table_data.append([event_name, description])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
                click.echo(f"\n共找到 {len(table_data)} 个事件")
        else:
            click.echo(f"\n未找到事件")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-custom-events')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-event-id', help='自定义事件ID')
@click.option('--name', help='事件名称（支持模糊搜索）')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=20, help='页大小，默认为20')
@click.pass_context
@handle_error
def query_custom_events(ctx, region_id: str, custom_event_id: Optional[str],
                       name: Optional[str], page_no: int, page_size: int):
    """查询自定义事件"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_custom_events(
        region_id=region_id,
        custom_event_id=custom_event_id,
        name=name,
        page_no=page_no,
        page_size=page_size
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n自定义事件列表")
        click.echo("=" * 80)
        
        total_count = data.get('totalCount', 0)
        total_page = data.get('totalPage', 0)
        current_count = data.get('currentCount', 0)
        
        click.echo(f"总记录数: {total_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"当前页记录数: {current_count}")
        click.echo(f"当前页码: {page_no}")
        
        custom_event_list = data.get('customEventList', [])
        if custom_event_list:
            click.echo(f"\n事件详情:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['事件ID', '事件名称', '描述', '创建时间', '修改时间']
            
            for event in custom_event_list:
                if not isinstance(event, dict):
                    continue
                    
                event_id = event.get('customEventID', '')
                event_name = event.get('name', '')
                description = event.get('description', '')
                create_time = event.get('createTime', 0)
                update_time = event.get('updateTime', 0)
                
                # 格式化时间（毫秒时间戳）
                try:
                    from datetime import datetime
                    create_dt = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
                    update_dt = datetime.fromtimestamp(update_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if update_time else '未知'
                except:
                    create_dt = str(create_time)
                    update_dt = str(update_time)
                
                table_data.append([event_id, event_name, description, create_dt, update_dt])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
        else:
            click.echo(f"\n未找到自定义事件")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-custom-event-data')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-event-id', multiple=True, help='自定义事件ID，可多次指定')
@click.option('--start-time', type=int, help='查询起始时间戳（秒），默认7天前')
@click.option('--end-time', type=int, help='查询截止时间戳（秒），默认当前时间')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=20, help='页大小，默认为20')
@click.pass_context
@handle_error
def query_custom_event_data(ctx, region_id: str, custom_event_id: tuple,
                           start_time: Optional[int], end_time: Optional[int],
                           page_no: int, page_size: int):
    """查询自定义事件监控详情"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    # 转换custom_event_id为列表
    event_id_list = list(custom_event_id) if custom_event_id else None
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_custom_event_data(
        region_id=region_id,
        custom_event_id_list=event_id_list,
        start_time=start_time,
        end_time=end_time,
        page_no=page_no,
        page_size=page_size
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n自定义事件监控详情")
        click.echo("=" * 80)
        
        total_count = data.get('totalCount', 0)
        total_page = data.get('totalPage', 0)
        current_count = data.get('currentCount', 0)
        
        click.echo(f"总记录数: {total_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"当前页记录数: {current_count}")
        click.echo(f"当前页码: {page_no}")
        
        # 格式化时间范围
        if start_time and end_time:
            try:
                from datetime import datetime
                start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                click.echo(f"时间范围: {start_dt} ~ {end_dt}")
            except:
                click.echo(f"时间范围: {start_time} ~ {end_time}")
        
        monitor_list = data.get('customEventMonitorList', [])
        if monitor_list:
            click.echo(f"\n事件监控详情:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['事件ID', '事件名称', '详情信息', '发生时间']
            
            for monitor in monitor_list:
                if not isinstance(monitor, dict):
                    continue
                    
                event_id = monitor.get('customEventID', '')
                event_name = monitor.get('name', '')
                info = monitor.get('info', '')
                clock = monitor.get('clock', 0)
                
                # 格式化时间（毫秒时间戳）
                try:
                    from datetime import datetime
                    clock_dt = datetime.fromtimestamp(clock / 1000).strftime('%Y-%m-%d %H:%M:%S') if clock else '未知'
                except:
                    clock_dt = str(clock)
                
                table_data.append([event_id, event_name, info, clock_dt])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
        else:
            click.echo(f"\n未找到事件监控详情")
        
        click.echo(f"\n{'='*80}")


@monitor.command('describe-custom-event-alarm-rule')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--alarm-rule-id', required=True, help='告警规则ID')
@click.pass_context
@handle_error
def describe_custom_event_alarm_rule(ctx, region_id: str, alarm_rule_id: str):
    """查看自定义事件告警规则详情"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.describe_custom_event_alarm_rule(
        region_id=region_id,
        alarm_rule_id=alarm_rule_id
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        # 特殊错误码处理
        if error_code == 'RuleNotFound':
            click.echo(f"❌ 告警规则不存在: {alarm_rule_id}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n自定义事件告警规则详情")
        click.echo("=" * 80)
        
        # 基本信息
        click.echo(f"告警规则ID: {data.get('alarmRuleID', '')}")
        click.echo(f"资源池ID: {data.get('regionID', '')}")
        click.echo(f"规则名称: {data.get('name', '')}")
        click.echo(f"描述: {data.get('desc', '')}")
        click.echo(f"自定义事件ID: {data.get('customEventID', '')}")
        
        # 告警条件
        click.echo(f"\n告警条件:")
        click.echo("-" * 80)
        click.echo(f"  出现次数阈值: {data.get('value', '')}")
        click.echo(f"  统计周期: {data.get('period', '')}")
        
        # 状态信息
        status = data.get('status', 0)
        status_text = '启用' if status == 0 else '停用'
        alarm_status = data.get('alarmStatus', 0)
        alarm_status_text = '正常' if alarm_status == 0 else '正在告警'
        click.echo(f"\n状态信息:")
        click.echo("-" * 80)
        click.echo(f"  规则状态: {status_text}")
        click.echo(f"  告警状态: {alarm_status_text}")
        
        # 通知设置
        click.echo(f"\n通知设置:")
        click.echo("-" * 80)
        notify_type = data.get('notifyType', [])
        click.echo(f"  通知方式: {', '.join(notify_type) if notify_type else '未设置'}")
        click.echo(f"  重复通知次数: {data.get('repeatTimes', 0)}")
        click.echo(f"  静默时间: {data.get('silenceTime', 0)} 秒")
        
        recover_notify = data.get('recoverNotify', 0)
        recover_text = '是' if recover_notify == 1 else '否'
        click.echo(f"  恢复通知: {recover_text}")
        
        # 通知时段
        weekdays_map = {0: '周日', 1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六'}
        notify_weekdays = data.get('notifyWeekdays', [])
        weekdays_text = ', '.join([weekdays_map.get(d, str(d)) for d in notify_weekdays])
        click.echo(f"  通知周期: {weekdays_text}")
        click.echo(f"  通知时段: {data.get('notifyStart', '')} ~ {data.get('notifyEnd', '')}")
        
        # 联系人组
        contact_groups = data.get('contactGroupList', [])
        if contact_groups:
            click.echo(f"\n告警联系人组: {len(contact_groups)} 个")
            for group_id in contact_groups:
                click.echo(f"  - {group_id}")
        else:
            click.echo(f"\n告警联系人组: 未设置")
        
        # Webhook
        webhook_urls = data.get('webhookUrl', [])
        if webhook_urls:
            click.echo(f"\nWebhook URL: {len(webhook_urls)} 个")
            for url in webhook_urls:
                click.echo(f"  - {url}")
        
        # 时间信息
        create_time = data.get('createTime', 0)
        update_time = data.get('updateTime', 0)
        try:
            from datetime import datetime
            create_dt = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
            update_dt = datetime.fromtimestamp(update_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if update_time else '未知'
        except:
            create_dt = str(create_time)
            update_dt = str(update_time)
        
        click.echo(f"\n创建时间: {create_dt}")
        click.echo(f"更新时间: {update_dt}")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-alert-history')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--status', required=True, type=int, help='状态（0：正在告警，1：告警历史）')
@click.option('--resource-group-id', help='资源分组ID')
@click.option('--search-key', type=click.Choice(['alarmRuleID', 'name']), help='搜索关键词')
@click.option('--search-value', help='搜索值')
@click.option('--service', multiple=True, help='告警服务，可多次指定')
@click.option('--start-time', type=int, help='起始时间戳（秒），status=1时使用')
@click.option('--end-time', type=int, help='结束时间戳（秒），status=1时使用')
@click.option('--page-no', type=int, default=1, help='页码，默认为1')
@click.option('--page-size', type=int, default=10, help='页大小，默认为10')
@click.pass_context
@handle_error
def query_alert_history(ctx, region_id: str, status: int,
                       resource_group_id: Optional[str], search_key: Optional[str],
                       search_value: Optional[str], service: tuple,
                       start_time: Optional[int], end_time: Optional[int],
                       page_no: int, page_size: int):
    """查询告警历史"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    # 转换service为列表
    service_list = list(service) if service else None
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_alert_history(
        region_id=region_id,
        status=status,
        resource_group_id=resource_group_id,
        search_key=search_key,
        search_value=search_value,
        service=service_list,
        start_time=start_time,
        end_time=end_time,
        page_no=page_no,
        page_size=page_size
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n告警历史")
        click.echo("=" * 80)
        
        total_count = data.get('totalCount', 0)
        total_page = data.get('totalPage', 0)
        current_count = data.get('currentCount', 0)
        page = data.get('page', page_no)
        
        click.echo(f"总记录数: {total_count}")
        click.echo(f"总页数: {total_page}")
        click.echo(f"当前页记录数: {current_count}")
        click.echo(f"当前页码: {page}")
        
        status_text = '正在告警' if status == 0 else '告警历史'
        click.echo(f"查询状态: {status_text}")
        
        # 格式化时间范围
        if start_time and end_time:
            try:
                from datetime import datetime
                start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                click.echo(f"时间范围: {start_dt} ~ {end_dt}")
            except:
                click.echo(f"时间范围: {start_time} ~ {end_time}")
        
        issues = data.get('issues', [])
        if issues:
            click.echo(f"\n告警事件列表:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['告警ID', '规则名称', '服务/维度', '类型', '状态', '持续时间', '触发时间']
            
            for issue in issues:
                if not isinstance(issue, dict):
                    continue
                    
                issue_id = issue.get('issueID', '')
                rule_name = issue.get('name', '')
                service_name = issue.get('service', '')
                dimension = issue.get('dimension', '')
                alarm_type = issue.get('alarmType', '')
                issue_status = issue.get('status', 0)
                duration = issue.get('duration', 0)
                create_time = issue.get('createTime', 0)
                
                # 状态文本
                if issue_status == 0:
                    data_status = issue.get('dataStatus', 0)
                    status_str = '正在告警(有数据)' if data_status == 0 else '正在告警(无数据)'
                else:
                    expired_status = issue.get('expiredStatus', 0)
                    status_str = '告警历史' if expired_status == 0 else '已失效'
                
                # 类型文本
                type_str = '指标' if alarm_type == 'series' else '事件'
                
                # 持续时间格式化
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours}h{minutes}m{seconds}s" if hours > 0 else f"{minutes}m{seconds}s"
                
                # 格式化触发时间
                try:
                    from datetime import datetime
                    create_dt = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
                except:
                    create_dt = str(create_time)
                
                service_dim = f"{service_name}/{dimension}"
                
                table_data.append([
                    issue_id[:16] + '...' if len(issue_id) > 16 else issue_id,
                    rule_name[:20] if len(rule_name) <= 20 else rule_name[:17] + '...',
                    service_dim[:20] if len(service_dim) <= 20 else service_dim[:17] + '...',
                    type_str,
                    status_str,
                    duration_str,
                    create_dt
                ])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
                
                # 显示详细信息（第一条）
                if issues:
                    click.echo(f"\n第一条告警详情:")
                    click.echo("-" * 80)
                    first = issues[0]
                    click.echo(f"  告警历史ID: {first.get('issueID', '')}")
                    click.echo(f"  告警规则ID: {first.get('alarmRuleID', '')}")
                    click.echo(f"  通知方式: {', '.join(first.get('notifyType', []))}")
                    
                    contact_groups = first.get('contactGroupList', [])
                    if contact_groups:
                        click.echo(f"  联系人组:")
                        for group in contact_groups:
                            if isinstance(group, dict):
                                click.echo(f"    - {group.get('name', '')} ({group.get('contactGroupID', '')})")
                    
                    resources = first.get('resources', [])
                    if resources:
                        click.echo(f"  告警资源:")
                        for res_group in resources[:3]:  # 只显示前3个
                            if isinstance(res_group, dict):
                                resource_list = res_group.get('resource', [])
                                for res in resource_list:
                                    if isinstance(res, dict):
                                        click.echo(f"    - {res.get('name', '')}: {res.get('value', '')}")
        else:
            click.echo(f"\n未找到告警事件")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-alert-history-info')
@click.option('--issue-id', required=True, help='告警历史ID')
@click.pass_context
@handle_error
def query_alert_history_info(ctx, issue_id: str):
    """查询告警历史详情"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_alert_history_info(issue_id=issue_id)
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', [])
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n告警历史详情")
        click.echo("=" * 80)
        click.echo(f"告警历史ID: {issue_id}")
        
        if not data or not isinstance(data, list):
            click.echo("\n未找到告警详情")
            click.echo(f"\n{'='*80}")
            return
        
        click.echo(f"\n共 {len(data)} 条详情记录")
        
        for idx, info in enumerate(data, 1):
            if not isinstance(info, dict):
                continue
            
            click.echo(f"\n详情记录 #{idx}")
            click.echo("-" * 80)
            
            # 基本信息
            info_id = info.get('infoID', '')
            status = info.get('status', 0)
            alarm_type = info.get('alarmType', '')
            service = info.get('service', '')
            dimension = info.get('dimension', '')
            
            status_text = '正在告警' if status == 0 else '告警历史'
            type_text = '指标' if alarm_type == 'series' else '事件'
            
            click.echo(f"详情ID: {info_id}")
            click.echo(f"服务: {service}")
            click.echo(f"维度: {dimension}")
            click.echo(f"告警类型: {type_text}")
            click.echo(f"状态: {status_text}")
            
            # 告警资源
            resources = info.get('resource', [])
            if resources:
                click.echo(f"\n告警资源:")
                for res in resources:
                    if isinstance(res, dict):
                        res_name = res.get('name', '')
                        res_value = res.get('value', '')
                        click.echo(f"  - {res_name}: {res_value}")
            
            # 告警条件
            condition = info.get('condition', {})
            if condition:
                click.echo(f"\n告警条件:")
                metric = condition.get('metric', '')
                metric_cn = condition.get('metricCnName', '')
                fun = condition.get('fun', '')
                operator = condition.get('operator', '')
                threshold = condition.get('threshold', '')
                unit = condition.get('unit', '')
                period = condition.get('period', '')
                
                # 算法文本
                fun_map = {'last': '原始值', 'avg': '平均值', 'max': '最大值', 'min': '最小值'}
                fun_text = fun_map.get(fun, fun)
                
                # 比较符文本
                op_map = {'eq': '等于', 'gt': '大于', 'ge': '大于等于', 'lt': '小于', 'le': '小于等于'}
                op_text = op_map.get(operator, operator)
                
                click.echo(f"  指标: {metric_cn} ({metric})")
                click.echo(f"  算法: {fun_text}")
                if period:
                    click.echo(f"  统计周期: {period}")
                click.echo(f"  条件: {op_text} {threshold}{unit}")
            
            # 告警数据
            count = info.get('count', 0)
            value = info.get('value', 0)
            click.echo(f"\n告警数据:")
            click.echo(f"  出现次数: {count}")
            click.echo(f"  告警值: {value}")
            
            # 时间信息
            create_time = info.get('createTime', 0)
            update_time = info.get('updateTime', 0)
            try:
                from datetime import datetime
                create_dt = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S') if create_time else '未知'
                update_dt = datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S') if update_time else '未知'
            except:
                create_dt = str(create_time)
                update_dt = str(update_time)
            
            click.echo(f"\n时间信息:")
            click.echo(f"  触发时间: {create_dt}")
            click.echo(f"  结束时间: {update_dt}")
            
            if update_time and create_time:
                duration = update_time - create_time
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours}h{minutes}m{seconds}s" if hours > 0 else f"{minutes}m{seconds}s"
                click.echo(f"  持续时间: {duration_str}")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-alarm-top-dimension')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--range', type=click.Choice(['7d', '24h', '6h']), default='7d', help='时间范围，默认7d')
@click.pass_context
@handle_error
def query_alarm_top_dimension(ctx, region_id: str, range: str):
    """查询告警Top产品"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_alarm_top_dimension(
        region_id=region_id,
        time_range=range
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        # 特殊错误码处理
        if error_code == 'ParamValueOutOfRange':
            click.echo(f"❌ 参数取值超出范围: {range}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n告警Top产品")
        click.echo("=" * 80)
        click.echo(f"时间范围: {range}")
        
        items = data.get('items', [])
        if items:
            click.echo(f"\n产品告警排名:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['排名', '服务', '服务描述', '维度', '维度描述', '告警次数']
            
            for idx, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    continue
                    
                service = item.get('service', '')
                service_desc = item.get('serviceDesc', '')
                dimension = item.get('dimension', '')
                dimension_desc = item.get('dimensionDesc', '')
                count = item.get('count', 0)
                
                table_data.append([idx, service, service_desc, dimension, dimension_desc, count])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
                
                total_count = sum([item.get('count', 0) for item in items if isinstance(item, dict)])
                click.echo(f"\n总告警次数: {total_count}")
                click.echo(f"产品数量: {len(items)}")
        else:
            click.echo(f"\n未找到告警产品")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-alarm-top-resource')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--range', type=click.Choice(['7d', '24h', '6h']), default='7d', help='时间范围，默认7d')
@click.pass_context
@handle_error
def query_alarm_top_resource(ctx, region_id: str, range: str):
    """查询告警Top实例"""
    client = ctx.obj['client']
    output_format = ctx.obj.get('output', 'table')
    
    monitor_client = MonitorClient(client)
    result = monitor_client.query_alarm_top_resource(
        region_id=region_id,
        time_range=range
    )
    
    if not result.get('success'):
        error_code = result.get('error', '')
        error_msg = result.get('message', '未知错误')
        if error_code == 'ParamValueOutOfRange':
            click.echo(f"❌ 参数取值超出范围: {range}", err=True)
        else:
            click.echo(f"❌ 查询失败 [{error_code}]: {error_msg}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', [])
    
    if output_format in ['json', 'yaml']:
        if output_format == 'json':
            click.echo(OutputFormatter.format_json(data))
        else:
            try:
                import yaml
                click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
            except ImportError:
                click.echo("错误: 需要安装PyYAML库", err=True)
                import sys
                sys.exit(1)
    else:
        click.echo(f"\n告警Top实例")
        click.echo("=" * 80)
        click.echo(f"时间范围: {range}")
        
        if data and isinstance(data, list):
            click.echo(f"\n实例告警排名:")
            click.echo("-" * 80)
            
            table_data = []
            headers = ['排名', '服务/维度', '实例信息', '告警次数']
            
            for idx, item in enumerate(data, 1):
                if not isinstance(item, dict):
                    continue
                    
                service = item.get('service', '')
                dimension = item.get('dimension', '')
                service_desc = item.get('serviceDesc', '')
                dimension_desc = item.get('dimensionDesc', '')
                count = item.get('count', 0)
                
                # 组合服务/维度描述
                service_dim = f"{service_desc}/{dimension_desc}" if service_desc and dimension_desc else f"{service}/{dimension}"
                
                # 提取实例信息
                resources = item.get('resource', [])
                instance_info = []
                for res in resources:
                    if isinstance(res, dict):
                        name = res.get('name', '')
                        value = res.get('value', '')
                        if name and value:
                            instance_info.append(f"{name}={value}")
                
                instance_str = '\n'.join(instance_info[:3])  # 最多显示3个属性
                
                table_data.append([idx, service_dim, instance_str, count])
            
            if table_data:
                from tabulate import tabulate
                table = tabulate(table_data, headers=headers, tablefmt='grid')
                click.echo(f"\n{table}")
                
                total_count = sum([item.get('count', 0) for item in data if isinstance(item, dict)])
                click.echo(f"\n总告警次数: {total_count}")
                click.echo(f"实例数量: {len(data)}")
        else:
            click.echo(f"\n未找到告警实例")
        
        click.echo(f"\n{'='*80}")


@monitor.command('query-alarm-top-metric')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--range', type=click.Choice(['7d', '24h', '6h']), default='7d', help='时间范围')
@click.pass_context
@handle_error
def query_alarm_top_metric(ctx, region_id: str, range: str):
    """查询告警Top指标"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_alarm_top_metric(region_id, range)
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys; sys.exit(1)
    data = result.get('data', [])
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif not data:
        click.echo("未找到告警指标")
    else:
        from tabulate import tabulate
        click.echo(f"\n告警Top指标 (时间范围: {range})\n" + "="*80)
        table_data = [[idx, f"{i.get('serviceDesc')}/{i.get('dimensionDesc')}", i.get('metricDesc'), i.get('count')] 
                      for idx, i in enumerate(data, 1) if isinstance(i, dict)]
        click.echo(f"\n{tabulate(table_data, headers=['排名','服务/维度','指标','告警次数'], tablefmt='grid')}\n" + "="*80)


@monitor.command('query-alarm-top-event')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--range', type=click.Choice(['7d', '24h', '6h']), default='7d', help='时间范围')
@click.pass_context
@handle_error
def query_alarm_top_event(ctx, region_id: str, range: str):
    """查询告警Top事件"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_alarm_top_event(region_id, range)
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys; sys.exit(1)
    data = result.get('data', [])
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif not data:
        click.echo("未找到告警事件")
    else:
        from tabulate import tabulate
        click.echo(f"\n告警Top事件 (时间范围: {range})\n" + "="*80)
        table_data = [[idx, f"{i.get('serviceDesc')}/{i.get('dimensionDesc')}", i.get('eventDesc'), i.get('count')] 
                      for idx, i in enumerate(data, 1) if isinstance(i, dict)]
        click.echo(f"\n{tabulate(table_data, headers=['排名','服务/维度','事件','告警次数'], tablefmt='grid')}\n" + "="*80)


@monitor.command('query-alarm-rules')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--service', required=True, help='服务')
@click.option('--alarm-status', type=int, help='告警状态(0:未触发,1:触发,2:无数据)')
@click.option('--status', type=int, help='规则状态(0:启用,1:停用)')
@click.option('--name', help='规则名称(模糊查询)')
@click.option('--contact-group-name', help='联系组名(模糊查询)')
@click.option('--instance-name', help='监控对象名(模糊查询)')
@click.option('--sort-key', help='排序字段')
@click.option('--sort-type', type=click.Choice(['ASC', 'DESC']), help='排序类型')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.option('--res-group-id', help='资源分组ID')
@click.pass_context
@handle_error
def query_alarm_rules(ctx, region_id, service, alarm_status, status, name, contact_group_name, 
                     instance_name, sort_key, sort_type, page_no, page_size, res_group_id):
    """查询告警规则列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_alarm_rules(region_id, service, alarm_status, status, name,
                                                      contact_group_name, instance_name, sort_key,
                                                      sort_type, page_no, page_size, res_group_id)
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys; sys.exit(1)
    
    data = result.get('data', {})
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n告警规则列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('page', 0)}")
        
        rules = data.get('alarmRules', [])
        if rules:
            table_data = []
            for rule in rules:
                status_map = {0: '启用', 1: '停用'}
                alarm_status_map = {0: '未触发', 1: '触发', 2: '无数据'}
                table_data.append([
                    rule.get('name', '')[:30],
                    f"{rule.get('service')}/{rule.get('dimension')}",
                    status_map.get(rule.get('status', 0), '未知'),
                    alarm_status_map.get(rule.get('alarmStatus', 0), '未知'),
                    len(rule.get('contactGroupList', []))
                ])
            click.echo(f"\n{tabulate(table_data, headers=['规则名称','服务/维度','状态','告警状态','联系组'], tablefmt='grid')}")
        else:
            click.echo("\n未找到告警规则")
        click.echo("\n" + "="*80)


@monitor.command('describe-alarm-rule')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--alarm-rule-id', required=True, help='告警规则ID')
@click.pass_context
@handle_error
def describe_alarm_rule(ctx, region_id, alarm_rule_id):
    """查询告警规则详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).describe_alarm_rule(region_id, alarm_rule_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    alarm_rule = data.get('alarmRule', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(alarm_rule))
    else:
        from tabulate import tabulate
        click.echo(f"\n告警规则详情\n" + "="*80)
        
        status_map = {0: '启用', 1: '停用'}
        alarm_status_map = {0: '未触发', 1: '触发', 2: '无数据'}
        alarm_type_map = {'series': '时序类监控', 'event': '事件类'}
        condition_type_map = {0: '或（任一条件触发）', 1: '且（全部条件满足触发）'}
        
        click.echo(f"  规则ID: {alarm_rule.get('alarmRuleID', '')}")
        click.echo(f"  规则名称: {alarm_rule.get('name', '')}")
        click.echo(f"  描述: {alarm_rule.get('desc', '')}")
        click.echo(f"  服务/维度: {alarm_rule.get('service')}/{alarm_rule.get('dimension')}")
        click.echo(f"  规则状态: {status_map.get(alarm_rule.get('status', 0), '未知')}")
        click.echo(f"  告警状态: {alarm_status_map.get(alarm_rule.get('alarmStatus', 0), '未知')}")
        click.echo(f"  告警类型: {alarm_type_map.get(alarm_rule.get('alarmType', ''), '未知')}")
        click.echo(f"  条件类型: {condition_type_map.get(alarm_rule.get('conditionType', 0), '未知')}")
        click.echo(f"  静默时间: {alarm_rule.get('silenceTime', 0)}秒")
        click.echo(f"  重复通知: {alarm_rule.get('repeatTimes', 0)}次")
        click.echo(f"  恢复通知: {'是' if alarm_rule.get('recoverNotify') == 1 else '否'}")
        
        notify_types = alarm_rule.get('notifyType', [])
        click.echo(f"  通知方式: {', '.join(notify_types) if notify_types else '无'}")
        
        weekday_map = {0: '周日', 1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六'}
        notify_weekdays = alarm_rule.get('notifyWeekdays', [])
        weekday_strs = [weekday_map.get(d, str(d)) for d in notify_weekdays]
        click.echo(f"  通知周期: {', '.join(weekday_strs)}")
        click.echo(f"  通知时段: {alarm_rule.get('notifyStart', '')} - {alarm_rule.get('notifyEnd', '')}")
        
        contact_groups = alarm_rule.get('contactGroupList', [])
        if contact_groups:
            click.echo(f"\n  联系组({len(contact_groups)}个):")
            for group in contact_groups:
                click.echo(f"    - {group.get('name', '')} ({group.get('groupID', '')})")
        
        conditions = alarm_rule.get('condition', [])
        if conditions:
            click.echo(f"\n  告警条件({len(conditions)}个):")
            for idx, cond in enumerate(conditions, 1):
                fun_map = {'last': '原始值', 'avg': '平均值', 'max': '最大值', 'min': '最小值'}
                operator_map = {
                    'eq': '等于', 'gt': '大于', 'ge': '大于等于', 
                    'lt': '小于', 'le': '小于等于', 
                    'rg': '环比上升', 'cf': '环比下降', 'rc': '环比变化'
                }
                click.echo(f"    {idx}. {cond.get('metricCnName', cond.get('metric', ''))}")
                click.echo(f"       算法: {fun_map.get(cond.get('fun', ''), cond.get('fun', ''))} | " +
                          f"周期: {cond.get('period', 'N/A')}")
                click.echo(f"       条件: {operator_map.get(cond.get('operator', ''), cond.get('operator', ''))} " +
                          f"{cond.get('value', '')} {cond.get('unit', '')}")
                click.echo(f"       持续: {cond.get('evaluationCount', 0)}次")
        
        resources = alarm_rule.get('resources', [])
        if resources:
            click.echo(f"\n  监控资源({len(resources)}个):")
            for idx, res in enumerate(resources, 1):
                res_info = res.get('resource', [])
                res_dict = {r.get('name'): r.get('value') for r in res_info}
                instance_name = res_dict.get('instancename', res_dict.get('uuid', ''))
                click.echo(f"    {idx}. {instance_name}")
        
        webhooks = alarm_rule.get('webhookUrl', [])
        if webhooks:
            click.echo(f"\n  Webhook URL({len(webhooks)}个):")
            for url in webhooks:
                click.echo(f"    - {url}")
        
        from datetime import datetime
        create_time = alarm_rule.get('createTime', 0)
        update_time = alarm_rule.get('updateTime', 0)
        if create_time:
            click.echo(f"\n  创建时间: {datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')}")
        if update_time:
            click.echo(f"  更新时间: {datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-contacts')
@click.option('--name', help='联系人姓名')
@click.option('--email', help='邮箱')
@click.option('--phone', help='手机号')
@click.option('--search', help='模糊搜索（姓名/手机/邮箱）')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_contacts(ctx, name, email, phone, search, page_no, page_size):
    """查询告警联系人列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_contacts(name, email, phone, search, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n告警联系人列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        contacts = data.get('contactList', [])
        if contacts:
            table_data = []
            for contact in contacts:
                phone_status = '✓' if contact.get('phoneActivation') == 1 else '✗'
                email_status = '✓' if contact.get('emailActivation') == 1 else '✗'
                groups = contact.get('contactGroupList', [])
                group_names = ', '.join([g.get('name', '') for g in groups[:2]])
                if len(groups) > 2:
                    group_names += f'...(+{len(groups)-2})'
                
                table_data.append([
                    contact.get('name', ''),
                    contact.get('phone', ''),
                    phone_status,
                    contact.get('email', ''),
                    email_status,
                    group_names or '无'
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['姓名','手机号','激活','邮箱','激活','所属组'], tablefmt='grid')}")
        else:
            click.echo("\n未找到联系人")
        
        click.echo("\n" + "="*80)


@monitor.command('query-contact-groups')
@click.option('--name', help='联系人组名称')
@click.option('--search', help='模糊搜索（组名/联系人姓名/手机/邮箱）')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_contact_groups(ctx, name, search, page_no, page_size):
    """查询告警联系人组列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_contact_groups(name, search, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n告警联系人组列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        groups = data.get('contactGroupList', [])
        if groups:
            table_data = []
            for group in groups:
                contacts = group.get('contactList', [])
                contact_names = ', '.join([c.get('name', '') for c in contacts[:3]])
                if len(contacts) > 3:
                    contact_names += f'...(+{len(contacts)-3})'
                
                table_data.append([
                    group.get('name', ''),
                    group.get('desc', '')[:30] if group.get('desc') else '',
                    len(contacts),
                    contact_names or '无'
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['组名','描述','成员数','成员'], tablefmt='grid')}")
            
            if data.get('currentCount', 0) > 0:
                first_group = groups[0]
                click.echo(f"\n第一个联系组详情:")
                click.echo(f"  组ID: {first_group.get('contactGroupID', '')}")
                click.echo(f"  组名: {first_group.get('name', '')}")
                click.echo(f"  描述: {first_group.get('desc', '')}")
                
                contacts = first_group.get('contactList', [])
                if contacts:
                    click.echo(f"  成员列表({len(contacts)}人):")
                    for contact in contacts:
                        phone_status = '✓' if contact.get('phoneActivation') == 1 else '✗'
                        email_status = '✓' if contact.get('emailActivation') == 1 else '✗'
                        click.echo(f"    - {contact.get('name', '')}: {contact.get('phone', '')}({phone_status}) | {contact.get('email', '')}({email_status})")
        else:
            click.echo("\n未找到联系人组")
        
        click.echo("\n" + "="*80)


@monitor.command('query-custom-trend')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-item-id', required=True, help='自定义监控项ID')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--period', type=int, default=300, help='聚合周期(秒)，默认300')
@click.option('--dimensions', help='维度JSON，格式: [{"name":"uuid","value":["val1"]}]')
@click.pass_context
@handle_error
def query_custom_trend(ctx, region_id, custom_item_id, start_time, end_time, period, dimensions):
    """查询自定义监控趋势数据"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    
    dims = None
    if dimensions:
        import json
        dims = json.loads(dimensions)
    
    result = MonitorClient(client).query_custom_item_trendmetricdata(
        region_id, custom_item_id, start_time, end_time, period, dims
    )
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    results = data.get('result', [])
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        from datetime import datetime
        
        click.echo(f"\n自定义监控趋势数据\n" + "="*80)
        click.echo(f"监控项ID: {custom_item_id}")
        click.echo(f"数据记录组数: {len(results)}")
        
        for idx, res in enumerate(results, 1):
            click.echo(f"\n数据组 {idx}:")
            dims_info = res.get('dimensions', [])
            if dims_info:
                dim_str = ', '.join([f"{d.get('name')}={d.get('value')}" for d in dims_info if d.get('value')])
                click.echo(f"  维度: {dim_str}")
            
            data_points = res.get('data', [])
            if data_points:
                table_data = []
                for dp in data_points:
                    ts = datetime.fromtimestamp(dp.get('samplingTime', 0)).strftime('%Y-%m-%d %H:%M:%S')
                    table_data.append([
                        ts,
                        f"{dp.get('avg', 0):.4f}",
                        f"{dp.get('max', 0):.4f}",
                        f"{dp.get('min', 0):.4f}",
                        f"{dp.get('variance', 0):.4f}"
                    ])
                click.echo(f"\n{tabulate(table_data, headers=['时间','平均值','最大值','最小值','方差'], tablefmt='grid')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-custom-history')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-item-id', required=True, help='自定义监控项ID')
@click.option('--start-time', required=True, type=int, help='开始时间戳(秒)')
@click.option('--end-time', required=True, type=int, help='结束时间戳(秒)')
@click.option('--dimensions', help='维度JSON，格式: [{"name":"uuid","value":["val1"]}]')
@click.pass_context
@handle_error
def query_custom_history(ctx, region_id, custom_item_id, start_time, end_time, dimensions):
    """查询自定义监控历史数据"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    
    dims = None
    if dimensions:
        import json
        dims = json.loads(dimensions)
    
    result = MonitorClient(client).query_custom_item_historymetricdata(
        region_id, custom_item_id, start_time, end_time, dims
    )
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    results = data.get('result', [])
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        from datetime import datetime
        
        click.echo(f"\n自定义监控历史数据\n" + "="*80)
        click.echo(f"监控项ID: {custom_item_id}")
        click.echo(f"数据记录组数: {len(results)}")
        
        for idx, res in enumerate(results, 1):
            click.echo(f"\n数据组 {idx}:")
            dims_info = res.get('dimensions', [])
            if dims_info:
                dim_str = ', '.join([f"{d.get('name')}={d.get('value')}" for d in dims_info if d.get('value')])
                click.echo(f"  维度: {dim_str}")
            
            data_points = res.get('data', [])
            if data_points:
                table_data = []
                for dp in data_points:
                    ts = datetime.fromtimestamp(dp.get('samplingTime', 0)).strftime('%Y-%m-%d %H:%M:%S')
                    table_data.append([ts, dp.get('value', '')])
                click.echo(f"\n{tabulate(table_data, headers=['时间','值'], tablefmt='grid')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-custom-dimension-values')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-item-id', required=True, help='自定义监控项ID')
@click.option('--dimension-name', required=True, help='维度名称')
@click.option('--filter', help='过滤条件JSON，格式: [{"name":"uuid","value":["val1"]}]')
@click.pass_context
@handle_error
def query_custom_dimension_values(ctx, region_id, custom_item_id, dimension_name, filter):
    """查询自定义监控项维度值"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    
    filter_dims = None
    if filter:
        import json
        filter_dims = json.loads(filter)
    
    result = MonitorClient(client).query_custom_item_dimension_values(
        region_id, custom_item_id, dimension_name, filter_dims
    )
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    values = data.get('dimensionValueList', [])
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        click.echo(f"\n维度值列表\n" + "="*80)
        click.echo(f"维度名称: {dimension_name}")
        click.echo(f"值数量: {len(values)}")
        
        if values:
            click.echo(f"\n维度值:")
            for idx, val in enumerate(values, 1):
                click.echo(f"  {idx}. {val}")
        else:
            click.echo("\n未找到维度值")
        
        click.echo("\n" + "="*80)


@monitor.command('query-custom-items')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--custom-item-id', help='自定义监控项ID')
@click.option('--name', help='监控项名称（模糊搜索）')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=10, help='页大小')
@click.pass_context
@handle_error
def query_custom_items(ctx, region_id, custom_item_id, name, page_no, page_size):
    """查询自定义监控项列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_custom_items(region_id, custom_item_id, name, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n自定义监控项列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        items = data.get('customItemList', [])
        if items:
            table_data = []
            for item in items:
                dims = item.get('dimensions', [])
                dim_names = ', '.join([d.get('name', '') for d in dims[:3]])
                if len(dims) > 3:
                    dim_names += f'...(+{len(dims)-3})'
                
                table_data.append([
                    item.get('name', ''),
                    item.get('customItemID', '')[:30] + '...',
                    item.get('unit', ''),
                    f"{item.get('interval', 0)}s",
                    dim_names
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['名称','监控项ID','单位','间隔','维度'], tablefmt='grid')}")
        else:
            click.echo("\n未找到自定义监控项")
        
        click.echo("\n" + "="*80)


@monitor.command('query-custom-alarm-rules')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--status', type=int, help='规则状态(0:启用,1:停用)')
@click.option('--alarm-status', type=int, help='告警状态(0:正常,1:告警)')
@click.option('--sort', help='排序(-updateTime:按更新时间降序)')
@click.option('--name', help='规则名称')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_custom_alarm_rules(ctx, region_id, status, alarm_status, sort, name, page_no, page_size):
    """查询自定义监控告警规则列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_custom_alarm_rules(region_id, status, alarm_status, sort, name, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n自定义监控告警规则列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        rules = data.get('alarmRules', [])
        if rules:
            table_data = []
            status_map = {0: '启用', 1: '停用'}
            alarm_status_map = {0: '正常', 1: '告警'}
            
            for rule in rules:
                table_data.append([
                    rule.get('name', '')[:30],
                    rule.get('customItemID', '')[:25] + '...',
                    f"{rule.get('fun', '')} {rule.get('operator', '')} {rule.get('value', '')}",
                    status_map.get(rule.get('status', 0), '未知'),
                    alarm_status_map.get(rule.get('alarmStatus', 0), '未知')
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['规则名称','监控项ID','条件','状态','告警状态'], tablefmt='grid')}")
        else:
            click.echo("\n未找到自定义监控告警规则")
        
        click.echo("\n" + "="*80)


@monitor.command('describe-custom-alarm-rule')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--alarm-rule-id', required=True, help='告警规则ID')
@click.pass_context
@handle_error
def describe_custom_alarm_rule(ctx, region_id, alarm_rule_id):
    """查询自定义监控告警规则详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).describe_custom_alarm_rule(region_id, alarm_rule_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from datetime import datetime
        click.echo(f"\n自定义监控告警规则详情\n" + "="*80)
        
        status_map = {0: '启用', 1: '停用'}
        alarm_status_map = {0: '正常', 1: '告警'}
        fun_map = {'last': '原始值', 'avg': '平均值', 'max': '最大值', 'min': '最小值'}
        operator_map = {'eq': '等于', 'gt': '大于', 'ge': '大于等于', 'lt': '小于', 'le': '小于等于'}
        weekday_map = {0: '周日', 1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六'}
        
        click.echo(f"  规则ID: {data.get('alarmRuleID', '')}")
        click.echo(f"  规则名称: {data.get('name', '')}")
        click.echo(f"  描述: {data.get('desc', '')}")
        click.echo(f"  监控项ID: {data.get('customItemID', '')}")
        click.echo(f"  规则状态: {status_map.get(data.get('status', 0), '未知')}")
        click.echo(f"  告警状态: {alarm_status_map.get(data.get('alarmStatus', 0), '未知')}")
        
        click.echo(f"\n  告警条件:")
        click.echo(f"    算法: {fun_map.get(data.get('fun', ''), data.get('fun', ''))}")
        click.echo(f"    周期: {data.get('period', 'N/A')}")
        click.echo(f"    条件: {operator_map.get(data.get('operator', ''), data.get('operator', ''))} {data.get('value', '')}")
        click.echo(f"    持续: {data.get('evaluationCount', 0)}次")
        
        dims = data.get('dimensions', [])
        if dims:
            click.echo(f"\n  维度过滤({len(dims)}个):")
            for dim in dims:
                values = dim.get('value', [])
                click.echo(f"    - {dim.get('name', '')}: {', '.join(values[:3])}{' ...' if len(values) > 3 else ''}")
        
        click.echo(f"\n  通知配置:")
        click.echo(f"    静默时间: {data.get('silenceTime', 0)}秒")
        click.echo(f"    重复通知: {data.get('repeatTimes', 0)}次")
        click.echo(f"    恢复通知: {'是' if data.get('recoverNotify') == 1 else '否'}")
        
        notify_types = data.get('notifyType', [])
        click.echo(f"    通知方式: {', '.join(notify_types) if notify_types else '无'}")
        
        weekdays = data.get('notifyWeekdays', [])
        weekday_strs = [weekday_map.get(d, str(d)) for d in weekdays]
        click.echo(f"    通知周期: {', '.join(weekday_strs)}")
        click.echo(f"    通知时段: {data.get('notifyStart', '')} - {data.get('notifyEnd', '')}")
        
        contact_groups = data.get('contactGroupList', [])
        if contact_groups:
            click.echo(f"    联系组: {', '.join(contact_groups)}")
        
        webhooks = data.get('webhookUrl', [])
        if webhooks:
            click.echo(f"\n  Webhook URL({len(webhooks)}个):")
            for url in webhooks:
                click.echo(f"    - {url}")
        
        create_time = data.get('createTime', 0)
        update_time = data.get('updateTime', 0)
        if create_time:
            click.echo(f"\n  创建时间: {datetime.fromtimestamp(create_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        if update_time:
            click.echo(f"  更新时间: {datetime.fromtimestamp(update_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-notice-templates')
@click.option('--service', help='服务（如ecs）')
@click.option('--dimension', help='维度（如ecs、disk）')
@click.option('--name', help='名称模糊搜索')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=10, help='页大小')
@click.pass_context
@handle_error
def query_notice_templates(ctx, service, dimension, name, page_no, page_size):
    """查询通知模板列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_notice_templates(service, dimension, name, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n通知模板列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        templates = data.get('noticeTemplateList', [])
        if templates:
            table_data = []
            for tpl in templates:
                contents = tpl.get('contents', [])
                notify_types = ', '.join([c.get('notifyType', '') for c in contents])
                
                table_data.append([
                    tpl.get('name', ''),
                    f"{tpl.get('service', '')}/{tpl.get('dimension', '')}",
                    notify_types,
                    '是' if tpl.get('isDefault') else '否'
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['名称','服务/维度','通知方式','默认'], tablefmt='grid')}")
        else:
            click.echo("\n未找到通知模板")
        
        click.echo("\n" + "="*80)


@monitor.command('describe-notice-template')
@click.option('--notice-template-id', required=True, help='通知模板ID')
@click.pass_context
@handle_error
def describe_notice_template(ctx, notice_template_id):
    """查询通知模板详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).describe_notice_template(notice_template_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from datetime import datetime
        click.echo(f"\n通知模板详情\n" + "="*80)
        
        click.echo(f"  模板ID: {data.get('noticeTemplateID', '')}")
        click.echo(f"  模板名称: {data.get('name', '')}")
        click.echo(f"  服务/维度: {data.get('service', '')}/{data.get('dimension', '')}")
        click.echo(f"  默认模板: {'是' if data.get('isDefault') else '否'}")
        
        contents = data.get('contents', [])
        if contents:
            click.echo(f"\n  通知内容({len(contents)}种方式):")
            for cont in contents:
                click.echo(f"\n    [{cont.get('notifyType', '')}]:")
                content_text = cont.get('content', '')
                for line in content_text.split('\n')[:5]:
                    click.echo(f"    {line}")
                if len(content_text.split('\n')) > 5:
                    click.echo(f"    ...")
        
        create_time = data.get('createTime', 0)
        update_time = data.get('updateTime', 0)
        if create_time:
            click.echo(f"\n  创建时间: {datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')}")
        if update_time:
            click.echo(f"  更新时间: {datetime.fromtimestamp(update_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-notice-template-variable')
@click.option('--group', required=True, type=click.Choice(['basic', 'entity']), help='分组(basic:基本信息,entity:告警对象)')
@click.option('--dimension', required=True, help='维度（如ecs、disk）')
@click.pass_context
@handle_error
def query_notice_template_variable(ctx, group, dimension):
    """查询通知模板变量"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_notice_template_variable(group, dimension)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', [])
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n通知模板变量\n" + "="*80)
        click.echo(f"分组: {group} | 维度: {dimension}")
        click.echo(f"变量数量: {len(data)}")
        
        if data:
            table_data = []
            for var in data:
                table_data.append([
                    var.get('name', ''),
                    var.get('description', '')
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['变量名','描述'], tablefmt='grid')}")
        else:
            click.echo("\n未找到模板变量")
        
        click.echo("\n" + "="*80)


@monitor.command('describe-alarm-template')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--template-id', required=True, help='告警模板ID')
@click.pass_context
@handle_error
def describe_alarm_template(ctx, region_id, template_id):
    """查询告警模板详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).describe_alarm_template(region_id, template_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from datetime import datetime
        click.echo(f"\n告警模板详情\n" + "="*80)
        
        click.echo(f"  模板ID: {data.get('templateID', '')}")
        click.echo(f"  模板名称: {data.get('name', '')}")
        click.echo(f"  服务/维度: {data.get('service', '')}/{data.get('dimension', '')}")
        click.echo(f"  描述: {data.get('desc', '')}")
        
        conditions = data.get('conditions', [])
        if conditions:
            fun_map = {'last': '原始值', 'avg': '平均值', 'max': '最大值', 'min': '最小值'}
            operator_map = {'eq': '等于', 'gt': '大于', 'ge': '大于等于', 'lt': '小于', 'le': '小于等于'}
            
            click.echo(f"\n  告警条件({len(conditions)}个):")
            for idx, cond in enumerate(conditions, 1):
                click.echo(f"    {idx}. {cond.get('metricCnName', cond.get('metric', ''))}")
                click.echo(f"       算法: {fun_map.get(cond.get('fun', ''), cond.get('fun', ''))} | 周期: {cond.get('period', 'N/A')}")
                click.echo(f"       条件: {operator_map.get(cond.get('operator', ''), cond.get('operator', ''))} {cond.get('value', '')} {cond.get('unit', '')}")
                click.echo(f"       持续: {cond.get('evaluationCount', 0)}次")
        
        create_time = data.get('createTime', 0)
        update_time = data.get('updateTime', 0)
        if create_time:
            click.echo(f"\n  创建时间: {datetime.fromtimestamp(create_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        if update_time:
            click.echo(f"  更新时间: {datetime.fromtimestamp(update_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-alarm-templates')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--query-content', help='名称模糊搜索')
@click.option('--services', help='服务列表JSON（如["ecs","evs"]）')
@click.option('--template-type', type=click.Choice(['system', 'custom', 'all']), help='模板类型')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=10, help='页大小')
@click.pass_context
@handle_error
def query_alarm_templates(ctx, region_id, query_content, services, template_type, page_no, page_size):
    """查询告警模板列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    
    service_list = None
    if services:
        import json
        service_list = json.loads(services)
    
    result = MonitorClient(client).query_alarm_templates(region_id, query_content, service_list, template_type, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n告警模板列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 配额: {data.get('templateQuota', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        templates = data.get('templateList', [])
        if templates:
            table_data = []
            for tpl in templates:
                conditions = tpl.get('conditions', [])
                cond_count = len(conditions)
                
                table_data.append([
                    tpl.get('name', '')[:30],
                    f"{tpl.get('service', '')}/{tpl.get('dimension', '')}",
                    cond_count,
                    tpl.get('desc', '')[:20]
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['模板名称','服务/维度','条件数','描述'], tablefmt='grid')}")
        else:
            click.echo("\n未找到告警模板")
        
        click.echo("\n" + "="*80)


@monitor.command('describe-contact')
@click.option('--contact-id', required=True, help='联系人ID')
@click.pass_context
@handle_error
def describe_contact(ctx, contact_id):
    """查询告警联系人详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).describe_contact(contact_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from datetime import datetime
        click.echo(f"\n告警联系人详情\n" + "="*80)
        
        phone_status = '已激活' if data.get('phoneActivation') == 1 else '未激活'
        email_status = '已激活' if data.get('emailActivation') == 1 else '未激活'
        
        click.echo(f"  联系人ID: {data.get('contactID', '')}")
        click.echo(f"  姓名: {data.get('name', '')}")
        click.echo(f"  手机号: {data.get('phone', '')} ({phone_status})")
        click.echo(f"  邮箱: {data.get('email', '')} ({email_status})")
        
        groups = data.get('contactGroupList', [])
        if groups:
            click.echo(f"\n  所属联系组({len(groups)}个):")
            for group in groups:
                click.echo(f"    - {group.get('name', '')} ({group.get('contactGroupID', '')})")
        else:
            click.echo(f"\n  所属联系组: 无")
        
        create_time = data.get('createTime', 0)
        update_time = data.get('updateTime', 0)
        if create_time:
            click.echo(f"\n  创建时间: {datetime.fromtimestamp(create_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        if update_time:
            click.echo(f"  更新时间: {datetime.fromtimestamp(update_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo("\n" + "="*80)


@monitor.command('describe-contact-group')
@click.option('--contact-group-id', required=True, help='联系人组ID')
@click.pass_context
@handle_error
def describe_contact_group(ctx, contact_group_id):
    """查询告警联系人组详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).describe_contact_group(contact_group_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from datetime import datetime
        from tabulate import tabulate
        click.echo(f"\n告警联系人组详情\n" + "="*80)
        
        click.echo(f"  组ID: {data.get('contactGroupID', '')}")
        click.echo(f"  组名: {data.get('name', '')}")
        click.echo(f"  描述: {data.get('desc', '')}")
        
        contacts = data.get('contactList', [])
        if contacts:
            click.echo(f"\n  成员列表({len(contacts)}人):")
            table_data = []
            for contact in contacts:
                phone_st = '✓' if contact.get('phoneActivation') == 1 else '✗'
                email_st = '✓' if contact.get('emailActivation') == 1 else '✗'
                table_data.append([
                    contact.get('name', ''),
                    contact.get('phone', ''),
                    phone_st,
                    contact.get('email', ''),
                    email_st
                ])
            click.echo(f"\n{tabulate(table_data, headers=['姓名','手机号','激活','邮箱','激活'], tablefmt='grid')}")
        else:
            click.echo(f"\n  成员列表: 无")
        
        create_time = data.get('createTime', 0)
        update_time = data.get('updateTime', 0)
        if create_time:
            click.echo(f"\n  创建时间: {datetime.fromtimestamp(create_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        if update_time:
            click.echo(f"  更新时间: {datetime.fromtimestamp(update_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-alarm-blacklists')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--device-uuid', help='设备UUID')
@click.option('--name', help='黑名单名称')
@click.option('--service', help='服务（如ecs）')
@click.option('--dimension', help='维度（如ecs、disk）')
@click.option('--contact-group-id', help='联系人组ID')
@click.option('--contact-group-name', help='联系人组名称')
@click.option('--create-time-from', type=int, help='创建起始时间（毫秒）')
@click.option('--create-time-till', type=int, help='创建截止时间（毫秒）')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_alarm_blacklists(ctx, region_id, device_uuid, name, service, dimension, contact_group_id,
                           contact_group_name, create_time_from, create_time_till, page_no, page_size):
    """查询告警黑名单列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_alarm_blacklists(region_id, device_uuid, name, service, dimension,
                                                          contact_group_id, contact_group_name, create_time_from,
                                                          create_time_till, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n告警黑名单列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        blacklists = data.get('AlarmBlacklists', [])
        if blacklists:
            table_data = []
            status_map = {0: '启用', 1: '停用'}
            for bl in blacklists:
                devices = bl.get('devices', [])
                device_str = ', '.join(devices[:2])
                if len(devices) > 2:
                    device_str += f'...(+{len(devices)-2})'
                
                table_data.append([
                    bl.get('name', ''),
                    f"{bl.get('service', '')}/{bl.get('dimension', '')}",
                    device_str or '无',
                    len(bl.get('metrics', [])),
                    status_map.get(bl.get('status', 0), '未知')
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['名称','服务/维度','设备','指标数','状态'], tablefmt='grid')}")
        else:
            click.echo("\n未找到告警黑名单")
        
        click.echo("\n" + "="*80)


@monitor.command('query-message-records')
@click.option('--receiver', help='通知对象（邮箱或手机号）')
@click.option('--record-type', type=int, help='通知类型(0:监控告警,1:外部告警)')
@click.option('--method', help='通知方式(email/sms/webhook)')
@click.option('--record-status', type=int, help='通知状态(0:成功,1:失败)')
@click.option('--start-time', type=int, help='起始时间（毫秒）')
@click.option('--end-time', type=int, help='截止时间（毫秒）')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_message_records(ctx, receiver, record_type, method, record_status, start_time, end_time, page_no, page_size):
    """查询通知记录列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_message_records(receiver, record_type, method, record_status,
                                                         start_time, end_time, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        from datetime import datetime
        click.echo(f"\n通知记录列表\n" + "="*80)
        click.echo(f"总记录数: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        records = data.get('MessageRecords', [])
        if records:
            table_data = []
            type_map = {0: '监控告警', 1: '外部告警'}
            status_map = {0: '成功', 1: '失败'}
            
            for rec in records:
                create_time = datetime.fromtimestamp(rec.get('createTime', 0)/1000).strftime('%m-%d %H:%M')
                table_data.append([
                    create_time,
                    rec.get('receiver', '')[:20],
                    rec.get('method', ''),
                    type_map.get(rec.get('recordType', 0), '未知'),
                    status_map.get(rec.get('recordStatus', 0), '未知'),
                    rec.get('subject', '')[:30]
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['时间','接收者','方式','类型','状态','主题'], tablefmt='grid')}")
            
            if records:
                first = records[0]
                click.echo(f"\n第一条记录详情:")
                click.echo(f"  记录ID: {first.get('recordID', '')}")
                click.echo(f"  主题: {first.get('subject', '')}")
                if first.get('errMessage'):
                    click.echo(f"  错误信息: {first.get('errMessage', '')}")
                content = first.get('content', '')
                if content:
                    click.echo(f"  内容预览:")
                    for line in content.split('\n')[:3]:
                        click.echo(f"    {line}")
                    if len(content.split('\n')) > 3:
                        click.echo(f"    ...")
        else:
            click.echo("\n未找到通知记录")
        
        click.echo("\n" + "="*80)


@monitor.command('query-inspection-task-overview')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--task-id', help='巡检任务ID')
@click.pass_context
@handle_error
def query_inspection_task_overview(ctx, region_id, task_id):
    """查询巡检任务结果总览"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_inspection_task_overview(region_id, task_id)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from datetime import datetime
        click.echo(f"\n巡检任务结果总览\n" + "="*80)
        
        status_map = {1: '运行中', 2: '已完成', 3: '失败'}
        click.echo(f"  任务ID: {data.get('taskID', '')}")
        click.echo(f"  任务状态: {status_map.get(data.get('status', 0), '未知')}")
        click.echo(f"  巡检得分: {data.get('inspectionScore', 0)}")
        
        inspection_time = data.get('inspectionTime', 0)
        if inspection_time:
            click.echo(f"  巡检时间: {datetime.fromtimestamp(inspection_time/1000).strftime('%Y-%m-%d %H:%M:%S')}")
        
        click.echo(f"\n  健康评估:")
        click.echo(f"    检查项数量: {data.get('healthCount', 0)}")
        click.echo(f"    问题数量: {data.get('healthProblemCount', 0)}")
        
        click.echo(f"\n  风险识别:")
        click.echo(f"    识别项数量: {data.get('riskCount', 0)}")
        click.echo(f"    风险数量: {data.get('riskProblemCount', 0)}")
        
        click.echo("\n" + "="*80)


@monitor.command('query-inspection-task-detail')
@click.option('--task-id', required=True, help='巡检任务ID')
@click.option('--inspection-type', required=True, type=int, help='巡检类型(1:健康评估,2:风险识别)')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_inspection_task_detail(ctx, task_id, inspection_type, page_no, page_size):
    """查询巡检任务结果详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_inspection_task_detail(task_id, inspection_type, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        type_map = {1: '健康评估', 2: '风险识别'}
        level_map = {1: '低', 2: '中', 3: '高'}
        
        click.echo(f"\n巡检任务详情 ({type_map.get(inspection_type, '未知')})\n" + "="*80)
        click.echo(f"任务ID: {data.get('taskID', '')} | 总记录: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        results = data.get('inspectionResultList', [])
        if results:
            table_data = []
            for item in results:
                table_data.append([
                    item.get('deviceName', ''),
                    item.get('productType', ''),
                    item.get('inspectionItem', ''),
                    level_map.get(item.get('level', 0), '未知')
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['设备名称','产品类型','巡检项','等级'], tablefmt='grid')}")
        else:
            click.echo("\n未找到巡检结果")
        
        click.echo("\n" + "="*80)


@monitor.command('query-inspection-items')
@click.option('--inspection-type', type=int, help='巡检类型(1:健康评估,2:风险识别)')
@click.option('--search', help='模糊搜索')
@click.pass_context
@handle_error
def query_inspection_items(ctx, inspection_type, search):
    """查询巡检项"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_inspection_items(inspection_type, search)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n巡检项列表\n" + "="*80)
        
        items = data.get('inspectionItemList', [])
        if items:
            type_map = {1: '健康评估', 2: '风险识别'}
            level_map = {1: '低', 2: '中', 3: '高'}
            
            table_data = []
            for item in items:
                status = '正常' if item.get('status') else '异常'
                table_data.append([
                    item.get('inspectionItemName', ''),
                    type_map.get(item.get('inspectionType', 0), '未知'),
                    level_map.get(item.get('level', 0), '未知'),
                    status,
                    item.get('description', '')[:40]
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['巡检项','类型','等级','状态','描述'], tablefmt='grid')}")
        else:
            click.echo("\n未找到巡检项")
        
        click.echo("\n" + "="*80)


@monitor.command('query-inspection-history-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', type=int, help='起始时间戳(秒)')
@click.option('--end-time', type=int, help='截止时间戳(秒)')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_inspection_history_list(ctx, region_id, start_time, end_time, page_no, page_size):
    """查询巡检历史列表"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_inspection_history_list(region_id, start_time, end_time, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        from datetime import datetime
        
        click.echo(f"\n巡检历史列表\n" + "="*80)
        click.echo(f"总记录: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        histories = data.get('inspectionHistoryList', [])
        if histories:
            table_data = []
            for hist in histories:
                time_str = datetime.fromtimestamp(hist.get('inspectionTime', 0)/1000).strftime('%m-%d %H:%M')
                table_data.append([
                    time_str,
                    hist.get('inspectionScore', 0),
                    f"{hist.get('healthProblemCount', 0)}/{hist.get('healthCount', 0)}",
                    f"{hist.get('riskProblemCount', 0)}/{hist.get('riskCount', 0)}",
                    hist.get('taskID', '')[:20] + '...'
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['时间','得分','健康(问题/项)','风险(问题/项)','任务ID'], tablefmt='grid')}")
        else:
            click.echo("\n未找到巡检历史")
        
        click.echo("\n" + "="*80)


@monitor.command('query-inspection-history-detail')
@click.option('--task-id', required=True, help='巡检任务ID')
@click.option('--inspection-item', required=True, type=int, help='巡检项(1-4)')
@click.option('--page-no', type=int, default=1, help='页码')
@click.option('--page-size', type=int, default=20, help='页大小')
@click.pass_context
@handle_error
def query_inspection_history_detail(ctx, task_id, inspection_item, page_no, page_size):
    """查询巡检历史详情"""
    client, output_format = ctx.obj['client'], ctx.obj.get('output', 'table')
    result = MonitorClient(client).query_inspection_history_detail(task_id, inspection_item, page_no, page_size)
    
    if not result.get('success'):
        click.echo(f"❌ 查询失败: {result.get('message')}", err=True)
        import sys
        sys.exit(1)
    
    data = result.get('data', {})
    
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    else:
        from tabulate import tabulate
        click.echo(f"\n巡检历史详情\n" + "="*80)
        click.echo(f"总记录: {data.get('totalCount', 0)} | 当前页: {data.get('currentCount', 0)}/{data.get('totalPage', 0)}")
        
        details = data.get('anomalyDetail', [])
        if details:
            table_data = []
            for detail in details:
                table_data.append([
                    detail.get('deviceName', ''),
                    detail.get('item', ''),
                    f"{detail.get('value', 0):.2f}",
                    detail.get('deviceUUID', '')[:30] + '...'
                ])
            
            click.echo(f"\n{tabulate(table_data, headers=['设备名称','监控项','异常值','设备UUID'], tablefmt='grid')}")
        else:
            click.echo("\n未找到异常详情")
        
        click.echo("\n" + "="*80)


if __name__ == '__main__':
    monitor()
