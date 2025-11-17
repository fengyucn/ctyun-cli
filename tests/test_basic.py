#!/usr/bin/env python3
"""
基本功能测试
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import ConfigManager
from auth.signature import CTYUNAuth
from client import CTYUNClient, CTYUNAPIError
from ecs.client import ECSClient
from utils.helpers import OutputFormatter, ValidationUtils


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""

    def setUp(self):
        """测试前准备"""
        self.config_manager = ConfigManager()

    def test_get_credentials(self):
        """测试获取认证信息"""
        credentials = self.config_manager.get_credentials()
        self.assertIn('access_key', credentials)
        self.assertIn('secret_key', credentials)
        self.assertIn('region', credentials)
        self.assertIn('endpoint', credentials)

    def test_set_credentials(self):
        """测试设置认证信息"""
        self.config_manager.set_credentials(
            access_key='test_key',
            secret_key='test_secret',
            region='cn-north-1',
            endpoint='https://test.api.com'
        )

        credentials = self.config_manager.get_credentials()
        self.assertEqual(credentials['access_key'], 'test_key')
        self.assertEqual(credentials['secret_key'], 'test_secret')
        self.assertEqual(credentials['region'], 'cn-north-1')
        self.assertEqual(credentials['endpoint'], 'https://test.api.com')

    def test_validate_credentials(self):
        """测试验证认证信息"""
        # 测试空的认证信息
        self.assertFalse(self.config_manager.validate_credentials('nonexistent'))

        # 设置有效的认证信息
        self.config_manager.set_credentials(
            access_key='valid_key',
            secret_key='valid_secret'
        )
        self.assertTrue(self.config_manager.validate_credentials())


class TestCTYUNAuth(unittest.TestCase):
    """认证类测试"""

    def setUp(self):
        """测试前准备"""
        self.auth = CTYUNAuth('test_access_key', 'test_secret_key')

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.auth.access_key, 'test_access_key')
        self.assertEqual(self.auth.secret_key, 'test_secret_key')

    def test_get_bearer_token(self):
        """测试获取Bearer Token"""
        token = self.auth.get_bearer_token()
        self.assertEqual(token, 'Bearer test_access_key')

    def test_sign_request(self):
        """测试请求签名"""
        headers = self.auth.sign_request(
            method='GET',
            uri='/test',
            params={'param1': 'value1'},
            headers={'Content-Type': 'application/json'}
        )

        self.assertIn('X-CTYUN-Signature', headers)
        self.assertIn('X-CTYUN-SignedHeaders', headers)
        self.assertIn('X-CTYUN-Date', headers)
        self.assertIn('X-CTYUN-Nonce', headers)
        self.assertIn('X-CTYUN-Algorithm', headers)
        self.assertEqual(headers['X-CTYUN-Algorithm'], 'CTYUN-HMAC-SHA256')


class TestCTYUNClient(unittest.TestCase):
    """API客户端测试"""

    def setUp(self):
        """测试前准备"""
        self.client = CTYUNClient(
            access_key='test_key',
            secret_key='test_secret',
            region='cn-north-1',
            endpoint='https://test.api.com'
        )

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.client.access_key, 'test_key')
        self.assertEqual(self.client.secret_key, 'test_secret')
        self.assertEqual(self.client.region, 'cn-north-1')
        self.assertEqual(self.client.endpoint, 'https://test.api.com')

    def test_build_url(self):
        """测试URL构建"""
        url = self.client._build_url('ecs', 'instances')
        expected = 'https://test.api.com/v1/ecs/instances'
        self.assertEqual(url, expected)

    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """测试成功的API请求"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'result': 'success'}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        url = 'https://test.api.com/v1/test'
        response = self.client._make_request('GET', url, sign=False)

        self.assertEqual(response.json(), {'result': 'success'})

    @patch('requests.Session.request')
    def test_make_request_error(self, mock_request):
        """测试API请求错误"""
        # 模拟错误响应
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'code': 'InvalidRequest',
            'message': 'Invalid request'
        }
        mock_request.return_value = mock_response

        url = 'https://test.api.com/v1/test'

        with self.assertRaises(CTYUNAPIError) as context:
            self.client._make_request('GET', url, sign=False)

        self.assertEqual(context.exception.code, 'InvalidRequest')
        self.assertEqual(context.exception.message, 'Invalid request')
        self.assertEqual(context.exception.status_code, 400)


