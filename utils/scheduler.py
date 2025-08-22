from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger
from sqlalchemy import desc
from database.connection import DatabaseManager
from database.models import SpiderConfig, PostData, NotificationConfig
from spider.xueqiu_spider import XueqiuSpider
from spider.weibo_spider import WeiboSpider
from spider.twitter_spider import TwitterSpider
from spider.taoguba_spider import TaogubaSpider
from spider.eastmoney_spider import EastmoneySpider
from notification.email_notifier import EmailNotifier
from notification.dingtalk_notifier import DingtalkNotifier
from notification.wechat_work_notifier import WechatWorkNotifier
from notification.wechat_mp_notifier import WechatMpNotifier
from notification.feishu_notifier import FeishuNotifier
from utils.image_cache import image_cache
import threading
import time
import schedule

class SpiderScheduler:  # 将 Scheduler 改为 SpiderScheduler
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.running = False
        self.thread = None
        
        # 爬虫映射
        self.spiders = {
            'xueqiu': XueqiuSpider,
            'weibo': WeiboSpider,
            'twitter': TwitterSpider,
            'taoguba': TaogubaSpider,
            'eastmoney': EastmoneySpider
        }
        
        # 通知器映射
        self.notifiers = {
            'email': EmailNotifier,
            'dingtalk': DingtalkNotifier,
            'wechat_work': WechatWorkNotifier,
            'wechat_mp': WechatMpNotifier,
            'feishu': FeishuNotifier
        }
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("调度器已停止")
    
    def _run_scheduler(self):
        """调度器主循环"""
        while self.running:
            try:
                # 获取所有启用的爬虫配置
                session = self.db_manager.get_session()
                configs = session.query(SpiderConfig).filter(
                    SpiderConfig.is_active == True,
                    SpiderConfig.schedule_enabled == True
                ).all()
                
                current_time = datetime.now()
                
                for config in configs:
                    # 检查是否需要执行
                    if self._should_run(config, current_time):
                        logger.info(f"执行爬虫任务: {config.platform} - {config.user_id}")
                        self.run_single_spider(config.id)
                        
                        # 更新执行时间
                        config.last_run_time = current_time
                        config.next_run_time = current_time + timedelta(seconds=config.schedule_interval)
                        session.commit()
                
                session.close()
                
            except Exception as e:
                logger.error(f"调度器运行异常: {str(e)}")
            
            # 等待一段时间再检查
            time.sleep(10)
    
    def _should_run(self, config: SpiderConfig, current_time: datetime) -> bool:
        """判断是否应该执行爬虫"""
        if not config.last_run_time:
            return True
        
        if config.schedule_type == 'interval':
            next_run = config.last_run_time + timedelta(seconds=config.schedule_interval)
            return current_time >= next_run
        
        # TODO: 实现cron表达式支持
        return False
    
    def run_single_spider(self, config_id: int):
        """运行单个爬虫"""
        try:
            session = self.db_manager.get_session()
            config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
            
            if not config:
                logger.error(f"爬虫配置不存在: config_id={config_id}")
                return
            
            platform = config.platform
            user_id = config.user_id
            auth_config = config.auth_config or {}
            
            # 获取对应的爬虫类
            spider_class = self.spiders.get(platform)
            if not spider_class:
                logger.error(f"不支持的平台: {platform}")
                return
            
            # 创建爬虫实例并执行
            spider = spider_class()
            if not spider.authenticate(auth_config):
                logger.error(f"爬虫认证失败: {platform} - {user_id}")
                return
            
            # 获取帖子数据
            raw_posts = spider.get_user_posts(user_id)
            if not raw_posts:
                logger.warning(f"未获取到帖子数据: {platform} - {user_id}")
                return
            
            # 解析并保存新帖子
            new_posts = []
            for raw_post in raw_posts:
                parsed_post = spider.parse_post(raw_post)
                if parsed_post and parsed_post.get('post_id'):
                    # 检查是否已存在
                    existing = session.query(PostData).filter(
                        PostData.platform == platform,
                        PostData.user_id == user_id,
                        PostData.post_id == parsed_post.get('post_id')
                    ).first()
                    
                    if not existing:
                        # 处理图片缓存
                        original_content = parsed_post.get('content', '')
                        processed_content = image_cache.process_content(original_content)
                        
                        post = PostData(
                            platform=platform,
                            user_id=user_id,
                            post_id=parsed_post.get('post_id'),
                            content=original_content,
                            processed_content=processed_content,
                            post_time=parsed_post.get('post_time'),
                            is_sent=False
                        )
                        session.add(post)
                        new_posts.append(post)
            
            session.commit()
            session.close()
            
            logger.info(f"爬虫 {platform} - {user_id} 获取到 {len(raw_posts)} 条帖子，新增 {len(new_posts)} 条")
            
            # 如果有新帖子，触发通知
            if new_posts:
                self.send_notifications_for_config(config_id)
            
        except Exception as e:
            logger.error(f"爬虫任务执行失败: config_id={config_id}, 错误: {str(e)}")
    
    def send_notifications_for_config(self, config_id: int):
        """为指定配置发送通知"""
        try:
            session = self.db_manager.get_session()
            
            # 获取爬虫配置和关联的通知配置
            config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
            if not config:
                logger.error(f"爬虫配置不存在: config_id={config_id}")
                return
            
            # 获取未发送的帖子
            unsent_posts = session.query(PostData).filter(
                PostData.platform == config.platform,
                PostData.user_id == config.user_id,
                PostData.is_sent == False
            ).order_by(desc(PostData.created_at)).limit(5).all()
            
            if not unsent_posts:
                logger.info(f"没有未发送的帖子: {config.platform} - {config.user_id}")
                return
            
            # 遍历关联的通知配置
            for notification_config in config.notification_configs:
                if not notification_config.is_active:
                    continue
                
                try:
                    # 创建通知器实例
                    notifier_class = self.notifiers.get(notification_config.method)
                    if not notifier_class:
                        logger.error(f"不支持的通知方式: {notification_config.method}")
                        continue
                    
                    notifier = notifier_class(notification_config.config)
                    
                    # 发送通知
                    for post in unsent_posts:
                        title = f"[{post.platform}] {config.username or config.user_id} 新消息"
                        # 使用处理后的内容（包含缓存的图片链接）
                        content = post.processed_content or post.content
                        
                        success = notifier.send_message(title, content)
                        if success:
                            logger.info(f"通知发送成功: {notification_config.method} - {post.post_id}")
                        else:
                            logger.error(f"通知发送失败: {notification_config.method} - {post.post_id}")
                    
                except Exception as e:
                    logger.error(f"通知发送异常: {notification_config.method}, 错误: {str(e)}")
            
            # 标记帖子为已发送
            for post in unsent_posts:
                post.is_sent = True
            
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"发送通知失败: config_id={config_id}, 错误: {str(e)}")
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        try:
            session = self.db_manager.get_session()
            
            # 统计信息
            total_configs = session.query(SpiderConfig).count()
            active_configs = session.query(SpiderConfig).filter(SpiderConfig.is_active == True).count()
            total_posts = session.query(PostData).count()
            
            session.close()
            
            return {
                'running': self.running,
                'total_configs': total_configs,
                'active_configs': active_configs,
                'total_posts': total_posts,
                'image_cache_stats': image_cache.get_cache_stats()
            }
            
        except Exception as e:
            logger.error(f"获取调度器状态失败: {str(e)}")
            return {'running': self.running, 'error': str(e)}

# 创建全局调度器实例
scheduler = SpiderScheduler()  # 将 Scheduler() 改为 SpiderScheduler()