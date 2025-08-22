import smtplib
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
from .base_notifier import BaseNotifier
from config import config

class EmailNotifier(BaseNotifier):
    """邮件推送"""
    
    def send_message(self, title: str, content: str, **kwargs) -> bool:
        """发送邮件"""
        try:
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port', 587)
            username = self.config.get('username')
            password = self.config.get('password')
            to_emails = self.config.get('to_emails', [])
            
            if not all([smtp_server, username, password, to_emails]):
                logger.error("邮件配置不完整")
                return False
            
            # 创建邮件
            msg = MIMEMultipart('related')
            msg['From'] = username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = title
            
            # 处理内容中的图片
            processed_content, image_attachments = self._process_images_in_content(content)
            
            # 创建邮件正文容器
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            
            # 添加纯文本版本（移除HTML标签）
            text_content = self._html_to_text(processed_content)
            msg_alternative.attach(MIMEText(text_content, 'plain', 'utf-8'))
            
            # 添加HTML版本
            html_content = self._format_html_content(processed_content)
            msg_alternative.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 添加图片附件
            for image_path, cid in image_attachments:
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                    
                    # 根据文件扩展名确定MIME类型
                    file_ext = Path(image_path).suffix.lower()
                    if file_ext in ['.jpg', '.jpeg']:
                        img = MIMEImage(img_data, 'jpeg')
                    elif file_ext == '.png':
                        img = MIMEImage(img_data, 'png')
                    elif file_ext == '.gif':
                        img = MIMEImage(img_data, 'gif')
                    elif file_ext == '.webp':
                        img = MIMEBase('image', 'webp')
                        img.set_payload(img_data)
                        encoders.encode_base64(img)
                    else:
                        continue
                    
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                    msg.attach(img)
            
            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功: {title}，包含 {len(image_attachments)} 张图片")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    def _process_images_in_content(self, content: str) -> tuple[str, List[tuple[str, str]]]:
        """处理内容中的图片，返回处理后的内容和图片附件列表"""
        if not content:
            return content, []
        
        image_attachments = []
        processed_content = content
        
        # 匹配本地缓存图片链接的正则表达式
        cache_img_pattern = r'<a href="(/static/images/cache/[^"]+)"[^>]*>查看图片</a>'
        direct_img_pattern = r'/static/images/cache/([^\s<>"\'\']+)'
        
        # 处理链接格式的图片
        matches = re.finditer(cache_img_pattern, content)
        for i, match in enumerate(matches):
            img_url = match.group(1)
            img_path = os.path.join(config.BASE_DIR, img_url.lstrip('/'))
            
            if os.path.exists(img_path):
                cid = f"image_{i+1}"
                image_attachments.append((img_path, cid))
                
                # 替换为HTML img标签
                img_filename = os.path.basename(img_path)
                img_tag = f'<img src="cid:{cid}" alt="{img_filename}" style="max-width: 100%; height: auto; border-radius: 4px; margin: 10px 0;">'
                processed_content = processed_content.replace(match.group(0), img_tag)
        
        # 处理直接的图片路径
        direct_matches = re.finditer(direct_img_pattern, processed_content)
        for i, match in enumerate(direct_matches, len(image_attachments)):
            img_url = match.group(0)
            img_path = os.path.join(config.BASE_DIR, img_url.lstrip('/'))
            
            if os.path.exists(img_path) and img_path not in [att[0] for att in image_attachments]:
                cid = f"image_{i+1}"
                image_attachments.append((img_path, cid))
                
                # 替换为HTML img标签
                img_filename = os.path.basename(img_path)
                img_tag = f'<img src="cid:{cid}" alt="{img_filename}" style="max-width: 100%; height: auto; border-radius: 4px; margin: 10px 0;">'
                processed_content = processed_content.replace(img_url, img_tag)
        
        return processed_content, image_attachments
    
    def _html_to_text(self, html_content: str) -> str:
        """将HTML内容转换为纯文本"""
        # 简单的HTML到文本转换
        import re
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # 解码HTML实体
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        text = text.replace('&nbsp;', ' ').replace('&quot;', '"')
        
        # 清理多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _format_html_content(self, content: str) -> str:
        """格式化HTML邮件内容"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>股票消息通知</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .content {{
                    margin-bottom: 20px;
                }}
                .footer {{
                    border-top: 1px solid #eee;
                    padding-top: 15px;
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                    margin: 10px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="color: #007bff; margin: 0;">📈 股票消息通知</h2>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>此邮件由股票消息爬虫系统自动发送</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template