class TestECSClient(unittest.TestCase):
    """ECS客户端测试"""

    def setUp(self):
        """测试前准备"""
        self.mock_client = Mock()
        self.ecs_client = ECSClient(self.mock_client)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.ecs_client.client, self.mock_client)
        self.assertEqual(self.ecs_client.service, 'ecs')

    def test_list_instances(self):
        """测试列出实例"""
        # 模拟API响应
        mock_response = {
            'instances': [
                {'instanceId': 'i-123', 'instanceName': 'test-1'},
                {'instanceId': 'i-456', 'instanceName': 'test-2'}
            ]
        }
        self.mock_client.list_resources.return_value = mock_response

        result = self.ecs_client.list_instances(page=1, page_size=10)

        self.mock_client.list_resources.assert_called_once_with(
            'ecs', 'instances', params={'page': 1, 'pageSize': 10}
        )
        self.assertEqual(result, mock_response)

    def test_get_instance(self):
        """测试获取实例详情"""
        mock_response = {'instanceId': 'i-123', 'instanceName': 'test-1'}
        self.mock_client.get_resource.return_value = mock_response

        result = self.ecs_client.get_instance('i-123')

        self.mock_client.get_resource.assert_called_once_with('ecs', 'instances/i-123')
        self.assertEqual(result, mock_response)

    def test_create_instance(self):
        """测试创建实例"""
        mock_response = {'instanceId': 'i-123', 'instanceName': 'test-instance'}
        self.mock_client.create_resource.return_value = mock_response

        result = self.ecs_client.create_instance(
            name='test-instance',
            instance_type='s6.small',
            image_id='img-ubuntu20',
            count=1
        )

        expected_data = {
            'name': 'test-instance',
            'instanceType': 's6.small',
            'imageId': 'img-ubuntu20',
            'systemDisk': {
                'diskType': 'SSD',
                'diskSize': 40
            },
            'count': 1
        }

        self.mock_client.create_resource.assert_called_once_with('ecs', 'instances', expected_data)
        self.assertEqual(result, mock_response)


class TestUtils(unittest.TestCase):
    """工具函数测试"""

    def test_output_formatter(self):
        """测试输出格式化"""
        data = [
            {'id': 1, 'name': 'test1', 'status': 'running'},
            {'id': 2, 'name': 'test2', 'status': 'stopped'}
        ]

        # 测试表格格式
        table_output = OutputFormatter.format_table(data)
        self.assertIn('test1', table_output)
        self.assertIn('test2', table_output)

        # 测试JSON格式
        json_output = OutputFormatter.format_json(data)
        self.assertIn('test1', json_output)
        self.assertIn('test2', json_output)

    def test_validation_utils(self):
        """测试验证工具"""
        # 测试区域验证
        self.assertTrue(ValidationUtils.is_valid_region('cn-north-1'))
        self.assertFalse(ValidationUtils.is_valid_region('invalid-region'))

        # 测试实例规格验证
        self.assertTrue(ValidationUtils.is_valid_instance_type('s6.small'))
        self.assertTrue(ValidationUtils.is_valid_instance_type('c6.large.2'))
        self.assertFalse(ValidationUtils.is_valid_instance_type('invalid'))

        # 测试必填字段验证
        data = {'field1': 'value1', 'field2': '', 'field3': None}
        required_fields = ['field1', 'field2', 'field3', 'field4']
        missing = ValidationUtils.validate_required_fields(data, required_fields)
        self.assertEqual(set(missing), {'field2', 'field3', 'field4'})


def run_tests():
    """运行所有测试"""
    print("=== 天翼云CLI基本功能测试 ===\n")

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试用例
    test_classes = [
        TestConfigManager,
        TestCTYUNAuth,
        TestCTYUNClient,
        TestECSClient,
        TestUtils
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出结果
    print(f"\n测试完成:")
    print(f"  运行测试: {result.testsRun}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"  成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)