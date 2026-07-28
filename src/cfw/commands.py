"""云防火墙（原生版）命令"""

import json
import click
from .client import CFWClient


def _echo(result):
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


@click.group()
def cfw():
    """云防火墙（原生版）管理"""
    pass


@cfw.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', help='防火墙ID')
@click.option('--firewall-name', help='防火墙名称')
@click.option('--firewall-type', help='防火墙类型: NorthSouth/EastWest')
@click.option('--firewall-state', help='状态: normal/overdue/unsubscribe/processing')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def list_firewalls(ctx, region_id, firewall_id, firewall_name, firewall_type,
                   firewall_state, page, size):
    """查询防火墙的简要信息"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.firewall_simple_query(
        region_id, firewall_id=firewall_id, firewall_name=firewall_name,
        firewall_type=firewall_type, firewall_state=firewall_state,
        page=page, size=size))


@cfw.command('region-maximums')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def region_maximums(ctx, region_id):
    """查询资源池规格"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_region_maximums(region_id))


@cfw.command('can-buy')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def can_buy(ctx, region_id):
    """查询能否订购防火墙"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.can_buy_firewall(region_id))


@cfw.command('show')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--firewall-type', help='防火墙类型: NorthSouth/EastWest')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def show_firewall(ctx, region_id, firewall_id, firewall_type, page, size):
    """查询防火墙详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.firewall_query(region_id, firewall_id,
                                firewall_type=firewall_type, page=page, size=size))


@cfw.command('overview')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def overview(ctx, region_id):
    """实例状态概览"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.firewall_overview(region_id))


@cfw.command('protection-overview')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--type', 'time_type', required=True,
              type=click.Choice(['day1', 'day3', 'day7']), help='时间范围')
@click.option('--firewall-id', help='防火墙ID')
@click.option('--firewall-type', help='防火墙类型: NorthSouth/EastWest')
@click.pass_context
def protection_overview(ctx, region_id, time_type, firewall_id, firewall_type):
    """安全防护概览"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.protection_statistics(region_id, time_type,
                                       firewall_id=firewall_id,
                                       firewall_type=firewall_type))


@cfw.command('asset-overview')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def asset_overview(ctx, region_id):
    """资产防护监控概览"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.asset_protection_overview(region_id))


@cfw.command('acl-overview')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', help='防火墙ID')
@click.option('--firewall-type', help='防火墙类型: NorthSouth/EastWest')
@click.pass_context
def acl_overview(ctx, region_id, firewall_id, firewall_type):
    """访问控制策略概览"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.ac_policy_overview(region_id, firewall_id=firewall_id,
                                    firewall_type=firewall_type))


@cfw.command('can-downgrade')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--master-resource-id', required=True, help='主资源ID')
@click.pass_context
def can_downgrade(ctx, region_id, master_resource_id):
    """查询能否降低版本"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.can_downgrade(region_id, master_resource_id))


@cfw.command('min-quota')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def min_quota(ctx, region_id):
    """查询降配配额最低值"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.min_quota(region_id))


@cfw.command('judge-upgrade')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--flow-capacity', required=True, type=int, help='公网流量处理能力(Mbps)')
@click.option('--protection-ip-num', required=True, type=int, help='可防护公网IP数')
@click.option('--uid', required=True, help='租户ID')
@click.option('--user-id', required=True, help='用户ID')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.pass_context
def judge_upgrade(ctx, region_id, flow_capacity, protection_ip_num, uid, user_id, vpc_id):
    """判断防护能力是否升级"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.judge_ability_upgrade(region_id, flow_capacity,
                                       protection_ip_num, uid, user_id, vpc_id))


@cfw.command('check-cidr')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--cidr', required=True, help='CIDR，如192.168.1.0/24')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.pass_context
def check_cidr(ctx, region_id, cidr, vpc_id):
    """校验CIDR合法性"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.check_cidr(region_id, cidr, vpc_id))


@cfw.command('random-name')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def random_name(ctx, region_id):
    """生成防火墙随机名称"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.random_firewall_name(region_id))


@cfw.command('vpc-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def vpc_list(ctx, region_id):
    """获取用户的VPC列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.firewall_vpc_list(region_id))


