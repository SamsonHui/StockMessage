import requests
import json
from typing import Dict, Any
from loguru import logger
from .base_notifier import BaseNotifier

class FeishuNotifier(BaseNotifier):
    """飞书推送"""
    
    def send_message(self, title: str, content: str, **kwargs) -> bool:
        """发送飞书消息"""
        try:
            webhook_url = self.config.get('webhook_url')
            secret = self.config.get('secret')
            
            if not webhook_url:
                logger.error("飞书webhook配置不完整")
                return False
            
            # 构造消息
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"{title}\n\n{content}"
                }
            }
            
            # 如果有secret，需要计算签名
            if secret:
                import time
                import hmac
                import hashlib
                import base64
                
                timestamp = str(int(time.time()))
                string_to_sign = f'{timestamp}\n{secret}'
                hmac_code = hmac.new(
                    string_to_sign.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
                sign = base64.b64encode(hmac_code).decode('utf-8')
                
                message['timestamp'] = timestamp
                message['sign'] = sign
            
            # 发送请求
            response = requests.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    logger.info(f"飞书消息发送成功: {title}")
                    return True
                else:
                    logger.error(f"飞书消息发送失败: {result.get('msg')}")
                    return False
            else:
                logger.error(f"飞书消息发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"飞书消息发送失败: {str(e)}")
            return False