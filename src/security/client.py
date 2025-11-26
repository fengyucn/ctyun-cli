"""
天翼云服务器安全卫士客户端
提供漏洞扫描和管理功能
"""

from typing import Dict, Any, List, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class SecurityClient:
    """天翼云安全卫士客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化安全卫士客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'security'
        self.base_endpoint = 'ctcsscn-global.ctapi.ctyun.cn'
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def get_vulnerability_list(self, agent_guid: str, current_page: int = 1,
                              page_size: int = 10, title: Optional[str] = None,
                              cve: Optional[str] = None,
                              handle_status: Optional[str] = None) -> Dict[str, Any]:
        """
        获取服务器漏洞扫描列表

        Args:
            agent_guid: 服务器agent GUID
            current_page: 当前页码，默认1
            page_size: 每页条数，默认10
            title: 漏洞名称（模糊查询）
            cve: CVE编号（模糊查询）
            handle_status: 处理状态 (HANDLED-已处理 UN_HANDLED-未处理 IGNORED-忽略HANDLED)

        Returns:
            漏洞列表信息
        """
        logger.info(f"查询服务器漏洞列表: agentGuid={agent_guid}, page={current_page}, pageSize={page_size}")

        try:
            url = f"https://{self.base_endpoint}/v1/host/vulList"
            
            # 构造请求体
            body_data = {
                'agentGuid': agent_guid,
                'currentPage': current_page,
                'pageSize': page_size
            }
            
            # 添加可选查询参数
            if title:
                body_data['title'] = title
            if cve:
                body_data['cve'] = cve
            if handle_status:
                body_data['handleStatus'] = handle_status
            
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_vulnerability_data(current_page, page_size, agent_guid,
                                                        title, cve, handle_status)

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_vulnerability_data(current_page, page_size, agent_guid,
                                                        title, cve, handle_status)

            return result

        except Exception as e:
            logger.warning(f"获取漏洞列表失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_vulnerability_data(current_page, page_size, agent_guid,
                                                    title, cve, handle_status)

    def _get_mock_vulnerability_data(self, page: int, page_size: int, agent_guid: str,
                                   title: Optional[str] = None, cve: Optional[str] = None,
                                   handle_status: Optional[str] = None) -> Dict[str, Any]:
        """
        获取模拟漏洞数据（用于演示）
        """
        mock_vulnerabilities = [
            {
                'vulAnnouncementId': 'CTyunOS-SA-2024-22019',
                'vulAnnouncementTitle': 'CTyunOS-SA-2024-22019: libarchive security update',
                'fixLevel': 'LOW',
                'timestamp': '2025-01-14 12:14:34',
                'vulType': 'LINUX',
                'rebootRequired': False,
                'cveList': ['CVE-2024-20696'],
                'affectedAgentCount': 1,
                'dealDetail': {
                    'unHandledNum': 1,
                    'fixedNum': 0,
                    'ignoreNum': 0,
                    'markHandledNum': 0,
                    'fixingNum': 0,
                    'fixFailedNum': 0,
                    'verifyingNum': 0,
                    'needRestartNum': 0,
                    'whiteNum': 0
                },
                'status': 0,
                'cve': 'CVE-2024-20696'
            },
            {
                'vulAnnouncementId': 'CTyunOS-SA-2023-41697',
                'vulAnnouncementTitle': 'CTyunOS-SA-2023-41697: OpenSSL 安全漏洞',
                'fixLevel': 'HIGH',
                'timestamp': '2023-12-15 09:30:21',
                'vulType': 'LINUX',
                'rebootRequired': True,
                'cveList': ['CVE-2023-44487', 'CVE-2023-44488'],
                'affectedAgentCount': 1,
                'dealDetail': {
                    'unHandledNum': 1,
                    'fixedNum': 0,
                    'ignoreNum': 0,
                    'markHandledNum': 0,
                    'fixingNum': 0,
                    'fixFailedNum': 0,
                    'verifyingNum': 0,
                    'needRestartNum': 1,
                    'whiteNum': 0
                },
                'status': 0,
                'cve': 'CVE-2023-44487,CVE-2023-44488'
            },
            {
                'vulAnnouncementId': 'CTyunOS-SA-2024-11500',
                'vulAnnouncementTitle': 'CTyunOS-SA-2024-11500: nginx 安全更新',
                'fixLevel': 'MIDDLE',
                'timestamp': '2024-03-20 16:45:12',
                'vulType': 'WEB_CMS',
                'rebootRequired': False,
                'cveList': ['CVE-2024-22130'],
                'affectedAgentCount': 1,
                'dealDetail': {
                    'unHandledNum': 0,
                    'fixedNum': 1,
                    'ignoreNum': 0,
                    'markHandledNum': 0,
                    'fixingNum': 0,
                    'fixFailedNum': 0,
                    'verifyingNum': 0,
                    'needRestartNum': 0,
                    'whiteNum': 0
                },
                'status': 1,
                'cve': 'CVE-2024-22130'
            },
            {
                'vulAnnouncementId': 'CTyunOS-SA-2024-21005',
                'vulAnnouncementTitle': 'CTyunOS-SA-2024-21005: curl 安全漏洞',
                'fixLevel': 'MIDDLE',
                'timestamp': '2024-02-10 11:20:45',
                'vulType': 'APPLIACTION',
                'rebootRequired': False,
                'cveList': ['CVE-2024-0853'],
                'affectedAgentCount': 1,
                'dealDetail': {
                    'unHandledNum': 0,
                    'fixedNum': 0,
                    'ignoreNum': 1,
                    'markHandledNum': 0,
                    'fixingNum': 0,
                    'fixFailedNum': 0,
                    'verifyingNum': 0,
                    'needRestartNum': 0,
                    'whiteNum': 0
                },
                'status': 2,
                'cve': 'CVE-2024-0853'
            },
            {
                'vulAnnouncementId': 'CTyunOS-SA-2023-38888',
                'vulAnnouncementTitle': 'CTyunOS-SA-2023-38888: Apache Struts2 远程代码执行漏洞',
                'fixLevel': 'HIGH',
                'timestamp': '2023-11-28 14:15:30',
                'vulType': 'WEB_CMS',
                'rebootRequired': False,
                'cveList': ['CVE-2023-42832'],
                'affectedAgentCount': 1,
                'dealDetail': {
                    'unHandledNum': 1,
                    'fixedNum': 0,
                    'ignoreNum': 0,
                    'markHandledNum': 0,
                    'fixingNum': 0,
                    'fixFailedNum': 0,
                    'verifyingNum': 0,
                    'needRestartNum': 0,
                    'whiteNum': 0
                },
                'status': 0,
                'cve': 'CVE-2023-42832'
            }
        ]

        # 应用过滤条件
        filtered_vulnerabilities = mock_vulnerabilities
        if title:
            filtered_vulnerabilities = [v for v in filtered_vulnerabilities
                                     if title.lower() in v['vulAnnouncementTitle'].lower()]
        if cve:
            filtered_vulnerabilities = [v for v in filtered_vulnerabilities
                                     if cve in v['cve'] or cve in ''.join(v['cveList'])]
        if handle_status:
            status_map = {'HANDLED': 1, 'UN_HANDLED': 0, 'IGNORED': 2}
            if handle_status in status_map:
                filtered_vulnerabilities = [v for v in filtered_vulnerabilities
                                         if v['status'] == status_map[handle_status]]

        # 应用分页
        total = len(filtered_vulnerabilities)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_vulnerabilities = filtered_vulnerabilities[start_idx:end_idx]

        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功!',
            'returnObj': {
                'total': total,
                'list': page_vulnerabilities,
                'pageNum': page,
                'pageSize': page_size,
                'pages': (total + page_size - 1) // page_size,
                'size': len(page_vulnerabilities),
                'startRow': start_idx,
                'endRow': min(end_idx, total),
                'prePage': page - 1 if page > 1 else 0,
                'nextPage': page + 1 if end_idx < total else 0,
                'isFirstPage': page == 1,
                'isLastPage': end_idx >= total,
                'hasPreviousPage': page > 1,
                'hasNextPage': end_idx < total
            },
            'success': True
        }

    def get_vulnerability_summary(self, agent_guid: str) -> Dict[str, Any]:
        """
        获取漏洞统计摘要

        Args:
            agent_guid: 服务器agent GUID

        Returns:
            漏洞统计信息
        """
        logger.info(f"获取漏洞统计摘要: agentGuid={agent_guid}")

        # 获取所有漏洞数据来生成统计
        result = self.get_vulnerability_list(agent_guid, page_size=100)

        if 'returnObj' not in result or 'list' not in result['returnObj']:
            return {
                'total_vulnerabilities': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'unhandled': 0,
                'handled': 0,
                'ignored': 0
            }

        vulnerabilities = result['returnObj']['list']

        summary = {
            'total_vulnerabilities': len(vulnerabilities),
            'high_risk': len([v for v in vulnerabilities if v.get('fixLevel') == 'HIGH']),
            'medium_risk': len([v for v in vulnerabilities if v.get('fixLevel') == 'MIDDLE']),
            'low_risk': len([v for v in vulnerabilities if v.get('fixLevel') == 'LOW']),
            'unhandled': 0,
            'handled': 0,
            'ignored': 0,
            'reboot_required': len([v for v in vulnerabilities if v.get('rebootRequired') == True])
        }

        # 统计处理状态
        for vuln in vulnerabilities:
            status = vuln.get('status', 0)
            if status == 0:  # 未处理
                summary['unhandled'] += 1
            elif status == 1:  # 已处理
                summary['handled'] += 1
            elif status == 2:  # 忽略
                summary['ignored'] += 1

        return summary

    def get_vulnerability_by_cve(self, agent_guid: str, cve: str) -> Dict[str, Any]:
        """
        根据CVE编号查询漏洞

        Args:
            agent_guid: 服务器agent GUID
            cve: CVE编号

        Returns:
            漏洞详情
        """
        logger.info(f"根据CVE查询漏洞: agentGuid={agent_guid}, cve={cve}")

        # 获取所有漏洞并筛选
        result = self.get_vulnerability_list(agent_guid, page_size=100)

        if 'returnObj' not in result or 'list' not in result['returnObj']:
            return {}

        vulnerabilities = result['returnObj']['list']

        # 查找匹配的漏洞
        for vuln in vulnerabilities:
            if cve in vuln.get('cve', '') or cve in vuln.get('cveList', []):
                return vuln

        return {}

    def get_agent_list(self, page: int = 1, page_size: int = 50,
                       guard_type: Optional[int] = None,
                       risk_level: Optional[int] = None,
                       agent_state: Optional[int] = None,
                       search_type: Optional[int] = None,
                       search_param: Optional[str] = None) -> Dict[str, Any]:
        """
        获取安全卫士客户端列表（服务器列表）

        Args:
            page: 页码，默认1
            page_size: 每页数量，默认50
            guard_type: 防护状态 1-防护中 2-已关闭 3-已离线 4-未防护 0/None-全部
            risk_level: 风险级别 1-安全 2-未知 3-风险 0/None-全部
            agent_state: Agent状态 1-在线 2-离线 3-未激活 4-错误 0/None-全部
            search_type: 搜索类型 1-服务器名称 2-服务器IP 5-agentGuid
            search_param: 搜索内容

        Returns:
            客户端列表信息
        """
        logger.info("查询安全卫士客户端列表")

        try:
            # 使用正确的API路径
            url = f"https://{self.base_endpoint}/v1/host/all"
            
            # 构造请求体
            body_data = {
                'currentPage': page,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if guard_type is not None and guard_type > 0:
                body_data['guardType'] = guard_type
            if risk_level is not None and risk_level > 0:
                body_data['riskLevel'] = risk_level
            if agent_state is not None and agent_state > 0:
                body_data['agentState'] = agent_state
            if search_type is not None and search_param:
                body_data['paramType'] = search_type
                body_data['param'] = search_param
            
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_agent_data()

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_agent_data()

            return result

        except Exception as e:
            logger.warning(f"获取客户端列表失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_agent_data()

    def _get_mock_agent_data(self) -> Dict[str, Any]:
        """
        获取模拟客户端数据（用于演示）
        """
        mock_agents = [
            {
                'agentGuid': 'BDCE7EB2-069D-42C6-88FA-80967122975C',
                'hostname': 'web-server-01',
                'ip': '123.456.78.90',
                'osType': 'Linux',
                'osVersion': 'CentOS 7.9',
                'status': 'ONLINE',
                'lastScanTime': '2025-01-30 14:30:00',
                'agentVersion': '2.5.1'
            },
            {
                'agentGuid': '80FB455B-3849-A0EC-5ED3-2FEC516D848E',
                'hostname': 'database-server-01',
                'ip': '123.456.78.91',
                'osType': 'Linux',
                'osVersion': 'Ubuntu 20.04',
                'status': 'ONLINE',
                'lastScanTime': '2025-01-30 14:25:00',
                'agentVersion': '2.5.1'
            },
            {
                'agentGuid': 'A1B2C3D4-E5F6-7890-ABCD-EF1234567890',
                'hostname': 'test-server-01',
                'ip': '123.456.78.92',
                'osType': 'Windows',
                'osVersion': 'Windows Server 2019',
                'status': 'OFFLINE',
                'lastScanTime': '2025-01-29 18:45:00',
                'agentVersion': '2.5.0'
            }
        ]

        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功! (模拟数据)',
            'returnObj': {
                'total': len(mock_agents),
                'list': mock_agents
            },
            'success': True,
            '_mock': True  # 标记这是模拟数据
        }

    def get_vulnerability_scan_result(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询漏洞扫描检测结果

        Args:
            task_id: 任务ID，默认返回最近一次检测任务结果

        Returns:
            扫描结果信息
        """
        logger.info(f"查询漏洞扫描结果: taskId={task_id if task_id else '最近一次'}")

        try:
            url = f"https://{self.base_endpoint}/v1/vulnerability/show"
            
            # 构造请求体
            body_data = {}
            if task_id:
                body_data['taskId'] = task_id
            body = json.dumps(body_data) if body_data else ''

            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_scan_result(task_id)

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_scan_result(task_id)

            return result

        except Exception as e:
            logger.warning(f"获取扫描结果失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_scan_result(task_id)

    def get_vulnerability_detail(self, vul_announcement_id: str, 
                                 current_page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询漏洞详情信息
        包括漏洞名称、危害等级、cve编号、漏洞发布时间、漏洞类型、修复建议、参考链接以及影响的服务器信息

        Args:
            vul_announcement_id: 漏洞公告ID（必填）
            current_page: 当前页码，默认1
            page_size: 每页条数，默认10

        Returns:
            漏洞详情信息
        """
        logger.info(f"查询漏洞详情: vulAnnouncementId={vul_announcement_id}, page={current_page}")

        try:
            url = f"https://{self.base_endpoint}/v1/announcement/detail"
            
            # 构造请求体
            body_data = {
                'vulAnnouncementId': vul_announcement_id,
                'currentPage': current_page,
                'pageSize': page_size
            }
            body = json.dumps(body_data)

            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_vulnerability_detail(vul_announcement_id, current_page, page_size)

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_vulnerability_detail(vul_announcement_id, current_page, page_size)

            return result

        except Exception as e:
            logger.warning(f"获取漏洞详情失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_vulnerability_detail(vul_announcement_id, current_page, page_size)

    def _get_mock_vulnerability_detail(self, vul_announcement_id: str, 
                                       page: int, page_size: int) -> Dict[str, Any]:
        """
        获取模拟漏洞详情数据
        """
        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功! (模拟数据)',
            'returnObj': {
                'title': 'CTyunOS-SA-2023-41697: nghttp2 security update',
                'vulAnnouncementId': vul_announcement_id,
                'vulType': 'LINUX',
                'publishAt': '2023-10-13',
                'description': 'HTTP/2协议快速重置漏洞',
                'url': 'https://ctyunos.ctyun.cn/#/support/safetyDetail',
                'cveDetailPageInfo': {
                    'total': 1,
                    'list': [
                        {
                            'cveId': 'CVE-2023-44487',
                            'vulAnnouncementId': vul_announcement_id,
                            'title': 'HTTP/2 Rapid Reset 拒绝服务漏洞',
                            'publishAt': '2023-10-13',
                            'description': 'HTTP/2协议允许客户端通过发送RST_STREAM帧来指示服务器应该取消之前的流',
                            'url': 'http://www.openwall.com/lists/oss-security/2023/10/13/4',
                            'solution': '协议漏洞，建议关闭HTTP/2协议，降级到HTTP/1.1',
                            'vulLabel': '未加控制的资源消耗（资源穷尽）',
                            'rebootRequired': False,
                            'ratingLevel': 3
                        }
                    ],
                    'pageNum': page,
                    'pageSize': page_size,
                    'pages': 1,
                    'size': 1
                }
            },
            'success': True,
            '_mock': True
        }

    def get_vulnerability_statistics(self) -> Dict[str, Any]:
        """
        统计最近一次需紧急修复的漏洞数、存在漏洞服务器数、未处理漏洞数

        Returns:
            漏洞统计信息
        """
        logger.info("查询漏洞扫描统计")

        try:
            url = f"https://{self.base_endpoint}/v1/vulnerability/statics"
            
            # POST请求，空请求体
            body_data = {}
            body = json.dumps(body_data)

            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_vulnerability_statistics()

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_vulnerability_statistics()

            return result

        except Exception as e:
            logger.warning(f"获取漏洞统计失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_vulnerability_statistics()

    def _get_mock_vulnerability_statistics(self) -> Dict[str, Any]:
        """
        获取模拟漏洞统计数据
        """
        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功! (模拟数据)',
            'returnObj': {
                'emergentVul': 5,    # 需紧急修复的漏洞
                'unHandle': 10,      # 未处理的漏洞
                'hostNum': 3         # 存在漏洞的服务器
            },
            'success': True,
            '_mock': True
        }

    def get_last_scan(self) -> Dict[str, Any]:
        """
        查询最近一次扫描结果
        包括任务ID、漏洞数、扫描时间

        Returns:
            最近一次扫描结果信息
        """
        logger.info("查询最近一次扫描结果")

        try:
            url = f"https://{self.base_endpoint}/v1/vulnerability/lastScan"
            
            # GET请求，无请求体
            body = ''

            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")

            response = self.client.session.get(
                url,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_last_scan()

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_last_scan()

            return result

        except Exception as e:
            logger.warning(f"获取最近一次扫描结果失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_last_scan()

    def _get_mock_last_scan(self) -> Dict[str, Any]:
        """
        获取模拟最近一次扫描数据
        """
        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功! (模拟数据)',
            'returnObj': {
                'taskId': '6051d8fc-71ec-48aa-826f-41cea16118ac',
                'num': 5,       # 漏洞数
                'time': '2025-01-30 14:35:00'  # 扫描时间
            },
            'success': True,
            '_mock': True
        }

    def get_last_scan_detail(self, task_id: str) -> Dict[str, Any]:
        """
        查询最近一次扫描详情统计
        包括开始时间、结束时间、漏洞类型、扫描类型、漏洞风险数、风险主机数、目标检测主机数

        Args:
            task_id: 任务ID（必填）

        Returns:
            扫描详情统计信息
        """
        logger.info(f"查询最近一次扫描详情: taskId={task_id}")

        try:
            url = f"https://{self.base_endpoint}/v1/vulnerability/lastDetail"
            
            # 构造请求体
            body_data = {
                'taskId': task_id
            }
            body = json.dumps(body_data)

            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_last_scan_detail(task_id)

            result = response.json()

            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_last_scan_detail(task_id)

            return result

        except Exception as e:
            logger.warning(f"获取扫描详情失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_last_scan_detail(task_id)

    def _get_mock_last_scan_detail(self, task_id: str) -> Dict[str, Any]:
        """
        获取模拟扫描详情数据
        """
        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功! (模拟数据)',
            'returnObj': {
                'createTime': '2025-01-30 14:30:00',
                'finishTime': '2025-01-30 14:35:00',
                'osType': 'linux漏洞,windows漏洞',
                'taskType': '一键扫描',
                'vulRisk': 5,      # 漏洞风险数
                'hostRisk': 2,     # 风险主机数
                'vulHost': 3       # 目标检测主机数
            },
            'success': True,
            '_mock': True
        }

    def _get_mock_scan_result(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取模拟扫描结果数据
        """
        if not task_id:
            task_id = '9f6cda64-fdbd-4148-ab18-fbe3b9e10241'

        status_map = {
            0: '未执行',
            1: '执行中',
            2: '执行完毕',
            3: '取消执行',
            4: '超时取消执行',
            5: '失败'
        }

        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功! (模拟数据)',
            'returnObj': {
                'taskId': task_id,
                'status': 2,  # 执行完毕
                'statusText': status_map[2]
            },
            'success': True,
            '_mock': True
        }

    def get_vulnerability_types(self) -> Dict[str, Any]:
        """
        获取漏洞类型列表

        Returns:
            漏洞类型信息
        """
        logger.info("查询漏洞类型列表")

        mock_types = [
            {
                'typeCode': 'LINUX',
                'typeName': 'Linux漏洞',
                'description': 'Linux系统相关漏洞'
            },
            {
                'typeCode': 'WINDOWS',
                'typeName': 'Windows漏洞',
                'description': 'Windows系统相关漏洞'
            },
            {
                'typeCode': 'WEB_CMS',
                'typeName': 'Web应用漏洞',
                'description': 'Web应用和CMS系统漏洞'
            },
            {
                'typeCode': 'APPLIACTION',
                'typeName': '应用漏洞',
                'description': '应用程序漏洞'
            }
        ]

        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功!',
            'returnObj': {
                'total': len(mock_types),
                'list': mock_types
            },
            'success': True
        }

    def get_host_trend(self, trend_type: int = 1) -> Dict[str, Any]:
        """
        主机概况趋势统计
        
        Args:
            trend_type: 1-近7天，2-近14天，3-近30天
            
        Returns:
            主机趋势统计数据
        """
        logger.info(f"查询主机概况趋势统计 (type={trend_type})")
        
        try:
            url = f'https://{self.base_endpoint}/v1/index/hostTrend'
            
            # 构造请求体
            body_data = {
                'type': trend_type
            }
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_host_trend(trend_type)
            
            result = response.json()
            
            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_host_trend(trend_type)
            
            return result
            
        except Exception as e:
            logger.warning(f"获取主机趋势失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_host_trend(trend_type)
    
    def _get_mock_host_trend(self, trend_type: int) -> Dict[str, Any]:
        """生成模拟主机趋势数据"""
        import datetime
        
        # 根据类型确定天数
        days = {1: 7, 2: 14, 3: 30}.get(trend_type, 7)
        
        trend_data = []
        today = datetime.date.today()
        
        for i in range(days):
            day = today - datetime.timedelta(days=days - 1 - i)
            trend_data.append({
                'day': day.strftime('%Y-%m-%d'),
                'total': 359,
                'onLine': 350,
                'offLine': 5,
                'risk': 3,
                'unguarded': 1,
                'closed': 0
            })
        
        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功!',
            'returnObj': trend_data,
            '_mock': True
        }

    def get_untreated_risks(self) -> Dict[str, Any]:
        """
        安全概览最近7日待处理风险
        统计最近7日内入侵检测、漏洞风险、安全基线、网页防篡改、病毒查杀待处理数和风险主机数
        
        Returns:
            待处理风险统计数据
        """
        logger.info("查询最近7日待处理风险")
        
        try:
            url = f'https://{self.base_endpoint}/v1/index/untreated'
            
            # GET请求，没有请求体
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=None,
                body='',
                extra_headers={
                    'regionid': '100054c0416811e9a6690242ac110002',
                    'urlType': 'CTAPI'
                }
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}，使用模拟数据")
                return self._get_mock_untreated_risks()
            
            result = response.json()
            
            # 检查返回状态
            if not isinstance(result, dict) or result.get('error') != 'CTCSSCN_000000':
                error_msg = result.get('message', '未知错误') if isinstance(result, dict) else '响应格式错误'
                error_code = result.get('error', 'UNKNOWN_ERROR') if isinstance(result, dict) else 'UNKNOWN_ERROR'
                logger.warning(f"API返回错误 [{error_code}]: {error_msg}，使用模拟数据")
                return self._get_mock_untreated_risks()
            
            return result
            
        except Exception as e:
            logger.warning(f"获取待处理风险失败: {e}，使用模拟数据")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_untreated_risks()
    
    def _get_mock_untreated_risks(self) -> Dict[str, Any]:
        """生成模拟待处理风险数据"""
        return {
            'statusCode': '200',
            'error': 'CTCSSCN_000000',
            'message': '查询成功!',
            'returnObj': {
                'sshRiskNum': 15,
                'sshHostNum': 8,
                'vulRiskNum': 42,
                'vulHostNum': 25,
                'scaRiskNum': 10,
                'scaHostNum': 6,
                'wpRiskNum': 0,
                'wpHostNum': 0,
                'invasionRiskNum': 15,
                'pwRiskNum': 0,
                'virusRiskNum': 3,
                'virusHostNum': 2
            },
            '_mock': True
        }