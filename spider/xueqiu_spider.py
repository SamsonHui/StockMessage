from typing import List, Dict, Any
import json
import re
import requests
from datetime import datetime
from loguru import logger
from fake_useragent import UserAgent
from .base_spider import BaseSpider
import time
import random

class XueqiuSpider(BaseSpider):
    def __init__(self):
        super().__init__('xueqiu')
        self.ua = UserAgent()
        self.setup_session()
    
    def authenticate(self, auth_config: Dict[str, Any]) -> bool:
        """雪球认证方法 - 雪球通常不需要登录即可获取公开数据"""
        try:
            # 雪球大部分公开数据不需要登录
            # 这里可以添加cookie设置或其他认证逻辑
            logger.info("雪球爬虫认证成功（无需登录）")
            return True
        except Exception as e:
            logger.error(f"雪球爬虫认证失败: {str(e)}")
            return False
    
    def setup_session(self):
        """设置会话，模拟真实浏览器行为"""
        # 更真实的浏览器头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        })
    
    def get_initial_cookies(self, user_id):
        """获取初始cookies，模拟真实访问流程"""
        try:
            # 1. 先访问首页
            logger.info("访问雪球首页...")
            response = self.session.get('https://xueqiu.com/', timeout=10)
            time.sleep(random.uniform(1, 3))
            
            # 2. 访问用户页面
            logger.info(f"访问用户页面 {user_id}...")
            user_url = f'https://xueqiu.com/u/{user_id}'
            self.session.headers['Referer'] = 'https://xueqiu.com/'
            response = self.session.get(user_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("成功获取用户页面")
                # 更新Referer为用户页面
                self.session.headers['Referer'] = user_url
                return True
            else:
                logger.warning(f"用户页面访问失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"获取初始cookies失败: {e}")
            return False
    
    def get_user_posts(self, user_id, limit=20):
        """获取用户发帖（增强版，带重试机制）"""
        max_retries = 3
        
        for attempt in range(max_retries):
            logger.info(f"尝试第 {attempt + 1} 次获取用户 {user_id} 的数据...")
            
            try:
                # 重新获取cookies
                if not self.get_initial_cookies(user_id):
                    continue
                
                # 尝试不同的API端点
                endpoints = [
                    'https://xueqiu.com/v4/statuses/user_timeline.json',
                    'https://xueqiu.com/statuses/user_timeline.json',
                    'https://xueqiu.com/v5/statuses/user_timeline.json'
                ]
                
                for endpoint in endpoints:
                    result = self._try_api_endpoint(endpoint, user_id, limit)
                    if result:
                        logger.success(f"成功获取用户 {user_id} 的 {len(result)} 条动态")
                        return result
                    
                    # 每次尝试后等待
                    time.sleep(random.uniform(2, 5))
                
                logger.warning(f"第 {attempt + 1} 次API尝试失败")
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次尝试异常: {e}")
                time.sleep(random.uniform(5, 10))
        
        logger.info("所有API尝试均失败，切换到HTML解析模式")
        return self._fallback_to_html_parsing(user_id, limit)
    
    def _try_api_endpoint(self, endpoint, user_id, limit):
        """尝试特定API端点"""
        try:
            params = {
                'user_id': user_id,
                'page': 1,
                'count': limit,
                '_': int(time.time() * 1000)  # 添加时间戳防止缓存
            }
            
            logger.debug(f"尝试API: {endpoint}")
            response = self.session.get(endpoint, params=params, timeout=15)
            
            logger.debug(f"状态码: {response.status_code}")
            logger.debug(f"响应长度: {len(response.text)}")
            
            if response.status_code == 200:
                # 检查是否是WAF页面
                if self._is_waf_blocked(response.text):
                    logger.warning("检测到WAF拦截")
                    return None
                
                try:
                    data = response.json()
                    statuses = data.get('statuses', [])
                    if statuses:
                        logger.info(f"API成功获取 {len(statuses)} 条动态")
                        return statuses
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"API请求异常: {e}")
            return None
    
    def _is_waf_blocked(self, response_text):
        """检测是否被WAF拦截"""
        waf_indicators = [
            'aliyun_waf',
            'renderData',
            '_waf_',
            'anti-scraping',
            'verification required'
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in waf_indicators)
    
    def _fallback_to_html_parsing(self, user_id, limit):
        """回退到HTML解析"""
        try:
            logger.info("使用HTML解析模式...")
            url = f'https://xueqiu.com/u/{user_id}'
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return self._parse_html_content(response.text, limit)
            else:
                logger.error(f"HTML页面访问失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")
            return []
    
    def _parse_html_content(self, html_content, limit):
        """解析HTML内容"""
        # 尝试提取页面中的JSON数据
        patterns = [
            r'window\.SNB\s*=\s*(\{.*?\});',
            r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
            r'window\.__NUXT__\s*=\s*(\{.*?\});',
            r'"statuses"\s*:\s*(\[.*?\])',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, html_content, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group(1)
                    data = json.loads(json_str)
                    
                    # 尝试提取statuses
                    if isinstance(data, list):
                        logger.info(f"从HTML中提取到 {len(data)} 条数据")
                        return data[:limit]
                    elif isinstance(data, dict):
                        statuses = self._extract_statuses_from_dict(data)
                        if statuses:
                            logger.info(f"从HTML中提取到 {len(statuses)} 条数据")
                            return statuses[:limit]
                            
                except json.JSONDecodeError:
                    continue
        
        logger.warning("HTML解析未找到有效数据")
        return []
    
    def _extract_statuses_from_dict(self, data):
        """从字典中递归提取statuses"""
        if isinstance(data, dict):
            if 'statuses' in data and isinstance(data['statuses'], list):
                return data['statuses']
            
            # 递归搜索
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self._extract_statuses_from_dict(value)
                    if result:
                        return result
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    result = self._extract_statuses_from_dict(item)
                    if result:
                        return result
        
        return []
    
    def _get_posts_via_api(self, user_id, limit):
        """通过API获取发帖（保留原方法作为简单版本）"""
        # 先访问用户主页
        self.session.get(f'https://xueqiu.com/u/{user_id}')
        time.sleep(1)
        
        url = 'https://xueqiu.com/v4/statuses/user_timeline.json'
        params = {
            'user_id': user_id,
            'page': 1,
            'count': limit
        }
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                return data.get('statuses', [])
            except json.JSONDecodeError:
                return []
        return []
    
    def _get_posts_via_html(self, user_id, limit):
        """通过HTML解析获取发帖（保留原方法）"""
        url = f'https://xueqiu.com/u/{user_id}'
        response = self.session.get(url)
        
        if response.status_code == 200:
            # 尝试从HTML中提取JSON数据
            json_data = self._extract_json_from_html(response.text)
            if json_data:
                return json_data[:limit]
            
            # 回退到DOM解析
            return self._parse_html_posts(response.text, limit)
        
        return []
    
    def _extract_json_from_html(self, html_content):
        """从HTML中提取JSON数据（原方法的简化版）"""
        return self._parse_html_content(html_content, 100)
    
    def _parse_html_posts(self, html_content, limit):
        """解析HTML DOM（占位方法，可根据需要实现）"""
        # 这里可以添加BeautifulSoup解析逻辑
        logger.warning("DOM解析功能待实现")
        return []

    def parse_post(self, raw_post: Any) -> Dict[str, Any]:
        """解析帖子数据"""
        try:
            # 处理时间戳
            created_at = raw_post.get('created_at', 0)
            if isinstance(created_at, (int, float)):
                # 雪球的时间戳是毫秒级
                post_time = datetime.fromtimestamp(created_at / 1000)
            else:
                post_time = datetime.now()
            
            return {
                'platform': self.platform,
                'post_id': str(raw_post.get('id', '')),
                'user_id': str(raw_post.get('user', {}).get('id', '')),
                'username': raw_post.get('user', {}).get('screen_name', ''),
                'content': raw_post.get('text', ''),
                'post_time': post_time,
                'reply_count': raw_post.get('reply_count', 0),
                'retweet_count': raw_post.get('retweet_count', 0),
                'fav_count': raw_post.get('fav_count', 0),
                'raw_data': raw_post
            }
        except Exception as e:
            logger.error(f"解析雪球帖子失败: {str(e)}")
            return None