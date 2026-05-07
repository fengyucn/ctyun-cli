"""
云电脑(CloudPC) API客户端
"""

from typing import Dict, List, Optional, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class CloudPCClient:
    """天翼云云电脑(CloudPC)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'ecpc-global.ctapi.ctyun.cn'
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

    def _get(self, path: str, region_id: str, query_params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """通用 GET 请求（regionId 作为 query 参数）"""
        try:
            url = f'https://{self.base_endpoint}{path}'
            params = {'regionId': region_id}
            if query_params:
                params.update({k: v for k, v in query_params.items() if v is not None})
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=params,
                body='', extra_headers={}
            )
            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {params}")
            response = self.client.session.get(
                url, params=params, headers=headers, timeout=self.timeout
            )
            logger.debug(f"响应状态码: {response.status_code}")
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"请求失败 ({path}): {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def _page_params(self, page_num: int = None, page_size: int = None) -> Dict[str, str]:
        params = {}
        if page_num is not None:
            params['pageNum'] = str(page_num)
        if page_size is not None:
            params['pageSize'] = str(page_size)
        return params

    # ========== 桌面实例查询 ==========

    def describe_desktops(self, region_id: str, desktop_oid: str = None,
                          nickname: str = None, prod_inst_id: str = None,
                          status: str = None, vpc_oid: str = None,
                          page_num: int = None, page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询云电脑列表"""
        params = {**self._page_params(page_num, page_size)}
        if desktop_oid: params['desktopOid'] = desktop_oid
        if nickname: params['desktopNickName'] = nickname
        if prod_inst_id: params['prodInstId'] = prod_inst_id
        if status: params['status'] = status
        if vpc_oid: params['vpcOid'] = vpc_oid
        return self._get('/v3/desktop/describe', region_id, params)

    def check_service_status(self, region_id: str) -> Optional[Dict[str, Any]]:
        """查询云电脑服务开通状态"""
        return self._get('/v3/desktopService/checkStatus', region_id)

    def describe_desktop_price(self, region_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """创建云电脑询价"""
        params = {}
        for k, v in kwargs.items():
            if v is not None:
                params[k] = v
        return self._get('/v3/desktop/price', region_id, params)

    def describe_desktop_flavor_templates(self, region_id: str, os_type: str = None,
                                          flavor_type: str = None, cpu_arch: str = None,
                                          page_num: int = None, page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询云电脑规格模版"""
        params = {**self._page_params(page_num, page_size)}
        if os_type: params['osType'] = os_type
        if flavor_type: params['flavorType'] = flavor_type
        if cpu_arch: params['cpuArch'] = cpu_arch
        return self._get('/v3/desktopTemplate/describe', region_id, params)

    # ========== ECS型云电脑 ==========

    def describe_ecs(self, region_id: str, desktop_oid: str = None,
                     nickname: str = None, vpc_oid: str = None,
                     status: str = None, page_num: int = None,
                     page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询弹性云电脑(ECS型)列表"""
        params = {**self._page_params(page_num, page_size)}
        if desktop_oid: params['desktopOid'] = desktop_oid
        if nickname: params['desktopNickName'] = nickname
        if vpc_oid: params['vpcOid'] = vpc_oid
        if status: params['status'] = status
        return self._get('/v3/ecs/describe', region_id, params)

    # ========== 镜像查询 ==========

    def describe_available_images(self, region_id: str, os_type: str = None,
                                  flavor_type: str = None, cpu_arch: str = None,
                                  page_num: int = None, page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询可用镜像列表"""
        params = {**self._page_params(page_num, page_size)}
        if os_type: params['osType'] = os_type
        if flavor_type: params['flavorType'] = flavor_type
        if cpu_arch: params['cpuArch'] = cpu_arch
        return self._get('/v3/image/describe', region_id, params)

    # ========== 云硬盘查询 ==========

    def describe_cloud_volumes(self, region_id: str, desktop_oid: str = None,
                               disk_type: str = None, for_sys_disk: bool = None,
                               status: str = None, page_num: int = None,
                               page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询云硬盘列表"""
        params = {**self._page_params(page_num, page_size)}
        if desktop_oid: params['desktopOid'] = desktop_oid
        if disk_type: params['diskType'] = disk_type
        if for_sys_disk is not None: params['forSysDisk'] = 'true' if for_sys_disk else 'false'
        if status: params['status'] = status
        return self._get('/v3/cloudVolume/describe', region_id, params)

    def describe_available_disk_types(self, region_id: str) -> Optional[Dict[str, Any]]:
        """查询可用磁盘类型"""
        return self._get('/v3/desktop/describeAvailableDiskType', region_id)

    # ========== 网络查询 ==========

    def describe_vpcs(self, region_id: str, vpc_oid: str = None,
                      vpc_name: str = None, page_num: int = None,
                      page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询VPC列表"""
        params = {**self._page_params(page_num, page_size)}
        if vpc_oid: params['vpcOid'] = vpc_oid
        if vpc_name: params['vpcName'] = vpc_name
        return self._get('/v3/vpc/describe', region_id, params)

    def describe_subnets(self, region_id: str, vpc_oid: str, subnet_oid: str = None,
                         page_num: int = None, page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询子网列表"""
        params = {'vpcOid': vpc_oid, **self._page_params(page_num, page_size)}
        if subnet_oid: params['subnetOid'] = subnet_oid
        return self._get('/v3/vpc/subnet/describe', region_id, params)

    # ========== 用户与部门查询 ==========

    def describe_users(self, region_id: str, org_oid: str = None,
                       user_name: str = None, user_account: str = None,
                       page_num: int = None, page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询用户列表"""
        params = {**self._page_params(page_num, page_size)}
        if org_oid: params['orgOid'] = org_oid
        if user_name: params['userName'] = user_name
        if user_account: params['userAccount'] = user_account
        return self._get('/v3/user/describe', region_id, params)

    def describe_organizations(self, region_id: str, parent_org_oid: str = None,
                               org_name: str = None, page_num: int = None,
                               page_size: int = None) -> Optional[Dict[str, Any]]:
        """查询部门列表"""
        params = {**self._page_params(page_num, page_size)}
        if parent_org_oid: params['parentOrgOid'] = parent_org_oid
        if org_name: params['orgName'] = org_name
        return self._get('/v3/org/describe', region_id, params)
