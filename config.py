import yaml
import os
from pathlib import Path
from urllib.parse import quote_plus

class Config:
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """从config.yaml文件加载配置"""
        config_file = Path(__file__).parent / 'config.yaml'
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件 {config_file} 不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 数据库配置
        db_config = config_data.get('database', {})
        self.MYSQL_HOST = db_config.get('host', 'localhost')
        self.MYSQL_PORT = db_config.get('port', 3306)
        self.MYSQL_USER = db_config.get('user', 'root')
        # 如果密码中包含@等特殊字符，需要进行URL编码
        password = db_config.get('password', '')
        self.MYSQL_PASSWORD = quote_plus(password)
        self.MYSQL_DATABASE = db_config.get('database', 'stock_message')
        
        # 爬虫配置
        spider_config = config_data.get('spider', {})
        self.SPIDER_INTERVAL = spider_config.get('interval', 60)
        self.USER_AGENT = spider_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.MAX_RETRY_TIMES = spider_config.get('max_retry_times', 3)
        self.REQUEST_TIMEOUT = spider_config.get('request_timeout', 30)
        
        # 图片缓存配置
        image_config = config_data.get('image_cache', {})
        self.IMAGE_CACHE_ENABLED = image_config.get('enabled', True)
        self.IMAGE_CACHE_DIR = image_config.get('cache_dir', 'static/images/cache')
        self.IMAGE_CACHE_EXPIRE_HOURS = image_config.get('expire_hours', 24)
        self.IMAGE_CACHE_MAX_SIZE_MB = image_config.get('max_size_mb', 500)
        self.IMAGE_CACHE_ALLOWED_FORMATS = image_config.get('allowed_formats', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
        self.IMAGE_CACHE_MAX_FILE_SIZE_MB = image_config.get('max_file_size_mb', 10)
        
        # 日志配置
        log_config = config_data.get('logging', {})
        self.LOG_LEVEL = log_config.get('level', 'INFO')
        self.LOG_FILE = log_config.get('file', 'logs/stock_message.log')

# 创建全局配置实例
config = Config()