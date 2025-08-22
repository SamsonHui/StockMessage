from typing import List, Dict, Any
import json
from datetime import datetime
from loguru import logger
from .base_spider import BaseSpider

class WeiboSpider(BaseSpider):
    """新浪微博爬虫"""
    
    def __init__(self):
        super().__init__('weibo')
        self.base_url = 'https://weibo.com'
        self.api_url = 'https://weibo.com/ajax/statuses/mymblog'
    
    def authenticate(self, auth_config: Dict[str, Any]) -> bool:
        """微博认证"""
        try:
            # 微博使用cookie认证
            cookies = auth_config.get('cookies', {})
            if cookies:
                self.session.cookies.update(cookies)
            
            # 设置必要的headers
            self.session.headers.update({
                'Referer': 'https://weibo.com/',
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            # 验证登录状态
            response = self.make_request('https://weibo.com/ajax/profile/info')
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"微博认证失败: {str(e)}")
            return False
    
    def get_user_posts(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户帖子"""
        try:
            params = {
                'uid': user_id,
                'page': 1,
                'feature': 0
            }
            
            response = self.make_request(self.api_url, params=params)
            data = response.json()
            
            posts = []
            if 'data' in data and 'list' in data['data']:
                for item in data['data']['list']:
                    post = self.parse_post(item)
                    if post:
                        posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"获取微博用户帖子失败: {str(e)}")
            return []
    
    def parse_post(self, raw_post: Any) -> Dict[str, Any]:
        """解析帖子数据"""
        try:
            return {
                'platform': self.platform,
                'post_id': str(raw_post.get('id', '')),
                'user_id': str(raw_post.get('user', {}).get('id', '')),
                'username': raw_post.get('user', {}).get('screen_name', ''),
                'content': raw_post.get('text_raw', ''),
                'post_time': datetime.strptime(raw_post.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y'),
                'raw_data': raw_post
            }
        except Exception as e:
            logger.error(f"解析微博帖子失败: {str(e)}")
            return None