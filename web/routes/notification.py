from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.connection import db_manager
from database.models import NotificationConfig
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

logger = setup_logger()
notification_bp = Blueprint('notification', __name__, url_prefix='/notification-config')

# 支持的通知类型
NOTIFICATION_TYPES = ['email', 'dingtalk', 'feishu', 'wechat_work', 'wechat_mp']

@notification_bp.route('/')
def notification_config():
    """通知配置页面"""
    logger.info("访问通知配置页面")
    try:
        session = db_manager.get_session()
        configs = session.query(NotificationConfig).all()
        
        # 转换为字典格式供模板使用
        configs_data = [{
            'id': config.id,
            'method': config.method,
            'notification_type': config.method,
            'name': config.config.get('name', f"{config.method}_{config.id}"),
            'config': config.config or {},
            'is_active': config.is_active,
            'enabled': config.is_active,
            'created_at': config.created_at,
            'updated_at': config.updated_at
        } for config in configs]
        
        session.close()
        logger.info(f"获取到{len(configs_data)}个通知配置")
        return render_template('notification_config.html', configs=configs_data)
    except Exception as e:
        logger.error(f"获取通知配置失败: {str(e)}")
        flash(f'获取通知配置失败: {str(e)}', 'error')
        return render_template('notification_config.html', configs=[])

@notification_bp.route('/add', methods=['GET', 'POST'])
def add_notification_config():
    """添加通知配置"""
    if request.method == 'POST':
        logger.info("尝试添加新的通知配置")
        try:
            notification_type = request.form['notification_type']
            name = request.form['name']
            
            # 根据通知类型构建配置
            if notification_type == 'email':
                config_data = {
                    'name': name,
                    'smtp_server': request.form['smtp_server'],
                    'smtp_port': int(request.form['smtp_port']),
                    'username': request.form['email_username'],
                    'password': request.form['email_password'],
                    'from_email': request.form['from_email'],
                    'to_emails': request.form['to_emails'].split(',')
                }
            elif notification_type == 'dingtalk':
                config_data = {
                    'name': name,
                    'webhook_url': request.form['webhook_url'],
                    'secret': request.form.get('secret', '')
                }
            elif notification_type == 'feishu':
                config_data = {
                    'name': name,
                    'webhook_url': request.form['webhook_url'],
                    'secret': request.form.get('secret', '')
                }
            elif notification_type == 'wechat_work':
                config_data = {
                    'name': name,
                    'webhook_url': request.form['webhook_url']
                }
            elif notification_type == 'wechat_mp':
                config_data = {
                    'name': name,
                    'app_id': request.form['appid'],
                    'app_secret': request.form['wechat_secret'],
                    'template_id': request.form['template_id'],
                    'user_openids': request.form['openids'].split(',')
                }
            
            config_manager = ConfigManager()
            config_manager.add_notification_config(
                method=notification_type,
                config=config_data
            )
            
            logger.info(f"成功添加通知配置: 类型={notification_type}, 名称={name}")
            flash('通知配置添加成功！', 'success')
            return redirect(url_for('notification.notification_config'))
        except Exception as e:
            logger.error(f"添加通知配置失败: {str(e)}")
            flash(f'添加通知配置失败: {str(e)}', 'error')
    
    # GET请求时传递通知类型列表
    return render_template('add_notification_config.html', notification_types=NOTIFICATION_TYPES)

@notification_bp.route('/edit/<int:config_id>', methods=['GET', 'POST'])
def edit_notification_config(config_id):
    """编辑通知配置"""
    try:
        session = db_manager.get_session()
        config = session.query(NotificationConfig).filter(NotificationConfig.id == config_id).first()
        
        if not config:
            flash('通知配置不存在！', 'error')
            return redirect(url_for('notification.notification_config'))
        
        if request.method == 'POST':
            logger.info(f"尝试更新通知配置: {config_id}")
            
            notification_type = request.form['notification_type']
            name = request.form['name']
            
            # 根据通知类型构建配置
            if notification_type == 'email':
                config_data = {
                    'name': name,
                    'smtp_server': request.form['smtp_server'],
                    'smtp_port': int(request.form['smtp_port']),
                    'username': request.form['email_username'],
                    'password': request.form['email_password'],
                    'from_email': request.form['from_email'],
                    'to_emails': request.form['to_emails'].split(',')
                }
            elif notification_type == 'dingtalk':
                config_data = {
                    'name': name,
                    'webhook_url': request.form['webhook_url'],
                    'secret': request.form.get('secret', '')
                }
            elif notification_type == 'feishu':
                config_data = {
                    'name': name,
                    'webhook_url': request.form['webhook_url'],
                    'secret': request.form.get('secret', '')
                }
            elif notification_type == 'wechat_work':
                config_data = {
                    'name': name,
                    'webhook_url': request.form['webhook_url']
                }
            elif notification_type == 'wechat_mp':
                config_data = {
                    'name': name,
                    'app_id': request.form['appid'],
                    'app_secret': request.form['wechat_secret'],
                    'template_id': request.form['template_id'],
                    'user_openids': request.form['openids'].split(',')
                }
            
            # 更新配置
            config.method = notification_type
            config.config = config_data
            session.commit()
            
            logger.info(f"成功更新通知配置: {config_id}")
            flash('通知配置更新成功！', 'success')
            session.close()
            return redirect(url_for('notification.notification_config'))
        
        # GET请求时显示编辑表单
        config_data = {
            'id': config.id,
            'method': config.method,
            'notification_type': config.method,
            'name': config.config.get('name', f"{config.method}_{config.id}"),
            'config': config.config or {},
            'is_active': config.is_active
        }
        
        session.close()
        return render_template('edit_notification_config.html', 
                             config=config_data, 
                             notification_types=NOTIFICATION_TYPES)
        
    except Exception as e:
        logger.error(f"编辑通知配置失败: {str(e)}")
        flash(f'编辑通知配置失败: {str(e)}', 'error')
        return redirect(url_for('notification.notification_config'))

@notification_bp.route('/delete/<int:config_id>')
def delete_notification_config(config_id):
    """删除通知配置"""
    try:
        session = db_manager.get_session()
        config = session.query(NotificationConfig).filter(NotificationConfig.id == config_id).first()
        
        if config:
            session.delete(config)
            session.commit()
            logger.info(f"成功删除通知配置: {config.method}")
            flash('通知配置删除成功！', 'success')
        else:
            flash('通知配置不存在！', 'error')
        
        session.close()
    except Exception as e:
        logger.error(f"删除通知配置失败: {str(e)}")
        flash(f'删除通知配置失败: {str(e)}', 'error')
    
    return redirect(url_for('notification.notification_config'))