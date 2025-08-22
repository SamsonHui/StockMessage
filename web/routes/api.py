from flask import Blueprint, jsonify
from datetime import datetime
from database.connection import db_manager
from database.models import SpiderConfig, NotificationConfig, PostData, SystemLog
from sqlalchemy import func
from utils.logger import setup_logger
from ..app import spider_status
import importlib
from utils.image_cache import image_cache
from loguru import logger

logger = setup_logger()
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/spider/toggle/<int:config_id>', methods=['POST'])
def toggle_spider(config_id):
    """切换爬虫配置状态"""
    try:
        session = db_manager.get_session()
        config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
        
        if config:
            config.is_active = not config.is_active
            config.updated_at = func.now()
            session.commit()
            
            status = "启用" if config.is_active else "禁用"
            logger.info(f"成功{status}爬虫配置: {config.platform}_{config.user_id}")
            session.close()
            return jsonify({'success': True, 'message': f'爬虫配置已{status}', 'is_active': config.is_active})
        else:
            session.close()
            return jsonify({'success': False, 'message': '爬虫配置不存在'})
    except Exception as e:
        logger.error(f"切换爬虫配置状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})

@api_bp.route('/notification/toggle/<int:config_id>', methods=['POST'])
def toggle_notification(config_id):
    """切换通知配置状态"""
    try:
        session = db_manager.get_session()
        config = session.query(NotificationConfig).filter(NotificationConfig.id == config_id).first()
        
        if config:
            config.is_active = not config.is_active
            config.updated_at = func.now()
            session.commit()
            
            status = "启用" if config.is_active else "禁用"
            logger.info(f"成功{status}通知配置: {config.method}")
            session.close()
            return jsonify({'success': True, 'message': f'通知配置已{status}', 'is_active': config.is_active})
        else:
            session.close()
            return jsonify({'success': False, 'message': '通知配置不存在'})
    except Exception as e:
        logger.error(f"切换通知配置状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})

@api_bp.route('/stats')
def get_stats():
    """获取统计信息API"""
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
        
        session.close()
        
        return jsonify({
            'active_spiders': active_spiders,
            'active_notifications': active_notifications,
            'posts_today': posts_today,
            'errors_today': errors_today,
            'spider_status': spider_status
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/spider/manual-execute/<int:config_id>', methods=['POST'])
def manual_execute_spider(config_id):
    """手动执行爬虫配置"""
    try:
        session = db_manager.get_session()
        config = session.query(SpiderConfig).filter(SpiderConfig.id == config_id).first()
        
        if not config:
            session.close()
            return jsonify({'success': False, 'message': '爬虫配置不存在'})
        
        if not config.is_active:
            session.close()
            return jsonify({'success': False, 'message': '爬虫配置已禁用，无法执行'})
        
        # 调用现有的爬虫执行逻辑
        from ..routes.spider import trigger_spider_crawl
        result = trigger_spider_crawl(config.platform, config.user_id, config.auth_config)
        
        # 更新最后执行时间
        if result.get('success'):
            config.last_run_time = func.now()
            session.commit()
            logger.info(f"手动执行爬虫配置成功: {config.platform}_{config.user_id}")
        
        session.close()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"手动执行爬虫配置失败: {str(e)}")
        return jsonify({'success': False, 'message': f'执行失败: {str(e)}'})

@api_bp.route('/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """获取调度器状态"""
    try:
        from web.app import get_scheduler
        scheduler = get_scheduler()
        
        if scheduler and scheduler.is_running:
            jobs = []
            for job in scheduler.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                })
            
            return jsonify({
                'success': True,
                'running': True,
                'jobs_count': len(jobs),
                'jobs': jobs
            })
        else:
            return jsonify({
                'success': True,
                'running': False,
                'jobs_count': 0,
                'jobs': []
            })
            
    except Exception as e:
        logger.error(f"获取调度器状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取状态失败: {str(e)}'})

@api_bp.route('/scheduler/restart', methods=['POST'])
def restart_scheduler():
    """重启调度器"""
    try:
        from web.app import get_scheduler
        scheduler = get_scheduler()
        
        if scheduler:
            scheduler.stop()
            scheduler.start()
            logger.info("调度器重启成功")
            return jsonify({'success': True, 'message': '调度器重启成功'})
        else:
            return jsonify({'success': False, 'message': '调度器未初始化'})
            
    except Exception as e:
        logger.error(f"重启调度器失败: {str(e)}")
        return jsonify({'success': False, 'message': f'重启失败: {str(e)}'})

@api_bp.route('/image-cache/stats', methods=['GET'])
def get_image_cache_stats():
    """获取图片缓存统计信息"""
    try:
        stats = image_cache.get_cache_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"获取图片缓存统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500

@api_bp.route('/image-cache/cleanup', methods=['POST'])
def cleanup_image_cache():
    """清理图片缓存"""
    try:
        image_cache._cleanup_expired_files()
        image_cache._cleanup_by_size()
        
        stats = image_cache.get_cache_stats()
        return jsonify({
            'success': True,
            'message': '缓存清理完成',
            'data': stats
        })
    except Exception as e:
        logger.error(f"清理图片缓存失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'清理缓存失败: {str(e)}'
        }), 500