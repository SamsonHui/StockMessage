from web import create_app
from utils.logger import setup_logger

logger = setup_logger()

if __name__ == '__main__':
    logger.info("启动Web管理界面服务器（包含定时调度器）")
    app = create_app()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在关闭应用...")
    except Exception as e:
        logger.error(f"应用运行失败: {str(e)}")