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

# 根据版本选择导入方式
try:
    # 尝试导入 v20.x 版本
    from telegram import Update
    from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters
    TELEGRAM_VERSION = 20
    print("✅ 使用 python-telegram-bot v20.x")
except ImportError:
    # 回退到 v13.x 版本
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
    TELEGRAM_VERSION = 13
    print("✅ 使用 python-telegram-bot v13.x")

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

# 115 API功能 (保持不变)
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

# 根据版本定义不同的机器人函数
if TELEGRAM_VERSION == 20:
    # v20.x 版本的机器人函数
    async def start_command(update: Update, context):
        await update.message.reply_text("🤖 欢迎使用 115 网盘机器人！")
    
    async def auth_command(update: Update, context):
        if not config.openapi_115:
            app_id = config.bot_config.get('115_app_id')
            if not app_id:
                await update.message.reply_text("❌ 115 App ID 未配置")
                return
            config.openapi_115 = OpenAPI115(app_id, config.bot_config.get('115_user_agent'))
        
        qrcode_token = config.openapi_115.get_qrcode()
        if qrcode_token:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qrcode_token)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            bio = BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            await update.message.reply_photo(photo=bio, caption="📱 请使用115手机App扫描二维码登录")
        else:
            await update.message.reply_text("❌ 获取二维码失败")
    
    async def status_command(update: Update, context):
        if not config.openapi_115:
            await update.message.reply_text("❌ 115 API未初始化")
            return
        
        if config.openapi_115.check_login():
            messages = config.openapi_115.welcome_message()
            await update.message.reply_text("\n".join(messages))
        else:
            messages = config.openapi_115.welcome_message()
            await update.message.reply_text("\n".join(messages))
    
    async def handle_message(update: Update, context):
        await update.message.reply_text("请使用命令：/start, /auth, /status")

else:
    # v13.x 版本的机器人函数
    def start_command(update: Update, context):
        update.message.reply_text("🤖 欢迎使用 115 网盘机器人！")
    
    def auth_command(update: Update, context):
        if not config.openapi_115:
            app_id = config.bot_config.get('115_app_id')
            if not app_id:
                update.message.reply_text("❌ 115 App ID 未配置")
                return
            config.openapi_115 = OpenAPI115(app_id, config.bot_config.get('115_user_agent'))
        
        qrcode_token = config.openapi_115.get_qrcode()
        if qrcode_token:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qrcode_token)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            bio = BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            update.message.reply_photo(photo=bio, caption="📱 请使用115手机App扫描二维码登录")
        else:
            update.message.reply_text("❌ 获取二维码失败")
    
    def status_command(update: Update, context):
        if not config.openapi_115:
            update.message.reply_text("❌ 115 API未初始化")
            return
        
        if config.openapi_115.check_login():
            messages = config.openapi_115.welcome_message()
            update.message.reply_text("\n".join(messages))
        else:
            messages = config.openapi_115.welcome_message()
            update.message.reply_text("\n".join(messages))
    
    def handle_message(update: Update, context):
        update.message.reply_text("请使用命令：/start, /auth, /status")

# Web界面 (保持不变)
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'telegram-115bot-secret-key'

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

def start_bot():
    """启动Telegram机器人"""
    token = config.bot_config.get('bot_token')
    if not token:
        logger.warning("未配置Bot Token，跳过机器人启动")
        return
    
    try:
        if TELEGRAM_VERSION == 20:
            # v20.x 启动方式
            application = Application.builder().token(token).build()
            application.add_handler(CommandHandler("start", start_command))
            application.add_handler(CommandHandler("auth", auth_command))
            application.add_handler(CommandHandler("status", status_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            application.run_polling()
        else:
            # v13.x 启动方式
            updater = Updater(token, use_context=True)
            dispatcher = updater.dispatcher
            dispatcher.add_handler(CommandHandler("start", start_command))
            dispatcher.add_handler(CommandHandler("auth", auth_command))
            dispatcher.add_handler(CommandHandler("status", status_command))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            updater.start_polling()
            updater.idle()
            
    except Exception as e:
        logger.error(f"机器人启动失败: {e}")

def main():
    print("🚀 启动 Telegram-115Bot...")
    
    # 加载配置
    if not config.load_config():
        logger.error("配置加载失败")
        return
    
    # 启动Web界面
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    print(f"🌐 Web管理界面: http://0.0.0.0:{config.WEB_PORT}")
    print("📝 请通过Web界面配置必要参数")
    
    # 检查Bot Token
    token = config.bot_config.get('bot_token')
    if not token:
        print("⚠️  Bot Token未配置，只运行Web界面")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("程序退出")
    else:
        print("✅ Bot Token已配置，启动Telegram Bot...")
        start_bot()

if __name__ == '__main__':
    main()