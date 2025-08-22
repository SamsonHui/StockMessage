import requests
import json
from typing import Dict, Any
from loguru import logger
from .base_notifier import BaseNotifier

class WechatWorkNotifier(BaseNotifier):
    """企业微信推送"""
    
    def send_message(self, title: str, content: str, **kwargs) -> bool:
        """发送企业微信消息"""
        try:
            webhook_url = self.config.get('webhook_url')
            
            if not webhook_url:
                logger.error("企业微信webhook配置不完整")
                return False
            
            # 构造消息
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"{title}\n\n{content}"
                }
            }
            
            # 发送请求
            response = requests.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info(f"企业微信消息发送成功: {title}")
                    return True
                else:
                    logger.error(f"企业微信消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                logger.error(f"企业微信消息发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"企业微信消息发送失败: {str(e)}")
            return False