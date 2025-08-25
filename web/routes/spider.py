from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database.connection import db_manager
from database.models import SpiderConfig, NotificationConfig, PostData
from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from sqlalchemy import func, desc
import importlib

logger = setup_logger()
spider_bp = Blueprint('spider', __name__, url_prefix='/spider-config')

@spider_bp.route('/')
def spider_config():
    """爬虫配置列表页面"""
    try:
        session = db_manager.get_session()
        configs = session.query(SpiderConfig).all()
        
        # 转换为字典格式供模板使用，包含通知配置信息
        configs_data = []
        for config in configs:
            # 修复：使用多对多关系获取通知配置
            notification_configs = []
            try:
                if config.notification_configs:
                    for notif_config in config.notification_configs:
                        notification_configs.append({
                            'id': notif_config.id,
                            'method': notif_config.method,
                            'name': notif_config.config.get('name', '未命名')
                        })
            except Exception as e:
                logger.warning(f"获取配置{config.id}的通知配置失败: {str(e)}")
            
            # 格式化定时配置显示
            if config.schedule_enabled:
                if config.schedule_type == 'cron':
                    schedule_display = f"Cron: {config.cron_expression}"
                else:
                    schedule_display = f"间隔: {config.schedule_interval}秒"
            else:
                schedule_display = "已禁用"
            
            configs_data.append({
                'id': config.id,
                'platform': config.platform,
                'user_id': config.user_id,
                'username': config.username,
                'auth_config': config.auth_config or {},
                'notification_configs': notification_configs,  # 修复：添加正确的字段
                'is_active': config.is_active,
                'enabled': config.is_active,
                'name': f"{config.platform}_{config.user_id}",
                # 添加定时配置字段
                'schedule_enabled': config.schedule_enabled,
                'schedule_type': config.schedule_type,
                'schedule_interval': config.schedule_interval,
                'cron_expression': config.cron_expression,
                'schedule_display': schedule_display,
                'last_run_time': config.last_run_time,
                'next_run_time': config.next_run_time,
                'created_at': config.created_at,
                'updated_at': config.updated_at
            })
        
        session.close()
        logger.info(f"获取到{len(configs_data)}个爬虫配置")
        return render_template('spider_config.html', configs=configs_data)
    except Exception as e:
        logger.error(f"获取爬虫配置失败: {str(e)}")
        flash(f'获取爬虫配置失败: {str(e)}', 'error')
        return render_template('spider_config.html', configs=[])

@spider_bp.route('/edit-notification/<int:config_id>', methods=['GET', 'POST'])
def edit_spider_notification(config_id):
    """修改爬虫配置的通知设置"""
    if request.method == 'POST':
        try:
            # 修复：处理多选通知配置，过滤空值
            notification_config_ids = request.form.getlist('notification_config_ids')
            # 过滤掉空字符串和无效值
            notification_config_ids = [nid for nid in notification_config_ids if nid and nid.strip()]
            
            session = db_manager.get_session()
            spider_config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
            
            if spider_config:
                # 清除现有关联
                spider_config.notification_configs.clear()
                
                # 添加新的关联
                if notification_config_ids:
                    for notif_id in notification_config_ids:
                        try:
                            # 添加类型检查和转换
                            notif_id_int = int(notif_id)
                            notif_config = session.query(NotificationConfig).filter(
                                NotificationConfig.id == notif_id_int
                            ).first()
                            if notif_config:
                                spider_config.notification_configs.append(notif_config)
                        except (ValueError, TypeError) as e:
                            logger.warning(f"无效的通知配置ID: {notif_id}, 错误: {str(e)}")
                            continue
                
                spider_config.updated_at = func.now()
                session.commit()
                
                logger.info(f"成功修改爬虫配置{config_id}的通知设置为{notification_config_ids}")
                flash('通知配置修改成功！', 'success')
            else:
                flash('爬虫配置不存在！', 'error')
            
            session.close()
            return redirect(url_for('spider.spider_config'))
        except Exception as e:
            logger.error(f"修改通知配置失败: {str(e)}")
            flash(f'修改通知配置失败: {str(e)}', 'error')
            return redirect(url_for('spider.spider_config'))
    
    # GET请求，显示编辑表单
    try:
        session = db_manager.get_session()
        spider_config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
        notification_configs = session.query(NotificationConfig).filter(NotificationConfig.is_active == True).all()
        
        if not spider_config:
            flash('爬虫配置不存在！', 'error')
            session.close()
            return redirect(url_for('spider.spider_config'))
        
        # 修复：在 session 关闭前访问关联属性，避免懒加载问题
        current_notification_ids = [nc.id for nc in spider_config.notification_configs]
        
        # 创建用于模板的数据字典
        spider_data = {
            'id': spider_config.id,
            'platform': spider_config.platform,
            'user_id': spider_config.user_id,
            'username': spider_config.username,
            'current_notification_ids': current_notification_ids
        }
        
        session.close()
        
        return render_template('edit_spider_notification.html', 
                             spider_config=spider_data, 
                             notification_configs=notification_configs)
    except Exception as e:
        logger.error(f"获取编辑数据失败: {str(e)}")
        flash(f'获取编辑数据失败: {str(e)}', 'error')
        return redirect(url_for('spider.spider_config'))

