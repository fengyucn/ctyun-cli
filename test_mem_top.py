"""
测试云主机内存使用率Top-N查询
"""

import sys
import os
sys.path.insert(0, 'src')

from client import CTYUNClient
from monitor.client import MonitorClient

def test_mem_top():
    """测试内存Top-N查询"""
    print("=" * 60)
    print("测试云主机内存使用率Top-N查询")
    print("=" * 60)
    
    client = CTYUNClient(
        access_key=os.getenv('CTYUN_ACCESS_KEY'),
        secret_key=os.getenv('CTYUN_SECRET_KEY'),
        region='cn-north-1'
    )
    
    monitor_client = MonitorClient(client)
    
    print("\n✓ 监控客户端初始化成功")
    print(f"  服务: {monitor_client.service}")
    print(f"  端点: {monitor_client.base_endpoint}")
    
    test_region_id = "bb9fdb42056f11eda1610242ac110002"
    
    print(f"\n{'=' * 60}")
    print("测试: 查询内存使用率Top 3")
    print(f"{'=' * 60}")
    
    print(f"参数:")
    print(f"  region_id: {test_region_id} (华东1)")
    print(f"  number: 3")
    
    result = monitor_client.query_mem_top(
        region_id=test_region_id,
        number=3
    )
    
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    
    if result.get('success'):
        data = result.get('data', {})
        mem_list = data.get('memList', [])
        print(f"  云主机数量: {len(mem_list)}")
        
        if mem_list:
            print(f"\n内存使用率Top 3:")
            for idx, item in enumerate(mem_list, 1):
                device_id = item.get('deviceID', '')
                device_name = item.get('name', '')
                mem_value = item.get('value', '0')
                mem_percent = float(mem_value)
                
                print(f"\n  #{idx} {device_name}")
                print(f"    设备ID: {device_id}")
                print(f"    内存使用率: {mem_percent:.2f}%")
        else:
            print("  未找到云主机数据")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("测试: 查询内存使用率Top 10")
    print(f"{'=' * 60}")
    
    print(f"参数:")
    print(f"  region_id: {test_region_id}")
    print(f"  number: 10")
    
    result = monitor_client.query_mem_top(
        region_id=test_region_id,
        number=10
    )
    
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    
    if result.get('success'):
        data = result.get('data', {})
        mem_list = data.get('memList', [])
        print(f"  云主机数量: {len(mem_list)}")
        
        if mem_list:
            mem_values = [float(item.get('value', 0)) for item in mem_list]
            print(f"\n统计信息:")
            print(f"  最高内存: {max(mem_values):.2f}%")
            print(f"  最低内存: {min(mem_values):.2f}%")
            print(f"  平均内存: {sum(mem_values)/len(mem_values):.2f}%")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("✓ 测试完成")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    test_mem_top()
