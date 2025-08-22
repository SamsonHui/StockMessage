# 爬虫模块初始化文件
from .xueqiu_spider import XueqiuSpider
# 如果有其他爬虫，也需要导入
# from .weibo_spider import WeiboSpider
# from .taoguba_spider import TaogubaSpider
# from .eastmoney_spider import EastmoneySpider
# from .twitter_spider import TwitterSpider

SPIDER_MAP = {
    'xueqiu': XueqiuSpider,
    # 'weibo': WeiboSpider,
    # 'taoguba': TaogubaSpider,
    # 'eastmoney': EastmoneySpider,
    # 'twitter': TwitterSpider
}