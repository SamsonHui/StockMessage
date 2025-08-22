from flask import Blueprint, render_template, request, flash
from database.connection import db_manager
from database.models import SystemLog
from utils.logger import setup_logger

logger = setup_logger()
log_bp = Blueprint('log', __name__, url_prefix='/logs')

@log_bp.route('/')
def logs():
    """日志页面"""
    logger.info("访问日志页面")
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level', '')
        module = request.args.get('module', '')
        
        session = db_manager.get_session()
        
        # 构建查询
        query = session.query(SystemLog)
        
        # 添加过滤条件
        if level:
            query = query.filter(SystemLog.level == level)
        if module:
            query = query.filter(SystemLog.module == module)
        
        # 分页查询
        total = query.count()
        logs_data = query.order_by(SystemLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # 获取可用的级别和模块列表用于过滤
        levels = session.query(SystemLog.level).distinct().all()
        levels = [l[0] for l in levels if l[0]]
        
        modules = session.query(SystemLog.module).distinct().all()
        modules = [m[0] for m in modules if m[0]]
        
        session.close()
        
        # 计算分页信息
        has_prev = page > 1
        has_next = page * per_page < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': prev_num,
            'next_num': next_num
        }
        
        logger.info(f"获取到{len(logs_data)}条日志，第{page}页，共{total}条")
        return render_template('logs.html', 
                             logs=logs_data, 
                             pagination=pagination,
                             levels=levels,
                             modules=modules,
                             current_level=level,
                             current_module=module)
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        flash(f'获取日志失败: {str(e)}', 'error')
        return render_template('logs.html', logs=[], pagination={})