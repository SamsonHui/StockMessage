from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from loguru import logger
from config import config

class BaseSpider(ABC):
    """爬虫基类"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
    
    @abstractmethod
    def authenticate(self, auth_config: Dict[str, Any]) -> bool:
        """认证登录"""
        pass
    
    @abstractmethod
    def get_user_posts(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户帖子"""
        pass
    
    @abstractmethod
    def parse_post(self, raw_post: Any) -> Dict[str, Any]:
        """解析帖子数据"""
        pass
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """发起HTTP请求"""
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=config.REQUEST_TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"请求失败: {url}, 错误: {str(e)}")
            raise