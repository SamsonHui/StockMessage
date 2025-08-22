from typing import List, Dict, Any
from loguru import logger
from database.connection import db_manager
from database.models import SpiderConfig, NotificationConfig, PostData

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.db_session = db_manager.get_session()
    
    def get_spider_configs(self) -> List[Dict[str, Any]]:
        """获取爬虫配置"""
        try:
            configs = self.db_session.query(SpiderConfig).filter(
                SpiderConfig.is_active == True
            ).all()
            
            return [{
                'id': config.id,
                'platform': config.platform,
                'user_id': config.user_id,
                'username': config.username,
                'auth_config': config.auth_config or {}
            } for config in configs]
            
        except Exception as e:
            logger.error(f"获取爬虫配置失败: {str(e)}")
            return []
        finally:
            self.db_session.close()
    
    def get_notification_configs(self) -> List[Dict[str, Any]]:
        """获取推送配置"""
        try:
            configs = self.db_session.query(NotificationConfig).filter(
                NotificationConfig.is_active == True
            ).all()
            
            return [{
                'id': config.id,
                'method': config.method,
                'config': config.config or {}
            } for config in configs]
            
        except Exception as e:
            logger.error(f"获取推送配置失败: {str(e)}")
            return []
        finally:
            self.db_session.close()
    
    def add_spider_config(self, platform, user_id, username=None, auth_config=None, notification_config_id=None):
        """添加爬虫配置"""
        try:
            session = self.db_manager.get_session()
            
            # 检查是否已存在相同配置
            existing = session.query(SpiderConfig).filter(
                SpiderConfig.platform == platform,
                SpiderConfig.user_id == user_id
            ).first()
            
            if existing:
                raise ValueError(f"平台 {platform} 的用户 {user_id} 配置已存在")
            
            config = SpiderConfig(
                platform=platform,
                user_id=user_id,
                username=username,
                auth_config=auth_config or {},
                notification_config_id=notification_config_id
            )
            
            session.add(config)
            session.commit()
            
            self.logger.info(f"添加爬虫配置成功: {platform}_{user_id}, 通知配置ID: {notification_config_id}")
            session.close()
            return config.id
        except Exception as e:
            session.rollback()
            session.close()
            self.logger.error(f"添加爬虫配置失败: {str(e)}")
            raise
    
    def _initial_crawl(self, platform: str, user_id: str, auth_config: Dict = None):
        """初始化爬取最近10条消息"""
        try:
            # 导入爬虫映射
            from spider import SPIDER_MAP
            
            # 获取对应的爬虫类
            spider_class = SPIDER_MAP.get(platform)
            if not spider_class:
                logger.warning(f"不支持的平台: {platform}")
                return
            
            # 创建爬虫实例
            spider = spider_class()
            
            # 认证
            if auth_config and not spider.authenticate(auth_config):
                logger.warning(f"初始化爬取认证失败: {platform} - {user_id}")
                return
            
            # 获取帖子（限制为10条）
            posts = spider.get_user_posts(user_id)
            
            # 只保存最近10条
            recent_posts = posts[:10] if len(posts) > 10 else posts
            
            # 保存到数据库
            saved_count = self._save_initial_posts(recent_posts)
            
            logger.info(f"初始化爬取完成: {platform} - {user_id}, 保存了 {saved_count} 条消息")
            
        except Exception as e:
            logger.error(f"初始化爬取失败: {platform} - {user_id}, 错误: {str(e)}")
    
    def _save_initial_posts(self, posts: List[Dict[str, Any]]) -> int:
        """保存初始化爬取的帖子"""
        saved_count = 0
        db_session = db_manager.get_session()
        
        try:
            for post in posts:
                # 检查是否已存在
                existing = db_session.query(PostData).filter(
                    PostData.platform == post['platform'],
                    PostData.post_id == post['post_id']
                ).first()
                
                if not existing:
                    # 创建新记录
                    post_data = PostData(
                        platform=post['platform'],
                        user_id=post['user_id'],
                        post_id=post['post_id'],
                        content=post['content'],
                        post_time=post['post_time']
                    )
                    
                    db_session.add(post_data)
                    saved_count += 1
            
            db_session.commit()
            return saved_count
            
        except Exception as e:
            logger.error(f"保存初始化帖子失败: {str(e)}")
            db_session.rollback()
            return 0
        finally:
            db_session.close()
    
    def add_notification_config(self, method: str, config: Dict) -> bool:
        """添加推送配置"""
        try:
            notification_config = NotificationConfig(
                method=method,
                config=config
            )
            
            self.db_session.add(notification_config)
            self.db_session.commit()
            
            logger.info(f"添加推送配置成功: {method}")
            return True
            
        except Exception as e:
            logger.error(f"添加推送配置失败: {str(e)}")
            self.db_session.rollback()
            return False
        finally:
            self.db_session.close()
    
    def delete_spider_config(self, config_id: int) -> bool:
        """删除爬虫配置"""
        try:
            config = self.db_session.query(SpiderConfig).filter(
                SpiderConfig.id == config_id
            ).first()
            
            if config:
                self.db_session.delete(config)
                self.db_session.commit()
                logger.info(f"删除爬虫配置成功: ID={config_id}")
                return True
            else:
                logger.warning(f"未找到爬虫配置: ID={config_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除爬虫配置失败: {str(e)}")
            self.db_session.rollback()
            return False
        finally:
            self.db_session.close()
    
    def delete_notification_config(self, config_id: int) -> bool:
        """删除通知配置"""
        try:
            config = self.db_session.query(NotificationConfig).filter(
                NotificationConfig.id == config_id
            ).first()
            
            if config:
                self.db_session.delete(config)
                self.db_session.commit()
                logger.info(f"删除通知配置成功: ID={config_id}")
                return True
            else:
                logger.warning(f"未找到通知配置: ID={config_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除通知配置失败: {str(e)}")
            self.db_session.rollback()
            return False
        finally:
            self.db_session.close()