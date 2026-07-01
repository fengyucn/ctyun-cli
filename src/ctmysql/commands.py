"""
关系数据库MySQL版(RDS)命令行接口

命令组名使用 ctmysql (而非 mysql)，避免与系统 mysql 命令冲突。
"""

import click
from typing import Optional, List
from utils import OutputFormatter


@click.group()
def ctmysql():
    """关系数据库MySQL版(RDS)管理"""
    pass


def _output(ctx, result: dict, output: Optional[str]):
    """统一输出处理"""
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


# ==================== 查询实例列表 ====================

@ctmysql.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page-now', type=int, default=1, help='当前页码，默认1')
@click.option('--page-size', type=int, default=10, help='每页条数，默认10')
@click.option('--name', default=None, help='实例名称(模糊查询)')
@click.option('--engine', default=None, type=click.Choice(['5.7', '8.0']),
              help='数据库引擎版本')
@click.option('--vip', default=None, help='连接IP地址')
@click.option('--project-id', default=None, help='企业项目ID')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def list_instances(ctx, region_id: str, page_now: int, page_size: int,
                   name: Optional[str], engine: Optional[str],
                   vip: Optional[str], project_id: Optional[str],
                   output: Optional[str]):
    """查询RDS实例列表"""
    from ctmysql.client import RDSClient

    client = ctx.obj['client']
    rds_client = RDSClient(client)

    result = rds_client.list_instances(
        region_id=region_id, page_now=page_now, page_size=page_size,
        prod_inst_name=name, res_db_engine=engine, vip=vip,
        project_id=project_id
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    return_obj = result.get('returnObj', {})
    instances = return_obj.get('list', [])
    total = return_obj.get('total', 0)
    click.echo(f"RDS实例列表 (共 {total} 个，当前 {len(instances)} 个)")
    if instances:
        table_data = []
        for inst in instances:
            running_status = inst.get('prodRunningStatus', -1)
            order_status = inst.get('prodOrderStatus', -1)
            alive = inst.get('alive', -1)
            bill_map = {0: '按月', 1: '按天', 2: '按年', 4: '按需'}
            type_map = {0: '单机', 1: '一主一从', 2: '一主两从', 4: '只读'}
            table_data.append({
                '实例ID': inst.get('outerProdInstId', ''),
                '实例名称': inst.get('prodInstName', ''),
                '引擎': inst.get('prodDbEngine', ''),
                '版本': inst.get('newMysqlVersion', ''),
                '规格': inst.get('machineSpec', ''),
                '存储(GB)': inst.get('diskSize', ''),
                '类型': type_map.get(inst.get('prodType', -1), str(inst.get('prodType', ''))),
                '状态': '正常' if alive == 0 else '异常',
                '运行状态': _running_status_text(running_status),
                '订单状态': _order_status_text(order_status),
                '连接IP': inst.get('vip', ''),
                '计费': bill_map.get(inst.get('prodBillType', -1), str(inst.get('prodBillType', ''))),
            })
        click.echo(OutputFormatter.format_table(table_data))


def _running_status_text(code: int) -> str:
    """运行状态码转中文"""
    status_map = {
        0: '正常', 1: '重启中', 2: '备份中', 3: '恢复中',
        4: '修改参数中', 5: '应用参数组中', 6: '扩容预处理中',
        7: '扩容预处理完成', 8: '修改端口中', 9: '迁移中',
        10: '重置密码中', 11: '修改数据复制方式中',
        12: '缩容预处理中', 13: '缩容预处理完成',
        15: '内核小版本升级', 17: '迁移可用区中',
        18: '修改备份配置中', 20: '停止中', 21: '已停止',
        22: '启动中', 26: '白名单配置中',
    }
    return status_map.get(code, f'未知({code})')


def _order_status_text(code: int) -> str:
    """订单状态码转中文"""
    status_map = {
        0: '正常', 1: '欠费暂停', 2: '已注销', 3: '创建中',
        4: '施工失败', 5: '到期退订', 6: 'OpenAPI暂停',
        7: '等待变更', 8: '待注销', 9: '手动暂停', 10: '手动退订',
    }
    return status_map.get(code, f'未知({code})')


# ==================== 批量实例绑定解绑标签 ====================

@ctmysql.command('batch-label')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--action', required=True, type=click.Choice(['bind', 'unbind']),
              help='操作类型: bind(绑定) / unbind(解绑)')