@cfw.command('subnet-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--traffic-subnet/--no-traffic-subnet', default=True, help='是否查询业务子网')
@click.option('--filter-not-valid', is_flag=True, default=None, help='过滤无效子网')
@click.pass_context
def subnet_list(ctx, region_id, vpc_id, traffic_subnet, filter_not_valid):
    """获取VPC的子网列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.firewall_subnet_list(region_id, vpc_id,
                                      traffic_subnet=traffic_subnet,
                                      filter_not_valid=filter_not_valid))


@cfw.group()
def asset():
    """资产管理"""
    pass


@asset.command('all')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def asset_all(ctx, region_id):
    """查询所有东西向资产"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.asset_all(region_id))


@asset.command('statistics')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', help='防火墙ID')
@click.option('--firewall-type', help='防火墙类型: NorthSouth/EastWest')
@click.pass_context
def asset_statistics(ctx, region_id, firewall_id, firewall_type):
    """查询资产统计"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.vrf_bind_statistics(region_id, firewall_id=firewall_id,
                                     firewall_type=firewall_type))


@asset.command('nat-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--nat-name', help='NAT名称')
@click.option('--protect-status', type=bool, help='防护状态')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def asset_nat_list(ctx, region_id, nat_name, protect_status, page, size):
    """查看NAT列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.assert_nat_query(region_id, nat_name=nat_name,
                                  protect_status=protect_status,
                                  page=page, size=size))


@asset.command('cda-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def asset_cda_list(ctx, region_id):
    """查询云专线列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.assert_cda_query(region_id))


@asset.command('ec-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def asset_ec_list(ctx, region_id):
    """查询云间高速列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.assert_express_connect_query(region_id))


@asset.command('vpc-peer-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def asset_vpc_peer_list(ctx, region_id):
    """查询对等连接列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.assert_vpc_peer_query(region_id))


@asset.command('protect-check')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--vpc-id', required=True, help='VPC ID')
@click.option('--scenario-type', required=True,
              type=click.Choice(['nat', 'vpcPeer', 'cda', 'ec']), help='场景类型')
@click.option('--scenario-id', required=True, help='场景ID')
@click.pass_context
def asset_protect_check(ctx, region_id, vpc_id, scenario_type, scenario_id):
    """开启防护自动检查"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.assert_protect_check(region_id, vpc_id, scenario_type, scenario_id))


@asset.command('vpc-statistics')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def asset_vpc_statistics(ctx, region_id):
    """VPC边界统计"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.assert_statistics(region_id))


@asset.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', help='防火墙ID')
@click.option('--eip', help='EIP地址')
@click.option('--eip-id', help='EIP ID')
@click.option('--eip-name', help='EIP名称')
@click.option('--attached-type', help='绑定设备类型，如INSTANCE')
@click.option('--ip-type', help='IP类型: ipv4/ipv6')
@click.option('--protect-status', type=bool, help='防护状态')
@click.option('--subnet-id', help='子网ID')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def asset_list(ctx, region_id, firewall_id, eip, eip_id, eip_name, attached_type,
               ip_type, protect_status, subnet_id, page, size):
    """查询资产（EIP绑定）"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.vrf_bind_query(region_id, firewall_id=firewall_id, eip=eip,
                                eip_id=eip_id, eip_name=eip_name,
                                attached_type=attached_type, ip_type=ip_type,
                                protect_status=protect_status,
                                subnet_id=subnet_id, page=page, size=size))


@asset.command('info')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--eip-id', required=True, help='EIP ID')
@click.option('--uid', required=True, help='租户ID')
@click.pass_context
def asset_info(ctx, region_id, eip_id, uid):
    """获取资产详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.vrf_bind_info(region_id, eip_id, uid))


@asset.command('sync-status')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--type', 'sync_type', default='eip', help='资产同步类型，默认eip')
@click.pass_context
def asset_sync_status(ctx, region_id, sync_type):
    """获取资产同步状态"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.vrf_bind_sync_status(region_id, sync_type))


