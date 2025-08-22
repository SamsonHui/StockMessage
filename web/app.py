from flask import Flask
from utils.logger import setup_logger
from utils.scheduler import SpiderScheduler
from database.connection import db_manager
import atexit

logger = setup_logger()

# 全局爬虫运行状态
spider_status = {
    'running': False,
    'last_run': None,
    'next_run': None,
    'total_posts': 0,
    'total_notifications': 0
}

# 全局调度器实例
scheduler = None

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # 设置密钥
    app.secret_key = 'your-secret-key-here'
    
    # 注册蓝图
    from web.routes.dashboard import dashboard_bp
    from web.routes.spider import spider_bp
    from web.routes.notification import notification_bp
    from web.routes.message import message_bp
    from web.routes.log import log_bp
    from web.routes.api import api_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(spider_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(api_bp)
    
    # 初始化数据库和调度器
    def initialize_app():
        global scheduler
        try:
            # 初始化数据库
            db_manager.create_tables()
            logger.info("数据库初始化完成")
            
            # 启动调度器
            scheduler = SpiderScheduler()
            scheduler.start()
            logger.info("调度器已集成到Flask应用")
            
        except Exception as e:
            logger.error(f"应用初始化失败: {str(e)}")
    
    # 在应用上下文中初始化
    with app.app_context():
        initialize_app()
    
    # 注册应用关闭时的清理函数
    def cleanup():
        global scheduler
        if scheduler:
            try:
                scheduler.stop()
                logger.info("调度器已停止")
            except Exception as e:
                logger.error(f"停止调度器时出错: {str(e)}")
    
    atexit.register(cleanup)
    
    return app

def get_scheduler():
    """获取调度器实例"""
    global scheduler
    return scheduler