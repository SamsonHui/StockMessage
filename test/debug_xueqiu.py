import requests

def test_xueqiu_api():
    session = requests.Session()
    
    # 设置完整的cookie和headers
    cookies = {
        # 你的完整cookie
    }
    
    headers = {
        # 完整的headers
    }
    
    session.cookies.update(cookies)
    session.headers.update(headers)
    
    # 测试不同的API
    apis = [
        "https://xueqiu.com/v4/statuses/user_timeline.json?user_id=6070369404&count=5",
        "https://stock.xueqiu.com/v5/stock/timeline/statuses.json?symbol_id=6070369404&count=5&source=user",
    ]
    
    for api in apis:
        print(f"Testing: {api}")
        response = session.get(api)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_xueqiu_api()