@asset.command('sync-time')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--type', 'sync_type', default='eip', help='资产同步类型，默认eip')
@click.pass_context
def asset_sync_time(ctx, region_id, sync_type):
    """获取资产同步时间"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.vrf_bind_sync_time(region_id, sync_type))


@cfw.group()
def policy():
    """防护规则（访问控制）管理"""
    pass


@policy.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', help='防火墙ID（与类型二选一）')
@click.option('--firewall-type', help='防火墙类型: NorthSouth/EastWest（与ID二选一）')
@click.option('--action', help='动作: drop/pass')
@click.option('--direction', help='方向: in/out')
@click.option('--src-ip', help='源IP')
@click.option('--dst-ip', help='目的IP')
@click.option('--ip-proto', help='IP协议: v4/v6')
@click.option('--service', help='服务类型: any/icmp/tcp/udp')
@click.option('--status', help='规则开关: disable/enable')
@click.option('--rule-name', help='规则名称')
@click.option('--address-group', help='地址簿名称')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def policy_list(ctx, region_id, firewall_id, firewall_type, action, direction,
                src_ip, dst_ip, ip_proto, service, status, rule_name,
                address_group, page, size):
    """查询防护规则"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.sec_policy_query(region_id, firewall_id=firewall_id,
                                  firewall_type=firewall_type, action=action,
                                  direction=direction, src_ip=src_ip, dst_ip=dst_ip,
                                  ip_proto=ip_proto, service=service, status=status,
                                  rule_name=rule_name, address_group=address_group,
                                  page=page, size=size))


@policy.command('show')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--rule-id', required=True, type=int, help='规则ID')
@click.pass_context
def policy_show(ctx, region_id, firewall_id, rule_id):
    """查询防护规则详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.sec_policy_info(region_id, firewall_id, rule_id))


@policy.command('statistics')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.pass_context
def policy_statistics(ctx, region_id, firewall_id):
    """获取防护规则统计数据"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.sec_policy_statistics(region_id, firewall_id))


@policy.command('export-template')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', default='sec_policy_template.xlsx', help='保存文件路径')
@click.pass_context
def policy_export_template(ctx, region_id, output):
    """获取访问规则的excel文件模板"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.sec_policy_export_module(region_id, output=output))


@cfw.group('blackwhite')
def blackwhite():
    """黑白名单管理"""
    pass


@blackwhite.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--type', 'bw_type', required=True,
              type=click.Choice(['BLACK', 'WHITE']), help='黑白类型')
@click.option('--address-direction', help='地址方向: src/dst')
@click.option('--ip', help='IP地址')
@click.option('--ip-proto', help='IP协议: v4/v6')
@click.option('--rule-id', type=int, help='规则ID')
@click.option('--rule-name', help='规则名称')
@click.option('--address-group', help='地址簿名称')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def blackwhite_list(ctx, region_id, firewall_id, bw_type, address_direction, ip,
                    ip_proto, rule_id, rule_name, address_group, page, size):
    """查询黑白名单"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.black_white_policy_query(region_id, firewall_id, bw_type,
                                          address_direction=address_direction,
                                          ip=ip, ip_proto=ip_proto, rule_id=rule_id,
                                          rule_name=rule_name,
                                          address_group=address_group,
                                          page=page, size=size))


@blackwhite.command('show')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--type', 'bw_type', required=True,
              type=click.Choice(['black', 'white']), help='黑白类型')
@click.option('--rule-id', required=True, type=int, help='规则ID')
@click.option('--uid', required=True, help='租户ID')
@click.pass_context
def blackwhite_show(ctx, region_id, firewall_id, bw_type, rule_id, uid):
    """查询黑白名单详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.black_white_policy_info(region_id, firewall_id, bw_type, rule_id, uid))


@blackwhite.command('export-template')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--output', default='black_white_template.xlsx', help='保存文件路径')
@click.pass_context
def blackwhite_export_template(ctx, region_id, output):
    """获取黑白名单规则的excel文件模板"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.black_white_policy_export_module(region_id, output=output))


@cfw.group('address-book')
def address_book():
    """地址簿管理"""
    pass


@address_book.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--ip', help='IP地址')
@click.option('--address-type', help='地址簿类型: v4/v6/port')
@click.option('--name', 'address_group_name', help='地址簿名称')
@click.option('--group-id', type=int, help='地址簿ID')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def address_book_list(ctx, region_id, ip, address_type, address_group_name,
                      group_id, page, size):
    """查询地址簿"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.address_group_query(region_id, ip=ip, address_type=address_type,
                                     address_group_name=address_group_name,
                                     group_id=group_id, page=page, size=size))


@address_book.command('items')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--group-id', required=True, type=int, help='地址簿ID')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def address_book_items(ctx, region_id, group_id, page, size):
    """地址簿详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.address_group_items(region_id, group_id, page=page, size=size))


