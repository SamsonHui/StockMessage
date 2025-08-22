from abc import ABC, abstractmethod
from typing import Dict, Any
from loguru import logger

class BaseNotifier(ABC):
    """推送基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def send_message(self, title: str, content: str, **kwargs) -> bool:
        """发送消息"""
        pass
    
    def format_post_message(self, post_data: Dict[str, Any]) -> tuple:
        """格式化帖子消息"""
        platform = post_data.get('platform', '')
        username = post_data.get('username', '')
        content = post_data.get('content', '')
        post_time = post_data.get('post_time', '')
        
        title = f"【{platform}】{username} 发布新动态"
        message = f"""平台: {platform}
用户: {username}
时间: {post_time}
内容: {content}"""
        
        return title, message