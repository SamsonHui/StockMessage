-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_message CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE stock_message;

-- 爬虫配置表
CREATE TABLE IF NOT EXISTS spider_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL COMMENT '平台名称',
    user_id VARCHAR(100) NOT NULL COMMENT '用户ID',
    username VARCHAR(100) COMMENT '用户名',
    auth_config JSON COMMENT '认证配置',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_platform_user (platform, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 推送配置表
CREATE TABLE IF NOT EXISTS notification_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method VARCHAR(50) NOT NULL COMMENT '推送方式',
    config JSON NOT NULL COMMENT '推送配置',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 帖子数据表
CREATE TABLE IF NOT EXISTS post_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL COMMENT '平台名称',
    user_id VARCHAR(100) NOT NULL COMMENT '用户ID',
    post_id VARCHAR(200) NOT NULL COMMENT '帖子ID',
    content TEXT COMMENT '帖子内容',
    post_time DATETIME COMMENT '发帖时间',
    is_sent BOOLEAN DEFAULT FALSE COMMENT '是否已推送',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_platform_post (platform, post_id),
    INDEX idx_is_sent (is_sent),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 系统日志表
CREATE TABLE IF NOT EXISTS system_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL COMMENT '日志级别',
    message TEXT NOT NULL COMMENT '日志消息',
    module VARCHAR(100) COMMENT '模块名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- 爬虫配置和通知配置的多对多关联表
CREATE TABLE IF NOT EXISTS spider_notification_association (
    spider_config_id INT NOT NULL,
    notification_config_id INT NOT NULL,
    PRIMARY KEY (spider_config_id, notification_config_id),
    FOREIGN KEY (spider_config_id) REFERENCES spider_config(id) ON DELETE CASCADE,
    FOREIGN KEY (notification_config_id) REFERENCES notification_config(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;