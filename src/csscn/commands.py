"""服务器安全卫士(原生版)命令行接口"""

import click
from typing import Optional
from utils import OutputFormatter


@click.group()
def csscn():
    """服务器安全卫士(原生版)管理"""
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


# ==================== 查询服务器列表 ====================

@csscn.command('list')
@click.option('--page', type=int, default=1, show_default=True, help='当前页码')
@click.option('--size', type=int, default=10, show_default=True, help='每页大小')
@click.option('--guard-status', type=click.Choice(['1', '4']), default=None,
              help='防护状态: 1=防护中 4=未防护')
@click.option('--agent-state', type=click.Choice(['1', '2']), default=None,
              help='Agent状态: 1=在线 2=离线')
@click.option('--risk-level', type=click.Choice(['1', '2', '3']), default=None,
              help='风险状态: 1=无风险 2=未知 3=风险')
@click.option('--param', default=None, help='查询参数(配合--param-type使用)')
@click.option('--param-type', type=click.Choice(['1', '2', '5', '15']), default=None,
              help='查询类型: 1=实例名称 2=服务器IP 5=agentGuid 15=代理IP')
@click.option('--quota-version', type=click.Choice(['1', '2']), default=None,
              help='配额版本: 1=基础版 2=企业版')
@click.option('--server-status', type=click.Choice(['4', '5', '40']), default=None,
              help='服务器状态: 4=已关机 5=运行中 40=其他')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None,
              help='输出格式')
