"""
容器引擎(CCE)管理模块

天翼云容器引擎（Cloud Container Engine，CCE）是基于Kubernetes的企业级容器化服务平台。
提供完整的容器应用生命周期管理能力。
"""

from typing import Dict, Any, List, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class CCEClient:
    """容器引擎客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化CCE客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'cce'
        self.base_endpoint = 'ccse-global.ctapi.ctyun.cn'
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    # ========== 集群管理 ==========

    def create_cluster(self, region_id: str, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建集群

        Args:
            region_id: 区域ID
            cluster_config: 集群配置信息

        Returns:
            创建集群的响应结果
        """
        logger.info(f"创建集群: regionId={region_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters'

        headers = self.eop_auth.sign_request(
            method='POST',
            url=url,
            body=json.dumps(cluster_config),
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.post(url, json=cluster_config, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_clusters(self, region_id: str, page_size: int = 10, page_no: int = 1,
                      cluster_name: Optional[str] = None, res_pool_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询集群列表

        Args:
            region_id: 区域ID
            page_size: 每页条数
            page_no: 当前页码
            cluster_name: 集群名称（可选）
            res_pool_id: 资源池ID（可选）

        Returns:
            集群列表的响应结果
        """
        logger.info(f"查询集群列表: regionId={region_id}, pageSize={page_size}, pageNow={page_no}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/page'

        query_params = {
            'pageSize': page_size,
            'pageNow': page_no
        }

        if cluster_name:
            query_params['clusterName'] = cluster_name
        if res_pool_id:
            query_params['resPoolId'] = res_pool_id

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def describe_cluster(self, region_id: str, cluster_id: str) -> Dict[str, Any]:
        """
        查询集群详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID

        Returns:
            集群详情的响应结果
        """
        logger.info(f"查询集群详情: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def delete_cluster(self, region_id: str, cluster_id: str, delete_efs: bool = False) -> Dict[str, Any]:
        """
        删除集群

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            delete_efs: 是否删除弹性文件系统

        Returns:
            删除集群的响应结果
        """
        logger.info(f"删除集群: regionId={region_id}, clusterId={cluster_id}, deleteEfs={delete_efs}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}'

        query_params = {
            'deleteEfs': 'true' if delete_efs else 'false'
        }

        headers = self.eop_auth.sign_request(
            method='DELETE',
            url=url,
            query_params=query_params,
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.delete(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def modify_cluster(self, region_id: str, cluster_id: str, modify_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        修改集群

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            modify_config: 修改配置信息

        Returns:
            修改集群的响应结果
        """
        logger.info(f"修改集群: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}'

        headers = self.eop_auth.sign_request(
            method='PUT',
            url=url,
            body=json.dumps(modify_config),
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.put(url, json=modify_config, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def query_cluster_quota(self, region_id: str) -> Dict[str, Any]:
        """
        查询集群配额与使用量

        Args:
            region_id: 区域ID

        Returns:
            集群配额与使用量的响应结果
        """
        logger.info(f"查询集群配额与使用量: regionId={region_id}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/quota'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def query_cluster_quota_usage(self, region_id: str) -> Dict[str, Any]:
        """
        查询租户集群配额和使用量

        Args:
            region_id: 区域ID

        Returns:
            集群配额与使用量的响应结果
        """
        logger.info(f"查询集群配额与使用量: regionId={region_id}")

        url = f'https://{self.base_endpoint}/v2/cce/quotas/query'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_cluster_kubeconfig(self, region_id: str, cluster_id: str,
                              config_type: str = 'external', expire_hours: int = 24) -> Dict[str, Any]:
        """
        获取集群的KubeConfig配置文件

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            config_type: KubeConfig类型 (internal/external)
            expire_hours: 过期时间（小时），默认24小时

        Returns:
            KubeConfig配置文件的响应结果
        """
        logger.info(f"获取集群KubeConfig: regionId={region_id}, clusterId={cluster_id}, type={config_type}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/kubeconfig'

        query_params = {
            'type': config_type,
            'expireHours': expire_hours
        }

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_kubernetes_versions(self, region_id: str, cluster_type: Optional[int] = None) -> Dict[str, Any]:
        """
        查询Kubernetes版本列表

        Args:
            region_id: 区域ID
            cluster_type: 集群类型 (0-专有版, 2-托管版)

        Returns:
            Kubernetes版本列表的响应结果
        """
        logger.info(f"查询Kubernetes版本: regionId={region_id}, clusterType={cluster_type}")

        url = f'https://{self.base_endpoint}/v2/cce/kubernetes-versions'

        query_params = {}
        if cluster_type is not None:
            query_params['clusterType'] = cluster_type

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    # ========== 节点与节点池管理 ==========

    def list_node_pools(self, region_id: str, cluster_id: str, page_size: int = 10, page_no: int = 1,
                        node_pool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        查询节点池列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            page_size: 每页条数
            page_no: 当前页码
            node_pool_name: 节点池名称（可选）

        Returns:
            节点池列表的响应结果
        """
        logger.info(f"查询节点池列表: regionId={region_id}, clusterId={cluster_id}, pageSize={page_size}, pageNow={page_no}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/nodepools'

        query_params = {
            'pageSize': page_size,
            'pageNow': page_no
        }

        if node_pool_name:
            query_params['nodePoolName'] = node_pool_name

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_cluster_nodes(self, region_id: str, cluster_id: str, node_name: Optional[str] = None) -> Dict[str, Any]:
        """
        查询集群节点列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            node_name: 集群节点名称（可选）

        Returns:
            节点列表的响应结果
        """
        logger.info(f"查询集群节点列表: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/nodes/list'

        query_params = {}
        if node_name:
            query_params['nodeName'] = node_name

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_node_pool(self, region_id: str, cluster_id: str, node_pool_id: str) -> Dict[str, Any]:
        """
        查询节点池详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            node_pool_id: 节点池ID

        Returns:
            节点池详情的响应结果
        """
        logger.info(f"查询节点池详情: regionId={region_id}, clusterId={cluster_id}, nodePoolId={node_pool_id}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/nodepool/{node_pool_id}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_node_detail(self, region_id: str, cluster_id: str, node_id: str) -> Dict[str, Any]:
        """
        查询节点详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            node_id: 节点ID

        Returns:
            节点详情的响应结果
        """
        logger.info(f"查询节点详情: regionId={region_id}, clusterId={cluster_id}, nodeId={node_id}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/nodes/{node_id}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def create_node_pool(self, region_id: str, cluster_id: str, node_pool_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建节点池

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            node_pool_config: 节点池配置信息

        Returns:
            创建节点池的响应结果
        """
        logger.info(f"创建节点池: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}/nodepools'

        headers = self.eop_auth.sign_request(
            method='POST',
            url=url,
            body=json.dumps(node_pool_config),
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.post(url, json=node_pool_config, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_nodes(self, region_id: str, cluster_id: str, page_size: int = 10, page_no: int = 1) -> Dict[str, Any]:
        """
        查询节点列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            page_size: 分页大小
            page_no: 页码

        Returns:
            节点列表的响应结果
        """
        logger.info(f"查询节点列表: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}/nodes'

        query_params = {
            'pageSize': page_size,
            'pageNo': page_no
        }

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params,
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def scale_node_pool(self, region_id: str, cluster_id: str, node_pool_id: str,
                       desired_node_count: int, current_node_count: int = None) -> Dict[str, Any]:
        """
        节点池扩缩容

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            node_pool_id: 节点池ID
            desired_node_count: 期望节点数
            current_node_count: 当前节点数

        Returns:
            节点池扩缩容的响应结果
        """
        logger.info(f"节点池扩缩容: regionId={region_id}, clusterId={cluster_id}, nodePoolId={node_pool_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}/nodepools/{node_pool_id}/scale'

        scale_config = {
            'desiredNodeCount': desired_node_count
        }
        if current_node_count is not None:
            scale_config['currentNodeCount'] = current_node_count

        headers = self.eop_auth.sign_request(
            method='POST',
            url=url,
            body=json.dumps(scale_config),
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.post(url, json=scale_config, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    # ========== 任务管理 ==========

    def list_tasks(self, region_id: str, cluster_id: str, page_number: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询任务列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            page_number: 分页查询页数（可选，默认1）
            page_size: 每页显示数量（可选，默认10）

        Returns:
            任务列表的响应结果
        """
        logger.info(f"查询任务列表: regionId={region_id}, clusterId={cluster_id}, pageNumber={page_number}, pageSize={page_size}")

        url = f'https://{self.base_endpoint}/v2/cce/tasks/{cluster_id}/alltasks'

        query_params = {
            'pageNumber': page_number,
            'pageSize': page_size
        }

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_task_events(self, region_id: str, cluster_id: str, task_id: str, page_number: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询指定集群任务事件列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            task_id: 任务ID
            page_number: 分页查询页数（可选，默认1）
            page_size: 每页显示数量（可选，默认10）

        Returns:
            任务事件列表的响应结果
        """
        logger.info(f"查询任务事件列表: regionId={region_id}, clusterId={cluster_id}, taskId={task_id}, pageNumber={page_number}, pageSize={page_size}")

        # 根据文档：GET /v2/cce/events/{clusterId}/{taskId}
        url = f'https://{self.base_endpoint}/v2/cce/events/{cluster_id}/{task_id}'

        query_params = {
            'pageNumber': page_number,
            'pageSize': page_size
        }

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    # ========== Kubernetes资源查询 ==========

    def list_deployments(self, region_id: str, cluster_id: str, namespace: str,
                         label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询Deployment列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            Deployment列表的响应结果
        """
        logger.info(f"查询Deployment列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace}/deployments'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_deployment(self, region_id: str, cluster_id: str, namespace: str, deployment_name: str) -> Dict[str, Any]:
        """
        查询Deployment详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            deployment_name: Deployment名称

        Returns:
            Deployment详情的响应结果
        """
        logger.info(f"查询Deployment详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}, deployment={deployment_name}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace}/deployments/{deployment_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_pods(self, region_id: str, cluster_id: str, namespace: str,
                  label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询Pod列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            Pod列表的响应结果
        """
        logger.info(f"查询Pod列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/api/v1/namespaces/{namespace}/pods'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_daemonsets(self, region_id: str, cluster_id: str, namespace_name: str,
                       label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询指定集群下的DaemonSet列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace_name: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            DaemonSet列表的响应结果
        """
        logger.info(f"查询DaemonSet列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace_name}")

        # 根据文档：GET /v2/cce/clusters/*/apis/apps/v1/namespaces/*/daemonsets
        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace_name}/daemonsets'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_replicasets(self, region_id: str, cluster_id: str, namespace_name: str,
                          label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        获取指定集群下的ReplicaSet资源列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace_name: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            ReplicaSet列表的响应结果
        """
        logger.info(f"查询ReplicaSet列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace_name}")

        # 根据文档：GET /v2/cce/clusters/*/apis/apps/v1/namespaces/*/replicasets
        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace_name}/replicasets'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_replicaset(self, region_id: str, cluster_id: str, namespace_name: str, replicaset_name: str) -> Dict[str, Any]:
        """
        查询指定集群下的ReplicaSet资源详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace_name: 命名空间名称
            replicaset_name: ReplicaSet资源名称

        Returns:
            ReplicaSet详情的响应结果
        """
        logger.info(f"查询ReplicaSet详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace_name}, name={replicaset_name}")

        # 根据文档：GET /v2/cce/clusters/*/apis/apps/v1/namespaces/*/replicasets/*
        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace_name}/replicasets/{replicaset_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_daemonset(self, region_id: str, cluster_id: str, namespace_name: str, daemonset_name: str) -> Dict[str, Any]:
        """
        查询指定集群下的DaemonSet详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace_name: 命名空间名称
            daemonset_name: DaemonSet名称

        Returns:
            DaemonSet详情的响应结果
        """
        logger.info(f"查询DaemonSet详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace_name}, daemonset={daemonset_name}")

        # 根据文档：GET /v2/cce/clusters/*/apis/apps/v1/namespaces/*/daemonsets/*
        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace_name}/daemonsets/{daemonset_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_pod(self, region_id: str, cluster_id: str, namespace_name: str, pod_name: str) -> Dict[str, Any]:
        """
        查询指定Pod的详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace_name: 命名空间名称
            pod_name: Pod名称

        Returns:
            Pod详情的响应结果
        """
        logger.info(f"查询Pod详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace_name}, pod={pod_name}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/api/v1/namespaces/{namespace_name}/pods/{pod_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_services(self, region_id: str, cluster_id: str, namespace: str,
                      label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询Service列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            Service列表的响应结果
        """
        logger.info(f"查询Service列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/api/v1/namespaces/{namespace}/services'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_service(self, region_id: str, cluster_id: str, namespace: str, service_name: str) -> Dict[str, Any]:
        """
        查询Service详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            service_name: Service名称

        Returns:
            Service详情的响应结果
        """
        logger.info(f"查询Service详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}, service={service_name}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/api/v1/namespaces/{namespace}/services/{service_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_jobs(self, region_id: str, cluster_id: str, namespace: str,
                  label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询Job列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            Job列表的响应结果
        """
        logger.info(f"查询Job列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/batch/v1/namespaces/{namespace}/jobs'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_job(self, region_id: str, cluster_id: str, namespace: str, job_name: str) -> Dict[str, Any]:
        """
        查询Job详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            job_name: Job名称

        Returns:
            Job详情的响应结果
        """
        logger.info(f"查询Job详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}, job={job_name}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/batch/v1/namespaces/{namespace}/jobs/{job_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_statefulsets(self, region_id: str, cluster_id: str, namespace: str,
                         label_selector: Optional[str] = None, field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询StatefulSet列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            label_selector: Kubernetes标签选择器（可选）
            field_selector: Kubernetes字段选择器（可选）

        Returns:
            StatefulSet列表的响应结果
        """
        logger.info(f"查询StatefulSet列表: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace}/statefulsets'

        query_params = {}
        if label_selector:
            query_params['labelSelector'] = label_selector
        if field_selector:
            query_params['fieldSelector'] = field_selector

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def get_statefulset(self, region_id: str, cluster_id: str, namespace: str, statefulset_name: str) -> Dict[str, Any]:
        """
        查询StatefulSet详情

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            namespace: 命名空间名称
            statefulset_name: StatefulSet名称

        Returns:
            StatefulSet详情的响应结果
        """
        logger.info(f"查询StatefulSet详情: regionId={region_id}, clusterId={cluster_id}, namespace={namespace}, statefulset={statefulset_name}")

        url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace}/statefulsets/{statefulset_name}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    # ========== 弹性伸缩 ==========

    def create_auto_scaling_policy(self, region_id: str, cluster_id: str,
                                  scaling_policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建节点弹性伸缩策略

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            scaling_policy: 弹性伸缩策略配置

        Returns:
            创建弹性伸缩策略的响应结果
        """
        logger.info(f"创建弹性伸缩策略: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}/auto-scaling-policies'

        headers = self.eop_auth.sign_request(
            method='POST',
            url=url,
            body=json.dumps(scaling_policy),
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.post(url, json=scaling_policy, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def list_auto_scaling_policies(self, region_id: str, cluster_id: str,
                                  page_size: int = 10, page_no: int = 1) -> Dict[str, Any]:
        """
        查询节点弹性伸缩策略列表

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            page_size: 分页大小
            page_no: 页码

        Returns:
            弹性伸缩策略列表的响应结果
        """
        logger.info(f"查询弹性伸缩策略列表: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}/auto-scaling-policies'

        query_params = {
            'pageSize': page_size,
            'pageNo': page_no
        }

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params,
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.get(url, params=query_params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    # ========== 其他功能接口 ==========

    def list_authorized_namespaces(self, region_id: str, cluster_name: str) -> Dict[str, Any]:
        """
        查询用户被授权的命名空间列表

        Args:
            region_id: 区域ID
            cluster_name: 集群名称

        Returns:
            用户被授权的命名空间列表的响应结果
        """
        logger.info(f"查询用户被授权的命名空间列表: regionId={region_id}, clusterName={cluster_name}")

        url = f'https://{self.base_endpoint}/v1.1/cce/clusters/{cluster_name}/binding/namespaces'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url
        )
        headers['regionId'] = region_id
        headers['Content-Type'] = 'application/json'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('statusCode') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('statusCode', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def bind_cluster_tag(self, region_id: str, cluster_id: str, tag_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        绑定集群标签

        Args:
            region_id: 区域ID
            cluster_id: 集群ID
            tag_config: 标签配置信息

        Returns:
            绑定集群标签的响应结果
        """
        logger.info(f"绑定集群标签: regionId={region_id}, clusterId={cluster_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/clusters/{cluster_id}/tags/bind'

        headers = self.eop_auth.sign_request(
            method='POST',
            url=url,
            body=json.dumps(tag_config),
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.post(url, json=tag_config, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    def query_async_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """
        查询异步任务

        Args:
            region_id: 区域ID
            task_id: 任务ID

        Returns:
            异步任务状态的响应结果
        """
        logger.info(f"查询异步任务: regionId={region_id}, taskId={task_id}")

        url = f'https://{self.base_endpoint}/cse-apig/v2/tasks/{task_id}'

        headers = self.eop_auth.sign_request(
            method='GET',
            url=url,
            content_type='application/json'
        )
        headers['regionid'] = region_id
        headers['urlType'] = 'CTAPI'

        response = self.client.session.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 800:
                return result
            else:
                from core import CTYUNAPIError
                raise CTYUNAPIError(result.get('code', 'unknown'), result.get('message', 'Unknown error'))
        else:
            from core import CTYUNAPIError
            raise CTYUNAPIError('HTTP_ERROR', f'HTTP {response.status_code}: {response.text}')

    # ========== ConfigMap配置管理 ==========

    def get_config_map_detail(self, region_id: str, cluster_id: str,
                             namespace_name: str, configmap_name: str) -> Dict[str, Any]:
        """
        查询ConfigMap详情

        Args:
            region_id: 区域ID (必填)
            cluster_id: 集群ID (必填)
            namespace_name: 命名空间名称 (必填)
            configmap_name: ConfigMap资源名称 (必填)

        Returns:
            ConfigMap的YAML格式详细信息
        """
        logger.info(f"查询ConfigMap详情: clusterId={cluster_id}, namespace={namespace_name}, name={configmap_name}")

        try:
            url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace_name}/configmaps/{configmap_name}'

            headers = {
                'regionId': region_id
            }

            # 使用EOP签名认证
            signed_headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=None,
                body=None
            )

            # 合并签名后的headers
            headers.update(signed_headers)

            response = self.client.session.get(
                url,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_msg = data.get('message', '未知错误')
                error_code = data.get('error', 'UNKNOWN_ERROR')
                raise Exception(f"CCE API错误 [{error_code}]: {error_msg}")

            logger.info("成功获取ConfigMap详情")
            return data

        except Exception as e:
            logger.error(f"查询ConfigMap详情失败: {str(e)}")
            raise

    def list_config_maps(self, region_id: str, cluster_id: str,
                        namespace_name: str, label_selector: Optional[str] = None,
                        field_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        查询ConfigMap列表

        Args:
            region_id: 区域ID (必填)
            cluster_id: 集群ID (必填)
            namespace_name: 命名空间名称 (必填)
            label_selector: 标签选择器，用于过滤资源 (可选)
            field_selector: 字段选择器，用于过滤资源 (可选)

        Returns:
            ConfigMap列表的YAML格式数据
        """
        logger.info(f"查询ConfigMap列表: clusterId={cluster_id}, namespace={namespace_name}")

        try:
            url = f'https://{self.base_endpoint}/v2/cce/clusters/{cluster_id}/apis/apps/v1/namespaces/{namespace_name}/configmaps'

            # 构建查询参数
            query_params = {}
            if label_selector:
                query_params['labelSelector'] = label_selector
            if field_selector:
                query_params['fieldSelector'] = field_selector

            headers = {
                'regionId': region_id
            }

            # 使用EOP签名认证
            signed_headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params if query_params else None,
                body=None
            )

            # 合并签名后的headers
            headers.update(signed_headers)

            response = self.client.session.get(
                url,
                params=query_params if query_params else None,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_msg = data.get('message', '未知错误')
                error_code = data.get('error', 'UNKNOWN_ERROR')
                raise Exception(f"CCE API错误 [{error_code}]: {error_msg}")

            logger.info("成功获取ConfigMap列表")
            return data

        except Exception as e:
            logger.error(f"查询ConfigMap列表失败: {str(e)}")
            raise

    def query_cluster_logs(self, region_id: str, cluster_name: str,
                          page_now: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询集群日志

        Args:
            region_id: 区域ID (必填)
            cluster_name: 集群名称 (必填)
            page_now: 当前页码，默认为1
            page_size: 每页条数，默认为10

        Returns:
            集群日志查询结果，包含分页信息和日志记录
        """
        logger.info(f"查询集群日志: clusterName={cluster_name}, pageNow={page_now}, pageSize={page_size}")

        try:
            url = f'https://{self.base_endpoint}/v1.1/ccse/clusters/{cluster_name}/logs'

            # 构建查询参数
            query_params = {
                'pageNow': page_now,
                'pageSize': page_size
            }

            headers = {
                'regionId': region_id
            }

            # 使用EOP签名认证
            signed_headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None
            )

            # 合并签名后的headers
            headers.update(signed_headers)

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_msg = data.get('message', '未知错误')
                error_code = data.get('error', 'UNKNOWN_ERROR')
                raise Exception(f"CCE API错误 [{error_code}]: {error_msg}")

            # 提取日志统计信息
            return_obj = data.get('returnObj', {})
            if return_obj:
                total = return_obj.get('total', 0)
                current = return_obj.get('current', page_now)
                pages = return_obj.get('pages', 0)
                records = return_obj.get('records', [])

                logger.info(f"成功获取集群日志: 总计{total}条记录，第{current}页，共{pages}页，本页{len(records)}条")

            return data

        except Exception as e:
            logger.error(f"查询集群日志失败: {str(e)}")
            raise