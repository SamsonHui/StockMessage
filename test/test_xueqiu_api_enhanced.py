import requests
import json
import time
import random
from fake_useragent import UserAgent
import urllib.parse

class EnhancedXueqiuClient:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.cookies = {}
        self.setup_session()
    
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
            print("访问雪球首页...")
            response = self.session.get('https://xueqiu.com/', timeout=10)
            time.sleep(random.uniform(1, 3))
            
            # 2. 访问用户页面
            print(f"访问用户页面 {user_id}...")
            user_url = f'https://xueqiu.com/u/{user_id}'
            self.session.headers['Referer'] = 'https://xueqiu.com/'
            response = self.session.get(user_url, timeout=10)
            
            if response.status_code == 200:
                print("成功获取用户页面")
                # 更新Referer为用户页面
                self.session.headers['Referer'] = user_url
                return True
            else:
                print(f"用户页面访问失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"获取初始cookies失败: {e}")
            return False
    
    def get_user_timeline_with_retry(self, user_id, max_retries=3):
        """带重试机制的获取用户动态"""
        for attempt in range(max_retries):
            print(f"\n尝试第 {attempt + 1} 次获取数据...")
            
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
                result = self._try_api_endpoint(endpoint, user_id)
                if result:
                    return result
                
                # 每次尝试后等待
                time.sleep(random.uniform(2, 5))
            
            print(f"第 {attempt + 1} 次尝试失败")
            time.sleep(random.uniform(5, 10))
        
        print("所有尝试均失败，切换到HTML解析模式")
        return self.fallback_to_html_parsing(user_id)
    
    def _try_api_endpoint(self, endpoint, user_id):
        """尝试特定API端点"""
        try:
            params = {
                'user_id': user_id,
                'page': 1,
                'count': 20,
                '_': int(time.time() * 1000)  # 添加时间戳防止缓存
            }
            
            print(f"尝试API: {endpoint}")
            response = self.session.get(endpoint, params=params, timeout=15)
            
            print(f"状态码: {response.status_code}")
            print(f"响应长度: {len(response.text)}")
            print(f"响应开头: {response.text[:200]}")
            
            if response.status_code == 200:
                # 检查是否是WAF页面
                if 'aliyun_waf' in response.text or 'renderData' in response.text:
                    print("检测到WAF拦截")
                    return None
                
                try:
                    data = response.json()
                    statuses = data.get('statuses', [])
                    if statuses:
                        print(f"成功获取 {len(statuses)} 条动态")
                        return statuses
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
            
            return None
            
        except Exception as e:
            print(f"API请求异常: {e}")
            return None
    
    def fallback_to_html_parsing(self, user_id):
        """回退到HTML解析"""
        try:
            print("\n使用HTML解析模式...")
            url = f'https://xueqiu.com/u/{user_id}'
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return self.parse_html_content(response.text)
            else:
                print(f"HTML页面访问失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"HTML解析失败: {e}")
            return []
    
    def parse_html_content(self, html_content):
        """解析HTML内容"""
        import re
        
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
                        print(f"从HTML中提取到 {len(data)} 条数据")
                        return data
                    elif isinstance(data, dict):
                        statuses = self._extract_statuses_from_dict(data)
                        if statuses:
                            print(f"从HTML中提取到 {len(statuses)} 条数据")
                            return statuses
                            
                except json.JSONDecodeError:
                    continue
        
        print("HTML解析未找到有效数据")
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
    
    def parse_status(self, status):
        """解析单条动态"""
        return {
            'id': status.get('id'),
            'text': status.get('text', ''),
            'created_at': status.get('created_at'),
            'user': {
                'name': status.get('user', {}).get('screen_name', ''),
                'id': status.get('user', {}).get('id')
            },
            'reply_count': status.get('reply_count', 0),
            'retweet_count': status.get('retweet_count', 0),
            'fav_count': status.get('fav_count', 0)
        }

# 测试代码
if __name__ == '__main__':
    client = EnhancedXueqiuClient()
    user_id = '1247347556'  # 示例用户ID
    
    print(f"获取用户 {user_id} 的动态...")
    statuses = client.get_user_timeline_with_retry(user_id)
    
    if statuses:
        print(f"\n=== 成功获取 {len(statuses)} 条动态 ===")
        for i, status in enumerate(statuses[:3], 1):
            parsed = client.parse_status(status)
            print(f"\n{i}. {parsed['text'][:100]}...")
            print(f"   时间: {parsed['created_at']}")
            print(f"   点赞: {parsed['fav_count']}, 转发: {parsed['retweet_count']}, 评论: {parsed['reply_count']}")
    else:
        print("\n未获取到任何动态数据")
        print("\n建议尝试以下方案:")
        print("1. 使用代理服务器")
        print("2. 降低请求频率")
        print("3. 使用不同的User-Agent")
        print("4. 考虑使用Selenium作为最后手段")