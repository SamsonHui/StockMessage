from utils.config_manager import ConfigManager
"""动态配置"""

config_manager = ConfigManager()

# 添加雪球用户监控
config_manager.add_spider_config(
    platform='xueqiu',
    user_id='1234567890',
    username='某用户',
    auth_config={'cookies': {'xq_a_token': 'your_token'}}
)

# 添加邮件推送
config_manager.add_notification_config(
    method='email',
    config={
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_password',
        'to_emails': ['recipient@example.com']
    }
)