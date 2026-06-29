"""
物理机(DPS)管理模块 - 使用OpenAPI V4
"""

from typing import Dict, Any, Optional, List
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class DPSClient:
    """物理机(DPS)客户端 - OpenAPI V4"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.service = 'dps'
        self.base_endpoint = 'ebm-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _get(self, path: str, query_params: Dict[str, Any], desc: str) -> Dict[str, Any]:
        url = f'https://{self.base_endpoint}{path}'
        headers = self.eop_auth.sign_request(
            method='GET', url=url, query_params=query_params, body=None
        )
        try:
            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"DPS API错误 [{error_code}]: {error_msg}")
            logger.info(f"成功{desc}")
            return data
        except Exception as e:
            logger.error(f"{desc}失败: {str(e)}")
            raise

    def list_os(self, region_id: str, az_name: str,
                page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询操作系统列表 - GET /v4/ebm/list-os"""
        logger.info(f"查询操作系统列表: regionID={region_id}, azName={az_name}")
        query_params: Dict[str, Any] = {'regionID': region_id, 'azName': az_name}
        if page_no is not None:
            query_params['pageNo'] = page_no
        if page_size is not None:
            query_params['pageSize'] = page_size
        return self._get('/v4/ebm/list-os', query_params, '查询操作系统列表')

    def list_metadata(self, region_id: str, az_name: str, instance_uuid: str,
                      metadata_key: Optional[str] = None) -> Dict[str, Any]:
        """物理机元数据查询 - GET /v4/ebm/metadata/list"""
        logger.info(f"查询物理机元数据: regionID={region_id}, instanceUUID={instance_uuid}")
        query_params: Dict[str, Any] = {
            'regionID': region_id, 'azName': az_name, 'instanceUUID': instance_uuid
        }
        if metadata_key:
            query_params['metadataKey'] = metadata_key
        return self._get('/v4/ebm/metadata/list', query_params, '查询物理机元数据')

    def list_interfaces(self, region_id: str, az_name: str, instance_uuid: str) -> Dict[str, Any]:
        """物理机查询网卡信息 - GET /v4/ebm/instance-interface-list"""
        logger.info(f"查询物理机网卡信息: regionID={region_id}, instanceUUID={instance_uuid}")
        query_params = {
            'regionID': region_id, 'azName': az_name, 'instanceUUID': instance_uuid
        }
        return self._get('/v4/ebm/instance-interface-list', query_params, '查询物理机网卡信息')

    def list_attached_volume_ids(self, region_id: str, az_name: str, instance_uuid: str) -> Dict[str, Any]:
        """物理机查询挂载卷ID列表信息 - GET /v4/ebm/instance-attached-volume-id-list"""
        logger.info(f"查询物理机挂载卷ID: regionID={region_id}, instanceUUID={instance_uuid}")
        query_params = {
            'regionID': region_id, 'azName': az_name, 'instanceUUID': instance_uuid
        }
        return self._get('/v4/ebm/instance-attached-volume-id-list', query_params, '查询物理机挂载卷ID')

    def get_instance_image(self, region_id: str, az_name: str, instance_uuid: str) -> Dict[str, Any]:
        """查询物理机所使用镜像的信息 - GET /v4/ebm/instance-image"""
        logger.info(f"查询物理机镜像信息: regionID={region_id}, instanceUUID={instance_uuid}")
        query_params = {
            'regionID': region_id, 'azName': az_name, 'instanceUUID': instance_uuid
        }
        return self._get('/v4/ebm/instance-image', query_params, '查询物理机镜像信息')

    def get_device_stock(self, region_id: str, az_name: str,
                         device_type: Optional[str] = None,
                         count: Optional[int] = None) -> Dict[str, Any]:
        """物理机查询库存 - GET /v4/ebm/device-s"""
        logger.info(f"查询物理机库存: regionID={region_id}, azName={az_name}")
        query_params: Dict[str, Any] = {'regionID': region_id, 'azName': az_name}
        if device_type:
            query_params['deviceType'] = device_type
        if count is not None:
            query_params['count'] = count
        return self._get('/v4/ebm/device-stock-list', query_params, '查询物理机库存')

    def describe_instance(self, region_id: str, az_name: str, instance_uuid: str) -> Dict[str, Any]:
        """查询单台物理机 - GET /v4/ebm/describe-instance"""
        logger.info(f"查询单台物理机: regionID={region_id}, instanceUUID={instance_uuid}")
        query_params = {
            'regionID': region_id, 'azName': az_name, 'instanceUUID': instance_uuid
        }
        return self._get('/v4/ebm/describe-instance', query_params, '查询单台物理机')

    def list_instances(self, region_id: str, az_name: str,
                       resource_id: Optional[str] = None, ip: Optional[str] = None,
                       instance_name: Optional[str] = None, vpc_id: Optional[str] = None,
                       subnet_id: Optional[str] = None, device_type: Optional[str] = None,
                       device_uuid_list: Optional[str] = None, query_content: Optional[str] = None,
                       instance_uuid_list: Optional[str] = None, instance_uuid: Optional[str] = None,
                       status: Optional[str] = None, sort: Optional[str] = None,
                       asc: Optional[bool] = None, vip_id: Optional[str] = None,
                       volume_uuid: Optional[str] = None,
                       page_no: Optional[int] = None, page_size: Optional[int] = None,
                       project_id: Optional[str] = None) -> Dict[str, Any]:
        """批量查询物理机 - GET /v4/ebm/list-instance"""
        logger.info(f"批量查询物理机: regionID={region_id}, azName={az_name}")
        query_params: Dict[str, Any] = {'regionID': region_id, 'azName': az_name}
        optional_params = {
            'resourceID': resource_id, 'ip': ip, 'instanceName': instance_name,
            'vpcID': vpc_id, 'subnetID': subnet_id, 'deviceType': device_type,
            'deviceUUIDList': device_uuid_list, 'queryContent': query_content,
            'instanceUUIDList': instance_uuid_list, 'instanceUUID': instance_uuid,
            'status': status, 'sort': sort, 'vipID': vip_id, 'volumeUUID': volume_uuid,
            'projectID': project_id,
        }
        for key, val in optional_params.items():
            if val is not None:
                query_params[key] = val
        if asc is not None:
            query_params['asc'] = str(asc).lower()
        if page_no is not None:
            query_params['pageNo'] = page_no
        if page_size is not None:
            query_params['pageSize'] = page_size
        return self._get('/v4/ebm/list-instance', query_params, '批量查询物理机')
