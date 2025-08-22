from flask import Blueprint, render_template, request, flash
from database.connection import db_manager
from database.models import PostData, SpiderConfig
from utils.logger import setup_logger
from sqlalchemy import distinct

logger = setup_logger()
message_bp = Blueprint('message', __name__, url_prefix='/messages')

@message_bp.route('/')
def messages():
    """消息页面"""
    logger.info("访问消息页面")
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)  # 修改参数名
        platform = request.args.get('platform', '')
        user_id = request.args.get('user_id', '')
        
        session = db_manager.get_session()
        
        # 构建查询，关联SpiderConfig获取用户名
        query = session.query(
            PostData,
            SpiderConfig.username
        ).outerjoin(
            SpiderConfig,
            (PostData.platform == SpiderConfig.platform) & 
            (PostData.user_id == SpiderConfig.user_id)
        )
        
        # 添加过滤条件
        if platform:
            query = query.filter(PostData.platform == platform)
        if user_id:
            query = query.filter(PostData.user_id == user_id)
        
        # 分页查询
        total = query.count()
        results = query.order_by(PostData.post_time.desc()).offset((page - 1) * limit).limit(limit).all()
        
        # 处理查询结果，合并用户名信息
        posts = []
        for post_data, username in results:
            # 创建一个包含用户名的帖子对象
            post_dict = {
                'id': post_data.id,
                'platform': post_data.platform,
                'user_id': post_data.user_id,
                'post_id': post_data.post_id,
                'content': post_data.content,
                'post_time': post_data.post_time,
                'created_at': post_data.created_at,
                'is_sent': post_data.is_sent,
                'username': username or post_data.user_id  # 使用配置的用户名，如果没有则使用user_id
            }
            posts.append(post_dict)
        
        # 获取可用的平台列表
        platforms = session.query(distinct(PostData.platform)).all()
        platforms = [p[0] for p in platforms if p[0]]
        
        # 获取用户列表，关联SpiderConfig获取用户名
        users_query = session.query(
            PostData.platform,
            PostData.user_id,
            SpiderConfig.username
        ).outerjoin(
            SpiderConfig,
            (PostData.platform == SpiderConfig.platform) & 
            (PostData.user_id == SpiderConfig.user_id)
        ).distinct()
        
        users = []
        for platform_name, uid, username in users_query:
            users.append({
                'platform': platform_name,
                'user_id': uid,
                'username': username or uid  # 使用配置的用户名，如果没有则使用user_id
            })
        
        session.close()
        
        # 计算分页信息
        has_prev = page > 1
        has_next = page * limit < total
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        pagination = {
            'page': page,
            'per_page': limit,
            'total': total,
            'pages': (total + limit - 1) // limit,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': prev_num,
            'next_num': next_num
        }
        
        logger.info(f"获取到{len(posts)}条消息，第{page}页，共{total}条")
        return render_template('messages.html', 
                             posts=posts, 
                             pagination=pagination,
                             platforms=platforms,
                             users=users,  # 修改变量名
                             current_platform=platform,
                             current_user_id=user_id,
                             current_limit=limit)  # 添加当前限制数
    except Exception as e:
        logger.error(f"获取消息失败: {str(e)}")
        flash(f'获取消息失败: {str(e)}', 'error')
        return render_template('messages.html', posts=[], pagination={})