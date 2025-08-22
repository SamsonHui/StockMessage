from flask import Blueprint, render_template, flash
from datetime import datetime
from database.connection import db_manager
from database.models import SpiderConfig, NotificationConfig, PostData, SystemLog
from sqlalchemy import func
from utils.logger import setup_logger
from ..app import spider_status

logger = setup_logger()
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """仪表板页面"""
    logger.info("访问仪表板页面")
    try:
        session = db_manager.get_session()
        
        # 获取统计信息
        active_spiders = session.query(SpiderConfig).filter(SpiderConfig.is_active == True).count()
        active_notifications = session.query(NotificationConfig).filter(NotificationConfig.is_active == True).count()
        
        # 获取今日消息数
        today = datetime.now().date()
        posts_today = session.query(PostData).filter(func.date(PostData.created_at) == today).count()
        
        # 获取今日错误数
        errors_today = session.query(SystemLog).filter(
            SystemLog.level == 'ERROR',
            func.date(SystemLog.created_at) == today
        ).count()
        
        # 获取最近的系统日志
        recent_logs = session.query(SystemLog).order_by(SystemLog.created_at.desc()).limit(10).all()
        
        session.close()
        
        stats = {
            'active_spiders': active_spiders,
            'active_notifications': active_notifications,
            'posts_today': posts_today,
            'errors_today': errors_today,
            'spider_status': spider_status,
            'recent_logs': [{
                'level': log.level,
                'message': log.message,
                'module': log.module,
                'created_at': log.created_at
            } for log in recent_logs]
        }
        
        logger.info(f"仪表板数据加载成功: 活跃爬虫{active_spiders}个, 活跃通知{active_notifications}个, 今日消息{posts_today}条")
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"获取仪表板数据失败: {str(e)}")
        flash(f'获取仪表板数据失败: {str(e)}', 'error')
        return render_template('dashboard.html', stats={})