@spider_bp.route('/delete/<int:config_id>')
def delete_spider_config(config_id):
    """删除爬虫配置"""
    try:
        session = db_manager.get_session()
        config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
        
        if config:
            session.delete(config)
            session.commit()
            logger.info(f"成功删除爬虫配置: {config.platform}_{config.user_id}")
            flash('爬虫配置删除成功！', 'success')
        else:
            flash('爬虫配置不存在！', 'error')
        
        session.close()
    except Exception as e:
        logger.error(f"删除爬虫配置失败: {str(e)}")
        flash(f'删除爬虫配置失败: {str(e)}', 'error')
    
    return redirect(url_for('spider.spider_config'))

# 在 add_spider_config 函数中添加定时配置处理
@spider_bp.route('/add', methods=['GET', 'POST'])
def add_spider_config():
    """添加爬虫配置"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            platform = request.form.get('platform')
            user_id = request.form.get('user_id')
            username = request.form.get('username')
            cookies = request.form.get('cookies')
            headers = request.form.get('headers')
            token = request.form.get('token')
            notification_config_id = request.form.get('notification_config_id')
            
            # 获取定时配置
            schedule_enabled = request.form.get('schedule_enabled') == 'on'
            schedule_type = request.form.get('schedule_type', 'interval')
            schedule_interval = request.form.get('schedule_interval')
            custom_interval = request.form.get('custom_interval')
            cron_expression = request.form.get('cron_expression')
            
            # 处理间隔时间
            if schedule_type == 'interval':
                if schedule_interval == 'custom' and custom_interval:
                    final_interval = int(custom_interval)
                else:
                    final_interval = int(schedule_interval) if schedule_interval else 60
            else:
                final_interval = 300  # cron模式默认值
            
            # 构建认证配置
            auth_config = {}
            if cookies:
                auth_config['cookies'] = cookies
            if headers:
                try:
                    import json
                    auth_config['headers'] = json.loads(headers)
                except:
                    auth_config['headers'] = {'User-Agent': headers}
            if token:
                auth_config['token'] = token
            
            # 创建爬虫配置
            session = db_manager.get_session()
            config = SpiderConfig(
                platform=platform,
                user_id=user_id,
                username=username,
                auth_config=auth_config if auth_config else None,
                is_active=True,
                schedule_enabled=schedule_enabled,
                schedule_interval=final_interval,
                schedule_type=schedule_type,
                cron_expression=cron_expression if schedule_type == 'cron' else None
            )
            
            session.add(config)
            session.flush()  # 获取ID
            
            # 关联通知配置
            if notification_config_id:
                notif_config = session.query(NotificationConfig).filter(
                    NotificationConfig.id == int(notification_config_id)
                ).first()
                if notif_config:
                    config.notification_configs.append(notif_config)
            
            session.commit()
            session.close()
            
            logger.info(f"成功添加爬虫配置: {platform}_{user_id}，定时间隔: {final_interval}秒")
            flash('爬虫配置添加成功！', 'success')
            return redirect(url_for('spider.spider_config'))
            
        except Exception as e:
            logger.error(f"添加爬虫配置失败: {str(e)}")
            flash(f'添加爬虫配置失败: {str(e)}', 'error')
    
    # GET请求，显示表单
    try:
        session = db_manager.get_session()
        notification_configs = session.query(NotificationConfig).filter(
            NotificationConfig.is_active == True
        ).all()
        session.close()
        
        # 获取支持的平台列表
        spider_module = importlib.import_module('spider')
        platforms = list(getattr(spider_module, 'SPIDER_MAP', {}).keys())
        
        return render_template('add_spider_config.html', 
                             notification_configs=notification_configs,
                             platforms=platforms)
    except Exception as e:
        logger.error(f"获取配置数据失败: {str(e)}")
        flash(f'获取配置数据失败: {str(e)}', 'error')
        return render_template('add_spider_config.html', 
                             notification_configs=[],
                             platforms=[])

@spider_bp.route('/recent-data/<int:config_id>')
def get_recent_data(config_id):
    """获取爬虫配置的最近爬取数据"""
    try:
        session = db_manager.get_session()
        
        # 获取爬虫配置
        spider_config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
        if not spider_config:
            session.close()
            return jsonify({'success': False, 'message': '爬虫配置不存在'})
        
        # 查询最近5条数据
        recent_posts = session.query(PostData).filter(
            PostData.platform == spider_config.platform,
            PostData.user_id == spider_config.user_id
        ).order_by(desc(PostData.created_at)).limit(5).all()
        
        if recent_posts:
            # 如果有数据，直接返回
            posts_data = []
            for post in recent_posts:
                posts_data.append({
                    'id': post.id,
                    'post_id': post.post_id,
                    'content': post.content[:200] + '...' if len(post.content or '') > 200 else (post.content or ''),
                    'post_time': post.post_time.strftime('%Y-%m-%d %H:%M:%S') if post.post_time else '未知时间',
                    'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_sent': post.is_sent
                })
            
            session.close()
            return jsonify({
                'success': True, 
                'data': posts_data,
                'message': f'获取到{len(posts_data)}条最近数据'
            })
        else:
            # 如果没有数据，触发爬取
            session.close()
            crawl_result = trigger_spider_crawl(spider_config.platform, spider_config.user_id, spider_config.auth_config)
            
            if crawl_result['success']:
                # 重新查询数据
                session = db_manager.get_session()
                recent_posts = session.query(PostData).filter(
                    PostData.platform == spider_config.platform,
                    PostData.user_id == spider_config.user_id
                ).order_by(desc(PostData.created_at)).limit(5).all()
                
                posts_data = []
                for post in recent_posts:
                    posts_data.append({
                        'id': post.id,
                        'post_id': post.post_id,
                        'content': post.content[:200] + '...' if len(post.content or '') > 200 else (post.content or ''),
                        'post_time': post.post_time.strftime('%Y-%m-%d %H:%M:%S') if post.post_time else '未知时间',
                        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_sent': post.is_sent
                    })
                
                session.close()
                return jsonify({
                    'success': True, 
                    'data': posts_data,
                    'message': f'触发爬取成功，获取到{len(posts_data)}条数据'
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': f'触发爬取失败: {crawl_result["message"]}',
                    'data': []
                })
                
    except Exception as e:
        logger.error(f"获取最近数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'})

def trigger_spider_crawl(platform, user_id, auth_config):
    """触发单次爬虫爬取"""
    try:
        # 动态导入爬虫映射
        spider_module = importlib.import_module('spider')
        SPIDER_MAP = getattr(spider_module, 'SPIDER_MAP', {})
        
        # 获取爬虫类
        spider_class = SPIDER_MAP.get(platform)
        if not spider_class:
            return {'success': False, 'message': f'不支持的平台: {platform}'}
        
        # 创建爬虫实例
        spider = spider_class()
        
        # 认证（如果需要）
        if auth_config and not spider.authenticate(auth_config):
            return {'success': False, 'message': f'爬虫认证失败: {platform} - {user_id}'}
        
        # 获取原始帖子数据
        raw_posts = spider.get_user_posts(user_id, limit=5)
        
        if not raw_posts:
            return {'success': False, 'message': '未获取到任何数据'}
        
        # 解析帖子数据
        posts = []
        for raw_post in raw_posts:
            parsed_post = spider.parse_post(raw_post)
            if parsed_post and parsed_post.get('post_id'):  # 确保post_id不为空
                posts.append(parsed_post)
        
        if not posts:
            return {'success': False, 'message': '解析后无有效数据'}
        
        # 保存到数据库
        session = db_manager.get_session()
        saved_count = 0
        
        for post_data in posts:
            # 检查是否已存在
            existing = session.query(PostData).filter(
                PostData.platform == platform,
                PostData.user_id == user_id,
                PostData.post_id == post_data.get('post_id')
            ).first()
            
            if not existing:
                post = PostData(
                    platform=platform,
                    user_id=user_id,
                    post_id=post_data.get('post_id'),
                    content=post_data.get('content'),
                    post_time=post_data.get('post_time'),
                    is_sent=False
                )
                session.add(post)
                saved_count += 1
        
        session.commit()
        session.close()
        
        logger.info(f"爬虫 {platform} - {user_id} 获取到 {len(raw_posts)} 条原始帖子，解析出 {len(posts)} 条有效帖子，新增 {saved_count} 条")
        return {'success': True, 'message': f'爬取成功，新增{saved_count}条数据'}
        
    except Exception as e:
        logger.error(f"触发爬虫爬取失败: {platform} - {user_id}, 错误: {str(e)}")
        return {'success': False, 'message': f'爬取失败: {str(e)}'}

@spider_bp.route('/edit-schedule/<int:config_id>', methods=['GET', 'POST'])
def edit_spider_schedule(config_id):
    """编辑爬虫定时配置"""
    if request.method == 'POST':
        try:
            session = db_manager.get_session()
            config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
            
            if not config:
                flash('爬虫配置不存在！', 'error')
                return redirect(url_for('spider.spider_config'))
            
            # 获取表单数据
            schedule_enabled = request.form.get('schedule_enabled') == 'on'
            schedule_type = request.form.get('schedule_type', 'interval')
            schedule_interval = request.form.get('schedule_interval')
            custom_interval = request.form.get('custom_interval')
            cron_expression = request.form.get('cron_expression')
            
            # 处理间隔时间
            if schedule_type == 'interval':
                if schedule_interval == 'custom' and custom_interval:
                    final_interval = int(custom_interval)
                else:
                    final_interval = int(schedule_interval) if schedule_interval else 60
            else:
                final_interval = config.schedule_interval  # 保持原值
            
            # 更新配置
            config.schedule_enabled = schedule_enabled
            config.schedule_type = schedule_type
            config.schedule_interval = final_interval
            config.cron_expression = cron_expression if schedule_type == 'cron' else None
            config.updated_at = func.now()
            
            session.commit()
            session.close()
            
            flash('定时配置更新成功！', 'success')
            return redirect(url_for('spider.spider_config'))
            
        except Exception as e:
            logger.error(f"更新定时配置失败: {str(e)}")
            flash(f'更新定时配置失败: {str(e)}', 'error')
            return redirect(url_for('spider.spider_config'))
    
    # GET 请求 - 显示编辑表单
    try:
        session = db_manager.get_session()
        config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
        session.close()
        
        if not config:
            flash('爬虫配置不存在！', 'error')
            return redirect(url_for('spider.spider_config'))
        
        return render_template('edit_spider_schedule.html', config=config)
        
    except Exception as e:
        logger.error(f"获取爬虫配置失败: {str(e)}")
        flash(f'获取爬虫配置失败: {str(e)}', 'error')
        return redirect(url_for('spider.spider_config'))