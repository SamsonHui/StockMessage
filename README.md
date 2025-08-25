# 股票消息爬虫系统

一个功能完整的股票相关网站用户动态爬取和实时推送系统，支持多平台爬虫、多种推送方式和Web管理界面。

## 🌟 功能特性

### 🕷️ 多平台爬虫支持
- **雪球网** - 支持用户动态爬取
- **新浪微博** - 微博内容获取
- **东方财富** - 财经资讯爬取
- **淘股吧** - 股吧讨论内容
- **推特** - 国际财经动态

### 📱 多种推送方式
- **邮件推送** - SMTP邮件通知，支持HTML格式和图片附件
- **钉钉机器人** - 企业钉钉群消息推送
- **飞书机器人** - 飞书群组消息通知
- **企业微信** - 企业微信应用消息
- **微信公众号** - 微信公众号模板消息

### 🖥️ Web管理界面
- **仪表板** - 系统运行状态和统计信息
- **爬虫配置** - 可视化配置爬虫参数和定时任务
- **通知配置** - 管理各种推送方式的配置
- **消息展示** - 查看爬取到的消息内容，支持分页和筛选
- **系统日志** - 实时查看系统运行日志

### 🖼️ 图片缓存功能
- **自动缓存** - 自动下载并缓存消息中的图片
- **格式支持** - 支持jpg、jpeg、png、gif、webp格式
- **邮件嵌入** - 邮件推送时将图片作为附件嵌入
- **过期清理** - 自动清理过期的缓存文件

### ⚙️ 灵活配置
- **数据库存储** - 所有配置存储在MySQL数据库中
- **动态修改** - 支持通过Web界面动态修改配置
- **定时任务** - 支持间隔和Cron表达式两种定时方式
- **多对多关联** - 爬虫配置和通知配置支持多对多关联

### 📊 数据管理
- **MySQL存储** - 使用MySQL数据库存储所有数据
- **SQLAlchemy ORM** - 使用ORM进行数据库操作
- **数据去重** - 自动检测和去重重复的帖子
- **完整日志** - 详细的运行日志记录

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+
- Chrome浏览器（用于Selenium爬虫）
- ChromeDriver

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

#### 方式一：使用配置文件（推荐）

编辑 `config.yaml` 文件：

```yaml
# 数据库配置
database:
  host: localhost
  port: 3306
  user: root
  password: "your_password"
  database: stock_message

# 爬虫配置
spider:
  interval: 60
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  max_retry_times: 3
  request_timeout: 30

# 图片缓存配置
image_cache:
  enabled: true
  cache_dir: "static/images/cache"
  expire_hours: 24
  max_size_mb: 500
  allowed_formats: ["jpg", "jpeg", "png", "gif", "webp"]
  max_file_size_mb: 10

# 日志配置
logging:
  level: INFO
  file: logs/stock_message.log
```

#### 方式二：使用环境变量

创建 `.env` 文件：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=stock_message
```

### 4. 初始化数据库

```bash
# 创建数据库表
python -c "from database.connection import db_manager; db_manager.create_tables()"

# 或者使用SQL文件
mysql -u root -p stock_message < database/schema.sql
```

### 5. 运行方式

#### 命令行模式（仅爬虫）

```bash
python main.py
```

#### Web管理界面模式（推荐）

```bash
python web_app.py
```

然后访问 `http://localhost:5001` 进入Web管理界面。

## 📋 配置说明

### 爬虫配置

通过Web界面或直接在数据库中配置：

```sql
INSERT INTO spider_config (platform, user_id, username, auth_config, is_active, schedule_enabled, schedule_interval) 
VALUES ('xueqiu', 'user123', '用户名', '{"token": "your_token"}', 1, 1, 3600);
```

### 推送配置

#### 邮件配置

```sql
INSERT INTO notification_config (method, config, is_active) 
VALUES ('email', '{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "your_email@gmail.com",
  "password": "your_app_password",
  "to_emails": ["recipient@example.com"],
  "use_tls": true
}', 1);
```

#### 钉钉机器人配置

```sql
INSERT INTO notification_config (method, config, is_active) 
VALUES ('dingtalk', '{
  "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=your_token",
  "secret": "your_secret"
}', 1);
```

## 🏗️ 项目结构

- `spider/`: 各平台爬虫实现
- `notification/`: 各种推送方式实现
- `database/`: 数据库模型和连接
- `utils/`: 工具模块
- `logs/`: 日志文件

## 许可证

MIT License