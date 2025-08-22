import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spider.xueqiu_spider import XueqiuSpider

def test_spider_auth():
    spider = XueqiuSpider()
    
    # 确保cookie格式正确
    auth_config = {
        "cookies": {
            "xq_a_token": "02670a7f2e9d835dd2ddc5fb3ed1c25ef18a5301",
            "xq_r_token": "dd382559ed387214265d8e2a24eeefe60fbf1b7e",
            "u": "3160217153",
            "device_id": "1866b6a72fe75d41349a48b883d582da",
            # 添加其他必要的cookie字段
        }
    }
    
    # 测试认证
    if spider.authenticate(auth_config):
        print("✅ 认证成功！")
        
        # 测试获取用户动态
        posts = spider.get_user_posts('6070369404', limit=5)
        print(f"获取到 {len(posts)} 条动态")
        
        for post in posts[:2]:  # 显示前2条
            print(f"- {post.get('username', 'Unknown')}: {post.get('content', '')[:50]}...")
    else:
        print("❌ 认证失败")

if __name__ == "__main__":
    test_spider_auth()