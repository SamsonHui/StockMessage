from typing import List, Dict, Any
import json
from datetime import datetime
from loguru import logger
from .base_spider import BaseSpider

class EastmoneySpider(BaseSpider):
    """东财爬虫"""
    
    def __init__(self):
        super().__init__('eastmoney')
        self.base_url = 'https://guba.eastmoney.com'
        self.api_url = 'https://guba.eastmoney.com/list'
    
    def authenticate(self, auth_config: Dict[str, Any]) -> bool:
        """东财认证"""
        try:
            # 东财可能需要登录cookie
            cookies = auth_config.get('cookies', {})
            if cookies:
                self.session.cookies.update(cookies)
            
            return True
            
        except Exception as e:
            logger.error(f"东财认证失败: {str(e)}")
            return False
    
    def get_user_posts(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户帖子"""
        try:
            url = f"{self.base_url}/list,{user_id}.html"
            response = self.make_request(url)
            
            # 这里需要解析HTML页面
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            posts = []
            # 根据东财页面结构解析帖子
            post_items = soup.find_all('div', class_='articleh')
            
            for item in post_items:
                post = self.parse_post(item)
                if post:
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"获取东财用户帖子失败: {str(e)}")
            return []
    
    def parse_post(self, raw_post: Any) -> Dict[str, Any]:
        """解析帖子数据"""
        try:
            # 解析HTML元素
            title_elem = raw_post.find('span', class_='l3')
            time_elem = raw_post.find('span', class_='l5')
            
            if not title_elem:
                return None
            
            return {
                'platform': self.platform,
                'post_id': title_elem.find('a').get('href', '').split('/')[-1].replace('.html', ''),
                'user_id': '',  # 需要从页面中提取
                'username': '',
                'content': title_elem.get_text().strip(),
                'post_time': datetime.now(),  # 需要解析时间格式
                'raw_data': str(raw_post)
            }
        except Exception as e:
            logger.error(f"解析东财帖子失败: {str(e)}")
            return None