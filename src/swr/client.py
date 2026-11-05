"""容器镜像服务(SWR)客户端"""

from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode

from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class SWRClient:
    """容器镜像服务客户端（终端节点 crs-global.ctapi.ctyun.cn）"""

    ENDPOINT = 'crs-global.ctapi.ctyun.cn'

    def __init__(self, client):
        self.client = client
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _get(self, path: str, region_id: str, query_params: Optional[Dict[str, Any]] = None,
             desc: str = 'SWR查询') -> Dict[str, Any]:
        url = f'https://{self.ENDPOINT}{path}'
        qp = {k: str(v).lower() if isinstance(v, bool) else str(v)
              for k, v in (query_params or {}).items() if v is not None}
        try:
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=qp, body='',
                extra_headers={'regionId': region_id})
            # 与签名编码保持一致（quote 空格->%20），避免 requests params= 编码差异导致 403
            encoded_qs = urlencode(qp, quote_via=quote)
            full_url = f"{url}?{encoded_qs}" if encoded_qs else url
            response = self.client.session.get(full_url, headers=headers,
                                               timeout=30)
            logger.debug(f"{desc}响应: {response.text[:500]}")
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text[:200]}',
                        'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    def list_instances(self, region_id: str, instance_name: Optional[str] = None,
                       all_region: bool = False, page_num: int = 1,
                       page_size: int = 50) -> Dict[str, Any]:
        """查询镜像实例列表 - GET /v2/listInstance

        Args:
            region_id: 资源池ID（header regionId）
            instance_name: 实例名称（包含匹配，可选）
            all_region: 是否查询所有资源池的实例
            page_num: 页码（默认1）
            page_size: 每页数量（默认50）
        """
        logger.info(f"查询SWR实例列表: regionId={region_id}, allRegion={all_region}")
        return self._get('/v2/listInstance', region_id, {
            'instanceName': instance_name, 'allRegion': all_region,
            'pageNum': page_num, 'pageSize': page_size}, desc='查询SWR实例列表')

    def list_repositories(self, region_id: str, instance_id: str,
                          page_num: int = 1,
                          page_size: int = 50) -> Dict[str, Any]:
        """查询镜像仓库列表 - GET /v2/listRepository

        Args:
            region_id: 实例所属资源池ID（header regionId，取实例列表返回的region）
            instance_id: 实例ID
            page_num: 页码（默认1）
            page_size: 每页数量（默认50）
        """
        logger.info(f"查询SWR镜像仓库列表: regionId={region_id}, instanceId={instance_id}")
        return self._get('/v2/listRepository', region_id, {
            'instanceId': instance_id, 'pageNum': page_num,
            'pageSize': page_size}, desc='查询SWR镜像仓库列表')

    def get_instance(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """查询实例详情 - GET /v2/getInstance

        Args:
            region_id: 资源池ID（header regionId）
            instance_id: 实例ID
        """
        logger.info(f"查询SWR实例详情: regionId={region_id}, instanceId={instance_id}")
        return self._get('/v2/getInstance', region_id, {'instanceId': instance_id},
                         desc='查询SWR实例详情')

    def get_instance_usage(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """查询实例配额 - GET /v2/getInstanceUsage

        Args:
            region_id: 资源池ID（header regionId）
            instance_id: 实例ID
        """
        logger.info(f"查询SWR实例配额: regionId={region_id}, instanceId={instance_id}")
        return self._get('/v2/getInstanceUsage', region_id, {'instanceId': instance_id},
                         desc='查询SWR实例配额')

    def list_instance_regions(self, region_id: str) -> Dict[str, Any]:
        """查询实例Region列表 - GET /v2/listInstanceRegion

        Args:
            region_id: 资源池ID（header regionId）
        """
        logger.info(f"查询SWR实例Region列表: regionId={region_id}")
        return self._get('/v2/listInstanceRegion', region_id, None,
                         desc='查询SWR实例Region列表')

    def get_instance_count(self, region_id: str, all_region: bool = False) -> Dict[str, Any]:
        """查询用户实例个数 - GET /v2/getInstanceCount"""
        logger.info(f"查询SWR实例个数: regionId={region_id}, allRegion={all_region}")
        return self._get('/v2/getInstanceCount', region_id, {'allRegion': all_region},
                         desc='查询SWR实例个数')

    def get_storage_config(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """查询对象存储配置 - GET /v2/getStorageConfig"""
        logger.info(f"查询SWR对象存储配置: instanceId={instance_id}")
        return self._get('/v2/getStorageConfig', region_id, {'instanceId': instance_id},
                         desc='查询SWR对象存储配置')

    # ==================== 命名空间 / 仓库 / 版本 ====================

    def list_namespaces(self, region_id: str, instance_id: str,
                        namespace_name: Optional[str] = None, page_num: int = 1,
                        page_size: int = 10) -> Dict[str, Any]:
        """查询镜像命名空间列表 - GET /v2/listNamespace"""
        logger.info(f"查询SWR命名空间列表: instanceId={instance_id}, page={page_num}")
        return self._get('/v2/listNamespace', region_id, {
            'instanceId': instance_id, 'namespaceName': namespace_name,
            'pageNum': page_num, 'pageSize': page_size}, desc='查询SWR命名空间列表')

    def get_namespace(self, region_id: str, instance_id: str,
                      namespace_name: str) -> Dict[str, Any]:
        """查询镜像命名空间详情 - GET /v2/getNamespace"""
        logger.info(f"查询SWR命名空间详情: namespace={namespace_name}")
        return self._get('/v2/getNamespace', region_id, {
            'instanceId': instance_id, 'namespaceName': namespace_name},
            desc='查询SWR命名空间详情')

    def get_repository(self, region_id: str, instance_id: str,
                       repository_id: str) -> Dict[str, Any]:
        """查询镜像仓库详情 - GET /v2/getRepository"""
        logger.info(f"查询SWR仓库详情: repositoryId={repository_id}")
        return self._get('/v2/getRepository', region_id, {
            'instanceId': instance_id, 'repositoryId': repository_id},
            desc='查询SWR仓库详情')

    def list_repo_tags(self, region_id: str, instance_id: str, repository_id: str,
                       tag_name: Optional[str] = None, page_num: int = 1,
                       page_size: int = 10) -> Dict[str, Any]:
        """查询镜像版本(Tag)列表 - GET /v2/listRepoTag"""
        logger.info(f"查询SWR镜像版本列表: repositoryId={repository_id}, page={page_num}")
        return self._get('/v2/listRepoTag', region_id, {
            'instanceId': instance_id, 'repositoryId': repository_id,
            'tagName': tag_name, 'pageNum': page_num, 'pageSize': page_size},
            desc='查询SWR镜像版本列表')

    def get_repo_tag(self, region_id: str, instance_id: str, repository_id: str,
                     tag_name: str) -> Dict[str, Any]:
        """查询指定版本镜像 - GET /v2/getRepoTag"""
        logger.info(f"查询SWR镜像版本详情: tag={tag_name}")
        return self._get('/v2/getRepoTag', region_id, {
            'instanceId': instance_id, 'repositoryId': repository_id,
            'tagName': tag_name}, desc='查询SWR镜像版本详情')

    def list_artifacts(self, region_id: str, instance_id: str, repository_id: str,
                       page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """查询制品列表 - GET /v2/listArtifact"""
        logger.info(f"查询SWR制品列表: repositoryId={repository_id}, page={page_num}")
        return self._get('/v2/listArtifact', region_id, {
            'instanceId': instance_id, 'repositoryId': repository_id,
            'pageNum': page_num, 'pageSize': page_size}, desc='查询SWR制品列表')

    def get_artifact(self, region_id: str, instance_id: str, repository_id: str,
                     reference: str) -> Dict[str, Any]:
        """查询制品详情 - GET /v2/getArtifact"""
        logger.info(f"查询SWR制品详情: reference={reference}")
        return self._get('/v2/getArtifact', region_id, {
            'instanceId': instance_id, 'repositoryId': repository_id,
            'reference': reference}, desc='查询SWR制品详情')

    # ==================== Chart 命名空间 / 仓库 / 版本 ====================

    def list_chart_namespaces(self, region_id: str, instance_id: str,
                              namespace_name: Optional[str] = None, page_num: int = 1,
                              page_size: int = 10) -> Dict[str, Any]:
        """查询HelmChart命名空间列表 - GET /v2/listChartNamespace"""
        logger.info(f"查询SWR Chart命名空间列表: instanceId={instance_id}, page={page_num}")
        return self._get('/v2/listChartNamespace', region_id, {
            'instanceId': instance_id, 'namespaceName': namespace_name,
            'pageNum': page_num, 'pageSize': page_size},
            desc='查询SWR Chart命名空间列表')

    def get_chart_namespace(self, region_id: str, instance_id: str,
                            namespace_name: str) -> Dict[str, Any]:
        """查询HelmChart命名空间详情 - GET /v2/getChartNamespace"""
        logger.info(f"查询SWR Chart命名空间详情: namespace={namespace_name}")
        return self._get('/v2/getChartNamespace', region_id, {
            'instanceId': instance_id, 'namespaceName': namespace_name},
            desc='查询SWR Chart命名空间详情')

    def list_chart_repositories(self, region_id: str, instance_id: str,
                                namespace_name: Optional[str] = None,
                                repository_name: Optional[str] = None,
                                page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """查询Chart仓库列表 - GET /v2/listChartRepository"""
        logger.info(f"查询SWR Chart仓库列表: instanceId={instance_id}, page={page_num}")
        return self._get('/v2/listChartRepository', region_id, {
            'instanceId': instance_id, 'namespaceName': namespace_name,
            'repositoryName': repository_name, 'pageNum': page_num,
            'pageSize': page_size}, desc='查询SWR Chart仓库列表')

    def list_chart_tags(self, region_id: str, instance_id: str, repository_id: str,
                        tag_name: Optional[str] = None, page_num: int = 1,
                        page_size: int = 10) -> Dict[str, Any]:
        """查询Chart版本列表 - GET /v2/listChartTag"""
        logger.info(f"查询SWR Chart版本列表: repositoryId={repository_id}, page={page_num}")
        return self._get('/v2/listChartTag', region_id, {
            'instanceId': instance_id, 'repositoryId': repository_id,
            'tagName': tag_name, 'pageNum': page_num, 'pageSize': page_size},
            desc='查询SWR Chart版本列表')
