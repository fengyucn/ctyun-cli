"""
测试自定义监控服务客户端
"""

import sys
import os
sys.path.insert(0, 'src')

from client import CTYUNClient
from monitor.client import MonitorClient
from datetime import datetime, timedelta

def test_custom_monitor():
    """测试自定义监控客户端"""
    print("=" * 60)
    print("测试自定义监控服务客户端")
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
    print(f"  认证方式: EOP签名")
    
    test_region_id = "bb9fdb42056f11eda1610242ac110002"
    test_custom_item_id = "64ea1664-4347-558e-9bc6-651341c2fa15"
    
    print(f"\n{'=' * 60}")
    print("测试: 查询自定义监控趋势数据")
    print(f"{'=' * 60}")
    
    start_time = int((datetime.now() - timedelta(hours=1)).timestamp())
    end_time = int(datetime.now().timestamp())
    
    print(f"参数:")
    print(f"  region_id: {test_region_id}")
    print(f"  custom_item_id: {test_custom_item_id}")
    print(f"  start_time: {start_time} ({datetime.fromtimestamp(start_time)})")
    print(f"  end_time: {end_time} ({datetime.fromtimestamp(end_time)})")
    print(f"  period: 300")
    
    result = monitor_client.query_custom_item_trendmetricdata(
        region_id=test_region_id,
        custom_item_id=test_custom_item_id,
        start_time=start_time,
        end_time=end_time,
        period=300
    )
    
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        data = result.get('data', {})
        results = data.get('result', [])
        print(f"  custom_item_id: {result.get('custom_item_id')}")
        print(f"  数据组数量: {len(results)}")
        
        if results:
            for idx, item in enumerate(results[:2], 1):
                print(f"\n  数据组 #{idx}:")
                print(f"    regionID: {item.get('regionID')}")
                print(f"    customItemID: {item.get('customItemID')}")
                
                dimensions = item.get('dimensions', [])
                if dimensions:
                    print(f"    维度:")
                    for dim in dimensions[:3]:
                        print(f"      {dim.get('name')}: {dim.get('value')}")
                
                datapoints = item.get('data', [])
                print(f"    数据点数: {len(datapoints)}")
                if datapoints:
                    print(f"    首个数据点:")
                    dp = datapoints[0]
                    print(f"      采样时间: {dp.get('samplingTime')}")
                    print(f"      平均值: {dp.get('avg')}")
                    print(f"      最大值: {dp.get('max')}")
                    print(f"      最小值: {dp.get('min')}")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("测试: 带维度过滤的查询")
    print(f"{'=' * 60}")
    
    dimensions = [
        {
            'name': 'uuid',
            'value': ['00350e57-67af-f1db-1fa5-20193d873f5d']
        },
        {
            'name': 'job',
            'value': ['virtual_machine']
        }
    ]
    
    print(f"参数:")
    print(f"  region_id: {test_region_id}")
    print(f"  custom_item_id: {test_custom_item_id}")
    print(f"  dimensions: {dimensions}")
    
    result = monitor_client.query_custom_item_trendmetricdata(
        region_id=test_region_id,
        custom_item_id=test_custom_item_id,
        start_time=start_time,
        end_time=end_time,
        period=300,
        dimensions=dimensions
    )
    
    print(f"\n返回结果:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        data = result.get('data', {})
        results = data.get('result', [])
        print(f"  数据组数量: {len(results)}")
    else:
        print(f"  error: {result.get('error')}")
        print(f"  message: {result.get('message')}")
    
    print(f"\n{'=' * 60}")
    print("✓ 测试完成")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    test_custom_monitor()
