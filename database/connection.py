from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from .models import Base

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connect()
    
    def connect(self):
        """连接数据库"""
        database_url = f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}?charset=utf8mb4"
        
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """创建数据库表"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()

# 全局数据库管理器实例
db_manager = DatabaseManager()