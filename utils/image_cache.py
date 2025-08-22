import os
import re
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional, Tuple
from loguru import logger
from config import config

class ImageCache:
    """图片缓存管理器"""
    
    def __init__(self):
        self.cache_dir = Path(config.IMAGE_CACHE_DIR)
        self.expire_hours = config.IMAGE_CACHE_EXPIRE_HOURS
        self.max_size_mb = config.IMAGE_CACHE_MAX_SIZE_MB
        self.allowed_formats = config.IMAGE_CACHE_ALLOWED_FORMATS
        self.max_file_size_mb = config.IMAGE_CACHE_MAX_FILE_SIZE_MB
        self.enabled = config.IMAGE_CACHE_ENABLED
        
        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 启动时清理过期文件
        self._cleanup_expired_files()
    
    def process_content(self, content: str) -> str:
        """处理内容中的图片链接，返回处理后的内容"""
        if not self.enabled or not content:
            return content
        
        # 匹配图片URL的正则表达式
        img_url_patterns = [
            r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s<>"]*)?',  # 直接图片链接
            r'<img[^>]+src=["\']([^"\'>]+)["\'][^>]*>',  # HTML img标签
            r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown图片语法
        ]
        
        processed_content = content
        
        for pattern in img_url_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'src=' in pattern:  # HTML img标签
                    img_url = match.group(1)
                    cached_url = self._cache_image(img_url)
                    if cached_url:
                        processed_content = processed_content.replace(match.group(1), cached_url)
                elif '![' in pattern:  # Markdown语法
                    img_url = match.group(2)
                    cached_url = self._cache_image(img_url)
                    if cached_url:
                        processed_content = processed_content.replace(match.group(2), cached_url)
                else:  # 直接链接
                    img_url = match.group(0)
                    cached_url = self._cache_image(img_url)
                    if cached_url:
                        processed_content = processed_content.replace(img_url, cached_url)
        
        return processed_content
    
    def extract_image_urls(self, content: str) -> List[str]:
        """从内容中提取所有图片URL"""
        if not content:
            return []
        
        urls = []
        img_url_patterns = [
            r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s<>"]*)?',
            r'<img[^>]+src=["\']([^"\'>]+)["\'][^>]*>',
            r'!\[([^\]]*)\]\(([^)]+)\)',
        ]
        
        for pattern in img_url_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'src=' in pattern:
                    urls.append(match.group(1))
                elif '![' in pattern:
                    urls.append(match.group(2))
                else:
                    urls.append(match.group(0))
        
        return list(set(urls))  # 去重
    
    def _cache_image(self, img_url: str) -> Optional[str]:
        """缓存单个图片，返回本地URL"""
        try:
            # 生成缓存文件名
            url_hash = hashlib.md5(img_url.encode()).hexdigest()
            parsed_url = urlparse(img_url)
            file_ext = Path(parsed_url.path).suffix.lower().lstrip('.')
            
            # 检查文件扩展名
            if file_ext not in self.allowed_formats:
                logger.warning(f"不支持的图片格式: {file_ext}, URL: {img_url}")
                return None
            
            cache_filename = f"{url_hash}.{file_ext}"
            cache_filepath = self.cache_dir / cache_filename
            
            # 检查文件是否已存在且未过期
            if cache_filepath.exists():
                file_age = datetime.now() - datetime.fromtimestamp(cache_filepath.stat().st_mtime)
                if file_age < timedelta(hours=self.expire_hours):
                    # 文件存在且未过期，返回本地URL
                    return f"/static/images/cache/{cache_filename}"
                else:
                    # 文件过期，删除
                    cache_filepath.unlink()
            
            # 下载图片
            response = requests.get(img_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 检查Content-Type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                logger.warning(f"URL返回的不是图片类型: {content_type}, URL: {img_url}")
                return None
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_file_size_mb * 1024 * 1024:
                logger.warning(f"图片文件过大: {content_length} bytes, URL: {img_url}")
                return None
            
            # 保存文件
            with open(cache_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 检查保存后的文件大小
            if cache_filepath.stat().st_size > self.max_file_size_mb * 1024 * 1024:
                cache_filepath.unlink()
                logger.warning(f"下载的图片文件过大，已删除: {img_url}")
                return None
            
            logger.info(f"图片缓存成功: {img_url} -> {cache_filename}")
            return f"/static/images/cache/{cache_filename}"
            
        except Exception as e:
            logger.error(f"缓存图片失败: {img_url}, 错误: {str(e)}")
            return None
    
    def _cleanup_expired_files(self):
        """清理过期的缓存文件"""
        try:
            current_time = datetime.now()
            expired_count = 0
            
            for cache_file in self.cache_dir.glob('*'):
                if cache_file.is_file():
                    file_age = current_time - datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if file_age > timedelta(hours=self.expire_hours):
                        cache_file.unlink()
                        expired_count += 1
            
            if expired_count > 0:
                logger.info(f"清理了 {expired_count} 个过期的缓存图片")
                
        except Exception as e:
            logger.error(f"清理过期缓存文件失败: {str(e)}")
    
    def _cleanup_by_size(self):
        """按大小清理缓存（当缓存超过最大限制时）"""
        try:
            # 计算当前缓存大小
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob('*') if f.is_file())
            max_size_bytes = self.max_size_mb * 1024 * 1024
            
            if total_size <= max_size_bytes:
                return
            
            # 按修改时间排序，删除最旧的文件
            cache_files = [(f, f.stat().st_mtime) for f in self.cache_dir.glob('*') if f.is_file()]
            cache_files.sort(key=lambda x: x[1])  # 按时间排序
            
            deleted_count = 0
            for cache_file, _ in cache_files:
                cache_file.unlink()
                deleted_count += 1
                
                # 重新计算大小
                total_size = sum(f.stat().st_size for f in self.cache_dir.glob('*') if f.is_file())
                if total_size <= max_size_bytes * 0.8:  # 清理到80%
                    break
            
            logger.info(f"按大小清理了 {deleted_count} 个缓存图片")
            
        except Exception as e:
            logger.error(f"按大小清理缓存失败: {str(e)}")
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        try:
            cache_files = list(self.cache_dir.glob('*'))
            file_count = len([f for f in cache_files if f.is_file()])
            total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
            
            return {
                'enabled': self.enabled,
                'file_count': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'max_size_mb': self.max_size_mb,
                'expire_hours': self.expire_hours,
                'cache_dir': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {}

# 创建全局实例
image_cache = ImageCache()