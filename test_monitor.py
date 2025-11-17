"""
测试云监控服务客户端
"""

import sys
sys.path.insert(0, 'src')

from client import CTYUNClient
from monitor.client import MonitorClient
from datetime import datetime, timedelta

def test_monitor_client():
    """测试云监控客户端"""
    print("=" * 60)
    print("测试云监控服务客户端")
    print("=" * 60)
    
    client = CTYUNClient(
        access_key='test_ak',
        secret_key='test_sk',
        region='cn-north-1'
    )
    
    monitor_client = MonitorClient(client)
    
    print("\n✓ 云监控客户端初始化成功")
    print(f"  服务: {monitor_client.service}")
    print(f"  端点: {monitor_client.base_endpoint}")
    print(f"  认证方式: EOP签名")
    
    test_region_id = "bb9fdb42056f11eda1610242ac110002"
    test_device_id = "test_device_123"
    
    print(f"\n{'=' * 60}")
    print("测试1: 查询云专线设备列表")
    print(f"{'=' * 60}")
    print(f"参数:")
    print(f"  region_id: {test_region_id}")
    
    result = monitor_client.list_dcaas_devices(test_region_id)
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        devices = result.get('data', [])
        print(f"  设备数量: {len(devices)}")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("测试2: 查询云专线流量（流入）")
    print(f"{'=' * 60}")
    
    start_time = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    print(f"参数:")
    print(f"  device_id: {test_device_id}")
    print(f"  region_id: {test_region_id}")
    print(f"  metric: network_incoming_bytes")
    print(f"  start_time: {start_time}")
    print(f"  end_time: {end_time}")
    print(f"  period: 300")
    
    result = monitor_client.query_dcaas_traffic(
        device_id=test_device_id,
        region_id=test_region_id,
        start_time=start_time,
        end_time=end_time,
        metric='network_incoming_bytes'
    )
    
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        data = result.get('data', {})
        print(f"  metric: {result.get('metric')}")
        print(f"  device_id: {result.get('device_id')}")
        print(f"  period: {result.get('period')}")
        datapoints = data.get('datapoints', [])
        print(f"  数据点数量: {len(datapoints)}")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("测试3: 查询云专线流量（流出）")
    print(f"{'=' * 60}")
    
    print(f"参数:")
    print(f"  device_id: {test_device_id}")
    print(f"  region_id: {test_region_id}")
    print(f"  metric: network_outgoing_bytes")
    
    result = monitor_client.query_dcaas_traffic(
        device_id=test_device_id,
        region_id=test_region_id,
        metric='network_outgoing_bytes'
    )
    
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        data = result.get('data', {})
        print(f"  metric: {result.get('metric')}")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("✓ 测试完成")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    test_monitor_client()
