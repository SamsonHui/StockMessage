from typing import List, Dict, Any
import tweepy
from datetime import datetime
from loguru import logger
from .base_spider import BaseSpider

class TwitterSpider(BaseSpider):
    """推特爬虫"""
    
    def __init__(self):
        super().__init__('twitter')
        self.api = None
    
    def authenticate(self, auth_config: Dict[str, Any]) -> bool:
        """推特认证"""
        try:
            # 使用Twitter API v2
            bearer_token = auth_config.get('bearer_token')
            consumer_key = auth_config.get('consumer_key')
            consumer_secret = auth_config.get('consumer_secret')
            access_token = auth_config.get('access_token')
            access_token_secret = auth_config.get('access_token_secret')
            
            if bearer_token:
                self.api = tweepy.Client(bearer_token=bearer_token)
            elif all([consumer_key, consumer_secret, access_token, access_token_secret]):
                self.api = tweepy.Client(
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret
                )
            else:
                return False
            
            # 验证认证
            me = self.api.get_me()
            return me is not None
            
        except Exception as e:
            logger.error(f"推特认证失败: {str(e)}")
            return False
    
    def get_user_posts(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户帖子"""
        try:
            if not self.api:
                return []
            
            tweets = self.api.get_users_tweets(
                id=user_id,
                max_results=20,
                tweet_fields=['created_at', 'text', 'author_id']
            )
            
            posts = []
            if tweets.data:
                for tweet in tweets.data:
                    post = self.parse_post(tweet)
                    if post:
                        posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"获取推特用户帖子失败: {str(e)}")
            return []
    
    def parse_post(self, raw_post: Any) -> Dict[str, Any]:
        """解析帖子数据"""
        try:
            return {
                'platform': self.platform,
                'post_id': str(raw_post.id),
                'user_id': str(raw_post.author_id),
                'username': '',  # 需要额外获取用户信息
                'content': raw_post.text,
                'post_time': raw_post.created_at,
                'raw_data': raw_post.data
            }
        except Exception as e:
            logger.error(f"解析推特帖子失败: {str(e)}")
            return None
    
    def make_request(self, url: str, method: str = 'GET', **kwargs):
        """推特使用API，不需要直接HTTP请求"""
        pass