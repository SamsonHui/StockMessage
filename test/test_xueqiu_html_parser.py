import requests
import re
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class XueqiuHTMLParser:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_user_page_data(self, user_id):
        """获取用户页面并解析数据"""
        url = f'https://xueqiu.com/u/{user_id}'
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return self.parse_page_data(response.text)
            else:
                print(f"页面访问失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"请求异常: {e}")
            return []
    
    def parse_page_data(self, html_content):
        """从HTML中解析数据"""
        # 方法1: 解析页面中的JSON数据
        json_data = self.extract_json_from_html(html_content)
        if json_data:
            return json_data
        
        # 方法2: 直接解析HTML DOM
        return self.parse_html_dom(html_content)
    
    def extract_json_from_html(self, html_content):
        """从HTML中提取JSON数据"""
        patterns = [
            r'window\.SNB\s*=\s*(\{.*?\});',
            r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
            r'window\.__NUXT__\s*=\s*(\{.*?\});'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    # 尝试从不同路径提取动态数据
                    statuses = self.extract_statuses_from_json(data)
                    if statuses:
                        return statuses
                except json.JSONDecodeError:
                    continue
        
        return []
    
    def extract_statuses_from_json(self, data):
        """从JSON数据中提取动态"""
        # 常见的数据路径
        paths = [
            ['statuses'],
            ['timeline', 'statuses'],
            ['user', 'statuses'],
            ['data', 'statuses']
        ]
        
        for path in paths:
            current = data
            try:
                for key in path:
                    current = current[key]
                if isinstance(current, list) and current:
                    return current
            except (KeyError, TypeError):
                continue
        
        return []
    
    def parse_html_dom(self, html_content):
        """直接解析HTML DOM"""
        soup = BeautifulSoup(html_content, 'html.parser')
        statuses = []
        
        # 查找动态容器
        timeline_items = soup.find_all(['div', 'article'], class_=re.compile(r'timeline|status|post'))
        
        for item in timeline_items:
            status_data = self.parse_status_item(item)
            if status_data:
                statuses.append(status_data)
        
        return statuses
    
    def parse_status_item(self, item):
        """解析单个动态项"""
        try:
            # 提取文本内容
            text_elem = item.find(['div', 'p'], class_=re.compile(r'text|content|desc'))
            text = text_elem.get_text(strip=True) if text_elem else ''
            
            # 提取时间
            time_elem = item.find(['time', 'span'], class_=re.compile(r'time|date'))
            created_at = time_elem.get('datetime') or time_elem.get_text(strip=True) if time_elem else ''
            
            # 提取互动数据
            like_elem = item.find(['span', 'div'], class_=re.compile(r'like|fav'))
            retweet_elem = item.find(['span', 'div'], class_=re.compile(r'retweet|share'))
            comment_elem = item.find(['span', 'div'], class_=re.compile(r'comment|reply'))
            
            return {
                'text': text,
                'created_at': created_at,
                'fav_count': self.extract_count(like_elem),
                'retweet_count': self.extract_count(retweet_elem),
                'reply_count': self.extract_count(comment_elem)
            }
        except Exception as e:
            print(f"解析动态项失败: {e}")
            return None
    
    def extract_count(self, elem):
        """提取数量"""
        if not elem:
            return 0
        text = elem.get_text(strip=True)
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 0

# 测试代码
if __name__ == '__main__':
    parser = XueqiuHTMLParser()
    user_id = '1247347556'
    
    print(f"解析用户 {user_id} 的页面数据...")
    statuses = parser.get_user_page_data(user_id)
    
    if statuses:
        print(f"成功解析 {len(statuses)} 条动态:")
        for i, status in enumerate(statuses[:3], 1):
            print(f"\n{i}. {status['text'][:100]}...")
            print(f"   时间: {status['created_at']}")
            print(f"   点赞: {status['fav_count']}, 转发: {status['retweet_count']}, 评论: {status['reply_count']}")
    else:
        print("未解析到动态数据")