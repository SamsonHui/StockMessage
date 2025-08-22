from .dashboard import dashboard_bp
from .spider import spider_bp
from .notification import notification_bp
from .message import message_bp
from .log import log_bp
from .api import api_bp

__all__ = [
    'dashboard_bp',
    'spider_bp', 
    'notification_bp',
    'message_bp',
    'log_bp',
    'api_bp'
]