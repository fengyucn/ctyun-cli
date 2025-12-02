"""
云专线CDA (Cloud Dedicated Access) 管理模块 - 使用OpenAPI V4

云专线服务提供高速、安全、可靠的专线连接服务，支持：
- 专线网关管理
- 物理专线管理
- VPC管理
- 静态路由管理
- BGP路由管理
- 跨账号授权
- 健康检查
- 链路探测

服务端点: cda-global.ctapi.ctyun.cn
"""

from typing import Dict, Any, List, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class CDAClient:
    """云专线CDA客户端 - OpenAPI V4"""

    def __init__(self, client: CTYUNClient):
        """
        初始化CDA客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'cda'
        # 尝试不同的可能端点
        self.endpoints = [
            'cda-global.ctapi.ctyun.cn',
            'cda.ctapi.ctyun.cn',
            'ctcda-global.ctapi.ctyun.cn',
            'global-cda.ctapi.ctyun.cn'
        ]
        self.base_endpoint = self.endpoints[0]
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def make_eop_request(
        self,
        method: str,
        endpoint_path: str,
        query_params: Optional[Dict[str, Any]] = None,
        body_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        发送EOP认证的API请求，支持尝试多个端点

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint_path: API端点路径
            query_params: 查询参数
            body_data: 请求体数据
            timeout: 请求超时时间

        Returns:
            API响应结果
        """
        # 尝试不同的端点
        for endpoint in self.endpoints:
            url = f"https://{endpoint}{endpoint_path}"

            # 构造请求
            body = json.dumps(body_data) if body_data else None
            headers = self.eop_auth.sign_request(
                method=method,
                url=url,
                query_params=query_params,
                body=body,
                extra_headers={}
            )

            logger.debug(f"尝试端点: {endpoint}")
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求方法: {method}")
            if query_params:
                logger.debug(f"查询参数: {query_params}")
            if body_data:
                logger.debug(f"请求体: {body}")

            try:
                # 发送请求
                if method.upper() == 'GET':
                    # 对于GET方法，如果有body_data，将其作为data传递
                    # 这是天翼云API的特殊模式：GET方法但有请求体
                    if body_data:
                        response = self.client.session.get(
                            url,
                            params=query_params,
                            data=body,
                            headers=headers,
                            timeout=timeout,
                            verify=False
                        )
                    else:
                        response = self.client.session.get(
                            url,
                            params=query_params,
                            headers=headers,
                            timeout=timeout,
                            verify=False
                        )
                elif method.upper() == 'POST':
                    response = self.client.session.post(
                        url,
                        data=body,
                        headers=headers,
                        timeout=timeout,
                        verify=False
                    )
                elif method.upper() == 'PUT':
                    response = self.client.session.put(
                        url,
                        data=body,
                        headers=headers,
                        timeout=timeout,
                        verify=False
                    )
                elif method.upper() == 'DELETE':
                    response = self.client.session.delete(
                        url,
                        params=query_params,
                        headers=headers,
                        timeout=timeout,
                        verify=False
                    )
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")

                logger.debug(f"响应状态码: {response.status_code}")
                logger.debug(f"响应内容: {response.text}")

                if response.status_code == 200:
                    result = response.json()
                    # 检查业务状态码
                    if result.get('statusCode') == 800:
                        logger.debug(f"成功使用端点: {endpoint}")
                        return {
                            'success': True,
                            'data': result.get('returnObj', {}),
                            'endpoint': endpoint
                        }
                    else:
                        error_code = result.get('errorCode', 'UNKNOWN_ERROR')
                        error_msg = result.get('message', result.get('msgDesc', '未知错误'))
                        logger.debug(f"端点 {endpoint} 返回业务错误: {error_code} - {error_msg}")
                        continue
                elif response.status_code == 404:
                    logger.debug(f"端点 {endpoint} 返回404，尝试下一个端点")
                    continue
                else:
                    logger.error(f"端点 {endpoint} API调用失败 (HTTP {response.status_code}): {response.text}")
                    continue

            except Exception as e:
                logger.debug(f"端点 {endpoint} 请求异常: {str(e)}")
                continue

        # 所有端点都失败
        return {
            'success': False,
            'error': 'ALL_ENDPOINTS_FAILED',
            'message': f'所有端点都失败，已尝试: {", ".join(self.endpoints)}'
        }

    # ============ VPC相关API ============

    def list_vpcs(
        self,
        gateway_name: str,
        account: str
    ) -> Dict[str, Any]:
        """
        查询专线网关下的VPC列表

        Args:
            gateway_name: 专线网关名字
            account: 天翼云客户邮箱

        Returns:
            VPC列表信息
        """
        logger.info(f"查询专线网关VPC列表: gateway_name={gateway_name}, account={account}")

        # 首先尝试使用POST方法，因为很多天翼云API文档虽然是GET但实际需要POST
        body_data = {
            'gatewayName': gateway_name,
            'account': account
        }

        # 尝试不同的API路径
        for path in ['/v4/cda/vpc/list', '/v4/dcaas/vpc/list', '/v4/cda/vpc-list', '/v4/dcaas/vpc-list']:
            try:
                result = self.make_eop_request(
                    method='POST',
                    endpoint_path=path,
                    body_data=body_data
                )
                if result.get('success'):
                    return result
                logger.debug(f"路径 {path} 返回失败: {result}")
            except Exception as e:
                logger.debug(f"路径 {path} 异常: {str(e)}")
                continue

        # 所有路径都失败，返回最后一个路径的结果
        return self.make_eop_request(
            method='POST',
            endpoint_path='/v4/cda/vpc/list',
            body_data=body_data
        )

    def count_vpcs(
        self,
        gateway_name: str,
        account: str
    ) -> Dict[str, Any]:
        """
        查询专线网关下的VPC数量

        Args:
            gateway_name: 专线网关名字
            account: 天翼云客户邮箱

        Returns:
            VPC数量信息
        """
        logger.info(f"查询专线网关VPC数量: gateway_name={gateway_name}, account={account}")

        body_data = {
            'gatewayName': gateway_name,
            'account': account
        }

        return self.make_eop_request(
            method='POST',  # 使用POST方法，因为需要请求体
            endpoint_path='/v4/cda/vpc/count',
            body_data=body_data
        )

    def get_vpc_info(
        self,
        vpc_id: str,
        gateway_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取指定VPC的详细信息和能访问该VPC的物理专线信息

        Args:
            vpc_id: VPC ID
            gateway_name: 专线网关名字（可选）

        Returns:
            VPC详细信息
        """
        logger.info(f"查询VPC详细信息: vpc_id={vpc_id}, gateway_name={gateway_name}")

        body_data = {
            'vpcID': vpc_id
        }

        # gateway_name是可选参数
        if gateway_name:
            body_data['gatewayName'] = gateway_name

        return self.make_eop_request(
            method='POST',  # 使用POST方法，因为需要请求体
            endpoint_path='/v4/cda/vpc/info',
            body_data=body_data
        )

    # ============ 物理专线相关API ============

    def list_physical_lines(
        self,
        page_no: int = 1,
        page_size: int = 10,
        region_id: Optional[str] = None,
        line_type: Optional[str] = None,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询已创建的物理专线列表

        Args:
            page_no: 页码，默认1
            page_size: 每页数据量，默认10
            region_id: 资源池ID（可选）
            line_type: 专线类型(PON/IPRAN)（可选）
            account: 天翼云客户邮箱（可选）

        Returns:
            物理专线列表信息
        """
        logger.info(f"查询物理专线列表: page_no={page_no}, page_size={page_size}, region_id={region_id}, line_type={line_type}")

        body_data = {
            'pageNo': page_no,
            'pageSize': page_size
        }

        # 添加可选参数
        if region_id:
            body_data['regionID'] = region_id
        if line_type:
            body_data['type'] = line_type
        if account:
            body_data['account'] = account

        return self.make_eop_request(
            method='GET',  # 文档明确要求GET方法
            endpoint_path='/v4/cda/physical-line/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def count_physical_lines(self, account: str, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询用户已创建的物理专线数量

        Args:
            account: 天翼云客户邮箱
            region_id: 资源池ID（可选，但实际可能是必需的）

        Returns:
            物理专线数量信息
        """
        logger.info(f"查询物理专线数量: account={account}, region_id={region_id}")

        # 按照API文档，使用GET方法，但需要传递请求体参数
        # 根据实际测试，regionID参数是必需的
        body_data = {
            'account': account
        }

        # 如果提供了region_id，添加到请求体
        if region_id:
            body_data['regionID'] = region_id

        return self.make_eop_request(
            method='GET',  # 文档明确要求GET方法
            endpoint_path='/v4/cda/physical-line/count',
            body_data=body_data  # GET方法但传递body数据
        )

    def list_shared_physical_lines(
        self,
        page_no: int = 1,
        page_size: int = 10,
        region_id: Optional[str] = None,
        line_type: Optional[str] = None,
        line_code: Optional[str] = None,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询已创建的共享物理专线列表

        Args:
            page_no: 页码，默认1
            page_size: 每页行数，默认10
            region_id: 资源池ID（可选）
            line_type: 专线类型(PON/IPRAN)（可选）
            line_code: 电路代号（可选）
            account: 天翼云客户邮箱（可选）

        Returns:
            共享物理专线列表信息
        """
        logger.info(f"查询共享物理专线列表: page_no={page_no}, page_size={page_size}, region_id={region_id}, line_type={line_type}")

        body_data = {
            'pageNo': page_no,
            'pageSize': page_size
        }

        # 添加可选参数
        if region_id:
            body_data['regionID'] = region_id
        if line_type:
            body_data['type'] = line_type
        if line_code:
            body_data['lineCode'] = line_code
        if account:
            body_data['account'] = account

        return self.make_eop_request(
            method='GET',  # 文档第18行明确要求GET方法
            endpoint_path='/v4/cda/shared-physical-line/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_access_points(
        self,
        line_name: str,
        account: str,
        region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询物理专线的接入点

        Args:
            line_name: 物理专线名字（必填）
            account: 天翼云客户邮箱（必填）
            region_id: 资源池ID（实际必填，虽然文档未说明）

        Returns:
            接入点信息
        """
        logger.info(f"查询物理专线接入点: line_name={line_name}, account={account}, region_id={region_id}")

        body_data = {
            'lineName': line_name,
            'account': account
        }

        # 根据实际测试，regionID实际上是必填参数
        if region_id:
            body_data['regionID'] = region_id

        return self.make_eop_request(
            method='GET',  # 文档第18行明确要求GET方法
            endpoint_path='/v4/cda/physical-line/access-point-list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    # ============ 专线网关相关API ============

    def list_gateways(
        self,
        account: str,
        page_no: int = 1,
        page_size: int = 10,
        region_id: Optional[str] = None,
        project_id: Optional[str] = None,
        gateway_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询账户下已创建的云专线网关列表

        Args:
            page_no: 页码，默认1
            page_size: 每页数据量，默认10
            account: 天翼云客户邮箱（必填）
            region_id: 资源池ID（可选）
            project_id: 项目ID（可选）
            gateway_name: 专线网关名字（可选）

        Returns:
            专线网关列表信息
        """
        logger.info(f"查询专线网关列表: page_no={page_no}, page_size={page_size}, account={account}, region_id={region_id}")

        body_data = {
            'pageNo': page_no,
            'pageSize': page_size,
            'account': account
        }

        # 添加可选参数
        if region_id:
            body_data['regionID'] = region_id
        if project_id:
            body_data['projectID'] = project_id
        if gateway_name:
            body_data['gatewayName'] = gateway_name

        return self.make_eop_request(
            method='GET',  # 文档明确要求GET方法
            endpoint_path='/v4/cda/gateway/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def count_gateways(
        self,
        account: str,
        region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询用户已创建的专线网关数量

        Args:
            account: 天翼云客户邮箱（必填）
            region_id: 资源池ID（实际必填，虽然文档标为可选）

        Returns:
            专线网关数量信息
        """
        logger.info(f"查询专线网关数量: account={account}, region_id={region_id}")

        body_data = {
            'account': account
        }

        # 根据实际测试，regionID实际上是必填参数
        if region_id:
            body_data['regionID'] = region_id

        return self.make_eop_request(
            method='GET',  # 文档明确要求GET方法
            endpoint_path='/v4/cda/gateway/count',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_static_routes(
        self,
        gateway_name: str,
        account: str
    ) -> Dict[str, Any]:
        """
        查询专线网关下的静态路由

        Args:
            gateway_name: 专线网关名字（必填）
            account: 天翼云客户邮箱（必填）

        Returns:
            静态路由列表信息
        """
        logger.info(f"查询静态路由列表: gateway_name={gateway_name}, account={account}")

        body_data = {
            'gatewayName': gateway_name,
            'account': account
        }

        return self.make_eop_request(
            method='GET',  # 文档第26行明确要求GET方法
            endpoint_path='/v4/cda/static-route/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_gateway_physical_lines(
        self,
        gateway_name: str,
        account: str,
        region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询专线网关已绑定的物理专线

        Args:
            gateway_name: 专线网关名称（必填，将作为vrfName传递）
            account: 天翼云客户邮箱（必填）
            region_id: 资源池ID（实际必填，虽然文档可能未说明）

        Returns:
            专线网关已绑定的物理专线列表信息
        """
        logger.info(f"查询专线网关已绑定的物理专线: gateway_name={gateway_name}, account={account}, region_id={region_id}")

        body_data = {
            'vrfName': gateway_name,  # API实际需要的是vrfName参数
            'account': account
        }

        # 根据实际测试，regionID实际上是必填参数
        if region_id:
            body_data['regionID'] = region_id

        return self.make_eop_request(
            method='GET',  # 根据API文档使用GET方法
            endpoint_path='/v4/cda/gateway/physical-line-list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_bgp_routes(
        self,
        gateway_name: str,
        account: str
    ) -> Dict[str, Any]:
        """
        查询专线网关下的BGP动态路由

        Args:
            gateway_name: 专线网关名字（必填，将作为vrfName传递）
            account: 天翼云客户邮箱（必填）

        Returns:
            BGP路由列表信息
        """
        logger.info(f"查询专线网关BGP路由: gateway_name={gateway_name}, account={account}")

        body_data = {
            'vrfName': gateway_name,  # API实际需要的是vrfName参数
            'account': account
        }

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/bgp-route/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_account_authorizations(
        self,
        region_id: str,
        page_no: int = 1,
        page_size: int = 10,
        vpc_id: Optional[str] = None,
        auth_account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询账户下已添加的跨账号授权网络实例

        Args:
            region_id: 资源池ID（必填）
            page_no: 页数，默认1
            page_size: 每页数据量，默认10
            vpc_id: 查询被授权：指定VPC ID，会带跨账号VPC子网信息（可选）
            auth_account_id: 查询已授权：账号ID不传查询被授权：账号ID为自己账号ID（可选）

        Returns:
            跨账号授权列表信息
        """
        logger.info(f"查询跨账号授权: region_id={region_id}, page_no={page_no}, page_size={page_size}, vpc_id={vpc_id}, auth_account_id={auth_account_id}")

        body_data = {
            'regionID': region_id,
            'pageNo': page_no,
            'pageSize': page_size
        }

        # 添加可选参数
        if vpc_id:
            body_data['vpcID'] = vpc_id
        if auth_account_id:
            body_data['authAccountID'] = auth_account_id

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/accountauth/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def get_account_authorization_statistics(self, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        统计账号下已授权的VPC及授权给专线网关数量

        Args:
            region_id: 资源池ID（实际API需要，虽然文档未说明）

        Returns:
            跨账号授权统计信息
        """
        logger.info(f"查询跨账号授权统计: region_id={region_id}")

        body_data = {}

        # 根据实际测试，API实际上需要regionID参数
        if region_id:
            body_data['regionID'] = region_id

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/accountauth/statistics',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def get_health_check_config(
        self,
        gateway_name: str,
        vpc_id: str,
        vpc_name: str
    ) -> Dict[str, Any]:
        """
        专线网关查询健康检查设置项

        Args:
            gateway_name: 专线网关名字（必填，将作为vrfName传递）
            vpc_id: VPC ID（必填）
            vpc_name: VPC名字（必填）

        Returns:
            健康检查配置信息
        """
        logger.info(f"查询专线网关健康检查配置: gateway_name={gateway_name}, vpc_id={vpc_id}, vpc_name={vpc_name}")

        body_data = {
            'vrfName': gateway_name,  # 根据经验，API实际需要的是vrfName参数
            'vpcID': vpc_id,
            'vpcName': vpc_name
        }

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/health-check/get',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def get_health_check_status(
        self,
        region_id: str,
        resource_pool: str,
        gateway_name: str,
        vpc_id: str
    ) -> Dict[str, Any]:
        """
        健康检查查询检查结果

        Args:
            region_id: 资源池ID（必填）
            resource_pool: 资源池ID（必填）
            gateway_name: 专线网关名字（必填，将作为vrfName传递）
            vpc_id: VPC ID（必填）

        Returns:
            健康检查状态信息
        """
        logger.info(f"查询健康检查状态: region_id={region_id}, resource_pool={resource_pool}, gateway_name={gateway_name}, vpc_id={vpc_id}")

        body_data = {
            'regionID': region_id,
            'resourcePool': resource_pool,
            'vrfName': gateway_name,  # 根据经验，API实际需要的是vrfName参数
            'vpcID': vpc_id
        }

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/health-check/status/get',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def query_link_probe(self, gateway_name: str) -> Dict[str, Any]:
        """
        云专线链路探测查询

        Args:
            gateway_name: 专线网关名字

        Returns:
            API响应结果

        Raises:
            CDAAPIError: API调用失败
        """
        logger.info(f"查询链路探测历史数据: gateway_name={gateway_name}")

        # 构造请求体
        body_data = {
            'gatewayName': gateway_name,
            'vrfName': gateway_name  # 根据经验，同时提供两个参数
        }

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/link-probe/query',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def get_vpc_info(self, vpc_id: str, gateway_name: Optional[str] = None) -> Dict[str, Any]:
        """
        云专线VPC详情查询

        Args:
            vpc_id: VPC ID
            gateway_name: 专线网关名字（可选）

        Returns:
            API响应结果

        Raises:
            CDAAPIError: API调用失败
        """
        logger.info(f"查询VPC详情: vpc_id={vpc_id}, gateway_name={gateway_name}")

        # 构造请求体
        body_data = {
            'vpcID': vpc_id
        }

        if gateway_name:
            body_data['gatewayName'] = gateway_name
            # 根据经验，可能需要vrfName参数
            body_data['vrfName'] = gateway_name

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/vpc/info',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_switches(self, switch_id: Optional[str] = None, resource_pool: Optional[str] = None,
                      hostname: Optional[str] = None, name: Optional[str] = None,
                      ip: Optional[str] = None) -> Dict[str, Any]:
        """
        专线交换机查询

        Args:
            switch_id: 交换机ID（可选）
            resource_pool: 资源池ID（可选）
            hostname: 交换机hostname（可选）
            name: 交换机name（可选）
            ip: 交换机IP（可选）

        Returns:
            API响应结果

        Raises:
            CDAAPIError: API调用失败
        """
        logger.info(f"查询专线交换机: switch_id={switch_id}, resource_pool={resource_pool}")

        # 构造请求体（所有参数都是可选的）
        body_data = {}

        if switch_id:
            body_data['switchId'] = switch_id
        if resource_pool:
            body_data['resourcePool'] = resource_pool
        if hostname:
            body_data['hostname'] = hostname
        if name:
            body_data['name'] = name
        if ip:
            body_data['ip'] = ip

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/switch/list',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )

    def list_gateway_cloud_express(self, gateway_name: str) -> Dict[str, Any]:
        """
        专线网关绑定的云间高速查询

        Args:
            gateway_name: 专线网关名字

        Returns:
            API响应结果

        Raises:
            CDAAPIError: API调用失败
        """
        logger.info(f"查询专线网关绑定的云间高速: gateway_name={gateway_name}")

        # 构造请求体
        body_data = {
            'gatewayName': gateway_name,
            'vrfName': gateway_name  # 根据经验，同时提供两个参数
        }

        return self.make_eop_request(
            method='GET',  # API文档明确要求GET方法
            endpoint_path='/v4/cda/ec/info',
            body_data=body_data  # GET方法但传递body数据（天翼云特殊模式）
        )


# 创建全局CDA客户端实例
CDA_CLIENT = None


def init_cda_client(client: CTYUNClient) -> CDAClient:
    """
    初始化CDA客户端

    Args:
        client: 天翼云API客户端

    Returns:
        CDA客户端实例
    """
    global CDA_CLIENT
    CDA_CLIENT = CDAClient(client)
    return CDA_CLIENT


def get_cda_client() -> CDAClient:
    """
    获取CDA客户端实例

    Returns:
        CDA客户端实例

    Raises:
        RuntimeError: 如果客户端未初始化
    """
    if CDA_CLIENT is None:
        raise RuntimeError("CDA客户端未初始化，请先调用 init_cda_client()")
    return CDA_CLIENT