@address_book.command('statistics')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def address_book_statistics(ctx, region_id):
    """统计地址簿"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.address_group_statistic(region_id))


@cfw.group()
def ips():
    """入侵防御（IPS）管理"""
    pass


@ips.command('rules')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--method', help='攻击类型')
@click.option('--target', help='攻击对象')
@click.option('--type', 'query_type', help='类型: method-攻击类型 target-攻击对象')
@click.option('--rule-id', type=int, help='规则ID')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='每页条数')
@click.pass_context
def ips_rules(ctx, region_id, firewall_id, method, target, query_type, rule_id, page, size):
    """查询IPS规则"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.ips_rule_query(region_id, firewall_id, method=method,
                                target=target, type=query_type, rule_id=rule_id,
                                page=page, size=size))


@ips.command('attack-types')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def ips_attack_types(ctx, region_id):
    """查询攻击类型"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.ips_rule_query_all(region_id))


@ips.command('rule-types')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def ips_rule_types(ctx, region_id):
    """获取IPS规则类型列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.ips_rule_type(region_id))


@ips.command('dpi-info')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.pass_context
def ips_dpi_info(ctx, region_id, firewall_id):
    """查询DPI详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.dpi_info(region_id, firewall_id))


@cfw.group()
def app():
    """应用管理"""
    pass


@app.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def app_list(ctx, region_id):
    """查询全部应用"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.app_query_all(region_id))


@app.command('categories')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def app_categories(ctx, region_id):
    """查询应用大类和子类"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.app_query_with_parent(region_id))


@cfw.group()
def alarm():
    """告警管理"""
    pass


@alarm.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--start-time', required=True, help='开始时间, 如 2024-10-23T08:31:25Z')
@click.option('--finish-time', required=True, help='结束时间, 如 2024-10-23T08:31:25Z')
@click.option('--firewall-id', help='防火墙ID（与--firewall-type二选一）')
@click.option('--firewall-type', help='防火墙类型 NorthSouth/EastWest')
@click.option('--attack-ip', help='攻击IP')
@click.option('--affected-ip', help='受影响IP')
@click.option('--page-num', type=int, help='页码')
@click.option('--page-size', type=int, help='页大小')
@click.pass_context
def alarm_list(ctx, region_id, start_time, finish_time, firewall_id,
               firewall_type, attack_ip, affected_ip, page_num, page_size):
    """查询告警列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.alarm_query(region_id, start_time, finish_time,
                             firewall_id=firewall_id, firewall_type=firewall_type,
                             attack_ip=attack_ip, affected_ip=affected_ip,
                             page_num=page_num, page_size=page_size))


@alarm.command('show')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--alarm-id', required=True, help='告警ID')
@click.pass_context
def alarm_show(ctx, region_id, alarm_id):
    """告警详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.alarm_detail(region_id, alarm_id))


@alarm.command('statistics')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--finish-time', required=True, help='结束时间')
@click.pass_context
def alarm_statistics(ctx, region_id, firewall_id, start_time, finish_time):
    """告警统计"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.alarm_statics(region_id, firewall_id, start_time, finish_time))


@cfw.group()
def log():
    """日志管理"""
    pass


@log.command('flow-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--start-time', required=True, help='开始时间, 如 2024-10-23T08:31:25Z')
@click.option('--finish-time', required=True, help='结束时间')
@click.option('--attack-direction', default='3', help='方向 1出向 2入向 3全方向')
@click.option('--source-ip', help='来源IP')
@click.option('--target-ip', help='目标IP')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='页大小')
@click.pass_context
def log_flow_list(ctx, region_id, firewall_id, start_time, finish_time,
                  attack_direction, source_ip, target_ip, page, size):
    """流量日志列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.alarm_log_list(region_id, firewall_id, start_time, finish_time,
                                attack_direction=attack_direction,
                                source_ip=source_ip, target_ip=target_ip,
                                page=page, size=size))


@log.command('flow-trend')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-type', required=True, help='防火墙类型 NorthSouth/EastWest')
@click.option('--type', 'time_type', required=True, help='时间范围 day1/day7')
@click.option('--begin-time', required=True, type=int, help='开始时间(秒级时间戳)')
@click.option('--end-time', required=True, type=int, help='结束时间(秒级时间戳)')
@click.pass_context
def log_flow_trend(ctx, region_id, firewall_type, time_type, begin_time, end_time):
    """查询防火墙流量日志（趋势）"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.flow_log_query(region_id, firewall_type, time_type,
                                begin_time, end_time))


