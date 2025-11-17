#!/usr/bin/env python3
"""
天翼云CLI自动化示例
展示如何使用CLI进行自动化运维操作
"""

import sys
import os
import time
import json
from typing import List, Dict

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from client import CTYUNClient
from ecs.client import ECSClient
from utils.helpers import OutputFormatter, logger


class ECSSupervisor:
    """云服务器自动化管理类"""

    def __init__(self, profile: str = 'default'):
        """初始化管理器"""
        self.client = CTYUNClient(profile=profile)
        self.ecs_client = ECSClient(self.client)
        logger.info("ECS管理器初始化完成")

    def get_running_instances(self) -> List[Dict]:
        """获取所有运行中的实例"""
        try:
            result = self.ecs_client.list_instances(status='running', page_size=100)
            return result.get('instances', [])
        except Exception as e:
            logger.error(f"获取运行实例失败: {e}")
            return []

    def get_stopped_instances(self) -> List[Dict]:
        """获取所有已停止的实例"""
        try:
            result = self.ecs_client.list_instances(status='stopped', page_size=100)
            return result.get('instances', [])
        except Exception as e:
            logger.error(f"获取停止实例失败: {e}")
            return []

    def start_stopped_instances(self, dry_run: bool = True) -> bool:
        """启动所有已停止的实例"""
        stopped_instances = self.get_stopped_instances()

        if not stopped_instances:
            print("没有找到已停止的实例")
            return True

        print(f"找到 {len(stopped_instances)} 个已停止的实例:")
        for instance in stopped_instances:
            instance_id = instance.get('instanceId', 'Unknown')
            name = instance.get('instanceName', 'Unknown')
            print(f"  - {name} ({instance_id})")

        if dry_run:
            print("\n[DRY RUN] 不会实际启动实例")
            return True

        try:
            instance_ids = [inst.get('instanceId') for inst in stopped_instances]
            result = self.ecs_client.batch_start_instances(instance_ids)
            print(f"✓ 批量启动命令已发送: {len(instance_ids)} 个实例")
            return True
        except Exception as e:
            print(f"✗ 批量启动失败: {e}")
            return False

    def stop_unused_instances(self, threshold_hours: int = 24, dry_run: bool = True) -> bool:
        """停止长时间未使用的实例"""
        running_instances = self.get_running_instances()

        if not running_instances:
            print("没有找到运行中的实例")
            return True

        # 这里应该检查实例的使用情况，例如CPU利用率
        # 由于没有真实的监控数据，我们模拟这个逻辑
        unused_instances = []

        for instance in running_instances:
            instance_id = instance.get('instanceId', 'Unknown')
            name = instance.get('instanceName', 'Unknown')

            # 模拟判断条件 (实际应该查询监控数据)
            # 这里简单演示，假设某些实例是"未使用"的
            if 'test' in name.lower() or 'dev' in name.lower():
                unused_instances.append(instance)

        if not unused_instances:
            print("没有找到长时间未使用的实例")
            return True

        print(f"找到 {len(unused_instances)} 个可能未使用的实例:")
        for instance in unused_instances:
            instance_id = instance.get('instanceId', 'Unknown')
            name = instance.get('instanceName', 'Unknown')
            print(f"  - {name} ({instance_id})")

        if dry_run:
            print(f"\n[DRY RUN] 不会实际停止实例")
            return True

        try:
            instance_ids = [inst.get('instanceId') for inst in unused_instances]
            result = self.ecs_client.batch_stop_instances(instance_ids)
            print(f"✓ 批量停止命令已发送: {len(instance_ids)} 个实例")
            return True
        except Exception as e:
            print(f"✗ 批量停止失败: {e}")
            return False

    def backup_instances(self, instance_ids: List[str], backup_name_prefix: str = "backup") -> bool:
        """备份指定实例"""
        print(f"开始备份 {len(instance_ids)} 个实例...")

        success_count = 0
        failed_instances = []

        for instance_id in instance_ids:
            try:
                # 获取实例信息
                instance_info = self.ecs_client.get_instance(instance_id)
                instance_name = instance_info.get('instanceName', 'unknown')

                # 创建镜像
                backup_name = f"{backup_name_prefix}-{instance_name}-{int(time.time())}"
                result = self.ecs_client.create_instance_image(
                    instance_id=instance_id,
                    image_name=backup_name,
                    description=f"自动备份镜像 - {instance_name}"
                )

                print(f"✓ 实例 {instance_id} 备份成功: {backup_name}")
                success_count += 1

            except Exception as e:
                print(f"✗ 实例 {instance_id} 备份失败: {e}")
                failed_instances.append(instance_id)

        print(f"\n备份完成: 成功 {success_count} 个，失败 {len(failed_instances)} 个")
        if failed_instances:
            print(f"失败的实例: {', '.join(failed_instances)}")

        return len(failed_instances) == 0

    def generate_instance_report(self) -> Dict:
        """生成实例报告"""
        print("生成实例报告...")

        try:
            # 获取所有实例
            all_instances = self.ecs_client.list_instances(page_size=100).get('instances', [])

            # 统计信息
            total_count = len(all_instances)
            running_count = len([inst for inst in all_instances if inst.get('status') == 'running'])
            stopped_count = len([inst for inst in all_instances if inst.get('status') == 'stopped'])
            other_count = total_count - running_count - stopped_count

            # 按类型统计
            type_stats = {}
            for instance in all_instances:
                instance_type = instance.get('instanceType', 'Unknown')
                type_stats[instance_type] = type_stats.get(instance_type, 0) + 1

            report = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total': total_count,
                    'running': running_count,
                    'stopped': stopped_count,
                    'other': other_count
                },
                'by_type': type_stats,
                'instances': all_instances
            }

            return report

        except Exception as e:
            print(f"生成报告失败: {e}")
            return {}

    def cleanup_old_backups(self, keep_days: int = 7, dry_run: bool = True) -> bool:
        """清理旧备份镜像"""
        print(f"清理 {keep_days} 天前的备份镜像...")

        try:
            # 获取所有私有镜像
            images = self.ecs_client.list_images(image_type='private').get('images', [])

            # 筛选备份镜像 (名称包含"backup")
            backup_images = []
            cutoff_time = time.time() - (keep_days * 24 * 3600)

            for image in images:
                image_name = image.get('imageName', '')
                if 'backup' in image_name.lower():
                    creation_time = image.get('createTime', '')
                    # 这里需要解析时间，简化处理
                    backup_images.append(image)

            if not backup_images:
                print("没有找到需要清理的备份镜像")
                return True

            print(f"找到 {len(backup_images)} 个备份镜像:")
            for image in backup_images:
                image_name = image.get('imageName', 'Unknown')
                image_id = image.get('imageId', 'Unknown')
                print(f"  - {image_name} ({image_id})")

            if dry_run:
                print(f"\n[DRY RUN] 不会实际删除镜像")
                return True

            # 实际删除镜像的逻辑 (需要实现delete_image方法)
            print("注意: 镜像删除功能需要实现delete_image方法")

        except Exception as e:
            print(f"清理备份失败: {e}")
            return False


