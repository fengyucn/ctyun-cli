"""
云硬盘(EBS)服务客户端
"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class EBSClient:
    """天翼云云硬盘(EBS)服务客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化云硬盘服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'ebs'
        self.base_endpoint = 'ebs-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def list_ebs(self, region_id: str, page_no: int = 1, page_size: int = 10,
                 dec_pool_id: Optional[str] = None,
                 dec_pool_name: Optional[str] = None,
                 az_name: Optional[str] = None,
                 project_id: Optional[str] = None,
                 disk_type: Optional[str] = None,
                 disk_mode: Optional[str] = None,
                 disk_status: Optional[str] = None,
                 multi_attach: Optional[str] = None,
                 is_system_volume: Optional[str] = None,
                 is_encrypt: Optional[str] = None,
                 query_content: Optional[str] = None,
                 query_keys: Optional[str] = None) -> Dict[str, Any]:
        """
        查询云硬盘列表
        
        Args:
            region_id: 资源池ID
            page_no: 页编号，默认1
            page_size: 页大小，默认10，最大300
            dec_pool_id: 专属云存储池ID
            dec_pool_name: 专属云存储池名称
            az_name: 可用区
            project_id: 企业项目
            disk_type: 云硬盘类型（SATA/SAS/SSD/FAST-SSD/XSSD-0等）
            disk_mode: 云硬盘模式（VBD/ISCSI/FCSAN）
            disk_status: 云硬盘状态（in-use/available/diskAttaching等）
            multi_attach: 是否共享盘（true/false）
            is_system_volume: 是否为系统盘（true/false）
            is_encrypt: 是否加密盘（true/false）
            query_content: 模糊查询内容
            query_keys: 指定模糊查询的键（name/diskID/instanceID/instanceName）
            
        Returns:
            云硬盘列表
        """
        logger.info(f"查询云硬盘列表: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ebs/list-ebs'
            
            query_params = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            if dec_pool_id:
                query_params['decPoolID'] = dec_pool_id
            if dec_pool_name:
                query_params['decPoolName'] = dec_pool_name
            if az_name:
                query_params['azName'] = az_name
            if project_id:
                query_params['projectID'] = project_id
            if disk_type:
                query_params['diskType'] = disk_type
            if disk_mode:
                query_params['diskMode'] = disk_mode
            if disk_status:
                query_params['diskStatus'] = disk_status
            if multi_attach is not None:
                query_params['multiAttach'] = multi_attach
            if is_system_volume is not None:
                query_params['isSystemVolume'] = is_system_volume
            if is_encrypt is not None:
                query_params['isEncrypt'] = is_encrypt
            if query_content:
                query_params['queryContent'] = query_content
            if query_keys:
                query_params['queryKeys'] = query_keys
            
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {query_params}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()

            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")

            return result

        except Exception as e:
            logger.error(f"查询云硬盘列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    # ==================== 新增查询类 API（6个） ====================

    def _get(self, path: str, query_params: Dict) -> Dict[str, Any]:
        """通用 GET 请求"""
        url = f'https://{self.base_endpoint}{path}'
        filtered = {k: v for k, v in query_params.items() if v is not None}
        try:
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=filtered, body='',
                extra_headers={}
            )
            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {filtered}")

            response = self.client.session.get(
                url, params=filtered, headers=headers, timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}: {response.text}',
                    'returnObj': None
                }
            return response.json()
        except Exception as e:
            logger.error(f"GET {path} 失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    def get_ebs_info(self, region_id: str, disk_id: str) -> Dict[str, Any]:
        """查询云硬盘详情（基于diskID）- GET /v4/ebs/info-ebs"""
        logger.info(f"查询云硬盘详情: regionId={region_id}, diskID={disk_id}")
        return self._get('/v4/ebs/info-ebs', {
            'regionID': region_id, 'diskID': disk_id,
        })

    def get_ebs_info_by_name(self, region_id: str, disk_name: str) -> Dict[str, Any]:
        """查询云硬盘详情（基于regionID和diskName）- GET /v4/ebs/info-by-name-ebs"""
        logger.info(f"查询云硬盘详情(by name): regionId={region_id}, diskName={disk_name}")
        return self._get('/v4/ebs/info-by-name-ebs', {
            'regionID': region_id, 'diskName': disk_name,
        })

    def list_ebs_by_name(self, region_id: str, disk_name: str,
                         page_no: Optional[int] = None,
                         page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询云硬盘列表（基于regionID和diskName）- GET /v4/ebs/list-by-name-ebs"""
        logger.info(f"查询云硬盘列表(by name): regionId={region_id}, diskName={disk_name}")
        return self._get('/v4/ebs/list-by-name-ebs', {
            'regionID': region_id, 'diskName': disk_name,
            'pageNo': page_no, 'pageSize': page_size,
        })

    def list_ebs_snapshots(self, region_id: str,
                           disk_id: Optional[str] = None,
                           snapshot_id: Optional[str] = None,
                           snapshot_name: Optional[str] = None,
                           snapshot_status: Optional[str] = None,
                           snapshot_type: Optional[str] = None,
                           volume_attr: Optional[str] = None,
                           retention_policy: Optional[str] = None,
                           max_results: Optional[int] = None,
                           next_token: Optional[str] = None) -> Dict[str, Any]:
        """查询云硬盘快照列表 - GET /v4/ebs_snapshot/list-ebs-snap"""
        logger.info(f"查询云硬盘快照列表: regionId={region_id}")
        return self._get('/v4/ebs_snapshot/list-ebs-snap', {
            'regionID': region_id, 'diskID': disk_id, 'snapshotID': snapshot_id,
            'snapshotName': snapshot_name, 'snapshotStatus': snapshot_status,
            'snapshotType': snapshot_type, 'volumeAttr': volume_attr,
            'retentionPolicy': retention_policy,
            'maxResults': max_results, 'nextToken': next_token,
        })

    def query_ebs_snapshot_size(self, region_id: str) -> Dict[str, Any]:
        """查询云硬盘快照使用量 - GET /v4/ebs_snapshot/query_size-ebs-snap"""
        logger.info(f"查询云硬盘快照使用量: regionId={region_id}")
        return self._get('/v4/ebs_snapshot/query_size-ebs-snap', {
            'regionID': region_id,
        })

    def query_ebs_snapshot_policy(self, region_id: str,
                                  snapshot_policy_id: Optional[str] = None,
                                  snapshot_policy_name: Optional[str] = None) -> Dict[str, Any]:
        """查询云硬盘自动快照策略 - GET /v4/ebs_snapshot/query-policy-ebs-snap"""
        logger.info(f"查询云硬盘自动快照策略: regionId={region_id}")
        return self._get('/v4/ebs_snapshot/query-policy-ebs-snap', {
            'regionID': region_id,
            'snapshotPolicyID': snapshot_policy_id,
            'snapshotPolicyName': snapshot_policy_name,
        })
