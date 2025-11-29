#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import asyncio
import threading
import yaml
import logging
import requests
import qrcode
from io import BytesIO
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from telegram import Update, BotCommand
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局配置
class Config:
    def __init__(self):
        self.bot_config = {}
        self.openapi_115 = None
        self.IMAGE_PATH = "/app/data/images"
        self.WEB_PORT = 12808
        
    def load_config(self):
        config_file = "/app/data/config.yaml"
        if not os.path.exists(config_file):
            # 生成默认配置
            default_config = {
                'bot_token': os.getenv('BOT_TOKEN', ''),
                'allowed_user': os.getenv('ALLOWED_USER', ''),
                '115_app_id': os.getenv('APP_115_APP_ID', ''),
                '115_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'web_username': os.getenv('WEB_USERNAME', 'root'),
                'web_password': os.getenv('WEB_PASSWORD', 'root')
            }
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f)
            logger.info("生成默认配置文件")
        
        with open(config_file, 'r') as f:
            self.bot_config = yaml.safe_load(f) or {}
        return True

config = Config()

# 115 API功能
class OpenAPI115:
    def __init__(self, app_id, user_agent):
        self.app_id = app_id
        self.user_agent = user_agent
        self.qrcode_token = None
        self.uid = None
        self.cookie = None

    def welcome_message(self):
        if self.uid:
            return ("✅ 115登录状态：已登录", f"🆔 用户ID：{self.uid}", "📅 登录时间：最近", "💫 状态：正常")
        return ("❌ 115登录状态：未登录", "⚠️ 请使用 /auth 命令进行扫码登录", "📱 需要使用115手机App扫码", "🔐 授权后即可使用下载功能")

    def get_qrcode(self):
        try:
            url = "https://passportapi.115.com/app/1.0/web/1.0/login/qrcode"
            headers = {"User-Agent": self.user_agent, "App-ID": self.app_id}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.qrcode_token = data.get("data", {}).get("qrcode")
                return self.qrcode_token
        except Exception as e:
            logger.error(f"获取二维码失败: {e}")
        return None

    def check_login(self):
        if not self.qrcode_token:
            return False
        try:
            url = f"https://passportapi.115.com/app/1.0/web/1.0/login/qrcode/status?qrcode={self.qrcode_token}"
            headers = {"User-Agent": self.user_agent, "App-ID": self.app_id}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("status") == 1:
                    self.uid = data["data"]["uid"]
                    self.cookie = data["data"].get("cookie")
                    return True
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
        return False

# Telegram Bot 功能
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        "🤖 欢迎使用 115 网盘机器人！\n\n"
        "可用命令：\n"
        "/start - 显示此帮助信息\n"
        "/auth - 115网盘扫码登录\n"
        "/status - 查看登录状态"
    )

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /auth 命令 - 115扫码登录"""
    if not config.openapi_115:
        config.openapi_115 = OpenAPI115(
            config.bot_config.get('115_app_id', ''),
            config.bot_config.get('115_user_agent', '')
        )
    
    qrcode_token = config.openapi_115.get_qrcode()
    if qrcode_token:
        # 生成二维码图片
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qrcode_token)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        await update.message.reply_photo(
            photo=bio,
            caption="📱 请使用115手机App扫描二维码登录\n\n"
                   "扫码后请使用 /status 命令检查登录状态"
        )
    else:
        await update.message.reply_text("❌ 获取二维码失败，请稍后重试")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /status 命令 - 查看登录状态"""
    if not config.openapi_115:
        config.openapi_115 = OpenAPI115(
            config.bot_config.get('115_app_id', ''),
            config.bot_config.get('115_user_agent', '')
        )
    
    # 检查登录状态
    if config.openapi_115.check_login():
        messages = config.openapi_115.welcome_message()
        await update.message.reply_text("\n".join(messages))
    else:
        messages = config.openapi_115.welcome_message()
        await update.message.reply_text("\n".join(messages))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息"""
    await update.message.reply_text(
        "🤖 我是 115 网盘机器人\n"
        "请使用命令与我交互：\n"
        "/start - 显示帮助\n"
        "/auth - 扫码登录\n"
        "/status - 查看状态"
    )

def setup_bot_handlers(application):
    """设置机器人处理器"""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def start_bot():
    """启动Telegram机器人"""
    token = config.bot_config.get('bot_token')
    if not token:
        logger.warning("未配置Bot Token，跳过机器人启动")
        return
    
    try:
        application = Application.builder().token(token).build()
        setup_bot_handlers(application)
        
        logger.info("🤖 Telegram机器人启动成功")
        await application.run_polling()
    except Exception as e:
        logger.error(f"机器人启动失败: {e}")

# Web界面
app = Flask(__name__)
app.secret_key = 'telegram-115bot-secret-key'

# HTML模板保持不变...
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>登录</title></head>
<body>
    <h1>Telegram-115Bot 登录</h1>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    <form method="POST">
        <input type="text" name="username" placeholder="用户名" required><br>
        <input type="password" name="password" placeholder="密码" required><br>
        <button type="submit">登录</button>
    </form>
</body>
</html>
'''

INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head><title>管理界面</title></head>
<body>
    <h1>Telegram-115Bot 管理界面</h1>
    <p>✅ Web界面运行正常！</p>
    <p>请在配置文件中设置Bot Token等参数。</p>
    <a href="/logout">退出</a>
</body>
</html>
'''

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template_string(INDEX_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == config.bot_config.get('web_username', 'root') and password == config.bot_config.get('web_password', 'root'):
            session['logged_in'] = True
            return redirect('/')
        return render_template_string(LOGIN_HTML, error='用户名或密码错误')
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

def start_web_server():
    app.run(host='0.0.0.0', port=config.WEB_PORT, debug=False)

# 主函数
async def main_async():
    print("🚀 启动 Telegram-115Bot...")
    
    # 加载配置
    if not config.load_config():
        logger.error("配置加载失败")
        return
    
    # 启动Web界面（在单独线程中）
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    print(f"🌐 Web管理界面: http://0.0.0.0:{config.WEB_PORT}")
    print("👤 用户名: root")
    print("🔑 密码: root")
    
    # 检查并启动Telegram Bot
    token = config.bot_config.get('bot_token')
    if not token:
        print("⚠️  Bot Token未配置，只运行Web界面")
        # 保持程序运行
        while True:
            await asyncio.sleep(10)
    else:
        print("✅ Bot Token已配置，启动Telegram Bot...")
        await start_bot()

def main():
    """主入口函数"""
    asyncio.run(main_async())

if __name__ == '__main__':
    main()