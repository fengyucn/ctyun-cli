"""
天翼云账务中心客户端
提供账单查询、费用查询、欠费查询等功能
"""

from typing import Dict, Any, List, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class BillingClient:
    """天翼云账务中心客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化账务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'billing'
        self.base_endpoint = 'acct-global.ctapi.ctyun.cn'
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def query_bill_list(self, bill_cycle: str, page_no: int = 1,
                       page_size: int = 10, product_code: Optional[str] = None,
                       resource_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询账单明细（按需）
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202311
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            product_code: 产品编码（可选）
            resource_id: 资源ID（可选）
            
        Returns:
            账单列表信息
        """
        logger.info(f"查询账单明细: bill_cycle={bill_cycle}, page={page_no}, pageSize={page_size}")
        
        try:
            url = f"https://{self.base_endpoint}/bill_qryOnDemandBillDetail_Res_Detail"
            
            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': str(page_no),
                'pageSize': str(page_size),
                'hasTotal': False
            }
            
            if product_code:
                body_data['productCode'] = product_code
            if resource_id:
                body_data['resourceId'] = resource_id
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账单明细失败: {str(e)}")
            raise
    def query_ondemand_bill_by_product(self, bill_cycle: str, page_no: int = 1,
                                       page_size: int = 10, product_code: Optional[str] = None,
                                       bill_type: Optional[str] = None,
                                       contract_id: Optional[str] = None,
                                       group_by_day: Optional[str] = None) -> Dict[str, Any]:
        """
        查询账单明细产品+账期（按需）
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202508
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            product_code: 产品编码（可选）
            bill_type: 账单类型（可选）
            contract_id: 合同ID（可选）
            group_by_day: 是否按天查询，"1"为按天，"0"或不传为按账期（可选）
            
        Returns:
            按需账单明细（按产品汇总）
        """
        logger.info(f"查询按需账单明细(按产品): bill_cycle={bill_cycle}, page={page_no}")
        
        try:
            url = f"https://{self.base_endpoint}/qryOnDemandBillDetail_Prod_CycleId"
            
            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size,
                'hasTotal': False
            }
            
            if product_code:
                body_data['productCode'] = product_code
            if bill_type:
                body_data['billType'] = bill_type
            if contract_id:
                body_data['contractId'] = contract_id
            if group_by_day:
                body_data['groupByonDay'] = group_by_day
            
            body = json.dumps(body_data)
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            response = self.client.session.post(url, data=body, headers=headers, timeout=30)
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"按需账单明细(按产品)查询结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"按需账单明细(按产品)查询失败: {e}")
            raise
    
    def query_cycle_bill_by_product(self, bill_cycle: str, page_no: int = 1,
                                    page_size: int = 10, bill_type: Optional[str] = None,
                                    product_code: Optional[str] = None,
                                    contract_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询账单明细产品+账期（包周期）
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202508
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            bill_type: 账单类型（可选）
            product_code: 产品编码（可选）
            contract_id: 合同ID（可选）
            
        Returns:
            包周期账单明细（按产品汇总）
        """
        logger.info(f"查询包周期账单明细(按产品): bill_cycle={bill_cycle}, page={page_no}")
        
        try:
            url = f"https://{self.base_endpoint}/qryCycleBillDetail_Prod_CycleId"
            
            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            if bill_type:
                body_data['billType'] = bill_type
            if product_code:
                body_data['productCode'] = product_code
            if contract_id:
                body_data['contractId'] = contract_id
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询包周期账单明细(按产品)失败: {str(e)}")
            raise
    def query_ondemand_bill_flow(self, bill_cycle: str, page_no: int = 1,
                                 page_size: int = 10, contract_id: Optional[str] = None,
                                 project_id: Optional[str] = None,
                                 product_code: Optional[str] = None,
                                 bill_type: Optional[str] = None,
                                 pay_method: Optional[str] = None,
                                 master_order_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询按需流水账单
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202508
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            contract_id: 合同号（可选）
            project_id: 项目ID（可选）
            product_code: 产品编码（可选）
            bill_type: 账单类型（可选）
            pay_method: 支付方式（可选）
            master_order_id: 主订单号（可选）
            
        Returns:
            按需流水账单信息
        """
        logger.info(f"查询按需流水账单: bill_cycle={bill_cycle}, page={page_no}")
        
        try:
            url = f"https://{self.base_endpoint}/queryBillOnDemandFee"
            
            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size,
                'hasTotal': False
            }
            
            if contract_id:
                body_data['contractId'] = contract_id
            if project_id:
                body_data['projectId'] = project_id
            if product_code:
                body_data['productCode'] = product_code
            if bill_type:
                body_data['billType'] = bill_type
            if pay_method:
                body_data['payMethod'] = pay_method
            if master_order_id:
                body_data['masterOrderId'] = master_order_id
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询按需流水账单失败: {str(e)}")
            raise
    def query_cycle_bill_detail(self, bill_cycle: str, page_no: int = 1,
                                page_size: int = 10, resource_id: Optional[str] = None,
                                product_code: Optional[str] = None,
                                contract_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询包周期订单账单详情
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202311
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            resource_id: 资源ID（可选）
            product_code: 产品编码（可选）
            contract_id: 合同ID（可选）
            
        Returns:
            包周期账单详情信息
        """
        logger.info(f"查询包周期账单详情: bill_cycle={bill_cycle}, page={page_no}")
        
        try:
            url = f"https://{self.base_endpoint}/queryBillCycleFeeDetail"
            
            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            if resource_id:
                body_data['resourceId'] = resource_id
            if product_code:
                body_data['productCode'] = product_code
            if contract_id:
                body_data['contractId'] = contract_id
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询包周期账单详情失败: {str(e)}")
            raise
    def query_cycle_bill_flow(self, bill_cycle: str, page_no: int = 1,
                              page_size: int = 10, product_code: Optional[str] = None,
                              project_id: Optional[str] = None,
                              bill_type: Optional[str] = None,
                              contract_id: Optional[str] = None,
                              master_order_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询包周期流水账单
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202212
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            product_code: 产品编码（可选）
            project_id: 项目ID（可选）
            bill_type: 账单类型（可选）
            contract_id: 合同ID（可选）
            master_order_id: 主订单ID（可选）
            
        Returns:
            包周期流水账单信息
        """
        logger.info(f"查询包周期流水账单: bill_cycle={bill_cycle}, page={page_no}")
        
        try:
            url = f"https://{self.base_endpoint}/queryBillCycleFee"
            
            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            if product_code:
                body_data['productCode'] = product_code
            if project_id:
                body_data['projectId'] = project_id
            if bill_type:
                body_data['billType'] = bill_type
            if contract_id:
                body_data['contractId'] = contract_id
            if master_order_id:
                body_data['masterOrderId'] = master_order_id
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询包周期流水账单失败: {str(e)}")
            raise
    def query_bill_detail(self, bill_id: str) -> Dict[str, Any]:
        """
        查询账单详情
        
        Args:
            bill_id: 账单ID
            
        Returns:
            账单详情信息
        """
        logger.info(f"查询账单详情: bill_id={bill_id}")
        
        try:
            url = f"https://{self.base_endpoint}/v1/bill/queryBillDetail"
            
            body_data = {
                'billId': bill_id
            }
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={
                    'regionid': '200000001852',
                    'urlType': 'CTAPI'
                }
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                response.raise_for_status()
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账单详情失败: {str(e)}")
            raise

    def query_bill_summary_by_type(self, bill_cycle: str,
                                   contract_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询消费类型汇总（按需）
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202311
            contract_id: 合同ID（可选）
            
        Returns:
            消费类型汇总信息
        """
        logger.info(f"查询消费类型汇总: bill_cycle={bill_cycle}")
        
        try:
            url = f"https://{self.base_endpoint}/monthly_bill_summary_billType"
            
            body_data = {
                'billingCycleId': bill_cycle
            }
            
            if contract_id:
                body_data['contractId'] = contract_id
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询消费类型汇总失败: {str(e)}")
            raise
    def query_account_bill_by_account_id(self, bill_cycle: str, 
                                         account_ids: List[str]) -> Dict[str, Any]:
        """
        按账户查询账单
        
        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202206
            account_ids: 账户ID列表
            
        Returns:
            账户账单信息
        """
        logger.info(f"查询账户账单: bill_cycle={bill_cycle}, accounts={len(account_ids)}")
        
        try:
            url = f"https://{self.base_endpoint}/queryAccountBillByAccountId"
            
            account_list = [{'accountId': acc_id} for acc_id in account_ids]
            
            body_data = {
                'billingCycleId': bill_cycle,
                'account': account_list
            }
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账户账单失败: {str(e)}")
            raise
    def query_ondemand_bill_by_usage_cycle(self, bill_cycle: str, page_no: int = 1,
                                           page_size: int = 10, product_code: Optional[str] = None,
                                           resource_id: Optional[str] = None,
                                           project_id: Optional[str] = None,
                                           contract_id: Optional[str] = None,
                                           group_by_day: Optional[str] = None) -> Dict[str, Any]:
        """
        账单明细使用量类型+账期（按需）

        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202212
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            product_code: 产品编码（可选）
            resource_id: 资源实例ID（可选）
            project_id: 项目ID（可选）
            contract_id: 合同ID（可选）
            group_by_day: 是否为按天查询，"1"为按天查询，"0"或不传为按账期查询（可选）

        Returns:
            账单明细使用量类型+账期（按需）信息
        """
        logger.info(f"查询账单明细使用量类型+账期(按需): bill_cycle={bill_cycle}, page={page_no}")

        try:
            url = f"https://{self.base_endpoint}/qryOnDemandBillDetail_Usage_CycleId"

            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size,
                'hasTotal': False
            }

            if product_code:
                body_data['productCode'] = product_code
            if resource_id:
                body_data['resourceId'] = resource_id
            if project_id:
                body_data['projectId'] = project_id
            if contract_id:
                body_data['contractId'] = contract_id
            if group_by_day:
                body_data['groupByonDay'] = group_by_day

            body = json.dumps(body_data)

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result

        except Exception as e:
            logger.error(f"查询账单明细使用量类型+账期(按需)失败: {str(e)}")
            raise
    def query_ondemand_bill_by_usage_detail(self, bill_cycle: str, page_no: int = 1,
                                           page_size: int = 10, product_code: Optional[str] = None,
                                           resource_id: Optional[str] = None,
                                           project_id: Optional[str] = None,
                                           contract_id: Optional[str] = None) -> Dict[str, Any]:
        """
        账单明细使用量类型+明细（按需）

        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202212
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            product_code: 产品编码（可选）
            resource_id: 资源实例ID（可选）
            project_id: 项目ID（可选）
            contract_id: 合同ID（可选）

        Returns:
            账单明细使用量类型+明细（按需）信息
        """
        logger.info(f"查询账单明细使用量类型+明细(按需): bill_cycle={bill_cycle}, page={page_no}")

        try:
            url = f"https://{self.base_endpoint}/qryOnDemandBillDetail_Usage_Detail"

            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size,
                'hasTotal': False
            }

            if product_code:
                body_data['productCode'] = product_code
            if resource_id:
                body_data['resourceId'] = resource_id
            if project_id:
                body_data['projectId'] = project_id
            if contract_id:
                body_data['contractId'] = contract_id

            body = json.dumps(body_data)

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result

        except Exception as e:
            logger.error(f"查询账单明细使用量类型+明细(按需)失败: {str(e)}")
            raise
    def query_ondemand_bill_by_resource_cycle(self, bill_cycle: str, page_no: int = 1,
                                              page_size: int = 10, product_code: Optional[str] = None,
                                              resource_id: Optional[str] = None,
                                              contract_id: Optional[str] = None,
                                              group_by_day: Optional[str] = None) -> Dict[str, Any]:
        """
        账单明细资源+账期（按需）

        Args:
            bill_cycle: 账期，格式：YYYYMM，如：202212
            page_no: 页码，默认1
            page_size: 每页条数，默认10
            product_code: 产品编码（可选）
            resource_id: 资源ID（可选）
            contract_id: 合同ID（可选）
            group_by_day: 是否为按天查询，"1"为按天查询，"0"或不传为按账期查询（可选）

        Returns:
            账单明细资源+账期（按需）信息
        """
        logger.info(f"查询账单明细资源+账期(按需): bill_cycle={bill_cycle}, page={page_no}")

        try:
            url = f"https://{self.base_endpoint}/qryOnDemandBillDetail_Res_CycleId"

            body_data = {
                'billingCycleId': bill_cycle,
                'pageNo': page_no,
                'pageSize': page_size,
                'hasTotal': False
            }

            if product_code:
                body_data['productCode'] = product_code
            if resource_id:
                body_data['resourceId'] = resource_id
            if contract_id:
                body_data['contractId'] = contract_id
            if group_by_day:
                body_data['groupByonDay'] = group_by_day

            body = json.dumps(body_data)

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            response.raise_for_status()
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result

        except Exception as e:
            logger.error(f"查询账单明细资源+账期(按需)失败: {str(e)}")
            raise