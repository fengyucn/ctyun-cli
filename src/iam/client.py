"""
天翼云统一身份认证(IAM)服务客户端
提供统一身份认证全功能API
"""

from typing import Dict, Any, Optional, List
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class IAMClient:
    """天翼云统一身份认证(IAM)服务客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化IAM服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'iam'
        self.base_endpoint = 'ctiam-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _post(self, path: str, body_data: dict,
              extra_headers: Optional[dict] = None,
              description: str = "") -> Dict[str, Any]:
        """通用POST请求"""
        logger.info(f"{description}: {body_data}")
        try:
            url = f"https://{self.base_endpoint}{path}"
            body = json.dumps(body_data)
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params=None, body=body,
                extra_headers=extra_headers or {}
            )
            logger.debug(f"请求URL: {url}, 请求体: {body}")
            response = self.client.session.post(
                url, data=body, headers=headers, timeout=30, verify=False
            )
            logger.debug(f"响应状态码: {response.status_code}")
            if response.status_code != 200:
                return {
                    'statusCode': str(response.status_code),
                    'error': f'HTTP_{response.status_code}',
                    'message': response.text
                }
            return response.json()
        except Exception as e:
            logger.error(f"{description}失败: {str(e)}")
            return {'statusCode': '500', 'error': 'Exception', 'message': str(e)}

    def _get(self, path: str, query_params: Optional[dict] = None,
             extra_headers: Optional[dict] = None,
             description: str = "") -> Dict[str, Any]:
        """通用GET请求"""
        logger.info(f"{description}: {query_params}")
        try:
            url = f"https://{self.base_endpoint}{path}"
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params or {},
                body=None, extra_headers=extra_headers or {}
            )
            logger.debug(f"请求URL: {url}, 参数: {query_params}")
            response = self.client.session.get(
                url, params=query_params, headers=headers,
                timeout=30, verify=False
            )
            logger.debug(f"响应状态码: {response.status_code}")
            if response.status_code != 200:
                return {
                    'statusCode': str(response.status_code),
                    'error': f'HTTP_{response.status_code}',
                    'message': response.text
                }
            return response.json()
        except Exception as e:
            logger.error(f"{description}失败: {str(e)}")
            return {'statusCode': '500', 'error': 'Exception', 'message': str(e)}

    # ==================== 企业项目管理 (3 existing) ====================

    def list_enterprise_projects(
            self,
            account_id: str,
            current_page: int = 1,
            page_size: int = 10) -> Dict[str, Any]:
        """查询企业项目列表"""
        return self._post(
            '/v1/project/getEpPageList',
            {'accountId': account_id, 'currentPage': current_page, 'pageSize': page_size},
            {'accountId': account_id},
            '查询企业项目列表'
        )

    def get_enterprise_project(self, project_id: str) -> Dict[str, Any]:
        """查询企业项目详情"""
        return self._get(
            '/v1/project/getEnterpriseProjectById',
            {'id': project_id},
            {'accountId': self.client.access_key},
            '查询企业项目详情'
        )

    def list_resources(
            self,
            project_set_id: str,
            page_num: int = 1,
            page_size: int = 10) -> Dict[str, Any]:
        """分页查询资源信息"""
        return self._post(
            '/v1/resource/getResourcePageList',
            {'projectSetId': project_set_id, 'pageNum': page_num, 'pageSize': page_size},
            {'accountId': self.client.access_key},
            '分页查询资源信息'
        )

    # ==================== 用户管理 ====================

    def query_login_config(self, user_id: str) -> Dict[str, Any]:
        """用户登录设置_查询配置"""
        return self._post(
            '/v1/user/queryLoginAuthen',
            {'userId': user_id},
            description='查询用户登录配置'
        )

    def get_user_detail(self, user_id: str) -> Dict[str, Any]:
        """根据id查询用户详情"""
        return self._get(
            '/v1/user/getUser',
            {'userId': user_id},
            description='查询用户详情'
        )

    def list_users(self, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """分页查询用户"""
        return self._post(
            '/v1/openapi/user/getUsers',
            {'pageNum': page_num, 'pageSize': page_size},
            description='分页查询用户'
        )

    def query_access_control(self, user_id: str) -> Dict[str, Any]:
        """查询控制台和api编程式访问配置"""
        return self._post(
            '/v1/user/queryAccessControl',
            {'userId': user_id},
            description='查询访问控制配置'
        )

    # ==================== 用户组管理 ====================

    def get_group_info(self, group_id: str) -> Dict[str, Any]:
        """根据用户组ID查询用户组信息"""
        return self._get(
            '/v1/userGroup/getGroupByGroupId',
            {'groupId': group_id},
            description='查询用户组信息'
        )

    def list_group_users(self, page_num: int = 1, page_size: int = 10,
                         group_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """分页查询用户组下的用户"""
        if group_ids is None:
            group_ids = []
        return self._post(
            '/v1/userGroup/getGroupUser',
            {'pageNum': page_num, 'pageSize': page_size,
             'groups': [{'id': gid} for gid in group_ids]},
            description='分页查询用户组下的用户'
        )

    def list_groups(self, page_num: int = 1, page_size: int = 10,
                    group_name: Optional[str] = None) -> Dict[str, Any]:
        """分页查询用户组"""
        body = {'pageNum': page_num, 'pageSize': page_size}
        if group_name:
            body['groupName'] = group_name
        return self._post(
            '/v1/userGroup/getGroups',
            body,
            description='分页查询用户组'
        )

    # ==================== 权限管理 ====================

    def list_permissions_by_account(self, page_num: int = 1,
                                    page_size: int = 10) -> Dict[str, Any]:
        """通过账户ID分页查询权限"""
        return self._post(
            '/v1/perm/query',
            {'pageNum': page_num, 'pageSize': page_size},
            description='分页查询权限'
        )

    def list_user_policies(self, user_id: str) -> Dict[str, Any]:
        """通过用户ID查询权限"""
        return self._get(
            '/v1/perm/listUserPolicy',
            {'userId': user_id},
            description='查询用户权限'
        )

    def list_group_policies(self, group_id: str) -> Dict[str, Any]:
        """通过用户组ID查询权限"""
        return self._get(
            '/v1/perm/listGroupPolicy',
            {'groupId': group_id},
            description='查询用户组权限'
        )

    def get_privilege_by_id(self, privilege_id: str) -> Dict[str, Any]:
        """根据授权id查询授权信息"""
        return self._get(
            '/v1/perm/queryPrivilegeById',
            {'privilegeId': privilege_id},
            description='查询授权信息'
        )

    def list_user_own_policies(self, user_id: str) -> Dict[str, Any]:
        """查询用户自身权限"""
        return self._get(
            '/v1/perm/listUserOneselfPolicy',
            {'userId': user_id},
            description='查询用户自身权限'
        )

    def list_user_inherited_policies(self, user_id: str) -> Dict[str, Any]:
        """查询用户继承用户组的权限"""
        return self._get(
            '/v1/perm/listUserInheritGroupPolicy',
            {'userId': user_id},
            description='查询用户继承权限'
        )

    # ==================== 策略管理 ====================

    def list_policies(self, page_num: int = 1, page_size: int = 10,
                      policy_type: Optional[int] = None,
                      policy_range: Optional[int] = None,
                      policy_name: Optional[str] = None,
                      policy_description: Optional[str] = None) -> Dict[str, Any]:
        """根据账户ID查询所有策略"""
        body = {'pageNum': page_num, 'pageSize': str(page_size)}
        if policy_type is not None:
            body['policyType'] = policy_type
        if policy_range is not None:
            body['policyRange'] = policy_range
        if policy_name:
            body['policyName'] = policy_name
        if policy_description:
            body['policyDescription'] = policy_description
        return self._post(
            '/v1/policy/queryPolicy',
            body,
            description='查询所有策略'
        )

    def get_policy_detail(self, policy_id: str) -> Dict[str, Any]:
        """查询策略详情"""
        return self._get(
            '/v1/policy/getPolicyById',
            {'policyId': policy_id},
            description='查询策略详情'
        )

    # ==================== 委托管理 ====================

    def get_delegate_role_detail(self, delegate_id: str) -> Dict[str, Any]:
        """根据id查询委托角色详情"""
        return self._get(
            '/v1/delegate/getDelegateRole',
            {'id': delegate_id},
            description='查询委托角色详情'
        )

    def query_delegate_list(self, account_id: str,
                            service_code: Optional[str] = None,
                            delegate_type: Optional[int] = None,
                            name: Optional[str] = None) -> Dict[str, Any]:
        """查询指定账号下的云服务委托或内联委托列表"""
        params = {'accountId': account_id}
        if service_code:
            params['serviceCode'] = service_code
        if delegate_type is not None:
            params['type'] = delegate_type
        if name:
            params['name'] = name
        return self._get(
            '/v1/delegate/queryDelegateList',
            params,
            description='查询委托列表'
        )

    def list_delegate_roles(self, page_num: int = 1,
                            page_size: int = 10) -> Dict[str, Any]:
        """查询委托角色分页信息"""
        return self._post(
            '/v1/delegate/queryDelegateRoles',
            {'pageNum': page_num, 'pageSize': page_size},
            description='查询委托角色分页'
        )

    # ==================== 企业项目扩展 ====================

    def list_ep_group_page(self, project_id: str, page_num: int = 1,
                           page_size: int = 10) -> Dict[str, Any]:
        """企业项目关联用户组分页查询"""
        return self._post(
            '/v1/project/getEpGroupPageList',
            {'id': project_id, 'pageNum': page_num, 'pageSize': page_size},
            description='企业项目关联用户组分页查询'
        )

    def get_ep_group_policies(self, project_id: str,
                              group_id: str) -> Dict[str, Any]:
        """查询企业项目用户组策略"""
        return self._post(
            '/v1/project/getEpPloy',
            {'projectId': project_id, 'groupId': group_id},
            description='查询企业项目用户组策略'
        )

    # ==================== AK/SK管理 ====================

    def list_access_keys(self, user_id_list: List[str]) -> Dict[str, Any]:
        """查询密钥"""
        return self._post(
            '/v1/credential/queryAk',
            {'userIdList': user_id_list},
            description='查询密钥'
        )

    def list_recycle_bin_aks(self, user_id_list: List[str]) -> Dict[str, Any]:
        """查询回收站ak"""
        return self._post(
            '/v1/credential/queryRecycleBinAk',
            {'userIdList': user_id_list},
            description='查询回收站AK'
        )

    # ==================== 身份供应商 ====================

    def list_identity_providers(self, page_num: int = 1,
                                page_size: int = 10,
                                name: Optional[str] = None) -> Dict[str, Any]:
        """分页查询身份供应商"""
        body = {'pageNum': page_num, 'pageSize': page_size}
        if name:
            body['name'] = name
        return self._post(
            '/v1/identityProvider/queryIdPs',
            body,
            description='分页查询身份供应商'
        )

    def get_identity_provider_info(self, id_p_id: str, entity_id: str,
                                   name_id: str,
                                   login_email: Optional[str] = None
                                   ) -> Dict[str, Any]:
        """查询身份供应商和关联用户信息"""
        body = {
            'idPId': id_p_id,
            'entityId': entity_id,
            'nameId': name_id,
        }
        if login_email:
            body['loginEmail'] = login_email
        return self._post(
            '/v1/identityProvider/getIdentityProviderInfo',
            body,
            description='查询身份供应商和关联用户信息'
        )

    # ==================== MFA管理 ====================

    def check_totp_effective(self) -> Dict[str, Any]:
        """查询虚拟MFA是否绑定"""
        return self._get(
            '/v1/user/totpEffective',
            None,
            description='查询虚拟MFA是否绑定'
        )

    # ==================== 敏感操作 ====================

    def query_sensitive_events(self, page_num: int = 1,
                               page_size: int = 10,
                               start_time: str = "",
                               end_time: str = "") -> Dict[str, Any]:
        """查询敏感操作分页信息"""
        return self._post(
            '/v1/sensitive/querySensitiveEvent',
            {
                'pageNum': page_num,
                'pageSize': page_size,
                'startTime': start_time,
                'endTime': end_time
            },
            description='查询敏感操作分页信息'
        )

    def query_op_verify(self) -> Dict[str, Any]:
        """查询敏感操作保护"""
        return self._get(
            '/v1/security/queryOpVerify',
            None,
            description='查询敏感操作保护'
        )

    # ==================== 服务管理 ====================

    def query_service_authorities(self, service_id: int) -> Dict[str, Any]:
        """根据云服务ID查询云服务权限点"""
        return self._get(
            '/v1/service/queryAllAuthorityByServiceId',
            {'serviceId': service_id},
            description='查询云服务权限点'
        )

    def query_services_by_condition(self, service_name: Optional[str] = None,
                                    service_type: Optional[int] = None
                                    ) -> Dict[str, Any]:
        """根据条件查询云服务产品"""
        body = {}
        if service_name:
            body['serviceName'] = service_name
        if service_type is not None:
            body['serviceType'] = service_type
        return self._post(
            '/v1/service/queryCtapiServiceByCondition',
            body,
            description='查询云服务产品'
        )

    # ==================== 其他 ====================

    def query_quota_by_type(self, quota_type: int) -> Dict[str, Any]:
        """根据配额类型查询配额列表 (1:用户, 2:用户组, 3:策略)"""
        return self._post(
            '/v1/quota/queryQuotaByType',
            {'type': quota_type},
            description='查询配额'
        )

    def query_regions(self, zone_name: Optional[str] = None,
                      zone_id: Optional[str] = None) -> Dict[str, Any]:
        """查询账户资源池"""
        body = {}
        if zone_name:
            body['zoneName'] = zone_name
        if zone_id:
            body['zoneId'] = zone_id
        return self._post(
            '/v1/region/queryRegionByAccountId',
            body,
            description='查询账户资源池'
        )
