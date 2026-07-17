"""对象存储(ZOS)客户端"""

import json
from typing import Dict, Any, Optional
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class ZOSClient:
    """天翼云对象存储(ZOS)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.service = 'zos'
        self.base_endpoint = 'zos-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _get(self, path: str, query_params: Dict) -> Dict[str, Any]:
        """通用GET请求"""
        url = f'https://{self.base_endpoint}{path}'
        headers = self.eop_auth.sign_request(
            method='GET', url=url, query_params=query_params,
            body=None, extra_headers={}
        )
        logger.debug(f"请求URL: {url}")
        logger.debug(f"查询参数: {query_params}")

        try:
            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=30, verify=False
            )
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP_{response.status_code}: {response.text}',
                }
            return response.json()
        except Exception as e:
            logger.error(f"GET请求失败: {str(e)}")
            return {'statusCode': 500, 'message': str(e)}

    def _post(self, path: str, body_data: Dict) -> Dict[str, Any]:
        """通用POST请求"""
        url = f'https://{self.base_endpoint}{path}'
        body = json.dumps(body_data)
        headers = self.eop_auth.sign_request(
            method='POST', url=url, query_params=None,
            body=body, extra_headers={}
        )
        logger.debug(f"请求URL: {url}")
        logger.debug(f"请求体: {body}")

        try:
            response = self.client.session.post(
                url, data=body, headers=headers, timeout=30, verify=False
            )
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP_{response.status_code}: {response.text}',
                }
            return response.json()
        except Exception as e:
            logger.error(f"POST请求失败: {str(e)}")
            return {'statusCode': 500, 'message': str(e)}

    # ==================== 桶查询管理 ====================

    def list_buckets(self, region_id: str, project_id: Optional[str] = None,
                     page_size: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        """查询所有桶 - GET /v4/oss/list-buckets"""
        params = {'regionID': region_id}
        if project_id:
            params['projectID'] = project_id
        if page_size is not None:
            params['pageSize'] = page_size
        if page_no is not None:
            params['pageNo'] = page_no
        return self._get('/v4/oss/list-buckets', params)

    def get_bucket_info(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶信息 - GET /v4/oss/get-bucket-info"""
        return self._get('/v4/oss/get-bucket-info', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_location(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶位置信息 - GET /v4/oss/get-bucket-location"""
        return self._get('/v4/oss/get-bucket-location', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_statistics(self, region_id: str, start_time: str, end_time: str,
                              bucket: Optional[str] = None) -> Dict[str, Any]:
        """查询桶统计信息 - GET /v4/oss/get-bucket-statistics"""
        params = {'regionID': region_id, 'startTime': start_time, 'endTime': end_time}
        if bucket:
            params['bucket'] = bucket
        return self._get('/v4/oss/get-bucket-statistics', params)

    def head_bucket(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶访问权限 - GET /v4/oss/head-bucket"""
        return self._get('/v4/oss/head-bucket', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_versioning(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶版本控制配置 - GET /v4/oss/get-bucket-versioning"""
        return self._get('/v4/oss/get-bucket-versioning', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_tagging(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶标签 - GET /v4/oss/get-bucket-tagging"""
        return self._get('/v4/oss/get-bucket-tagging', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_policy(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶策略 - GET /v4/oss/get-bucket-policy"""
        return self._get('/v4/oss/get-bucket-policy', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_encryption(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶的加密配置 - GET /v4/oss/get-bucket-encryption"""
        return self._get('/v4/oss/get-bucket-encryption', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_logging(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶日志转存配置 - GET /v4/oss/get-bucket-logging"""
        return self._get('/v4/oss/get-bucket-logging', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_lifecycle(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询桶生命周期配置 - GET /v4/oss/get-bucket-lifecycle-conf"""
        return self._get('/v4/oss/get-bucket-lifecycle-conf', {'bucket': bucket, 'regionID': region_id})

    def get_object_num(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询对象桶对象数量(不含碎片) - GET /v4/oss/get-object-num"""
        return self._get('/v4/oss/get-object-num', {'bucket': bucket, 'regionID': region_id})

    def get_fragment_num(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """查询对象桶碎片数量 - GET /v4/oss/get-fragment-num"""
        return self._get('/v4/oss/get-fragment-num', {'bucket': bucket, 'regionID': region_id})

    def get_bucket_acl(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """获取桶ACL - GET /v4/oss/get-bucket-acl"""
        return self._get('/v4/oss/get-bucket-acl', {'bucket': bucket, 'regionID': region_id})

    def get_object_lock_conf(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """获取桶的合规保留策略 - GET /v4/oss/get-object-lock-conf"""
        return self._get('/v4/oss/get-object-lock-conf', {'bucket': bucket, 'regionID': region_id})

    # ==================== 对象查询管理 ====================

    def list_objects(self, region_id: str, bucket: str,
                     delimiter: Optional[str] = None, marker: Optional[str] = None,
                     max_keys: Optional[int] = None, prefix: Optional[str] = None) -> Dict[str, Any]:
        """查看对象列表 - GET /v4/oss/list-objects"""
        params = {'bucket': bucket, 'regionID': region_id}
        if delimiter is not None:
            params['delimiter'] = delimiter
        if marker is not None:
            params['marker'] = marker
        if max_keys is not None:
            params['maxKeys'] = max_keys
        if prefix is not None:
            params['prefix'] = prefix
        return self._get('/v4/oss/list-objects', params)

    def list_object_versions(self, region_id: str, bucket: str,
                             key_marker: Optional[str] = None,
                             prefix: Optional[str] = None) -> Dict[str, Any]:
        """查询对象版本信息 - GET /v4/oss/list-object-versions"""
        params = {'bucket': bucket, 'regionID': region_id}
        if key_marker is not None:
            params['keyMarker'] = key_marker
        if prefix is not None:
            params['prefix'] = prefix
        return self._get('/v4/oss/list-object-versions', params)

    def head_object(self, region_id: str, bucket: str, key: str,
                    version_id: Optional[str] = None) -> Dict[str, Any]:
        """查询对象是否存在 - GET /v4/oss/head-object"""
        params = {'bucket': bucket, 'regionID': region_id, 'key': key}
        if version_id:
            params['versionID'] = version_id
        return self._get('/v4/oss/head-object', params)

    def get_object_tagging(self, region_id: str, bucket: str, key: str,
                           version_id: Optional[str] = None) -> Dict[str, Any]:
        """查询对象标签 - GET /v4/oss/get-object-tagging"""
        params = {'bucket': bucket, 'key': key, 'regionID': region_id}
        if version_id:
            params['versionID'] = version_id
        return self._get('/v4/oss/get-object-tagging', params)

    def get_object_acl(self, region_id: str, bucket: str, key: str,
                       version_id: Optional[str] = None) -> Dict[str, Any]:
        """获取对象ACL - GET /v4/oss/get-object-acl"""
        params = {'bucket': bucket, 'key': key, 'regionID': region_id}
        if version_id:
            params['versionID'] = version_id
        return self._get('/v4/oss/get-object-acl', params)

    def get_object_retention(self, region_id: str, bucket: str, key: str,
                             version_id: str) -> Dict[str, Any]:
        """获取对象保留期限配置 - GET /v4/oss/get-object-retention"""
        return self._get('/v4/oss/get-object-retention', {
            'bucket': bucket, 'regionID': region_id, 'key': key, 'versionID': version_id,
        })

    def list_all_parts(self, region_id: str, bucket: str,
                       page: Optional[int] = None, page_size: Optional[int] = None,
                       page_no: Optional[int] = None) -> Dict[str, Any]:
        """查询桶内碎片列表 - GET /v4/oss/list-all-parts"""
        params = {'bucket': bucket, 'regionID': region_id}
        if page is not None:
            params['page'] = page
        if page_size is not None:
            params['pageSize'] = page_size
        if page_no is not None:
            params['pageNo'] = page_no
        return self._get('/v4/oss/list-all-parts', params)

    def list_multipart_uploads(self, region_id: str, bucket: str,
                               key_marker: Optional[str] = None,
                               upload_id_marker: Optional[str] = None,
                               max_uploads: Optional[int] = None,
                               prefix: Optional[str] = None) -> Dict[str, Any]:
        """查询正在进行中的分段上传 - GET /v4/oss/list-multipart-uploads"""
        params = {'bucket': bucket, 'regionID': region_id}
        if key_marker is not None:
            params['keyMarker'] = key_marker
        if upload_id_marker is not None:
            params['uploadIDMarker'] = upload_id_marker
        if max_uploads is not None:
            params['maxUploads'] = max_uploads
        if prefix is not None:
            params['prefix'] = prefix
        return self._get('/v4/oss/list-multipart-uploads', params)

    def list_parts(self, region_id: str, bucket: str, key: str, upload_id: str,
                   max_parts: Optional[int] = None,
                   part_number_marker: Optional[int] = None) -> Dict[str, Any]:
        """列出上传对象的全部分段 - GET /v4/oss/list-parts"""
        params = {'regionID': region_id, 'bucket': bucket, 'key': key, 'uploadID': upload_id}
        if max_parts is not None:
            params['maxParts'] = max_parts
        if part_number_marker is not None:
            params['partNumberMarker'] = part_number_marker
        return self._get('/v4/oss/list-parts', params)

    def list_migration_failed_detail(self, region_id: str, migration_id: str,
                                     page_size: Optional[int] = None,
                                     page_no: Optional[int] = None) -> Dict[str, Any]:
        """查询迁移任务的失败对象列表 - GET /v4/zms/list-migration-failed-detail"""
        params = {'regionID': region_id, 'migrationID': migration_id}
        if page_size is not None:
            params['pageSize'] = page_size
        if page_no is not None:
            params['pageNo'] = page_no
        return self._get('/v4/zms/list-migration-failed-detail', params)

    def get_endpoint(self, region_id: str) -> Dict[str, Any]:
        """查询访问控制endpoint - GET /v4/oss/get-endpoint"""
        return self._get('/v4/oss/get-endpoint', {'regionID': region_id})

    # ==================== 权限/资源池查询 ====================

    def get_keys(self, region_id: str) -> Dict[str, Any]:
        """查询ACCESS_KEY以及SECRET_KEY - GET /v4/oss/get-keys"""
        return self._get('/v4/oss/get-keys', {'regionID': region_id})

    def list_roles(self, region_id: str, keyword: Optional[str] = None,
                   page_size: Optional[int] = None,
                   page: Optional[int] = None,
                   page_no: Optional[int] = None) -> Dict[str, Any]:
        """查询角色列表 - GET /v4/oss/list-roles"""
        params = {'regionID': region_id}
        if keyword is not None:
            params['keyword'] = keyword
        if page_size is not None:
            params['pageSize'] = page_size
        if page is not None:
            params['page'] = page
        if page_no is not None:
            params['pageNo'] = page_no
        return self._get('/v4/oss/list-roles', params)

    def get_role_detail(self, region_id: str, role_name: str) -> Dict[str, Any]:
        """查询角色详情 - GET /v4/oss/role/detail"""
        return self._get('/v4/oss/role/detail', {'regionID': region_id, 'roleName': role_name})

    def list_policies(self, region_id: str, keyword: Optional[str] = None,
                      page_size: Optional[int] = None,
                      page: Optional[int] = None,
                      page_no: Optional[int] = None) -> Dict[str, Any]:
        """查询策略列表 - GET /v4/oss/list-policies"""
        params = {'regionID': region_id}
        if keyword is not None:
            params['keyword'] = keyword
        if page_size is not None:
            params['pageSize'] = page_size
        if page is not None:
            params['page'] = page
        if page_no is not None:
            params['pageNo'] = page_no
        return self._get('/v4/oss/list-policies', params)

    def get_policy_detail(self, region_id: str, policy_name: str) -> Dict[str, Any]:
        """查询策略详情 - GET /v4/oss/policy/detail"""
        return self._get('/v4/oss/policy/detail', {'regionID': region_id, 'policyName': policy_name})

    def list_regions(self) -> Dict[str, Any]:
        """查询所有对象存储资源池 - GET /v4/oss/list-regions"""
        return self._get('/v4/oss/list-regions', {})

    # ==================== 服务管理查询 ====================

    def get_oss_service_status(self, region_id: str) -> Dict[str, Any]:
        """查询对象存储开通状态 - GET /v4/oss/get-oss-service-status"""
        return self._get('/v4/oss/get-oss-service-status', {'regionID': region_id})

    def get_user_event_bridge(self, region_id: str) -> Dict[str, Any]:
        """获取对象存储用户级事件总线状态 - GET /v4/oss/get-user-event-bridge"""
        return self._get('/v4/oss/get-user-event-bridge', {'regionID': region_id})

    # ==================== 标签管理 ====================

    def put_bucket_tagging(self, region_id: str, bucket: str,
                           tags: list) -> Dict[str, Any]:
        """设置桶标签 - POST /v4/oss/put-bucket-tagging"""
        return self._post('/v4/oss/put-bucket-tagging', {
            'bucket': bucket, 'regionID': region_id,
            'tagging': {'tagSet': [{'key': t['key'], 'value': t['value']} for t in tags]},
        })

    def put_object_tagging(self, region_id: str, bucket: str, key: str,
                           tags: list, version_id: Optional[str] = None) -> Dict[str, Any]:
        """设置对象标签 - POST /v4/oss/put-object-tagging"""
        body = {
            'bucket': bucket, 'key': key, 'regionID': region_id,
            'tagging': {'tagSet': [{'key': t['key'], 'value': t['value']} for t in tags]},
        }
        if version_id:
            body['versionID'] = version_id
        return self._post('/v4/oss/put-object-tagging', body)

    def delete_bucket_tagging(self, region_id: str, bucket: str) -> Dict[str, Any]:
        """删除桶标签 - POST /v4/oss/delete-bucket-tagging"""
        return self._post('/v4/oss/delete-bucket-tagging', {
            'bucket': bucket, 'regionID': region_id,
        })

    def delete_object_tagging(self, region_id: str, bucket: str, key: str,
                              version_id: Optional[str] = None) -> Dict[str, Any]:
        """删除对象标签 - POST /v4/oss/delete-object-tagging"""
        body = {'bucket': bucket, 'key': key, 'regionID': region_id}
        if version_id:
            body['versionID'] = version_id
        return self._post('/v4/oss/delete-object-tagging', body)

    def query_resource_package_price(
        self,
        region_id: str,
        pkg_type: str,
        pkg_spec_type: str,
        pkg_spec: int,
        cycle_cnt: int,
        cycle_type: str,
        order_num: int,
        storage_class: str,
    ) -> Dict[str, Any]:
        """
        询价ZOS资源包 - POST /v4/oss/new-order/query-price

        Args:
            region_id: 区域ID
            pkg_type: 资源包类型 (zosSize/zosMzSize/zosBytesSend/zosRequest/zosRetrievalFlow/zosRetrievalFrequency)
            pkg_spec_type: 资源包规格类型 (fixed/defined)
            pkg_spec: 资源包规格大小(GB)，请求次数包和数据取回次数包单位为万次
            cycle_cnt: 订购周期 (month最大36, year最大3)
            cycle_type: 订购周期类型 (month/year)
            order_num: 订购数量(最大50)
            storage_class: 存储类型 (STANDARD/STANDARD_IA/GLACIER)

        Returns:
            询价结果，包含 totalPrice / discountPrice / finalPrice / subOrderPrices
        """
        logger.info(f"询价ZOS资源包: regionID={region_id}, pkgType={pkg_type}, "
                    f"pkgSpec={pkg_spec}, cycleType={cycle_type}, cycleCnt={cycle_cnt}")

        url = f'https://{self.base_endpoint}/v4/oss/new-order/query-price'
        body_data = {
            'regionID': region_id,
            'pkgType': pkg_type,
            'pkgSpecType': pkg_spec_type,
            'pkgSpec': pkg_spec,
            'cycleCnt': cycle_cnt,
            'cycleType': cycle_type,
            'orderNum': order_num,
            'storageClass': storage_class,
        }
        body = json.dumps(body_data)

        headers = self.eop_auth.sign_request(
            method='POST', url=url, query_params=None, body=body, extra_headers={}
        )

        try:
            response = self.client.session.post(url, data=body, headers=headers, timeout=30)

            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text}',
                        'returnObj': None}

            result = response.json()
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")

            return result

        except Exception as e:
            logger.error(f"询价ZOS资源包失败: {str(e)}")
            raise
