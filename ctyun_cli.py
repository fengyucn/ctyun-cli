#!/usr/bin/env python3
"""
天翼云CLI工具启动脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    try:
        from cli.main import cli
        cli()
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"运行出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()