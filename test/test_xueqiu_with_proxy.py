import requests
import random
import time

class ProxyXueqiuClient:
    def __init__(self):
        self.session = requests.Session()
        # 免费代理池（实际使用时建议使用付费代理）
        self.proxies_list = [
            # 添加你的代理列表
            # {'http': 'http://proxy1:port', 'https': 'https://proxy1:port'},
            # {'http': 'http://proxy2:port', 'https': 'https://proxy2:port'},
        ]
        self.current_proxy = None
    
    def get_random_proxy(self):
        """获取随机代理"""
        if self.proxies_list:
            return random.choice(self.proxies_list)
        return None
    
    def test_proxy(self, proxy):
        """测试代理是否可用"""
        try:
            response = requests.get('https://httpbin.org/ip', 
                                  proxies=proxy, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_user_timeline_with_proxy(self, user_id):
        """使用代理获取用户动态"""
        for proxy in self.proxies_list:
            if self.test_proxy(proxy):
                print(f"使用代理: {proxy}")
                try:
                    # 使用代理请求
                    response = self.session.get(
                        f'https://xueqiu.com/v4/statuses/user_timeline.json',
                        params={'user_id': user_id, 'count': 20},
                        proxies=proxy,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('statuses', [])
                        
                except Exception as e:
                    print(f"代理请求失败: {e}")
                    continue
        
        return []