def main():
    """主函数 - 自动化示例"""
    print("=== 天翼云CLI自动化示例 ===\n")

    # 创建管理器
    supervisor = ECSSupervisor()

    # 1. 生成实例报告
    print("1. 生成实例状态报告")
    report = supervisor.generate_instance_report()
    if report:
        summary = report['summary']
        print(f"  总实例数: {summary['total']}")
        print(f"  运行中: {summary['running']}")
        print(f"  已停止: {summary['stopped']}")
        print(f"  其他状态: {summary['other']}")

        # 保存报告到文件
        with open('instance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("  报告已保存到: instance_report.json")

    # 2. 停止未使用的实例 (模拟运行)
    print("\n2. 检查未使用的实例")
    supervisor.stop_unused_instances(threshold_hours=24, dry_run=True)

    # 3. 启动已停止的实例 (模拟运行)
    print("\n3. 启动已停止的实例")
    supervisor.start_stopped_instances(dry_run=True)

    # 4. 备份重要实例 (示例)
    print("\n4. 备份示例")
    running_instances = supervisor.get_running_instances()
    if running_instances:
        # 选择前2个实例进行备份示例
        backup_instances = [inst.get('instanceId') for inst in running_instances[:2]]
        print(f"选择实例进行备份示例: {backup_instances}")
        # supervisor.backup_instances(backup_instances, "automated-backup")
        print("(实际备份已注释，避免创建不必要的镜像)")

    # 5. 清理旧备份 (模拟运行)
    print("\n5. 清理旧备份")
    supervisor.cleanup_old_backups(keep_days=7, dry_run=True)

    print("\n=== 自动化示例完成 ===")
    print("这些示例展示了如何使用天翼云CLI进行:")
    print("  - 实例状态监控")
    print("  - 自动化运维操作")
    print("  - 批量管理")
    print("  - 备份和清理")
    print("\n在实际使用中，请根据需要调整参数和逻辑。")


if __name__ == '__main__':
    main()