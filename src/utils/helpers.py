"""
工具函数模块
提供通用的辅助函数
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from tabulate import tabulate
import colorama
from colorama import Fore, Style

# 初始化colorama
colorama.init()


class OutputFormatter:
    """输出格式化器"""

    @staticmethod
    def format_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None,
                    tablefmt: str = 'grid') -> str:
        """
        格式化为表格输出

        Args:
            data: 数据列表
            headers: 表头列表
            tablefmt: 表格格式

        Returns:
            格式化后的表格字符串
        """
        if not data:
            return "没有数据"

        if headers is None:
            headers = list(data[0].keys()) if data else []

        # 转换数据为列表格式
        table_data = []
        for item in data:
            row = []
            for header in headers:
                value = item.get(header, '')
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False, indent=2)
                elif value is None:
                    value = ''
                else:
                    value = str(value)
                row.append(value)
            table_data.append(row)

        return tabulate(table_data, headers=headers, tablefmt=tablefmt)

    @staticmethod
    def format_json(data: Any, indent: int = 2) -> str:
        """
        格式化为JSON输出

        Args:
            data: 要格式化的数据
            indent: 缩进空格数

        Returns:
            格式化后的JSON字符串
        """
        return json.dumps(data, ensure_ascii=False, indent=indent)

    @staticmethod
    def color_print(text: str, color: str = '', bold: bool = False) -> None:
        """
        彩色打印

        Args:
            text: 要打印的文本
            color: 颜色名称
            bold: 是否加粗
        """
        color_code = ''
        if color.lower() == 'red':
            color_code = Fore.RED
        elif color.lower() == 'green':
            color_code = Fore.GREEN
        elif color.lower() == 'yellow':
            color_code = Fore.YELLOW
        elif color.lower() == 'blue':
            color_code = Fore.BLUE
        elif color.lower() == 'cyan':
            color_code = Fore.CYAN
        elif color.lower() == 'magenta':
            color_code = Fore.MAGENTA
        elif color.lower() == 'white':
            color_code = Fore.WHITE

        style_code = Style.BRIGHT if bold else ''

        print(f"{color_code}{style_code}{text}{Style.RESET_ALL}")


class Logger:
    """日志管理器"""

    def __init__(self, name: str = 'ctyun_cli', level: str = 'INFO',
                 log_file: Optional[str] = None):
        """
        初始化日志器

        Args:
            name: 日志器名称
            level: 日志级别
            log_file: 日志文件路径
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # 清除现有的处理器
        self.logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 添加文件处理器（如果指定了日志文件）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        """记录调试信息"""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """记录信息"""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """记录警告"""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """记录错误"""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """记录严重错误"""
        self.logger.critical(message)


class DateTimeUtils:
    """日期时间工具类"""

    @staticmethod
    def format_datetime(dt: Union[str, datetime], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        格式化日期时间

        Args:
            dt: 日期时间对象或字符串
            format_str: 格式化字符串

        Returns:
            格式化后的日期时间字符串
        """
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except ValueError:
                return dt

        return dt.strftime(format_str)

    @staticmethod
    def parse_datetime(date_str: str) -> datetime:
        """
        解析日期时间字符串

        Args:
            date_str: 日期时间字符串

        Returns:
            日期时间对象
        """
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"无法解析日期时间字符串: {date_str}")


class ValidationUtils:
    """验证工具类"""

    @staticmethod
    def is_valid_region(region: str) -> bool:
        """
        验证区域名称是否有效

        Args:
            region: 区域名称

        Returns:
            是否有效
        """
        # 天翼云常见区域列表
        valid_regions = [
            'cn-north-1', 'cn-east-1', 'cn-south-1', 'cn-southwest-1',
            'ap-singapore-1', 'ap-hongkong-1', 'eu-west-1'
        ]
        return region in valid_regions

    @staticmethod
    def is_valid_instance_type(instance_type: str) -> bool:
        """
        验证实例规格是否有效

        Args:
            instance_type: 实例规格

        Returns:
            是否有效
        """
        # 简单的实例规格验证
        patterns = [
            r'^[a-z]+\d+\.[a-z]+$',
            r'^[a-z]+\d+\.[a-z]+\d+$',
            r'^[a-z]+\d+\.[a-z]+\.[a-z]+$'
        ]

    @staticmethod
    def validate_bill_cycle(bill_cycle: str) -> bool:
        """
        验证账期格式

        Args:
            bill_cycle: 账期，格式：YYYYMM

        Returns:
            是否有效
        """
        import re
        if not re.match(r'^\d{6}$', bill_cycle):
            return False

        year = int(bill_cycle[:4])
        month = int(bill_cycle[4:])

        if year < 2000 or year > 2100:
            return False
        if month < 1 or month > 12:
            return False

        return True

    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        验证日期格式

        Args:
            date_str: 日期字符串，格式：YYYY-MM-DD

        Returns:
            是否有效
        """
        import re
        from datetime import datetime
        
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return False
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

        import re
        return any(re.match(pattern, instance_type) for pattern in patterns)

    @staticmethod
    def validate_required_fields(data: Dict[str, Any],
                                required_fields: List[str]) -> List[str]:
        """
        验证必填字段

        Args:
            data: 数据字典
            required_fields: 必填字段列表

        Returns:
            缺失的字段列表
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                missing_fields.append(field)
        return missing_fields


# 全局日志实例
logger = Logger()