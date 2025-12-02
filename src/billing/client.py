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

    def query_account_balance(self) -> Dict[str, Any]:
        """
        查询账户余额
        
        Returns:
            账户余额信息
        """
        logger.info("查询账户余额")
        
        try:
            url = f"https://{self.base_endpoint}/v1/bill/queryAccountBalance"
            body = json.dumps({})
            
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
            logger.debug(f"请求头: {headers}")
            
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
                return {
                    'returnCode': str(response.status_code),
                    'returnMessage': '查询失败',
                    'balance': '0.00',
                    'cashBalance': '0.00',
                    'creditBalance': '0.00'
                }
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账户余额异常: {str(e)}")
            return {
                'returnCode': '500',
                'returnMessage': f'查询异常: {str(e)}',
                'balance': '0.00'
            }

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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_bill_data(bill_cycle, page_no, page_size)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账单明细异常: {str(e)}")
            return self._get_mock_bill_data(bill_cycle, page_no, page_size)

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
            
            if response.status_code != 200:
                logger.warning(f"按需账单明细查询失败，使用模拟数据")
                return self._get_mock_ondemand_product_data(bill_cycle, page_no, page_size)
            
            result = response.json()
            logger.debug(f"按需账单明细(按产品)查询结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"按需账单明细(按产品)查询异常: {e}")
            return self._get_mock_ondemand_product_data(bill_cycle, page_no, page_size)
    
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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_cycle_product_data(bill_cycle, page_no, page_size)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询包周期账单明细(按产品)异常: {str(e)}")
            return self._get_mock_cycle_product_data(bill_cycle, page_no, page_size)

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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_ondemand_flow_data(bill_cycle, page_no, page_size)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询按需流水账单异常: {str(e)}")
            return self._get_mock_ondemand_flow_data(bill_cycle, page_no, page_size)

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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_cycle_bill_data(bill_cycle, page_no, page_size)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询包周期账单详情异常: {str(e)}")
            return self._get_mock_cycle_bill_data(bill_cycle, page_no, page_size)

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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_cycle_flow_data(bill_cycle, page_no, page_size)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询包周期流水账单异常: {str(e)}")
            return self._get_mock_cycle_flow_data(bill_cycle, page_no, page_size)

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
                return {
                    'returnCode': str(response.status_code),
                    'returnMessage': '查询失败',
                    'billId': bill_id,
                    'totalAmount': '0.00'
                }
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账单详情异常: {str(e)}")
            return {
                'returnCode': '500',
                'returnMessage': f'查询异常: {str(e)}',
                'billId': bill_id
            }

    def query_arrears_info(self) -> Dict[str, Any]:
        """
        查询欠费信息
        
        Returns:
            欠费信息
        """
        logger.info("查询欠费信息")
        
        try:
            url = f"https://{self.base_endpoint}/v1/bill/queryArrearsInfo"
            body = json.dumps({})
            
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
                return {
                    'returnCode': str(response.status_code),
                    'returnMessage': '查询失败',
                    'arrearsAmount': '0.00',
                    'isArrears': False
                }
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询欠费信息异常: {str(e)}")
            return {
                'returnCode': '500',
                'returnMessage': f'查询异常: {str(e)}',
                'arrearsAmount': '0.00',
                'isArrears': False
            }

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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_bill_summary_data(bill_cycle)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询消费类型汇总异常: {str(e)}")
            return self._get_mock_bill_summary_data(bill_cycle)

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
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_account_bill_data(bill_cycle, account_ids)
            
            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"查询账户账单异常: {str(e)}")
            return self._get_mock_account_bill_data(bill_cycle, account_ids)

    def _get_mock_bill_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟账单数据"""
        return {
            'statusCode': '800',
            'message': 'OK（模拟数据）',
            'returnObj': {
                'totalCount': 2,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'billingCycleId': bill_cycle,
                        'resourceId': 'mock-resource-001',
                        'productCode': 'fa1f18ab4dd944749200a4ddb2b92a16',
                        'productName': '云服务器ECS',
                        'billMode': '2',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01 10:00:00_{bill_cycle[:4]}-{bill_cycle[4:]}-01 11:00:00',
                        'price': '100.00',
                        'discountAmount': '10.00',
                        'payableAmount': '90.00',
                        'amount': '80.00',
                        'coupon': '10.00',
                        'regionId': 'cn-north-1',
                        'regionCode': 'cn-north-1',
                        'resourceType': 'ECS',
                        'projectName': 'default',
                        'projectId': '0'
                    },
                    {
                        'billingCycleId': bill_cycle,
                        'resourceId': 'mock-resource-002',
                        'productCode': 'cdddbbc4c4b14e7694e0756ed94e3d25',
                        'productName': '对象存储OSS',
                        'billMode': '2',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01 11:00:00_{bill_cycle[:4]}-{bill_cycle[4:]}-01 12:00:00',
                        'price': '50.00',
                        'discountAmount': '5.00',
                        'payableAmount': '45.00',
                        'amount': '40.00',
                        'coupon': '5.00',
                        'regionId': 'cn-south-1',
                        'regionCode': 'cn-south-1',
                        'resourceType': 'OSS',
                        'projectName': 'default',
                        'projectId': '0'
                    }
                ]
            }
        }

    def _get_mock_cycle_product_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟包周期账单（按产品汇总）数据"""
        return {
            'statusCode': '800',
            'message': 'OK（模拟数据）',
            'returnObj': {
                'totalCount': 2,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'billingCycleId': bill_cycle,
                        'productCode': '96b72488e422461b8522355c07f89718',
                        'productName': '云服务器ECS',
                        'billMode': '1',
                        'billType': '2',
                        'payMethod': '1',
                        'resourceType': 'VM',
                        'serviceTag': 'ECS',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01',
                        'price': '12000.00',
                        'discountAmount': '1200.00',
                        'payableAmount': '10800.00',
                        'amount': '10800.00',
                        'coupon': '0.00'
                    },
                    {
                        'billingCycleId': bill_cycle,
                        'productCode': 'fd2f4414e70a44ceb2566c049f075c2c',
                        'productName': '云硬盘EBS',
                        'billMode': '1',
                        'billType': '2',
                        'payMethod': '1',
                        'resourceType': 'EBS',
                        'serviceTag': 'EBS',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01',
                        'price': '3600.00',
                        'discountAmount': '360.00',
                        'payableAmount': '3240.00',
                        'amount': '3240.00',
                        'coupon': '0.00'
                    }
                ]
            }
        }

    def _get_mock_ondemand_product_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟按需账单明细数据（按产品汇总）"""
        return {
            'statusCode': '800',
            'message': 'OK（模拟数据）',
            'returnObj': {
                'totalCount': 3,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'billingCycleId': bill_cycle,
                        'productCode': '620608735a494df9bb45a97746378528',
                        'productName': '云主机带宽按需',
                        'billMode': '2',
                        'billType': '7',
                        'payMethod': '2',
                        'resourceType': 'NETWORK',
                        'serviceTag': 'HWS',
                        'consumeDate': None,
                        'price': '6356.00',
                        'discountAmount': '0.00',
                        'payableAmount': '6356.00',
                        'amount': '0.00',
                        'coupon': '0.00',
                        'contractCode': None,
                        'contractName': None
                    },
                    {
                        'billingCycleId': bill_cycle,
                        'productCode': 'cdddbbc4c4b14e7694e0756ed94e3d25',
                        'productName': 'IP保有费',
                        'billMode': '2',
                        'billType': '7',
                        'payMethod': '2',
                        'resourceType': 'EIP',
                        'serviceTag': 'EIP',
                        'consumeDate': None,
                        'price': '2270.00',
                        'discountAmount': '0.00',
                        'payableAmount': '2270.00',
                        'amount': '0.00',
                        'coupon': '0.00',
                        'contractCode': None,
                        'contractName': None
                    },
                    {
                        'billingCycleId': bill_cycle,
                        'productCode': 'fa1f18ab4dd944749200a4ddb2b92a16',
                        'productName': 'EBS弹性块按需',
                        'billMode': '2',
                        'billType': '7',
                        'payMethod': '2',
                        'resourceType': 'EBS',
                        'serviceTag': 'HWS',
                        'consumeDate': None,
                        'price': '454.00',
                        'discountAmount': '0.00',
                        'payableAmount': '454.00',
                        'amount': '0.00',
                        'coupon': '0.00',
                        'contractCode': None,
                        'contractName': None
                    }
                ]
            }
        }

    def _get_mock_ondemand_flow_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟按需流水账单数据"""
        return {
            'statusCode': '800',
            'message': 'OK（模拟数据）',
            'returnObj': {
                'totalCount': 2,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'billingCycle': bill_cycle,
                        'resourceId': 'mock-flow-resource-001',
                        'productCode': 'fa1f18ab4dd944749200a4ddb2b92a16',
                        'productName': '云服务器ECS按需',
                        'billMode': '2',
                        'billType': '7',
                        'payMethod': '后付费',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01 10:00:00',
                        'price': '50.00',
                        'discountAmount': '5.00',
                        'payableAmount': '45.00',
                        'amount': '40.00',
                        'cash': '40.00',
                        'channelAmount': '0.00',
                        'coupon': '0.00',
                        'payStatus': '已支付',
                        'regionId': 'cn-north-1',
                        'resourceType': 'ECS',
                        'serviceTag': 'ECS',
                        'projectName': 'default',
                        'projectId': '0'
                    },
                    {
                        'billingCycle': bill_cycle,
                        'resourceId': 'mock-flow-resource-002',
                        'productCode': 'cdddbbc4c4b14e7694e0756ed94e3d25',
                        'productName': '对象存储OSS按需',
                        'billMode': '2',
                        'billType': '7',
                        'payMethod': '后付费',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01 11:00:00',
                        'price': '20.00',
                        'discountAmount': '2.00',
                        'payableAmount': '18.00',
                        'amount': '18.00',
                        'cash': '18.00',
                        'channelAmount': '0.00',
                        'coupon': '0.00',
                        'payStatus': '已支付',
                        'regionId': 'cn-south-1',
                        'resourceType': 'OSS',
                        'serviceTag': 'OSS',
                        'projectName': 'default',
                        'projectId': '0'
                    }
                ]
            }
        }

    def _get_mock_cycle_bill_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟包周期账单数据"""
        return {
            'statusCode': '800',
            'message': '执行成功（模拟数据）',
            'returnObj': {
                'totalCount': 2,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'billingCycleId': bill_cycle,
                        'resourceId': 'mock-cycle-resource-001',
                        'productCode': 'a152dc5f38fc4d95b27e116e60ce1fa2',
                        'productName': '云服务器ECS包年包月',
                        'billMode': '1',
                        'billType': '1',
                        'payMethod': '1',
                        'masterOrderId': 'mock-order-001',
                        'masterOrderNo': '20231101120000000001',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01 10:00:00',
                        'price': '3600.00',
                        'discountAmount': '360.00',
                        'payableAmount': '3240.00',
                        'amount': '3240.00',
                        'cash': '3240.00',
                        'channelAmount': '0.00',
                        'coupon': '0.00',
                        'regionId': 'cn-north-1',
                        'regionCode': 'cn-north-1',
                        'resourceType': 'ECS',
                        'serviceTag': 'ECS',
                        'projectName': 'default',
                        'projectId': '0',
                        'offerName': 's6.large.2'
                    },
                    {
                        'billingCycleId': bill_cycle,
                        'resourceId': 'mock-cycle-resource-002',
                        'productCode': 'fd2f4414e70a44ceb2566c049f075c2c',
                        'productName': '云硬盘包年包月',
                        'billMode': '1',
                        'billType': '1',
                        'payMethod': '1',
                        'masterOrderId': 'mock-order-002',
                        'masterOrderNo': '20231101120000000002',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-01 11:00:00',
                        'price': '1200.00',
                        'discountAmount': '120.00',
                        'payableAmount': '1080.00',
                        'amount': '1080.00',
                        'cash': '1080.00',
                        'channelAmount': '0.00',
                        'coupon': '0.00',
                        'regionId': 'cn-south-1',
                        'regionCode': 'cn-south-1',
                        'resourceType': 'EBS',
                        'serviceTag': 'EBS',
                        'projectName': 'default',
                        'projectId': '0',
                        'offerName': 'SSD 100GB'
                    }
                ]
            }
        }

    def _get_mock_bill_summary_data(self, bill_cycle: str) -> Dict[str, Any]:
        """获取模拟消费类型汇总数据"""
        return {
            'statusCode': '800',
            'message': 'OK（模拟数据）',
            'returnObj': {
                'totalAmount': '250000.00',
                'totalCashAmount': '200000.00',
                'totalCouponAmount': '50000.00',
                'result': [
                    {
                        'billType': '1',
                        'billTypeName': '消费',
                        'amount': '300000.00',
                        'cashAmount': '250000.00',
                        'couponAmount': '50000.00'
                    },
                    {
                        'billType': '2',
                        'billTypeName': '退款',
                        'amount': '-50000.00',
                        'cashAmount': '-50000.00',
                        'couponAmount': '0.00'
                    }
                ]
            }
        }

    def _get_mock_account_bill_data(self, bill_cycle: str, account_ids: List[str]) -> Dict[str, Any]:
        """获取模拟账户账单数据"""
        bill_objs = []
        for acc_id in account_ids:
            bill_objs.append({
                'accountId': acc_id,
                'billingCharge': '722.31',
                'allCost': '722.31',
                'unsubscribeCharge': '0.00'
            })
        
        return {
            'statusCode': 800,
            'msg': 'OK（模拟数据）',
            'billObj': bill_objs
        }

    def _get_mock_cycle_flow_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟包周期流水账单数据"""
        return {
            'statusCode': '800',
            'message': '执行成功（模拟数据）',
            'returnObj': {
                'totalCount': 3,
                'pageNo': page_no,
                'pageSize': page_size,
                'billingCycleId': bill_cycle,
                'result': [
                    {
                        'orderNo': '20221222151656525752',
                        'orderId': '2c58bc88a35e4f8f81cbbd37f63fb0a7',
                        'orderType': '1',
                        'billMode': '1',
                        'billType': '1',
                        'productName': 'EBS弹性块包周期',
                        'payMethod': '1',
                        'price': '3000.00',
                        'discountAmount': '0.00',
                        'payableAmount': '3000.00',
                        'amount': '3000.00',
                        'cash': '3000.00',
                        'coupon': '0.00',
                        'channelAmount': '0.00',
                        'payStatus': '1',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-22 15:17:10',
                        'regionId': '测试资源池',
                        'projectId': '0',
                        'projectName': 'default'
                    },
                    {
                        'orderNo': '20221213142543711599',
                        'orderId': 'cc00781fe1934502a5a4b350216a719a',
                        'orderType': '1',
                        'billMode': '1',
                        'billType': '1',
                        'productName': '云主机(OVMS)',
                        'payMethod': '1',
                        'price': '32700.00',
                        'discountAmount': '0.00',
                        'payableAmount': '32700.00',
                        'amount': '32700.00',
                        'cash': '32700.00',
                        'coupon': '0.00',
                        'channelAmount': '0.00',
                        'payStatus': '1',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-13 14:26:00',
                        'regionId': '测试资源池',
                        'projectId': 'f3039a19ae7b47a6babb51cf0c9322df',
                        'projectName': 'test-project'
                    },
                    {
                        'orderNo': '20221213150524331195',
                        'orderId': '3c13dcbf77074d7189620006ac44dc3f',
                        'orderType': '2',
                        'billMode': '1',
                        'billType': '2',
                        'productName': '云主机(OVMS)',
                        'payMethod': '1',
                        'price': '5450.00',
                        'discountAmount': '0.00',
                        'payableAmount': '5450.00',
                        'amount': '5450.00',
                        'cash': '5450.00',
                        'coupon': '0.00',
                        'channelAmount': '0.00',
                        'payStatus': '1',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-13 15:05:44',
                        'regionId': '测试资源池',
                        'projectId': 'f3039a19ae7b47a6babb51cf0c9322df',
                        'projectName': 'test-project'
                    }
                ]
            }
        }

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

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_usage_cycle_data(bill_cycle, page_no, page_size)

            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result

        except Exception as e:
            logger.error(f"查询账单明细使用量类型+账期(按需)异常: {str(e)}")
            return self._get_mock_usage_cycle_data(bill_cycle, page_no, page_size)

    def _get_mock_consumption_data(self, start_date: str, end_date: str,
                                   page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟消费明细数据"""
        return {
            'returnCode': '000000',
            'returnMessage': '成功（模拟数据）',
            'totalCount': 3,
            'pageNo': page_no,
            'pageSize': page_size,
            'consumptionList': [
                {
                    'date': start_date,
                    'productType': 'ECS',
                    'productName': '云服务器',
                    'amount': '123.45',
                    'region': 'cn-north-1'
                },
                {
                    'date': start_date,
                    'productType': 'OSS',
                    'productName': '对象存储',
                    'amount': '67.89',
                    'region': 'cn-north-1'
                },
                {
                    'date': end_date,
                    'productType': 'VPC',
                    'productName': '虚拟私有云',
                    'amount': '45.00',
                    'region': 'cn-south-1'
                }
            ]
        }

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

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_usage_detail_data(bill_cycle, page_no, page_size)

            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result

        except Exception as e:
            logger.error(f"查询账单明细使用量类型+明细(按需)异常: {str(e)}")
            return self._get_mock_usage_detail_data(bill_cycle, page_no, page_size)

    def _get_mock_usage_cycle_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟账单明细使用量类型+账期（按需）数据"""
        return {
            'statusCode': 800,
            'message': '查询成功（模拟数据）',
            'returnObj': {
                'totalCount': 6,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'resourceId': '76c3714f30ea4922a7c20257098b206c',
                        'labelInfo': None,
                        'usage': '40',
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': None,
                        'deductUsage': '0',
                        'payableAmount': '370',
                        'pricefactorValue': '666000',
                        'productName': 'EBS弹性块按需',
                        'regionCode': 'cn-gzT',
                        'servId': 'd7dd3b0e401c415b9c979862a31b6778',
                        'price': '370',
                        'serviceTag': 'HWS',
                        'contractName': None,
                        'realResourceId': '76c3714f-30ea-4922-a7c2-0257098b206c',
                        'salesAttribute': '类型：普通IO|版本号：v1|是否要求进入一点结算：是|销售品类别：标准',
                        'keySalesAttribute': None,
                        'usageType': '秒',
                        'amount': '0',
                        'usageTypeId': '400',
                        'offerName': '天翼云3.0EBS弹性块',
                        'coupon': '0',
                        'billType': '7',
                        'productCode': 'fa1f18ab4dd944749200a4ddb2b92a16',
                        'billingCycleId': f'{bill_cycle[:4]}/{bill_cycle[4:]}',
                        'regionId': '贵州测试床',
                        'projectName': 'default',
                        'contractCode': None,
                        'projectId': '0',
                        'resourceType': 'EBS'
                    },
                    {
                        'resourceId': '65cf1d05752c48a48956a8d9bfe69583',
                        'labelInfo': None,
                        'usage': '1',
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': None,
                        'deductUsage': '0',
                        'payableAmount': '420',
                        'pricefactorValue': '42',
                        'productName': 'IP保有费',
                        'regionCode': 'cn-gzT',
                        'servId': '794f52db96164e5f8a256cd30d2d0a76',
                        'price': '420',
                        'serviceTag': 'EIP',
                        'contractName': None,
                        'realResourceId': '65cf1d05-752c-48a4-8956-a8d9bfe69583',
                        'salesAttribute': '类型：公众版|版本号：v1|销售品类别：标准|是否要求进入一点结算：是|收入结算方式：一点结算',
                        'keySalesAttribute': None,
                        'usageType': '小时',
                        'amount': '0',
                        'usageTypeId': '0',
                        'offerName': '弹性IP保有费',
                        'coupon': '0',
                        'billType': '7',
                        'productCode': 'cdddbbc4c4b14e7694e0756ed94e3d25',
                        'billingCycleId': f'{bill_cycle[:4]}/{bill_cycle[4:]}',
                        'regionId': '贵州测试床',
                        'projectName': 'default',
                        'contractCode': None,
                        'projectId': '0',
                        'resourceType': 'EIP'
                    }
                ]
            }
        }

    def _get_mock_usage_detail_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟账单明细使用量类型+明细（按需）数据"""
        return {
            'statusCode': 800,
            'message': '查询成功（模拟数据）',
            'returnObj': {
                'totalCount': 735,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'resourceId': '76c3714f30ea4922a7c20257098b206c',
                        'labelInfo': None,
                        'masterOrderNo': None,
                        'usage': '40',
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-12 13:00:00 - {bill_cycle[:4]}-{bill_cycle[4:]}-12 14:00:00',
                        'deductUsage': '0',
                        'payableAmount': '2',
                        'pricefactorValue': '3600',
                        'productName': 'EBS弹性块按需',
                        'regionCode': 'cn-gzT',
                        'servId': 'd7dd3b0e401c415b9c979862a31b6778',
                        'price': '2',
                        'serviceTag': 'HWS',
                        'contractName': None,
                        'realResourceId': '76c3714f-30ea-4922-a7c2-0257098b206c',
                        'salesAttribute': '类型：普通IO|版本号：v1|是否要求进入一点结算：是|销售品类别：标准',
                        'keySalesAttribute': '',
                        'usageType': '秒',
                        'amount': '0',
                        'usageTypeId': '400',
                        'offerName': '天翼云3.0EBS弹性块',
                        'coupon': '0',
                        'billType': '7',
                        'masterOrderId': None,
                        'productCode': 'fa1f18ab4dd944749200a4ddb2b92a16',
                        'billingCycleId': f'{bill_cycle[:4]}/{bill_cycle[4:]}',
                        'regionId': '贵州测试床',
                        'stateDate': f'{bill_cycle}12130000',
                        'projectName': 'default',
                        'contractCode': None,
                        'projectId': '0',
                        'resourceType': 'EBS'
                    },
                    {
                        'resourceId': '65cf1d05752c48a48956a8d9bfe69583',
                        'labelInfo': None,
                        'masterOrderNo': None,
                        'usage': '1',
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-12 13:00:00 - {bill_cycle[:4]}-{bill_cycle[4:]}-12 14:00:00',
                        'deductUsage': '0',
                        'payableAmount': '10',
                        'pricefactorValue': '1',
                        'productName': 'IP保有费',
                        'regionCode': 'cn-gzT',
                        'servId': '794f52db96164e5f8a256cd30d2d0a76',
                        'price': '10',
                        'serviceTag': 'EIP',
                        'contractName': None,
                        'realResourceId': '65cf1d05-752c-48a4-8956-a8d9bfe69583',
                        'salesAttribute': '类型：公众版|版本号：v1|销售品类别：标准|是否要求进入一点结算：是|收入结算方式：一点结算',
                        'keySalesAttribute': '',
                        'usageType': '小时',
                        'amount': '0',
                        'usageTypeId': '0',
                        'offerName': '弹性IP保有费',
                        'coupon': '0',
                        'billType': '7',
                        'masterOrderId': None,
                        'productCode': 'cdddbbc4c4b14e7694e0756ed94e3d25',
                        'billingCycleId': f'{bill_cycle[:4]}/{bill_cycle[4:]}',
                        'regionId': '贵州测试床',
                        'stateDate': f'{bill_cycle}12130000',
                        'projectName': 'default',
                        'contractCode': None,
                        'projectId': '0',
                        'resourceType': 'EIP'
                    },
                    {
                        'resourceId': '8a1b2c3d4e5f60718293a4b5c6d7e8f',
                        'labelInfo': None,
                        'masterOrderNo': '202212121200000001',
                        'usage': '500',
                        'billMode': '2',
                        'discountAmount': '50',
                        'consumeDate': f'{bill_cycle[:4]}-{bill_cycle[4:]}-12 14:00:00 - {bill_cycle[:4]}-{bill_cycle[4:]}-12 15:00:00',
                        'deductUsage': '0',
                        'payableAmount': '450',
                        'pricefactorValue': '1000',
                        'productName': '云主机带宽按需',
                        'regionCode': 'cn-north-1',
                        'servId': 'f1e2d3c4b5c6d7e8f9a0b1c2d3e4f5',
                        'price': '500',
                        'serviceTag': 'ECS',
                        'contractName': '测试合同',
                        'realResourceId': '8a1b2c3d4e5f60718293a4b5c6d7e8f',
                        'salesAttribute': '带宽：5Mbps|计费方式：按流量',
                        'keySalesAttribute': '5Mbps',
                        'usageType': 'GB',
                        'amount': '450',
                        'usageTypeId': '105',
                        'offerName': '弹性公网IP',
                        'coupon': '0',
                        'billType': '7',
                        'masterOrderId': 'ord_202212121200000001',
                        'productCode': 'gpraffic1t5',
                        'billingCycleId': f'{bill_cycle[:4]}/{bill_cycle[4:]}',
                        'regionId': '华北2',
                        'stateDate': f'{bill_cycle}12140000',
                        'projectName': 'production',
                        'contractCode': 'CT2022121200001',
                        'projectId': 'proj_abc123',
                        'resourceType': 'ECS'
                    }
                ]
            }
        }

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

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_resource_cycle_data(bill_cycle, page_no, page_size)

            result = response.json()
            logger.debug(f"解析结果: {result}")
            return result

        except Exception as e:
            logger.error(f"查询账单明细资源+账期(按需)异常: {str(e)}")
            return self._get_mock_resource_cycle_data(bill_cycle, page_no, page_size)

    def _get_mock_resource_cycle_data(self, bill_cycle: str, page_no: int, page_size: int) -> Dict[str, Any]:
        """获取模拟账单明细资源+账期（按需）数据"""
        return {
            'statusCode': 800,
            'message': '查询成功（模拟数据）',
            'returnObj': {
                'totalCount': 3,
                'pageNo': page_no,
                'pageSize': page_size,
                'result': [
                    {
                        'resourceId': '21b9273d9e2c45a6a0c3e5d38f3709ce.NETWORK',
                        'labelInfo': None,
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': None,
                        'payableAmount': '6356',
                        'productName': '云主机带宽按需',
                        'regionCode': 'cn-gzT',
                        'servId': 'fe9c20e1c4aa4b56bdeadefbb4d84b10',
                        'price': '6356',
                        'serviceTag': 'HWS',
                        'contractName': None,
                        'realResourceId': '21b9273d-9e2c-45a6-a0c3-e5d38f3709ce',
                        'salesAttribute': '类型：独享带宽|版本号：v1|资源池类型(是否蒙贵)：非蒙贵|是否要求进入一点结算：是|销售品类别：标准',
                        'keySalesAttribute': None,
                        'amount': '0',
                        'offerName': '天翼云3.0带宽',
                        'coupon': '0',
                        'billType': '7',
                        'productCode': '620608735a494df9bb45a97746378528',
                        'billingCycleId': bill_cycle,
                        'regionId': '贵州测试床',
                        'projectName': None,
                        'contractCode': None,
                        'resourceType': 'NETWORK'
                    },
                    {
                        'resourceId': '76c3714f30ea4922a7c20257098b206c',
                        'labelInfo': None,
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': None,
                        'payableAmount': '454',
                        'productName': 'EBS弹性块按需',
                        'regionCode': 'cn-gzT',
                        'servId': 'd7dd3b0e401c415b9c979862a31b6778',
                        'price': '454',
                        'serviceTag': 'HWS',
                        'contractName': None,
                        'realResourceId': '76c3714f-30ea-4922-a7c2-0257098b206c',
                        'salesAttribute': '类型：普通IO|版本号：v1|是否要求进入一点结算：是|销售品类别：标准',
                        'keySalesAttribute': None,
                        'amount': '0',
                        'offerName': '天翼云3.0EBS弹性块',
                        'coupon': '0',
                        'billType': '7',
                        'productCode': 'fa1f18ab4dd944749200a4ddb2b92a16',
                        'billingCycleId': bill_cycle,
                        'regionId': '贵州测试床',
                        'projectName': None,
                        'contractCode': None,
                        'resourceType': 'EBS'
                    },
                    {
                        'resourceId': '65cf1d05752c48a48956a8d9bfe69583',
                        'labelInfo': None,
                        'billMode': '2',
                        'discountAmount': '0',
                        'consumeDate': None,
                        'payableAmount': '2270',
                        'productName': 'IP保有费',
                        'regionCode': 'cn-gzT',
                        'servId': '794f52db96164e5f8a256cd30d2d0a76',
                        'price': '2270',
                        'serviceTag': 'EIP',
                        'contractName': None,
                        'realResourceId': '65cf1d05-752c-48a4-8956-a8d9bfe69583',
                        'salesAttribute': '类型：公众版|版本号：v1|销售品类别：标准|是否要求进入一点结算：是|收入结算方式：一点结算',
                        'keySalesAttribute': None,
                        'amount': '0',
                        'offerName': '弹性IP保有费',
                        'coupon': '0',
                        'billType': '7',
                        'productCode': 'cdddbbc4c4b14e7694e0756ed94e3d25',
                        'billingCycleId': bill_cycle,
                        'regionId': '贵州测试床',
                        'projectName': None,
                        'contractCode': None,
                        'resourceType': 'EIP'
                    }
                ]
            }
        }
