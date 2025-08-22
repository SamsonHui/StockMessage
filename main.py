import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from utils.logger import setup_logger
from utils.scheduler import SpiderScheduler
from database.connection import db_manager
from config import config

def main():
    """主程序入口"""
    try:
        # 设置日志
        setup_logger()
        logger.info("股票消息爬虫系统启动")
        
        # 初始化数据库
        db_manager.create_tables()
        logger.info("数据库初始化完成")
        
        # 启动调度器
        scheduler = SpiderScheduler()
        scheduler.start()
        
        logger.info("调度器启动完成，系统正在运行...")
        
        # 保持程序运行
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("接收到停止信号，正在关闭系统...")
            scheduler.stop()
            
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()