@log.command('operation')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--begin-time', required=True, type=int, help='开始时间(秒级时间戳)')
@click.option('--end-time', required=True, type=int, help='结束时间(秒级时间戳)')
@click.option('--action', help='操作行为, 如 TURN_ON_FIREWALL')
@click.option('--content', help='日志内容关键字')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='页大小')
@click.pass_context
def log_operation(ctx, region_id, firewall_id, begin_time, end_time,
                  action, content, page, size):
    """查询操作日志"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.operation_log_query(region_id, firewall_id, begin_time, end_time,
                                     action=action, content=content,
                                     page=page, size=size))


@log.command('storage')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.pass_context
def log_storage(ctx, region_id, firewall_id):
    """查看日志存储容量"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.log_save_statistics(region_id, firewall_id))


@log.command('setting')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.pass_context
def log_setting(ctx, region_id, firewall_id):
    """查询日志配置详情"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.log_setting_info(region_id, firewall_id))


@log.command('deliver-list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.pass_context
def log_deliver_list(ctx, region_id, firewall_id):
    """查看日志投递列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.log_query_deliver_list(region_id, firewall_id))


@log.command('deliver-info')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.pass_context
def log_deliver_info(ctx, region_id, firewall_id):
    """查询日志投递类型信息"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.log_query_deliver_info(region_id, firewall_id))


@log.command('deliver-time')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--save-types', required=True, help='存储类型,逗号分隔: AC,IPS,FLOW,AV')
@click.pass_context
def log_deliver_time(ctx, region_id, firewall_id, save_types):
    """查询日志投递开始时间"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.log_query_deliver_time(region_id, firewall_id,
                                        save_types.split(',')))


@log.command('raw')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--log-type', required=True, help='日志类型 FLOW/IPS/AC/AV')
@click.option('--start-time', required=True, help='开始时间, 如 2024/11/14 10:37:34')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--page', type=int, default=1, help='页码')
@click.option('--size', type=int, default=10, help='页大小')
@click.pass_context
def log_raw(ctx, region_id, firewall_id, log_type, start_time, end_time, page, size):
    """查询日志内容"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.get_raw_log(region_id, firewall_id, log_type,
                             start_time, end_time, page=page, size=size))


@log.command('count')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--log-type', required=True, help='日志类型 FLOW/IPS/AC/AV')
@click.option('--start-time', required=True, help='开始时间, 如 2024/11/14 10:37:34')
@click.option('--end-time', required=True, help='结束时间')
@click.pass_context
def log_count(ctx, region_id, firewall_id, log_type, start_time, end_time):
    """统计日志数量"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.get_log_count(region_id, firewall_id, log_type,
                               start_time, end_time))


@cfw.group()
def report():
    """报表管理"""
    pass


@report.command('list')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--start-time', required=True, help='开始时间, 如 2024-09-25T05:36:13Z')
@click.option('--end-time', required=True, help='结束时间')
@click.option('--report-type', required=True, help='报表类型 DAY/WEEK/MONTH')
@click.option('--selected-time', help='选择时间')
@click.option('--page', type=int, help='页码')
@click.option('--size', type=int, help='条数')
@click.pass_context
def report_list(ctx, region_id, firewall_id, start_time, end_time,
                report_type, selected_time, page, size):
    """报表列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.report_list(region_id, firewall_id, start_time, end_time,
                             report_type, selected_time=selected_time,
                             page=page, size=size))


@report.command('statistics')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--start-time', required=True, help='开始时间')
@click.option('--end-time', required=True, help='结束时间')
@click.pass_context
def report_statistics(ctx, region_id, firewall_id, start_time, end_time):
    """报表统计"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.report_statistics(region_id, firewall_id, start_time, end_time))