@click.pass_context
def list_servers(ctx, page: int, size: int,
                 guard_status: Optional[str], agent_state: Optional[str],
                 risk_level: Optional[str], param: Optional[str],
                 param_type: Optional[str], quota_version: Optional[str],
                 server_status: Optional[str], output: Optional[str]):
    """查询服务器列表"""
    from csscn.client import CSSCNClient

    client = ctx.obj['client']
    csscn_client = CSSCNClient(client)

    result = csscn_client.list_servers(
        current_page=page, page_size=size,
        guard_status=int(guard_status) if guard_status else None,
        agent_state=int(agent_state) if agent_state else None,
        risk_level=int(risk_level) if risk_level else None,
        param=param, param_type=int(param_type) if param_type else None,
        quota_version=int(quota_version) if quota_version else None,
        server_status=int(server_status) if server_status else None,
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return

    return_obj = result.get('returnObj', {})
    servers = return_obj.get('list', [])
    total = return_obj.get('total', 0)
    click.echo(f"安全卫士服务器列表 (共 {total} 个，当前 {len(servers)} 个)")
    if servers:
        table_data = []
        for s in servers:
            table_data.append({
                '服务器名称': s.get('displayName', '') or s.get('hostName', ''),
                '内网IP': s.get('agentIp', ''),
                '公网IP': s.get('publicIp', '') or '无',
                '防护状态': s.get('guardStatus', ''),
                'Agent': s.get('agentStateCode', ''),
                '风险': s.get('riskStatus', ''),
                'OS': s.get('osType', ''),
                '漏洞': s.get('vulRisk', 0),
                '区域': s.get('regionName', ''),
            })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 服务器详情 ====================

@csscn.command('describe')
@click.option('--agent-guid', required=True, help='服务器agentGuid')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def server_detail(ctx, agent_guid: str, output: Optional[str]):
    """查询服务器详情"""
    from csscn.client import CSSCNClient
    client = ctx.obj['client']
    result = CSSCNClient(client).server_detail(agent_guid)
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    d = result.get('returnObj', {})
    if not d:
        click.echo("未找到该服务器"); return
    click.echo(f"服务器详情: {d.get('displayName', '') or d.get('hostName', '')}")
    click.echo("=" * 60)
    click.echo(f"  {'agentGuid':<12}: {d.get('agentGuid', '')}")
    click.echo(f"  {'内网IP':<12}: {d.get('ipAddress', '')}")
    click.echo(f"  {'公网IP':<12}: {d.get('publicIp', '') or '无'}")
    click.echo(f"  {'防护状态':<12}: {d.get('guardStatus', '')}")
    click.echo(f"  {'OS':<12}: {d.get('osNameVersion', '') or d.get('osType', '')}")
    click.echo(f"  {'Agent版本':<12}: {d.get('agentVersion', '')}")
    click.echo(f"  {'区域':<12}: {d.get('regionName', '')}")
    click.echo(f"  {'VPC':<12}: {d.get('vpcName', '')}")
    click.echo(f"  {'业务分组':<12}: {d.get('bgGroupName', '') or '无'}")
    click.echo(f"  {'创建时间':<12}: {d.get('createDate', '')}")
    click.echo(f"  {'到期时间':<12}: {d.get('expireDate', '')}")
    click.echo(f"  {'CPU':<12}: {d.get('cpuInfoList', [{}])[0].get('cpuName', '') if d.get('cpuInfoList') else ''}")
    click.echo(f"  {'内存(MB)':<12}: {d.get('memTotal', '')}")
    click.echo(f"  {'系统负载':<12}: {d.get('systemLoad', '')}")
    click.echo(f"  {'使用率':<12}: {d.get('usageRate', '')}")


# ==================== 待处理风险统计 ====================

@csscn.command('risk-stats')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def risk_stats(ctx, output: Optional[str]):
    """查询待处理风险统计数据"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).untreated_risk_stats()
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    d = result.get('returnObj', {})
    click.echo("待处理风险统计")
    click.echo("=" * 50)
    rows = [
        ('漏洞', d.get('vulRiskNum', 0), d.get('vulHostNum', 0)),
        ('软件合规(SCA)', d.get('scaRiskNum', 0), d.get('scaHostNum', 0)),
        ('网页防篡改', d.get('wpRiskNum', 0), d.get('wpHostNum', 0)),
        ('病毒', d.get('virusRiskNum', 0), d.get('virusHostNum', 0)),
        ('入侵事件', d.get('instrustonEventRiskNum', 0), d.get('instrustonEventRiskHostNum', 0)),
    ]
    table_data = [{'风险类型': r[0], '风险数': r[1], '影响主机数': r[2]} for r in rows]
    click.echo(OutputFormatter.format_table(table_data))


# ==================== 服务器统计 ====================

@csscn.command('server-stats')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def server_stats(ctx, output: Optional[str]):
    """查询服务器统计数据"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).server_total_stats()
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    d = result.get('returnObj', {})
    click.echo("服务器统计")
    click.echo("=" * 50)
    click.echo(f"  {'服务器总数':<14}: {d.get('totalServerCount', 0)}")
    click.echo(f"  {'有风险主机':<14}: {d.get('riskServerCount', 0)}")
    click.echo(f"  {'未防护主机':<14}: {d.get('unGuardServerCount', 0)}")
    click.echo(f"  {'在线Agent':<14}: {d.get('activeAgent', 0)}")
    click.echo(f"  {'离线Agent':<14}: {d.get('offlineAgent', 0)}")
    click.echo(f"  {'基础版配额':<14}: {d.get('freeQuotaCount', 0)}")
    click.echo(f"  {'企业版配额':<14}: {d.get('enterpriseQuotaCount', 0)}")
    click.echo(f"  {'旗舰版配额':<14}: {d.get('flagShipQuotaCount', 0)}")


# ==================== Agent防护状态统计 ====================

@csscn.command('agent-stats')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def agent_stats(ctx, output: Optional[str]):
    """查询Agent防护状态统计数据"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).agent_guard_stats()
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    d = result.get('returnObj', {})
    click.echo("Agent防护状态统计")
    click.echo("=" * 50)
    click.echo(f"  {'总数':<14}: {d.get('total', 0)}")
    click.echo(f"  {'已防护':<14}: {d.get('guard', 0)}")
    click.echo(f"  {'未防护':<14}: {d.get('unGuard', 0)}")
    click.echo(f"  {'离线':<14}: {d.get('offLine', 0)}")
    click.echo(f"  {'已关闭防护':<14}: {d.get('closedGuard', 0)}")
    click.echo(f"  {'基础版防护':<14}: {d.get('baseGuard', 0)}")
    click.echo(f"  {'企业版防护':<14}: {d.get('enterpriseGuard', 0)}")


# ==================== Agent状态分布 ====================

@csscn.command('agent-distribution')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def agent_distribution(ctx, output: Optional[str]):
    """查询Agent在线/离线状态分布"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).agent_status_distribution()
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    items = result.get('returnObj', [])
    if isinstance(items, dict):
        items = [{'name': k, 'count': v} for k, v in items.items()]
    click.echo("Agent状态分布")
    if items:
        table_data = [{'状态': i.get('name', ''), '数量': i.get('count', 0)} for i in items]
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 漏洞统计 ====================

@csscn.command('vuln-stats')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def vuln_stats(ctx, output: Optional[str]):
    """查询漏洞统计数据"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).vulnerability_stats()
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    d = result.get('returnObj', {})
    click.echo("漏洞统计")
    click.echo("=" * 50)
    click.echo(f"  {'紧急漏洞':<14}: {d.get('emergentVul', 0)}")
    click.echo(f"  {'未处理漏洞':<14}: {d.get('unHandle', 0)}")
    click.echo(f"  {'受影响主机':<14}: {d.get('hostNum', 0)}")


# ==================== 告警列表 ====================

@csscn.command('alarms')
@click.option('--time-type', required=True,
              type=click.Choice(['LAST_ONE_DAY', 'LAST_THREE_DAY', 'LAST_ONE_WEEK',
                                 'LAST_ONE_MONTH', 'LAST_THREE_MONTH', 'SELF_TIME']),
              help='时间范围')
@click.option('--page', type=int, default=1, show_default=True)
@click.option('--size', type=int, default=10, show_default=True)
@click.option('--severity', type=click.Choice(['1', '2', '3']), default=None,
              help='威胁等级: 1=提醒 2=可疑 3=紧急')
@click.option('--status', type=click.Choice(['0', '2', '3', '6', '7', '8', '10']), default=None,
              help='状态: 0=未处理 2=已加白 3=已隔离 6=已拦截 7=已忽略 10=已恢复')
@click.option('--alarm-type', default=None,
              help='告警类型: 1=进程异常 2=恶意软件 3=用户异常 4=恶意网络 5=其他')
@click.option('--keyword', default=None, help='模糊查询参数')
@click.option('--keyword-type', type=click.Choice(['1', '2', '5', '9']), default=None,
              help='模糊类型: 1=服务器名 2=服务器IP 5=guid 9=告警名')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def alarms(ctx, time_type: str, page: int, size: int,
           severity: Optional[str], status: Optional[str],
           alarm_type: Optional[str], keyword: Optional[str],
           keyword_type: Optional[str], output: Optional[str]):
    """查询告警中心告警列表"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).alarm_list(
        time_type=time_type, current_page=page, page_size=size,
        severity_code=int(severity) if severity else None,
        status=int(status) if status else None,
        alarm_type=alarm_type, like_query_param=keyword,
        like_query_type=int(keyword_type) if keyword_type else None,
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    ro = result.get('returnObj', {})
    items = ro.get('list', [])
    click.echo(f"告警列表 (共 {ro.get('total', 0)} 条，已处理 {ro.get('handleTotal', 0)} 未处理 {ro.get('unHandleTotal', 0)})")
    if items:
        sev_map = {1: '提醒', 2: '可疑', 3: '紧急'}
        status_map = {0: '未处理', 2: '已加白', 3: '已隔离', 6: '已拦截', 7: '已忽略', 8: '已删除', 10: '已恢复', 99: '处理中'}
        table_data = []
        for a in items:
            table_data.append({
                '告警名称': a.get('alarmName', '')[:25],
                '服务器': a.get('hostName', '')[:18],
                '服务器IP': a.get('serverIp', ''),
                '威胁等级': sev_map.get(a.get('severityCode'), str(a.get('severityCode', ''))),
                '状态': status_map.get(a.get('status'), str(a.get('status', ''))),
                '告警类型': a.get('alarmTypeName', ''),
                '时间': str(a.get('alarmTime', ''))[:19],
            })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 病毒事件列表 ====================

@csscn.command('viruses')
@click.option('--os-type', required=True, type=click.Choice(['1', '2', '3']),
              help='OS类型: 1=linux 2=windows 3=全部')
@click.option('--time-type', required=True,
              type=click.Choice(['LAST_ONE_DAY', 'LAST_THREE_DAY', 'LAST_ONE_WEEK',
                                 'LAST_ONE_MONTH', 'LAST_THREE_MONTH', 'SELF_TIME']),
              help='时间范围')
@click.option('--page', type=int, default=1, show_default=True)
@click.option('--size', type=int, default=10, show_default=True)
@click.option('--status', type=click.Choice(['0', '1', '2', '3', '7', '99']), default=None,
              help='状态: 0=未处理 1=已隔离 2=已加白 3=已删除 7=已忽略 99=处理中')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def viruses(ctx, os_type: str, time_type: str, page: int, size: int,
            status: Optional[str], output: Optional[str]):
    """查询病毒事件列表"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).virus_list(
        os_type=int(os_type), time_type=time_type,
        current_page=page, page_size=size,
        status=int(status) if status else None,
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    ro = result.get('returnObj', {})
    items = ro.get('list', [])
    click.echo(f"病毒事件列表 (共 {ro.get('total', 0)} 个)")
    if items:
        status_map = {0: '未处理', 1: '已隔离', 2: '已加白', 3: '已删除', 7: '已忽略', 99: '处理中'}
        table_data = []
        for v in items:
            table_data.append({
                '文件名': v.get('fileName', '')[:25],
                '服务器': v.get('hostName', '')[:18],
                '文件路径': v.get('filePath', '')[:30],
                '状态': status_map.get(v.get('status'), str(v.get('status', ''))),
                'MD5': str(v.get('fileMd5', ''))[:16],
                '时间': str(v.get('createTime', ''))[:19],
            })
        click.echo(OutputFormatter.format_table(table_data))


# ==================== 配额列表 ====================

@csscn.command('quotas')
@click.option('--page', type=int, default=1, show_default=True)
@click.option('--size', type=int, default=10, show_default=True)
@click.option('--version', type=click.Choice(['1', '2', '3']), default=None,
              help='配额版本: 1=基础版 2=企业版 3=旗舰版')
@click.option('--status', type=click.Choice(['1', '2', '3', '4', '8', '16', '32', '0']), default=None,
              help='状态: 1=未绑定 2=绑定中 3=正常 4=已过期 8=已冻结 16=已退订 32=已销毁')
@click.option('--server-ip', default=None, help='服务器IP')
@click.option('--name', default=None, help='服务器名称(模糊)')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), default=None)
@click.pass_context
def quotas(ctx, page: int, size: int, version: Optional[str], status: Optional[str],
           server_ip: Optional[str], name: Optional[str], output: Optional[str]):
    """查询配额列表"""
    from csscn.client import CSSCNClient
    result = CSSCNClient(ctx.obj['client']).quota_list(
        current_num=page, page_size=size,
        quota_version=int(version) if version else None,
        quota_status=int(status) if status else None,
        server_ip=server_ip, cust_name=name,
    )
    fmt = _output(ctx, result, output)
    if fmt != 'table':
        return
    ro = result.get('returnObj', {})
    items = ro.get('list', [])
    ver_map = {1: '基础版', 2: '企业版', 3: '旗舰版'}
    status_map = {1: '未绑定', 2: '绑定中', 3: '正常', 4: '已过期', 8: '已冻结', 16: '已退订', 32: '已销毁', 0: '无效'}
    click.echo(f"配额列表 (共 {ro.get('total', 0)} 个)")
    if items:
        table_data = []
        for q in items:
            table_data.append({
                '配额ID': str(q.get('quotaId', ''))[:20],
                '版本': ver_map.get(q.get('quotaVersion'), str(q.get('quotaVersion', ''))),
                '状态': status_map.get(q.get('quotaStatus'), str(q.get('quotaStatus', ''))),
                '服务器': q.get('custName', '')[:18],
                '服务器IP': q.get('serverIp', ''),
                '到期': str(q.get('expireTime', ''))[:10],
            })
        click.echo(OutputFormatter.format_table(table_data))
