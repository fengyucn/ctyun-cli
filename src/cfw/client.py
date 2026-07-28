"""云防火墙（原生版）客户端"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class CFWClient:
    """天翼云云防火墙（原生版）客户端

    终端节点: ctcfw-global.ctapi.ctyun.cn
    URI前缀: /vfw/
    请求头: regionId + urlType=CTAPI
    成功statusCode: "800" (字符串), error=CFW_0000
    """

    # API分散发布在两个节点上，404时自动切换另一节点重试
    ENDPOINTS = ['ctcfw-global.ctapi.ctyun.cn', 'ctcfw-east-a.ctapi.ctyun.cn']

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def _headers(self, region_id: str) -> Dict[str, str]:
        return {'regionId': region_id, 'urlType': 'CTAPI'}

    def _request(self, method: str, path: str, region_id: str,
                 query_params: Optional[Dict[str, Any]] = None,
                 body: Optional[Dict[str, Any]] = None,
                 desc: str = 'CFW查询',
                 extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        qp = {k: v for k, v in (query_params or {}).items() if v is not None}
        bd = {k: v for k, v in (body or {}).items() if v is not None}
        body_str = json.dumps(bd) if method == 'POST' else ''
        req_headers = self._headers(region_id)
        if extra_headers:
            req_headers.update({k: str(v) for k, v in extra_headers.items() if v is not None})
        last = None
        for endpoint in self.ENDPOINTS:
            url = f'https://{endpoint}{path}'
            try:
                headers = self.eop_auth.sign_request(
                    method=method, url=url, query_params=qp, body=body_str,
                    extra_headers=req_headers)
                logger.debug(f"{method} {url} | 参数: {qp} | body: {bd}")
                if method == 'GET':
                    response = self.client.session.get(url, params=qp, headers=headers, timeout=self.timeout)
                else:
                    response = self.client.session.post(url, json=bd, headers=headers, timeout=self.timeout)
                if response.status_code == 404:
                    last = {'statusCode': 404,
                            'message': f'HTTP 404: {response.text}',
                            'returnObj': None}
                    continue
                if response.status_code != 200:
                    return {'statusCode': response.status_code,
                            'message': f'HTTP {response.status_code}: {response.text}',
                            'returnObj': None}
                return response.json()
            except Exception as e:
                logger.error(f"{desc}失败: {e}")
                last = {'statusCode': 500, 'message': str(e), 'returnObj': None}
        return last

    def _get(self, path: str, region_id: str,
             query_params: Optional[Dict[str, Any]] = None,
             desc: str = 'CFW查询') -> Dict[str, Any]:
        return self._request('GET', path, region_id, query_params=query_params, desc=desc)

    def _post(self, path: str, region_id: str, body: Dict[str, Any],
              desc: str = 'CFW查询',
              extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self._request('POST', path, region_id, body=body, desc=desc,
                             extra_headers=extra_headers)

    # ==================== 防火墙管理 ====================

    def firewall_simple_query(self, region_id: str, firewall_id: Optional[str] = None,
                              firewall_name: Optional[str] = None,
                              firewall_type: Optional[str] = None,
                              firewall_state: Optional[str] = None,
                              page: Optional[int] = None,
                              size: Optional[int] = None) -> Dict[str, Any]:
        """查询防火墙的简要信息 - GET /vfw/v2_firewall_simple_query"""
        return self._get('/vfw/v2_firewall_simple_query', region_id, {
            'firewallId': firewall_id,
            'firewallName': firewall_name,
            'firewallType': firewall_type,
            'firewallState': firewall_state,
            'page': page,
            'size': size,
        }, desc='查询防火墙简要信息')

    def query_region_maximums(self, region_id: str) -> Dict[str, Any]:
        """查询资源池规格 - GET /vfw/v2_query_region_maximums"""
        return self._get('/vfw/v2_query_region_maximums', region_id,
                         desc='查询资源池规格')

    def can_buy_firewall(self, region_id: str) -> Dict[str, Any]:
        """能否订购防火墙 - GET /vfw/v2_can_bug_firewall"""
        return self._get('/vfw/v2_can_bug_firewall', region_id,
                         desc='能否订购防火墙')

    def firewall_query(self, region_id: str, firewall_id: str,
                       firewall_name: Optional[str] = None,
                       firewall_type: Optional[str] = None,
                       firewall_state: Optional[str] = None,
                       page: Optional[int] = None,
                       size: Optional[int] = None) -> Dict[str, Any]:
        """查询防火墙详情 - GET /vfw/v2_firewall_query"""
        return self._get('/vfw/v2_firewall_query', region_id, {
            'firewallId': firewall_id, 'firewallName': firewall_name,
            'firewallType': firewall_type, 'firewallState': firewall_state,
            'page': page, 'size': size}, desc='查询防火墙详情')

    # ==================== 概览 ====================

    def firewall_overview(self, region_id: str) -> Dict[str, Any]:
        """实例状态概览 - GET /vfw/v2_firewall_overview"""
        return self._get('/vfw/v2_firewall_overview', region_id, desc='实例状态概览')

    def protection_statistics(self, region_id: str, type: str,
                              firewall_id: Optional[str] = None,
                              firewall_type: Optional[str] = None) -> Dict[str, Any]:
        """安全防护概览 - GET /vfw/v2_protection_statistics"""
        return self._get('/vfw/v2_protection_statistics', region_id, {
            'type': type, 'firewallId': firewall_id,
            'firewallType': firewall_type}, desc='安全防护概览')

    def asset_protection_overview(self, region_id: str) -> Dict[str, Any]:
        """资产防护监控概览 - GET /vfw/v2_asset_protection_overview"""
        return self._get('/vfw/v2_asset_protection_overview', region_id,
                         desc='资产防护监控概览')

    def ac_policy_overview(self, region_id: str,
                           firewall_id: Optional[str] = None,
                           firewall_type: Optional[str] = None) -> Dict[str, Any]:
        """访问控制策略概览 - GET /vfw/v2_ac_policy_overview"""
        return self._get('/vfw/v2_ac_policy_overview', region_id, {
            'firewallId': firewall_id, 'firewallType': firewall_type},
            desc='访问控制策略概览')

    # ==================== 版本/配额 ====================

    def can_downgrade(self, region_id: str, master_resource_id: str) -> Dict[str, Any]:
        """能否降低版本 - GET /vfw/v2_can_downgrade"""
        return self._get('/vfw/v2_can_downgrade', region_id, {
            'masterResourceId': master_resource_id}, desc='能否降低版本')

    def min_quota(self, region_id: str) -> Dict[str, Any]:
        """降配配额最低值 - GET /vfw/v2_min_quota"""
        return self._get('/vfw/v2_min_quota', region_id, desc='降配配额最低值')

    def judge_ability_upgrade(self, region_id: str, flow_processing_capacity: int,
                              protection_ip_num: int, uid: str, user_id: str,
                              vpc_id: str) -> Dict[str, Any]:
        """判断防护能力是否升级 - GET /vfw/v2_firewall_judge_ability_upgrade"""
        return self._get('/vfw/v2_firewall_judge_ability_upgrade', region_id, {
            'flowProcessingCapacity': flow_processing_capacity,
            'protectionIpNum': protection_ip_num,
            'regionId': region_id, 'uid': uid, 'userId': user_id,
            'vpcId': vpc_id}, desc='判断防护能力是否升级')

    # ==================== 网络工具 ====================

    def check_cidr(self, region_id: str, cidr: str, vpc_id: str) -> Dict[str, Any]:
        """校验cidr合法 - GET /vfw/v2_check_cidr"""
        return self._get('/vfw/v2_check_cidr', region_id, {
            'cidr': cidr, 'vpcId': vpc_id}, desc='校验cidr合法')

    def random_firewall_name(self, region_id: str) -> Dict[str, Any]:
        """定义防火墙的随机名称 - GET /vfw/v2_firewall_random_firewall_name"""
        return self._get('/vfw/v2_firewall_random_firewall_name', region_id,
                         desc='防火墙随机名称')

    def firewall_vpc_list(self, region_id: str) -> Dict[str, Any]:
        """获取用户的vpc列表 - GET /vfw/v2_firewall_vpc_list"""
        return self._get('/vfw/v2_firewall_vpc_list', region_id, desc='获取vpc列表')

    def firewall_subnet_list(self, region_id: str, vpc_id: str,
                             traffic_subnet: bool = True,
                             filter_not_valid: Optional[bool] = None) -> Dict[str, Any]:
        """获取vpc的子网列表 - GET /vfw/v2_firewall_subnet_list"""
        return self._get('/vfw/v2_firewall_subnet_list', region_id, {
            'vpcId': vpc_id, 'trafficSubnet': traffic_subnet,
            'filterNotValid': filter_not_valid}, desc='获取子网列表')

    # ==================== 资产 ====================

    def asset_all(self, region_id: str) -> Dict[str, Any]:
        """查询所有东西向资产 - GET /vfw/v2_asset_all"""
        return self._get('/vfw/v2_asset_all', region_id, desc='查询东西向资产')

    def vrf_bind_statistics(self, region_id: str,
                            firewall_id: Optional[str] = None,
                            firewall_type: Optional[str] = None) -> Dict[str, Any]:
        """查询资产统计 - GET /vfw/v2_system_vrf_bind_statistics"""
        return self._get('/vfw/v2_system_vrf_bind_statistics', region_id, {
            'firewallId': firewall_id, 'firewallType': firewall_type},
            desc='查询资产统计')

    def assert_nat_query(self, region_id: str, nat_name: Optional[str] = None,
                         protect_status: Optional[bool] = None,
                         page: Optional[int] = None,
                         size: Optional[int] = None) -> Dict[str, Any]:
        """查看nat列表 - GET /vfw/v2_assert_nat_query"""
        return self._get('/vfw/v2_assert_nat_query', region_id, {
            'natName': nat_name, 'protectStatus': protect_status,
            'page': page, 'size': size}, desc='查看nat列表')

    def assert_cda_query(self, region_id: str) -> Dict[str, Any]:
        """查询云专线列表 - GET /vfw/v2_assert_cda_query"""
        return self._get('/vfw/v2_assert_cda_query', region_id, desc='查询云专线列表')

    def assert_express_connect_query(self, region_id: str) -> Dict[str, Any]:
        """查询云间高速列表 - GET /vfw/v2_assert_expressConnect_query"""
        return self._get('/vfw/v2_assert_expressConnect_query', region_id,
                         desc='查询云间高速列表')

    def assert_vpc_peer_query(self, region_id: str) -> Dict[str, Any]:
        """查询对等连接列表 - GET /vfw/v2_assert_vpcPeer_query"""
        return self._get('/vfw/v2_assert_vpcPeer_query', region_id,
                         desc='查询对等连接列表')

    def assert_protect_check(self, region_id: str, vpc_id: str,
                             scenario_type: str, scenario_id: str) -> Dict[str, Any]:
        """开启防护自动检查 - GET /vfw/v2_assert_protect_check"""
        return self._get('/vfw/v2_assert_protect_check', region_id, {
            'vpcId': vpc_id, 'scenarioType': scenario_type,
            'scenarioId': scenario_id}, desc='开启防护自动检查')

    def assert_statistics(self, region_id: str) -> Dict[str, Any]:
        """VPC边界统计 - GET /vfw/v2_assert_statistics"""
        return self._get('/vfw/v2_assert_statistics', region_id, desc='VPC边界统计')

    def vrf_bind_query(self, region_id: str, firewall_id: Optional[str] = None,
                       eip: Optional[str] = None, eip_id: Optional[str] = None,
                       eip_name: Optional[str] = None,
                       attached_type: Optional[str] = None,
                       ip_type: Optional[str] = None,
                       protect_status: Optional[bool] = None,
                       subnet_id: Optional[str] = None,
                       page: Optional[int] = None,
                       size: Optional[int] = None) -> Dict[str, Any]:
        """查询资产 - GET /vfw/v2_system_vrf_bind_query"""
        return self._get('/vfw/v2_system_vrf_bind_query', region_id, {
            'firewallId': firewall_id, 'eip': eip, 'eipId': eip_id,
            'eipName': eip_name, 'attachedType': attached_type,
            'ipType': ip_type, 'protectStatus': protect_status,
            'subnetId': subnet_id, 'page': page, 'size': size},
            desc='查询资产')

    def vrf_bind_info(self, region_id: str, eip_id: str, uid: str) -> Dict[str, Any]:
        """获取资产详情 - GET /vfw/v2_system_vrf_bind_info"""
        return self._get('/vfw/v2_system_vrf_bind_info', region_id, {
            'eipId': eip_id, 'regionId': region_id, 'uid': uid},
            desc='获取资产详情')

    def vrf_bind_sync_status(self, region_id: str, type: str = 'eip') -> Dict[str, Any]:
        """获取资产同步状态 - GET /vfw/v2_system_vrf_bind_sync_status"""
        return self._get('/vfw/v2_system_vrf_bind_sync_status', region_id,
                         {'type': type}, desc='获取资产同步状态')

    def vrf_bind_sync_time(self, region_id: str, type: str = 'eip') -> Dict[str, Any]:
        """获取资产同步时间 - GET /vfw/v2_system_vrf_bind_sync_time"""
        return self._get('/vfw/v2_system_vrf_bind_sync_time', region_id,
                         {'type': type}, desc='获取资产同步时间')

    # ==================== 防护规则（访问控制） ====================

    def sec_policy_query(self, region_id: str, firewall_id: Optional[str] = None,
                         firewall_type: Optional[str] = None,
                         action: Optional[str] = None,
                         direction: Optional[str] = None,
                         src_ip: Optional[str] = None,
                         dst_ip: Optional[str] = None,
                         ip_proto: Optional[str] = None,
                         service: Optional[str] = None,
                         status: Optional[str] = None,
                         rule_name: Optional[str] = None,
                         rule_ids: Optional[str] = None,
                         address_group: Optional[str] = None,
                         page: Optional[int] = None,
                         size: Optional[int] = None) -> Dict[str, Any]:
        """查询防护规则 - GET /vfw/v2_system_sec_policy_query"""
        return self._get('/vfw/v2_system_sec_policy_query', region_id, {
            'firewallId': firewall_id, 'firewallType': firewall_type,
            'action': action, 'direction': direction, 'srcIp': src_ip,
            'dstIp': dst_ip, 'ipProto': ip_proto, 'service': service,
            'status': status, 'ruleName': rule_name, 'ruleIds': rule_ids,
            'addressGroup': address_group, 'page': page, 'size': size},
            desc='查询防护规则')

    def sec_policy_info(self, region_id: str, firewall_id: str,
                        rule_id: int) -> Dict[str, Any]:
        """查询防护规则详情 - GET /vfw/v2_system_sec_policy_info"""
        return self._get('/vfw/v2_system_sec_policy_info', region_id, {
            'firewallId': firewall_id, 'ruleId': rule_id}, desc='查询防护规则详情')

    def sec_policy_statistics(self, region_id: str, firewall_id: str) -> Dict[str, Any]:
        """获取防护规则统计数据 - GET /vfw/v2_system_sec_policy_statistics"""
        return self._get('/vfw/v2_system_sec_policy_statistics', region_id, {
            'firewallId': firewall_id}, desc='防护规则统计')

    def _download(self, path: str, region_id: str, output: str,
                  desc: str = 'CFW下载') -> Dict[str, Any]:
        """下载文件类API（返回xlsx等二进制流）"""
        url = f'https://{self.ENDPOINTS[0]}{path}'
        try:
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params={}, body='',
                extra_headers=self._headers(region_id))
            response = self.client.session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text[:200]}',
                        'returnObj': None}
            ct = response.headers.get('Content-Type', '')
            if 'json' in ct:
                return response.json()
            with open(output, 'wb') as f:
                f.write(response.content)
            return {'statusCode': '800', 'message': '成功！',
                    'returnObj': {'file': output, 'size': len(response.content),
                                  'contentType': ct}}
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    def sec_policy_export_module(self, region_id: str,
                                 output: str = 'sec_policy_template.xlsx') -> Dict[str, Any]:
        """获取访问规则的excel文件模板 - GET /vfw/v2_system_sec_policy_export_module"""
        return self._download('/vfw/v2_system_sec_policy_export_module', region_id,
                              output, desc='访问规则excel模板')

    # ==================== 黑白名单 ====================

    def black_white_policy_query(self, region_id: str, firewall_id: str,
                                 black_white_type: str,
                                 address_direction: Optional[str] = None,
                                 ip: Optional[str] = None,
                                 ip_proto: Optional[str] = None,
                                 rule_id: Optional[int] = None,
                                 rule_name: Optional[str] = None,
                                 address_group: Optional[str] = None,
                                 page: Optional[int] = None,
                                 size: Optional[int] = None) -> Dict[str, Any]:
        """查询黑白名单 - GET /vfw/v2_black_white_policy_query"""
        return self._get('/vfw/v2_black_white_policy_query', region_id, {
            'firewallId': firewall_id, 'blackWhiteType': black_white_type,
            'addressDirection': address_direction, 'ip': ip,
            'ipProto': ip_proto, 'ruleId': rule_id, 'ruleName': rule_name,
            'addressGroup': address_group, 'page': page, 'size': size},
            desc='查询黑白名单')

    def black_white_policy_info(self, region_id: str, firewall_id: str,
                                black_white_type: str, rule_id: int,
                                uid: str) -> Dict[str, Any]:
        """查询黑白名单详情 - GET /vfw/v2_black_white_policy_info"""
        return self._get('/vfw/v2_black_white_policy_info', region_id, {
            'firewallId': firewall_id, 'blackWhiteType': black_white_type,
            'ruleId': rule_id, 'regionId': region_id, 'uid': uid},
            desc='查询黑白名单详情')

    def black_white_policy_export_module(self, region_id: str,
                                         output: str = 'black_white_template.xlsx') -> Dict[str, Any]:
        """获取黑白名单规则的excel文件模板 - GET /vfw/v2_black_white_policy_export_module"""
        return self._download('/vfw/v2_black_white_policy_export_module', region_id,
                              output, desc='黑白名单excel模板')

    # ==================== 地址簿 ====================

    def address_group_query(self, region_id: str, ip: Optional[str] = None,
                            address_type: Optional[str] = None,
                            address_group_name: Optional[str] = None,
                            group_id: Optional[int] = None,
                            page: Optional[int] = None,
                            size: Optional[int] = None) -> Dict[str, Any]:
        """查询地址簿 - GET /vfw/v2_address_group_query"""
        return self._get('/vfw/v2_address_group_query', region_id, {
            'ip': ip, 'addressType': address_type,
            'addressGroupName': address_group_name, 'groupId': group_id,
            'page': page, 'size': size}, desc='查询地址簿')

    def address_group_items(self, region_id: str, group_id: int,
                            page: Optional[int] = None,
                            size: Optional[int] = None) -> Dict[str, Any]:
        """地址簿详情 - GET /vfw/v2_address_group_items"""
        return self._get('/vfw/v2_address_group_items', region_id, {
            'groupId': group_id, 'page': page, 'size': size}, desc='地址簿详情')

    def address_group_statistic(self, region_id: str) -> Dict[str, Any]:
        """统计地址簿 - GET /vfw/v2_address_group_statistic"""
        return self._get('/vfw/v2_address_group_statistic', region_id,
                         desc='统计地址簿')

    # ==================== IPS / 应用 ====================

    def ips_rule_query(self, region_id: str, firewall_id: str,
                       method: Optional[str] = None,
                       target: Optional[str] = None,
                       type: Optional[str] = None,
                       rule_id: Optional[int] = None,
                       page: Optional[int] = None,
                       size: Optional[int] = None) -> Dict[str, Any]:
        """查询ips规则 - GET /vfw/v2_ips_rule_query"""
        return self._get('/vfw/v2_ips_rule_query', region_id, {
            'firewallId': firewall_id, 'method': method, 'target': target,
            'type': type, 'ruleId': rule_id, 'page': page, 'size': size},
            desc='查询ips规则')

    def ips_rule_query_all(self, region_id: str) -> Dict[str, Any]:
        """查询攻击类型 - GET /vfw/v2_ips_rule_queryAll"""
        return self._get('/vfw/v2_ips_rule_queryAll', region_id, desc='查询攻击类型')

    def ips_rule_type(self, region_id: str) -> Dict[str, Any]:
        """获取ips规则类型列表 - GET /vfw/v2_ips_rule_type"""
        return self._get('/vfw/v2_ips_rule_type', region_id, desc='ips规则类型列表')

    def dpi_info(self, region_id: str, firewall_id: str) -> Dict[str, Any]:
        """查询dpi详情 - GET /vfw/v2_dpi_info"""
        return self._get('/vfw/v2_dpi_info', region_id, {
            'firewallId': firewall_id, 'regionId': region_id}, desc='查询dpi详情')

    def app_query_all(self, region_id: str) -> Dict[str, Any]:
        """查询全部应用 - GET /vfw/v2_app_queryAll"""
        return self._get('/vfw/v2_app_queryAll', region_id, desc='查询全部应用')

    def app_query_with_parent(self, region_id: str) -> Dict[str, Any]:
        """查询应用大类和子类 - GET /vfw/v2_app_queryAppWithParent"""
        return self._get('/vfw/v2_app_queryAppWithParent', region_id,
                         desc='查询应用大类和子类')

    # ==================== 告警 ====================

    def alarm_query(self, region_id: str, start_time: str, finish_time: str,
                    firewall_id: Optional[str] = None,
                    firewall_type: Optional[str] = None,
                    attack_ip: Optional[str] = None,
                    affected_ip: Optional[str] = None,
                    page_num: Optional[int] = None,
                    page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询告警列表 - GET /vfw/v2_alarm_query"""
        return self._get('/vfw/v2_alarm_query', region_id, {
            'firewallId': firewall_id, 'firewallType': firewall_type,
            'startTime': start_time, 'finishTime': finish_time,
            'attackIp': attack_ip, 'affectedIp': affected_ip,
            'pageNum': page_num, 'pageSize': page_size},
            desc='查询告警列表')

    def alarm_detail(self, region_id: str, alarm_id: str) -> Dict[str, Any]:
        """告警详情 - GET /vfw/v2_alarm_detail"""
        return self._get('/vfw/v2_alarm_detail', region_id,
                         {'alarmId': alarm_id}, desc='告警详情')

    def alarm_statics(self, region_id: str, firewall_id: str,
                      start_time: str, finish_time: str) -> Dict[str, Any]:
        """告警统计 - GET /vfw/v2_alarm_statics"""
        return self._get('/vfw/v2_alarm_statics', region_id, {
            'firewallId': firewall_id, 'startTime': start_time,
            'finishTime': finish_time}, desc='告警统计')

    def alarm_log_list(self, region_id: str, firewall_id: str,
                       start_time: str, finish_time: str,
                       attack_direction: str = '3',
                       source_ip: Optional[str] = None,
                       target_ip: Optional[str] = None,
                       page: Optional[int] = None,
                       size: Optional[int] = None) -> Dict[str, Any]:
        """流量日志列表 - GET /vfw/v2_alarm_logList

        attackDirection为实测必填参数（1出向 2入向 3全方向），文档未列出
        """
        return self._get('/vfw/v2_alarm_logList', region_id, {
            'firewallId': firewall_id, 'startTime': start_time,
            'finishTime': finish_time, 'attackDirection': attack_direction,
            'sourceIp': source_ip,
            'targetIp': target_ip, 'page': page, 'size': size},
            desc='流量日志列表')

    # ==================== 日志 ====================

    def flow_log_query(self, region_id: str, firewall_type: str, type: str,
                       begin_time: int, end_time: int) -> Dict[str, Any]:
        """查询防火墙流量日志 - GET /vfw/v2_flow_log_query"""
        return self._get('/vfw/v2_flow_log_query', region_id, {
            'firewallType': firewall_type, 'type': type,
            'beginTime': begin_time, 'endTime': end_time},
            desc='查询防火墙流量日志')

    def operation_log_query(self, region_id: str, firewall_id: str,
                            begin_time: int, end_time: int,
                            action: Optional[str] = None,
                            content: Optional[str] = None,
                            page: Optional[int] = None,
                            size: Optional[int] = None) -> Dict[str, Any]:
        """查询操作日志 - GET /vfw/v2_operation_log_query"""
        return self._get('/vfw/v2_operation_log_query', region_id, {
            'firewallId': firewall_id, 'beginTime': begin_time,
            'endTime': end_time, 'action': action, 'content': content,
            'page': page, 'size': size}, desc='查询操作日志')

    def log_save_statistics(self, region_id: str, firewall_id: str) -> Dict[str, Any]:
        """查看日志存储容量 - GET /vfw/v2_log_save_statistics"""
        return self._get('/vfw/v2_log_save_statistics', region_id,
                         {'firewallId': firewall_id}, desc='查看日志存储容量')

    def log_setting_info(self, region_id: str, firewall_id: str) -> Dict[str, Any]:
        """查询日志配置详情 - GET /vfw/v2_log_setting_info"""
        return self._get('/vfw/v2_log_setting_info', region_id,
                         {'firewallId': firewall_id}, desc='查询日志配置详情')

    def log_query_deliver_list(self, region_id: str, firewall_id: str) -> Dict[str, Any]:
        """查看日志投递列表 - GET /vfw/v2_log_query_deliver_list"""
        return self._get('/vfw/v2_log_query_deliver_list', region_id,
                         {'firewallId': firewall_id}, desc='查看日志投递列表')

    def log_query_deliver_info(self, region_id: str, firewall_id: str) -> Dict[str, Any]:
        """查询日志投递类型信息 - GET /vfw/v2_log_query_deliver_info"""
        return self._get('/vfw/v2_log_query_deliver_info', region_id,
                         {'firewallId': firewall_id}, desc='查询日志投递类型信息')

    def log_query_deliver_time(self, region_id: str, firewall_id: str,
                               save_types: list) -> Dict[str, Any]:
        """查询日志投递开始时间 - POST /vfw/v2_log_query_deliver_time"""
        return self._post('/vfw/v2_log_query_deliver_time', region_id, {
            'firewallId': firewall_id, 'saveTypes': save_types},
            desc='查询日志投递开始时间')

    # 网关仅注册官方文档(ID 17175/17174)中的字面路径段，不接受regionId/防火墙ID替换
    _RAW_LOG_PATH_SEG = 'bb9fdb42056f11eda1610242ac110002'

    def get_raw_log(self, region_id: str, firewall_id: str, log_type: str,
                    start_time: str, end_time: str,
                    keys: Optional[list] = None,
                    page: int = 1, size: int = 10) -> Dict[str, Any]:
        """查询日志内容 - POST /vfw/bb9fdb42.../v2_get_raw_log

        loggroup=防火墙id, logunit=防火墙id_{FLOW|IPS|AC|AV}，分页走header；
        时间格式 yyyy/MM/dd HH:mm:ss（北京时间）
        """
        return self._post(f'/vfw/{self._RAW_LOG_PATH_SEG}/v2_get_raw_log', region_id, {
            'startTime': start_time, 'endTime': end_time,
            'isFullIndex': 1, 'judgeMode': 1,
            'keys': keys or []},
            desc='查询日志内容',
            extra_headers={'loggroup': firewall_id,
                           'logunit': f'{firewall_id}_{log_type}',
                           'page': page, 'size': size})

    def get_log_count(self, region_id: str, firewall_id: str, log_type: str,
                      start_time: str, end_time: str,
                      keys: Optional[list] = None) -> Dict[str, Any]:
        """统计日志数量 - POST /vfw/bb9fdb42.../v2_get_log_count"""
        body: Dict[str, Any] = {'startTime': start_time, 'endTime': end_time,
                                'isFullIndex': 1, 'judgeMode': 1}
        if keys:
            body['keys'] = keys
        return self._post(f'/vfw/{self._RAW_LOG_PATH_SEG}/v2_get_log_count',
                          region_id, body, desc='统计日志数量',
                          extra_headers={'loggroup': firewall_id,
                                         'logunit': f'{firewall_id}_{log_type}'})

    # ==================== 报表 / 通知 ====================

    def report_list(self, region_id: str, firewall_id: str,
                    start_time: str, end_time: str, report_type: str,
                    selected_time: Optional[str] = None,
                    page: Optional[int] = None,
                    size: Optional[int] = None) -> Dict[str, Any]:
        """报表列表 - GET /vfw/v2_report_list"""
        return self._get('/vfw/v2_report_list', region_id, {
            'firewallId': firewall_id, 'startTime': start_time,
            'endTime': end_time, 'reportType': report_type,
            'selectedTime': selected_time, 'page': page, 'size': size},
            desc='报表列表')

    def report_statistics(self, region_id: str, firewall_id: str,
                          start_time: str, end_time: str) -> Dict[str, Any]:
        """报表统计 - GET /vfw/v2_report_statistics"""
        return self._get('/vfw/v2_report_statistics', region_id, {
            'firewallId': firewall_id, 'startTime': start_time,
            'endTime': end_time}, desc='报表统计')

    def report_subscribe(self, region_id: str) -> Dict[str, Any]:
        """订阅列表 - GET /vfw/v2_report_subscribe"""
        return self._get('/vfw/v2_report_subscribe', region_id, desc='订阅列表')

    def notification(self, region_id: str) -> Dict[str, Any]:
        """获取通知设置 - GET /vfw/v2_notification"""
        return self._get('/vfw/v2_notification', region_id, desc='获取通知设置')

    # ==================== 询价 (C100型) ====================

    def query_order_price(self, region_id: str, cycle_cnt: int, cycle_type: str,
                          spec: str, protection_ip_num: int,
                          flow_processing_capacity: int,
                          vpc_quota: Optional[int] = None,
                          vpc_flow_processing_capacity: Optional[int] = None) -> Dict[str, Any]:
        """查询新购订单价格(C100型) - GET /vfw/v2_userControl_query_order_price"""
        return self._get('/vfw/v2_userControl_query_order_price', region_id, {
            'cycleCnt': cycle_cnt, 'cycleType': cycle_type, 'spec': spec,
            'protectionIpNum': protection_ip_num,
            'flowProcessingCapacity': flow_processing_capacity,
            'vpcQuota': vpc_quota,
            'vpcFlowProcessingCapacity': vpc_flow_processing_capacity},
            desc='查询新购订单价格')

    def query_renew_price(self, region_id: str, firewall_id: str,
                          cycle_cnt: int, cycle_type: str) -> Dict[str, Any]:
        """查询续订订单价格(C100型) - GET /vfw/v2_userControl_query_renew_price"""
        return self._get('/vfw/v2_userControl_query_renew_price', region_id, {
            'cycleCnt': cycle_cnt, 'cycleType': cycle_type,
            'firewallId': firewall_id}, desc='查询续订订单价格')

    def query_upgrade_price(self, region_id: str, firewall_id: str,
                            upgrade_type: str,
                            spec: Optional[str] = None,
                            upgrade_value: Optional[str] = None) -> Dict[str, Any]:
        """查询升配订单价格(C100型) - GET /vfw/v2_userControl_query_upgrade_price"""
        return self._get('/vfw/v2_userControl_query_upgrade_price', region_id, {
            'firewallId': firewall_id, 'upgradeType': upgrade_type,
            'spec': spec, 'upgradeValue': upgrade_value},
            desc='查询升配订单价格')

    # ==================== 询价 (N100型) ====================

    def query_new_purchase_price_n100(self, region_id: str,
                                      orders: list) -> Dict[str, Any]:
        """查询新购订单价格(N100型) - POST /v1/cngfw/order/query_newPurchase_price"""
        return self._post('/v1/cngfw/order/query_newPurchase_price', region_id,
                          {'orders': orders}, desc='查询新购订单价格N100')

    def query_renew_price_n100(self, region_id: str, resource_ids: list,
                               cycle_cnt: int, cycle_type: int) -> Dict[str, Any]:
        """查询续订订单价格(N100型) - POST /v1/cngfw/order/query_renew_price

        实测后端参数名为cycleCount（文档误写为cycleCnt）
        """
        return self._post('/v1/cngfw/order/query_renew_price', region_id, {
            'cycleCount': cycle_cnt, 'cycleType': cycle_type,
            'resourceIds': resource_ids}, desc='查询续订订单价格N100')

    def query_upgrade_price_n100(self, region_id: str, resource_id: str,
                                 ismain: str, firewall_edition: str) -> Dict[str, Any]:
        """查询升配订单价格(N100型) - POST /v1/cngfw/order/query_upgrade_price"""
        return self._post('/v1/cngfw/order/query_upgrade_price', region_id, {
            'resourceId': resource_id, 'ismain': ismain,
            'firewallEdition': firewall_edition}, desc='查询升配订单价格N100')
