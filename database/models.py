from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

# 创建关联表
spider_notification_association = Table(
    'spider_notification_association',
    Base.metadata,
    Column('spider_config_id', Integer, ForeignKey('spider_config.id'), primary_key=True),
    Column('notification_config_id', Integer, ForeignKey('notification_config.id'), primary_key=True)
)

class SpiderConfig(Base):
    """爬虫配置表"""
    __tablename__ = 'spider_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, comment='平台名称')
    user_id = Column(String(100), nullable=False, comment='用户ID')
    username = Column(String(100), comment='用户名')
    auth_config = Column(JSON, comment='认证配置')
    # 移除单一外键，使用多对多关系
    # notification_config_id = Column(Integer, ForeignKey('notification_config.id'), comment='关联的通知配置ID')
    is_active = Column(Boolean, default=True, comment='是否启用')
    
    # 新增定时配置字段
    schedule_enabled = Column(Boolean, default=True, comment='是否启用定时执行')
    schedule_interval = Column(Integer, default=300, comment='执行间隔（秒）')
    schedule_type = Column(String(20), default='interval', comment='调度类型：interval(间隔), cron(定时)')
    cron_expression = Column(String(100), comment='Cron表达式（当schedule_type为cron时使用）')
    last_run_time = Column(DateTime, comment='上次执行时间')
    next_run_time = Column(DateTime, comment='下次执行时间')
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 建立多对多关系
    notification_configs = relationship(
        "NotificationConfig", 
        secondary=spider_notification_association,
        back_populates="spider_configs"
    )

class NotificationConfig(Base):
    """推送配置表"""
    __tablename__ = 'notification_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String(50), nullable=False, comment='推送方式')
    config = Column(JSON, nullable=False, comment='推送配置')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 建立多对多关系
    spider_configs = relationship(
        "SpiderConfig", 
        secondary=spider_notification_association,
        back_populates="notification_configs"
    )

class PostData(Base):
    """帖子数据表"""
    __tablename__ = 'post_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, comment='平台名称')
    user_id = Column(String(100), nullable=False, comment='用户ID')
    post_id = Column(String(200), nullable=False, comment='帖子ID')
    content = Column(Text, comment='帖子内容')
    processed_content = Column(Text, comment='处理后的内容（图片链接已缓存）')
    post_time = Column(DateTime, comment='发帖时间')
    is_sent = Column(Boolean, default=False, comment='是否已推送')
    created_at = Column(DateTime, default=func.now())
    
class SystemLog(Base):
    """系统日志表"""
    __tablename__ = 'system_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, comment='日志级别')
    message = Column(Text, nullable=False, comment='日志消息')
    module = Column(String(100), comment='模块名称')
    created_at = Column(DateTime, default=func.now())