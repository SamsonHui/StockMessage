import requests
import json
import time
from fake_useragent import UserAgent

class XueqiuAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.base_headers = {
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://xueqiu.com/',
            'Origin': 'https://xueqiu.com'
        }
        self.session.headers.update(self.base_headers)
    
    def get_user_timeline(self, user_id, page=1, count=20):
        """获取用户动态"""
        url = f'https://xueqiu.com/v4/statuses/user_timeline.json'
        params = {
            'user_id': user_id,
            'page': page,
            'count': count
        }
        
        try:
            # 先访问用户主页获取必要的cookie
            self.session.get(f'https://xueqiu.com/u/{user_id}')
            time.sleep(1)
            
            # 调用API
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data.get('statuses', [])
                except json.JSONDecodeError:
                    print(f"JSON解析失败: {response.text[:200]}")
                    return []
            else:
                print(f"API调用失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"请求异常: {e}")
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
    client = XueqiuAPIClient()
    user_id = '1247347556'  # 示例用户ID
    
    print(f"获取用户 {user_id} 的动态...")
    statuses = client.get_user_timeline(user_id)
    
    if statuses:
        print(f"成功获取 {len(statuses)} 条动态:")
        for i, status in enumerate(statuses[:3], 1):
            parsed = client.parse_status(status)
            print(f"\n{i}. {parsed['text'][:100]}...")
            print(f"   时间: {parsed['created_at']}")
            print(f"   点赞: {parsed['fav_count']}, 转发: {parsed['retweet_count']}, 评论: {parsed['reply_count']}")
    else:
        print("未获取到动态数据")