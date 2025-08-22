# 股票消息爬虫系统

一个用于爬取多个股票相关网站用户动态并进行实时推送的Python项目。

## 功能特性

- 🕷️ 支持多平台爬虫：雪球、新浪微博、东财、淘股吧、推特
- 📱 多种推送方式：邮件、钉钉、飞书、企业微信、微信公众号
- ⚙️ 灵活配置：所有配置存储在数据库中，支持动态修改
- ⏰ 定时任务：1分钟间隔自动爬取
- 📊 数据存储：MySQL数据库存储
- 📝 完整日志：详细的运行日志记录

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=stock_message
```

### 3. 初始化数据库

```bash
python -c "from database.connection import db_manager; db_manager.create_tables()"
```

### 4. 运行程序

```bash
python main.py
```

## 配置说明

### 爬虫配置

在 `spider_config` 表中配置要爬取的用户：

```sql
INSERT INTO spider_config (platform, user_id, username, auth_config, is_active) 
VALUES ('xueqiu', 'user123', '用户名', '{"token": "your_token"}', 1);
```

### 推送配置

在 `notification_config` 表中配置推送方式：

```sql
INSERT INTO notification_config (method, config, is_active) 
VALUES ('email', '{"smtp_server": "smtp.gmail.com", "username": "your_email", "password": "your_password", "to_emails": ["recipient@example.com"]}', 1);
```

## 项目结构

- `spider/`: 各平台爬虫实现
- `notification/`: 各种推送方式实现
- `database/`: 数据库模型和连接
- `utils/`: 工具模块
- `logs/`: 日志文件

## 许可证

MIT License