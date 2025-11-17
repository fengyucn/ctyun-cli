"""
缓存工具模块
提供文件缓存功能，避免重复查询常用数据
"""

import json
import os
import time
from typing import Any, Dict, Optional
from pathlib import Path


class FileCache:
    """文件缓存管理器"""
    
    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，默认为 ~/.ctyun/cache
            default_ttl: 默认缓存时间（秒），默认1小时
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.ctyun/cache')
        
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        
        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 将key转换为安全的文件名
        safe_key = key.replace('/', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            if 'expire_time' in cache_data:
                if time.time() > cache_data['expire_time']:
                    # 缓存已过期，删除文件
                    cache_path.unlink(missing_ok=True)
                    return None
            
            return cache_data.get('data')
            
        except (json.JSONDecodeError, IOError):
            # 缓存文件损坏，删除
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            ttl: 缓存时间（秒），None表示使用默认值
            
        Returns:
            是否设置成功
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'data': data,
            'expire_time': time.time() + ttl,
            'created_time': time.time()
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cache_path.unlink(missing_ok=True)
            return True
        except IOError:
            return False
    
    def clear(self) -> int:
        """
        清空所有缓存
        
        Returns:
            删除的缓存文件数量
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink(missing_ok=True)
                count += 1
        except IOError:
            pass
        
        return count
    
    def clean_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            删除的过期缓存数量
        """
        count = 0
        current_time = time.time()
        
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if 'expire_time' in cache_data:
                        if current_time > cache_data['expire_time']:
                            cache_file.unlink(missing_ok=True)
                            count += 1
                except (json.JSONDecodeError, IOError):
                    # 损坏的缓存文件也删除
                    cache_file.unlink(missing_ok=True)
                    count += 1
        except IOError:
            pass
        
        return count


# 全局缓存实例
_global_cache: Optional[FileCache] = None


def get_cache() -> FileCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = FileCache()
    return _global_cache