@click.option('--instance-ids', required=True,
              help='实例ID列表，逗号分隔，如 id1,id2,id3')
@click.option('--label', required=True, multiple=True,
              help='标签，格式 key=value，可多次指定，如 --label env=prod --label app=mysql')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def batch_label(ctx, region_id: str, action: str, instance_ids: str,
                label: tuple, output: Optional[str]):
    """批量实例绑定/解绑标签"""
    import sys
    from ctmysql.client import RDSClient

    client = ctx.obj['client']
    rds_client = RDSClient(client)

    inst_ids = [s.strip() for s in instance_ids.split(',') if s.strip()]
    labels = []
    for lv in label:
        if '=' not in lv:
            click.echo(f"错误: 标签格式应为 key=value，收到: {lv}", err=True)
            sys.exit(1)
        k, v = lv.split('=', 1)
        labels.append({'key': k.strip(), 'value': v.strip()})

    result = rds_client.batch_label(
        region_id=region_id, action=action,
        outer_prod_inst_ids=inst_ids, labels=labels
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    action_text = '绑定' if action == 'bind' else '解绑'
    click.echo(f"✓ 批量{action_text}标签成功")
    click.echo(f"  实例数: {len(inst_ids)}")
    click.echo(f"  标签数: {len(labels)}")
    click.echo(f"  实例: {', '.join(inst_ids)}")
    label_str = ', '.join(f"{l['key']}={l['value']}" for l in labels)
    click.echo(f"  标签: {label_str}")


# ==================== 批量查询实例监控数据 ====================

@ctmysql.command('batch-monitor')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--engine', required=True, default='Mysql', show_default=True,
              type=click.Choice(['Mysql', 'PostgreSQL']),
              help='实例类型')
@click.option('--instance-ids', required=True,
              help='实例ID列表，逗号分隔(最多20个)')
@click.option('--metric', required=True,
              help='监控指标名，如 mysql_monitor_cpu_util')
@click.option('--period', required=True, type=click.Choice([15, 60, 900, 3600]),
              help='采样周期(秒): 15/60/900/3600')
@click.option('--start-time', type=int, default=None,
              help='开始时间戳(秒)，如 1733207910')
@click.option('--end-time', type=int, default=None,
              help='结束时间戳(秒)，如 1733211510')
@click.option('--last-hours', type=int, default=None,
              help='便捷选项: 查询最近N小时数据(与start/end-time二选一)')