@report.command('subscribe')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def report_subscribe(ctx, region_id):
    """订阅列表"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.report_subscribe(region_id))


@cfw.command('notification')
@click.option('--region-id', required=True, help='资源池ID')
@click.pass_context
def cfw_notification(ctx, region_id):
    """获取通知设置"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.notification(region_id))


@cfw.group()
def price():
    """询价"""
    pass


@price.command('new')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--cycle-cnt', required=True, type=int, help='订购时长')
@click.option('--cycle-type', required=True, help='订购周期类型 MONTH/YEAR')
@click.option('--spec', required=True, help='版本 Advanced/Enterprise')
@click.option('--protection-ip-num', required=True, type=int, help='可防护公网IP数')
@click.option('--flow-processing-capacity', required=True, type=int, help='公网流量处理能力(Mbps)')
@click.option('--vpc-quota', type=int, help='VPC边界防火墙配额数(企业版必填)')
@click.option('--vpc-flow-processing-capacity', type=int, help='VPC边界流量处理能力(企业版必填)')
@click.pass_context
def price_new(ctx, region_id, cycle_cnt, cycle_type, spec, protection_ip_num,
              flow_processing_capacity, vpc_quota, vpc_flow_processing_capacity):
    """查询新购订单价格(C100型)"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_order_price(region_id, cycle_cnt, cycle_type, spec,
                                   protection_ip_num, flow_processing_capacity,
                                   vpc_quota=vpc_quota,
                                   vpc_flow_processing_capacity=vpc_flow_processing_capacity))


@price.command('renew')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--cycle-cnt', required=True, type=int, help='订购时长')
@click.option('--cycle-type', required=True, help='订购周期类型 MONTH/YEAR')
@click.pass_context
def price_renew(ctx, region_id, firewall_id, cycle_cnt, cycle_type):
    """查询续订订单价格(C100型)"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_renew_price(region_id, firewall_id, cycle_cnt, cycle_type))


@price.command('upgrade')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--firewall-id', required=True, help='防火墙ID')
@click.option('--upgrade-type', required=True,
              help='升级类型 spec/protectionIpNum/flowProcessingCapacity/vpcQuota/vpcFlowProcessingCapacity')
@click.option('--spec', help='版本 Advanced/Enterprise (upgradeType=spec时必填)')
@click.option('--upgrade-value', help='升级规格 (upgradeType非spec时必填)')
@click.pass_context
def price_upgrade(ctx, region_id, firewall_id, upgrade_type, spec, upgrade_value):
    """查询升配订单价格(C100型)"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_upgrade_price(region_id, firewall_id, upgrade_type,
                                     spec=spec, upgrade_value=upgrade_value))


@price.command('new-n100')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--orders-json', required=True, help='新购订单询价参数orders数组(JSON字符串)')
@click.pass_context
def price_new_n100(ctx, region_id, orders_json):
    """查询新购订单价格(N100型)"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_new_purchase_price_n100(region_id, json.loads(orders_json)))


@price.command('renew-n100')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--resource-ids', required=True, help='资源ID,逗号分隔')
@click.option('--cycle-cnt', required=True, type=int, help='续订周期数')
@click.option('--cycle-type', required=True, type=int, help='周期类型 3月 5年 6两年 7三年 8四年 9五年')
@click.pass_context
def price_renew_n100(ctx, region_id, resource_ids, cycle_cnt, cycle_type):
    """查询续订订单价格(N100型)"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_renew_price_n100(region_id, resource_ids.split(','),
                                        cycle_cnt, cycle_type))


@price.command('upgrade-n100')
@click.option('--region-id', required=True, help='资源池ID')
@click.option('--resource-id', required=True, help='云防火墙资源ID')
@click.option('--ismain', required=True, help='部署方式 single/dual')
@click.option('--firewall-edition', required=True, help='版本 standard/advanced/ultimated')
@click.pass_context
def price_upgrade_n100(ctx, region_id, resource_id, ismain, firewall_edition):
    """查询升配订单价格(N100型)"""
    client = CFWClient(ctx.obj['client'])
    _echo(client.query_upgrade_price_n100(region_id, resource_id, ismain,
                                          firewall_edition))
