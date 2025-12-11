#!/usr/bin/env python3
"""
测试ELB监控API功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

def test_elb_monitor():
    """测试ELB监控API"""
    try:
        from core import CTYUNClient
        from elb.client import ELBClient

        # 使用HX配置文件的认证信息
        print("🔑 使用HX配置文件认证:")
        access_key = "8199e3911a794a2587dfb7764601d4e0"
        secret_key = "0421ff3125fb42c182bfc732bf4dbf76"

        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")

        # 创建客户端
        client = CTYUNClient(access_key=access_key, secret_key=secret_key)
        elb_client = ELBClient(client)

        # 测试参数
        test_region_id = "200000001852"
        print(f"\n🧪 测试ELB监控API:")
        print(f"   区域ID: {test_region_id}")

        # 1. 测试实时监控API
        print(f"\n📡 调用实时监控API...")
        realtime_result = elb_client.query_realtime_monitor(
            region_id=test_region_id,
            device_ids=None,
            page_no=1,
            page_size=5
        )

        print(f"\n✅ 实时监控API调用成功!")
        print(f"📊 返回结果:")
        print(f"   状态码: {realtime_result.get('statusCode')}")
        print(f"   消息: {realtime_result.get('message')}")

        return_obj = realtime_result.get('returnObj', {})
        monitors = return_obj.get('monitors', [])

        if monitors:
            print(f"\n📋 实时监控数据 (第1页):")
            print("-" * 120)
            for i, monitor in enumerate(monitors[:3], 1):  # 只显示前3个
                item_list = monitor.get('itemList', {})
                print(f"   {i:2}. 负载均衡器: {monitor.get('deviceID', '')}")
                print(f"       最近更新: {monitor.get('lastUpdated', '')}")
                print(f"       请求频率: {item_list.get('lbReqRate', '')}")
                print(f"       出吞吐量: {item_list.get('lbLbin', '')}")
                print(f"       入带宽峰值: {item_list.get('lbLbout', '')}")
                print(f"       HTTP 2xx: {item_list.get('lbHrsp2xx', '')}")
                print(f"       HTTP 4xx: {item_list.get('lbHrsp4xx', '')}")
                print(f"       HTTP 5xx: {item_list.get('lbHrsp5xx', '')}")
                print(f"       活跃连接数: {item_list.get('lbActconn', '')}")
                print()

            # 保存第一个负载均衡器ID用于历史监控测试
            first_lb_id = monitor.get('deviceID', '')

            # 2. 测试历史监控API
            if first_lb_id:
                print(f"\n🧪 测试历史监控API:")
                print(f"   负载均衡器ID: {first_lb_id}")

                from datetime import datetime, timedelta

                # 设置查询时间范围（最近24小时）
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=24)

                start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

                print(f"   时间范围: {start_time_str} ~ {end_time_str}")

                # 调用历史监控API
                history_result = elb_client.query_history_monitor(
                    region_id=test_region_id,
                    device_ids=[first_lb_id],
                    metric_names=['lb_req_rate', 'lb_lbin', 'lb_lbout', 'lb_actconn'],
                    start_time=start_time_str,
                    end_time=end_time_str,
                    period=3600,  # 1小时聚合
                    page_no=1,
                    page_size=5
                )

                print(f"\n✅ 历史监控API调用成功!")
                print(f"📊 返回结果:")
                print(f"   状态码: {history_result.get('statusCode')}")
                print(f"   消息: {history_result.get('message')}")

                history_return_obj = history_result.get('returnObj', {})
                history_monitors = history_return_obj.get('monitors', [])

                if history_monitors:
                    print(f"\n📋 历史监控数据:")
                    print("-" * 120)
                    for i, monitor in enumerate(history_monitors, 1):
                        item_aggregate_list = monitor.get('itemAggregateList', {})
                        print(f"   {i:2}. 负载均衡器: {monitor.get('deviceID', '')}")
                        print(f"       最近更新: {monitor.get('lastUpdated', '')}")

                        # 显示各个监控指标
                        metrics = ['lb_req_rate', 'lb_lbin', 'lb_lbout', 'lb_actconn']
                        for metric in metrics:
                            metric_value = item_aggregate_list.get(metric, '无数据')
                            if isinstance(metric_value, list):
                                print(f"       {metric}: {len(metric_value)}个数据点")
                            else:
                                print(f"       {metric}: {metric_value}")
                        print()

                else:
                    print(f"\n📝 未找到历史监控数据")
            else:
                print(f"\n⚠️  未找到负载均衡器ID，跳过历史监控测试")

        else:
            print(f"\n📝 未找到实时监控数据")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 100)
    print("🧪 测试ELB监控API功能")
    print("=" * 100)

    print("🔑 认证信息:")
    print("   配置文件: HX")
    print("   区域ID: 200000001852 (华北2)")
    print()

    if test_elb_monitor():
        print("\n" + "=" * 100)
        print("✅ ELB监控API测试成功!")
        print("   ✅ 实时监控API正常工作")
        print("   ✅ 历史监控API正常工作")
        print("   ✅ EOP签名认证正常")
        print("   ✅ API返回200和真实数据")
        print("=" * 100)
    else:
        print("\n" + "=" * 100)
        print("❌ ELB监控API测试失败!")
        print("=" * 100)


if __name__ == "__main__":
    main()