@click.option('--agg-func', required=True, default='avg', show_default=True,
              type=click.Choice(['avg', 'max', 'min']),
              help='聚合函数: avg/max/min')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def batch_monitor(ctx, region_id: str, engine: str, instance_ids: str,
                  metric: str, period: int,
                  start_time: Optional[int], end_time: Optional[int],
                  last_hours: Optional[int], agg_func: str,
                  output: Optional[str]):
    """批量查询实例监控数据"""
    import sys
    import time
    from ctmysql.client import RDSClient

    client = ctx.obj['client']
    rds_client = RDSClient(client)

    inst_ids = [s.strip() for s in instance_ids.split(',') if s.strip()]
    if len(inst_ids) > 20:
        click.echo("错误: 一次最多查询20个实例", err=True)
        sys.exit(1)

    if last_hours is not None:
        if start_time or end_time:
            click.echo("错误: --last-hours 与 --start-time/--end-time 不可同时使用", err=True)
            sys.exit(1)
        end_time = int(time.time())
        start_time = end_time - last_hours * 3600
    elif not start_time or not end_time:
        click.echo("错误: 需要指定 --last-hours 或同时指定 --start-time 和 --end-time", err=True)
        sys.exit(1)

    result = rds_client.batch_metric_data(
        region_id=region_id, prod_engine_name=engine,
        inst_ids=inst_ids, metrics_type=metric, period=period,
        start_time=start_time, end_time=end_time, agg_func=agg_func
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    data_list = result.get('returnObj', {}).get('data', [])
    if not data_list:
        click.echo("未查询到监控数据")
        return

    click.echo(f"监控数据 (指标: {metric}, 周期: {period}s, 聚合: {agg_func})")
    click.echo(f"时间范围: {start_time} ~ {end_time}")
    click.echo("=" * 70)

    for item in data_list:
        label_obj = item.get('label', {})
        inst_id = label_obj.get('outProdInstId', '')
        ip = label_obj.get('vpcIp', '')
        device = label_obj.get('device', '')
        data_points = item.get('dataPoints', [])

        header = f"实例: {inst_id}"
        if ip:
            header += f"  IP: {ip}"
        if device:
            header += f"  设备: {device}"
        click.echo(f"\n{header} ({len(data_points)}个数据点)")

        if data_points:
            table_data = []
            for dp in data_points:
                ts = dp.get('timestamp', '')
                val = dp.get(agg_func, dp.get('avg', dp.get('max', dp.get('min', ''))))
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    dt = str(ts)
                table_data.append({'时间': dt, '值': val})
            click.echo(OutputFormatter.format_table(table_data))


# ==================== 询价 API ====================

def _display_price(result: dict, title: str):
    """统一展示询价结果 (v2/teledb-acceptor 响应结构)"""
    data = result.get('returnObj', {}).get('data', {})
    if not data:
        # 老版API可能直接在returnObj里返回
        data = result.get('returnObj', {})
    total = data.get('totalPrice', '-')
    final = data.get('finalPrice', '-')
    discount = data.get('discountPrice')
    sub_orders = data.get('subOrderPrices', [])

    click.echo("=" * 60)
    click.echo(title)
    click.echo("=" * 60)
    click.echo(f"  {'总价 (CNY)':<14}: {total}")
    click.echo(f"  {'最终价 (CNY)':<14}: {final}")
    if discount is not None:
        click.echo(f"  {'折后价 (CNY)':<14}: {discount}")

    if sub_orders:
        click.echo("\n子订单明细:")
        click.echo("-" * 60)
        for sub in sub_orders:
            click.echo(f"  服务标签: {sub.get('serviceTag', '-')}  "
                       f"总价: {sub.get('totalPrice', '-')}  "
                       f"最终价: {sub.get('finalPrice', '-')} CNY")
            for item in sub.get('orderItemPrices', []):
                click.echo(f"    [{item.get('resourceType', '-')}]  "
                           f"总价: {item.get('totalPrice', '-')}  "
                           f"最终价: {item.get('finalPrice', '-')} CNY")


@ctmysql.command('inquiry')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--project-id', required=True, help='企业项目ID')
@click.option('--bill-mode', required=True, type=click.Choice(['1', '2']),
              help='计费模式: 1=包周期, 2=按需')
@click.option('--prod-version', required=True, help='MySQL版本，如 5.7 / 8.0')
@click.option('--host-type', required=True,
              help='主机类型: S6/S7/S8/C6/C7/C8/M6/M7/M8/HS1/HC1/HM1/KS1/KC1/KM1')
@click.option('--period', required=True, type=int, help='购买时长(月)，1-36')
@click.option('--count', required=True, type=int, help='购买数量，1-50')
@click.option('--auto-renew', required=True, type=click.Choice(['0', '1']),
              help='自动续订: 0=否, 1=是')
@click.option('--prod-id', required=True, type=int, help='产品ID')
@click.option('--node-type', required=True, help='节点类型: master / readNode')
@click.option('--inst-spec', required=True,
              help='规格类型: 1=通用型,2=计算增强型,3=内存优化型,...')
@click.option('--storage-type', required=True,
              help='存储类型: SSD/SATA/SAS/SSD-genric/FAST-SSD/XSSD-0等')
@click.option('--storage-space', required=True, type=int, help='存储空间(GB)，100-32768')
@click.option('--perf-spec', required=True, help='规格名称，如 2C4G')
@click.option('--az-name', required=True, help='可用区名称')
@click.option('--az-count', type=int, default=1, show_default=True, help='可用区节点数')
@click.option('--az-node-type', default='master', show_default=True,
              help='可用区节点类型: master/slave/readNode')
@click.option('--vpc-id', default=None, help='VPC ID')
@click.option('--subnet-id', default=None, help='子网ID')
@click.option('--security-group-id', default=None, help='安全组ID')
@click.option('--inst-id', default=None, help='父实例ID(只读实例询价时使用)')
@click.option('--cpu-type', type=int, default=None,
              help='CPU类型: 10=鲲鹏, 20=海光, 30=intel')
@click.option('--os-type', type=int, default=None,
              help='系统类型: 2=centos, 11=ctyunos')
@click.option('--disks', type=int, default=1, show_default=True, help='磁盘数(默认1)')
@click.option('--backup-storage-type', default=None, help='备份盘存储类型(XSSD必填)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def inquiry(ctx, region_id: str, project_id: str, bill_mode: str,
            prod_version: str, host_type: str, period: int, count: int,
            auto_renew: str, prod_id: int, node_type: str, inst_spec: str,
            storage_type: str, storage_space: int, perf_spec: str,
            az_name: str, az_count: int, az_node_type: str,
            vpc_id: Optional[str], subnet_id: Optional[str],
            security_group_id: Optional[str], inst_id: Optional[str],
            cpu_type: Optional[int], os_type: Optional[int],
            disks: int, backup_storage_type: Optional[str],
            output: Optional[str]):
    """新建实例询价(v2)"""
    from ctmysql.client import RDSClient

    client = ctx.obj['client']
    rds_client = RDSClient(client)

    node_info = {
        'nodeType': node_type,
        'instSpec': inst_spec,
        'storageType': storage_type,
        'storageSpace': storage_space,
        'prodPerformanceSpec': perf_spec,
        'disks': disks,
        'availabilityZoneInfo': [{
            'availabilityZoneName': az_name,
            'availabilityZoneCount': az_count,
            'nodeType': az_node_type,
        }],
    }
    if backup_storage_type:
        node_info['backupStorageType'] = backup_storage_type

    result = rds_client.inquiry(
        region_id=region_id, project_id=project_id, bill_mode=bill_mode,
        prod_version=prod_version, host_type=host_type, period=period,
        count=count, auto_renew_status=int(auto_renew), prod_id=prod_id,
        mysql_node_info_list=[node_info],
        vpc_id=vpc_id, subnet_id=subnet_id,
        security_group_id=security_group_id, inst_id=inst_id,
        cpu_type=cpu_type, os_type=os_type,
        backup_storage_type=backup_storage_type,
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    _display_price(result, f"新建实例询价  {perf_spec} {storage_space}GB  {period}月 x{count}")


@ctmysql.command('inquiry-upgrade')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--project-id', required=True, help='企业项目ID')
@click.option('--inst-id', required=True, help='实例ID')
@click.option('--node-type', default=None, help='节点类型: master/backup(磁盘扩容/系列升级时必填)')
@click.option('--prod-id', default=None, help='产品ID(系列升级时传)')
@click.option('--disk-volume', default=None, help='目标磁盘容量(GB)，磁盘扩容时传')
@click.option('--perf-spec', default=None, help='目标规格名(如4C8G)，规格扩容时传')
@click.option('--az-name', default=None, help='可用区名(新增节点时传)')
@click.option('--az-count', type=int, default=None, help='新增节点数')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def inquiry_upgrade(ctx, region_id: str, project_id: str, inst_id: str,
                    node_type: Optional[str], prod_id: Optional[str],
                    disk_volume: Optional[str], perf_spec: Optional[str],
                    az_name: Optional[str], az_count: Optional[int],
                    output: Optional[str]):
    """变更实例询价(v2) - 支持规格扩容/磁盘扩容/系列升级"""
    from ctmysql.client import RDSClient

    client = ctx.obj['client']
    rds_client = RDSClient(client)

    az_list = None
    if az_name:
        az_list = [{'availabilityZoneName': az_name,
                    'availabilityZoneCount': str(az_count or 1)}]

    result = rds_client.inquiry_upgrade(
        region_id=region_id, project_id=project_id, inst_id=inst_id,
        node_type=node_type, prod_id=prod_id, disk_volume=disk_volume,
        prod_performance_spec=perf_spec, az_list=az_list,
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    desc_parts = [f"实例: {inst_id}"]
    if perf_spec:
        desc_parts.append(f"规格→{perf_spec}")
    if disk_volume:
        desc_parts.append(f"磁盘→{disk_volume}GB")
    if prod_id:
        desc_parts.append(f"产品→{prod_id}")
    _display_price(result, f"变更实例询价  {' '.join(desc_parts)}")


@ctmysql.command('inquiry-renew')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--inst-id', required=True, help='实例ID')
@click.option('--month', required=True, type=int, help='续费月数(1-36)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def inquiry_renew(ctx, region_id: str, inst_id: str, month: int,
                  output: Optional[str]):
    """续费询价"""
    from ctmysql.client import RDSClient

    client = ctx.obj['client']
    rds_client = RDSClient(client)

    result = rds_client.inquiry_renew(
        region_id=region_id, inst_id=inst_id, month=month
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    _display_price(result, f"续费询价  实例: {inst_id}  {month}月")


# ==================== 标签查询 ====================

@ctmysql.command('label-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-ids', required=True, help='实例ID列表，逗号分隔(最多10个)')
@click.option('--tag-filter', default=None, help='标签过滤，格式 key:value，逗号分隔')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def label_list(ctx, region_id: str, instance_ids: str, tag_filter: Optional[str], output: Optional[str]):
    """查询实例标签列表"""
    from ctmysql.client import RDSClient
    result = RDSClient(ctx.obj['client']).list_tag_resources(
        region_id=region_id, outer_prod_inst_id_list=instance_ids, tag_vo_list=tag_filter or '')
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    items = result.get('returnObj', [])
    if isinstance(items, dict):
        items = [items]
    click.echo(f"RDS实例标签 (共 {len(items)} 条)")
    if items:
        table_data = []
        for item in items:
            tags = item.get('tags', [])
            tag_str = ', '.join(f"{t.get('key','')}={t.get('value','')}" for t in tags)
            table_data.append({'实例ID': item.get('outerProdInstId', ''), '标签': tag_str})
        click.echo(OutputFormatter.format_table(table_data))


@ctmysql.command('label-instance')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--instance-id', required=True, help='实例ID')
@click.option('--page-now', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def label_instance(ctx, region_id: str, instance_id: str, page_now: int, page_size: int, output: Optional[str]):
    """获取实例所绑定的标签"""
    from ctmysql.client import RDSClient
    result = RDSClient(ctx.obj['client']).get_instance_labels(
        region_id=region_id, outer_prod_inst_id=instance_id, page_now=page_now, page_size=page_size)
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    ro = result.get('returnObj', {})
    records = ro.get('pageRecords', [])
    click.echo(f"实例 {instance_id} 标签 (共 {ro.get('total', 0)} 个)")
    if records:
        click.echo(OutputFormatter.format_table(records))


@ctmysql.command('label-all')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--page-now', type=int, default=1, show_default=True)
@click.option('--page-size', type=int, default=10, show_default=True)
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def label_all(ctx, region_id: str, page_now: int, page_size: int, output: Optional[str]):
    """获取用户的所有标签"""
    from ctmysql.client import RDSClient
    result = RDSClient(ctx.obj['client']).get_all_labels(
        region_id=region_id, page_now=page_now, page_size=page_size)
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    ro = result.get('returnObj', {})
    records = ro.get('pageRecords', [])
    click.echo(f"用户标签 (共 {ro.get('total', 0)} 个)")
    if records:
        table_data = []
        for r in records:
            values = ', '.join(v.get('value', '') for v in r.get('data', []))
            table_data.append({'Key': r.get('key', ''), 'Values': values})
        click.echo(OutputFormatter.format_table(table_data))
