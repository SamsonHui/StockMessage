import requests
import json
from typing import Dict, Any
from loguru import logger
from .base_notifier import BaseNotifier

class WechatMpNotifier(BaseNotifier):
    """微信公众号推送"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_token = None
    
    def get_access_token(self) -> str:
        """获取access_token"""
        try:
            appid = self.config.get('appid')
            secret = self.config.get('secret')
            
            if not all([appid, secret]):
                return None
            
            url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if 'access_token' in result:
                    self.access_token = result['access_token']
                    return self.access_token
            
            return None
            
        except Exception as e:
            logger.error(f"获取微信access_token失败: {str(e)}")
            return None
    
    def send_message(self, title: str, content: str, **kwargs) -> bool:
        """发送微信公众号消息"""
        try:
            if not self.access_token:
                self.access_token = self.get_access_token()
            
            if not self.access_token:
                logger.error("无法获取微信access_token")
                return False
            
            openids = self.config.get('openids', [])
            template_id = self.config.get('template_id')
            
            if not all([openids, template_id]):
                logger.error("微信公众号配置不完整")
                return False
            
            # 发送模板消息
            url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}"
            
            success_count = 0
            for openid in openids:
                message = {
                    "touser": openid,
                    "template_id": template_id,
                    "data": {
                        "title": {"value": title},
                        "content": {"value": content}
                    }
                }
                
                response = requests.post(url, json=message)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('errcode') == 0:
                        success_count += 1
            
            if success_count > 0:
                logger.info(f"微信公众号消息发送成功: {title}, 成功数量: {success_count}")
                return True
            else:
                logger.error(f"微信公众号消息发送失败: {title}")
                return False
                
        except Exception as e:
            logger.error(f"微信公众号消息发送失败: {str(e)}")
            return False