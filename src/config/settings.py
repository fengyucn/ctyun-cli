"""
配置管理模块
处理天翼云CLI的配置信息
"""

import os
import configparser
from pathlib import Path
from typing import Dict, Optional, Any


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，默认为 ~/.ctyun/config
        """
        if config_file is None:
            home_dir = Path.home()
            config_dir = home_dir / ".ctyun"
            config_dir.mkdir(exist_ok=True)
            config_file = str(config_dir / "config")

        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # 创建默认配置
            self._create_default_config()

    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        self.config['default'] = {
            'access_key': '',
            'secret_key': '',
            'region': 'cn-north-1',
            'endpoint': 'https://api.ctyun.cn',
            'timeout': '30',
            'retry': '3',
            'output_format': 'table'
        }
        self.config['logging'] = {
            'level': 'INFO',
            'file': '',
            'max_size': '10MB',
            'backup_count': '5'
        }
        self.save_config()

    def get(self, key: str, section: str = 'default', fallback: Any = None) -> str:
        """
        获取配置值

        Args:
            key: 配置键
            section: 配置节，默认为default
            fallback: 默认值

        Returns:
            配置值
        """
        return self.config.get(section, key, fallback=fallback)

    def set(self, key: str, value: str, section: str = 'default') -> None:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
            section: 配置节
        """
        if section not in self.config:
            self.config.add_section(section)
        self.config.set(section, key, value)

    def get_credentials(self, profile: str = 'default') -> Dict[str, str]:
        """
        获取认证信息

        Args:
            profile: 配置文件名称

        Returns:
            包含认证信息的字典
        """
        return {
            'access_key': self.get('access_key', profile),
            'secret_key': self.get('secret_key', profile),
            'region': self.get('region', profile),
            'endpoint': self.get('endpoint', profile)
        }

    def set_credentials(self, access_key: str, secret_key: str,
                       region: str = 'cn-north-1', endpoint: str = 'https://api.ctyun.cn',
                       profile: str = 'default') -> None:
        """
        设置认证信息

        Args:
            access_key: 访问密钥
            secret_key: 密钥
            region: 区域
            endpoint: API端点
            profile: 配置文件名称
        """
        self.set('access_key', access_key, profile)
        self.set('secret_key', secret_key, profile)
        self.set('region', region, profile)
        self.set('endpoint', endpoint, profile)
        self.save_config()

    def get_timeout(self) -> int:
        """获取请求超时时间"""
        return int(self.get('timeout', fallback='30'))

    def get_retry_count(self) -> int:
        """获取重试次数"""
        return int(self.get('retry', fallback='3'))

    def get_output_format(self) -> str:
        """获取输出格式"""
        return self.get('output_format', fallback='table')

    def save_config(self) -> None:
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def list_profiles(self) -> list:
        """列出所有配置文件"""
        return self.config.sections()

    def validate_credentials(self, profile: str = 'default') -> bool:
        """
        验证认证信息是否完整

        Args:
            profile: 配置文件名称

        Returns:
            是否有效
        """
        credentials = self.get_credentials(profile)
        return bool(credentials['access_key'] and credentials['secret_key'])


# 全局配置实例
config = ConfigManager()