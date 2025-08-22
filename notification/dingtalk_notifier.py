import requests
import json
from typing import Dict, Any
from loguru import logger
from .base_notifier import BaseNotifier

class DingtalkNotifier(BaseNotifier):
    """钉钉推送"""
    
    def send_message(self, title: str, content: str, **kwargs) -> bool:
        """发送钉钉消息"""
        try:
            webhook_url = self.config.get('webhook_url')
            secret = self.config.get('secret')
            
            if not webhook_url:
                logger.error("钉钉webhook配置不完整")
                return False
            
            # 构造消息
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"{title}\n\n{content}"
                }
            }
            
            # 如果有secret，需要计算签名
            if secret:
                import time
                import hmac
                import hashlib
                import base64
                import urllib.parse
                
                timestamp = str(round(time.time() * 1000))
                secret_enc = secret.encode('utf-8')
                string_to_sign = f'{timestamp}\n{secret}'
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                
                webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
            
            # 发送请求
            response = requests.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info(f"钉钉消息发送成功: {title}")
                    return True
                else:
                    logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                logger.error(f"钉钉消息发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"钉钉消息发送失败: {str(e)}")
            return False