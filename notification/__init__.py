# 推送模块初始化文件
from .email_notifier import EmailNotifier
from .dingtalk_notifier import DingtalkNotifier
from .feishu_notifier import FeishuNotifier
from .wechat_work_notifier import WechatWorkNotifier
from .wechat_mp_notifier import WechatMpNotifier

# 推送器映射
NOTIFIER_MAP = {
    'email': EmailNotifier,
    'dingtalk': DingtalkNotifier,
    'feishu': FeishuNotifier,
    'wechat_work': WechatWorkNotifier,
    'wechat_mp': WechatMpNotifier
}