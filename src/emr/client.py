"""
翼MapReduce(EMR) API客户端
"""

import json
from typing import Dict, List, Optional, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class EMRClient:
    """天翼云翼MapReduce(EMR)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'emr-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def _create_error_response(self, status_code: int, response_text: str) -> Dict[str, Any]:
        return {
            "error": True,
            "status_code": status_code,
            "message": f"HTTP {status_code}: {response_text}",
            "response": response_text
        }

    # ========== V1 API ==========

    def select_cluster_detail_pages(self, region_id: str, page_index: int = 1, page_size: int = 10,
                                    cluster_name: str = None, cluster_state_code: int = None,
                                    cluster_type_code: int = None) -> Optional[Dict[str, Any]]:
        """集群信息分页查询V1"""
        logger.info(f"查询EMR集群列表V1: regionId={region_id}")
        try:
            url = f'https://{self.base_endpoint}/v1/emr/openapi/cluster/clusterDetail/selectPage'
            body = {'regionId': region_id, 'pageIndex': page_index, 'pageSize': page_size}
            if cluster_name:
                body['clusterName'] = cluster_name
            if cluster_state_code is not None:
                body['clusterStateCode'] = cluster_state_code
            if cluster_type_code is not None:
                body['clusterTypeCode'] = cluster_type_code

            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(body), extra_headers={'Content-Type': 'application/json'}
            )
            response = self.client.session.post(url, json=body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR集群列表V1失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_cluster_detail_by_id(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """根据id查询集群信息V1"""
        logger.info(f"查询EMR集群详情V1: id={cluster_id}")
        try:
            url = f'https://{self.base_endpoint}/v1/emr/openapi/cluster/clusterDetail/getById'
            query_params = {'id': cluster_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='', extra_headers={}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR集群详情V1失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def meta_overview(self, cluster_id: str, timestamp: int) -> Optional[Dict[str, Any]]:
        """元数据概览"""
        logger.info(f"查询EMR元数据概览: clusterId={cluster_id}")
        try:
            url = f'https://{self.base_endpoint}/v1/emr/doctor/openapi/meta/hive/overview'
            query_params = {'clusterId': cluster_id, 'timestamp': str(timestamp)}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='', extra_headers={}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR元数据概览失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def meta_table_info(self, cluster_id: str, timestamp: int, database_name: str, table_name: str) -> Optional[Dict[str, Any]]:
        """元数据信息查询"""
        logger.info(f"查询EMR元数据表信息: clusterId={cluster_id}, db={database_name}, table={table_name}")
        try:
            url = f'https://{self.base_endpoint}/v1/emr/doctor/openapi/meta/hive/tableInfo'
            query_params = {
                'clusterId': cluster_id,
                'timestamp': str(timestamp),
                'databaseName': database_name,
                'tableName': table_name
            }
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='', extra_headers={}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR元数据表信息失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    # ========== V2 API ==========

    def select_cluster_page_v2(self, region_id: str, page_index: int = 1, page_size: int = 10,
                               cluster_name: str = None, cluster_state_code: int = None,
                               cluster_type_code: int = None) -> Optional[Dict[str, Any]]:
        """集群信息分页查询V2"""
        logger.info(f"查询EMR集群列表V2: regionId={region_id}")
        try:
            url = f'https://{self.base_endpoint}/v2/emr/openapi/cluster/clusterDetail/selectPage'
            body = {'regionId': region_id, 'pageIndex': page_index, 'pageSize': page_size}
            if cluster_name:
                body['clusterName'] = cluster_name
            if cluster_state_code is not None:
                body['clusterStateCode'] = cluster_state_code
            if cluster_type_code is not None:
                body['clusterTypeCode'] = cluster_type_code

            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(body), extra_headers={'Content-Type': 'application/json'}
            )
            response = self.client.session.post(url, json=body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR集群列表V2失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_cluster_by_id_v2(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """根据id查询集群信息V2"""
        logger.info(f"查询EMR集群详情V2: id={cluster_id}")
        try:
            url = f'https://{self.base_endpoint}/v2/emr/openapi/cluster/clusterDetail/getById'
            query_params = {'id': cluster_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='', extra_headers={}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR集群详情V2失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_node_group_by_cluster_id_v2(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """根据集群id查询节点组信息V2"""
        logger.info(f"查询EMR节点组信息V2: clusterId={cluster_id}")
        try:
            url = f'https://{self.base_endpoint}/v2/emr/openapi/cluster/clusterNodeGroup/getByClusterId'
            query_params = {'clusterId': cluster_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='', extra_headers={}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR节点组信息V2失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_group_and_host_by_condition_v2(self, cluster_id: str, node_state: int = None,
                                           select_key: str = None) -> Optional[Dict[str, Any]]:
        """查询集群节点组详情V2"""
        logger.info(f"查询EMR节点组详情V2: clusterId={cluster_id}")
        try:
            url = f'https://{self.base_endpoint}/v2/emr/openapi/cluster/nodeGroup/getGroupAndHostByCondition'
            body = {'clusterId': cluster_id}
            if node_state is not None:
                body['nodeState'] = node_state
            if select_key:
                body['selectKey'] = select_key

            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(body), extra_headers={'Content-Type': 'application/json'}
            )
            response = self.client.session.post(url, json=body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询EMR节点组详情V2失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}
