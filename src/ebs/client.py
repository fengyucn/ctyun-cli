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
