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

# 只使用v20.x版本
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters
from flask import Flask, render_template_string, request, session, redirect, url_for

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
        self.bot_application = None
        
    def load_config(self):
        config_file = "/app/data/config.yaml"
        if not os.path.exists(config_file):
            default_config = {
                'bot_token': os.getenv('BOT_TOKEN', ''),
                'allowed_users': os.getenv('ALLOWED_USERS', '').split(','),
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

def is_user_allowed(user_id):
    """检查用户是否有权限使用机器人"""
    allowed_users = config.bot_config.get('allowed_users', [])
    if not allowed_users:
        return True
    return str(user_id) in [user.strip() for user in allowed_users if user.strip()]

# Telegram Bot 功能
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ 您没有权限使用此机器人")
        return
    
    welcome_text = (
        "🤖 欢迎使用 115 网盘机器人！\n\n"
        "可用命令：\n"
        "/start - 显示此帮助信息\n"
        "/auth - 115网盘扫码登录\n"
        "/status - 查看登录状态\n\n"
        f"🆔 您的用户ID: {user_id}"
    )
    await update.message.reply_text(welcome_text)

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.id):
        await update.message.reply_text("❌ 您没有权限使用此机器人")
        return
    
    if not config.openapi_115:
        app_id = config.bot_config.get('115_app_id')
        if not app_id:
            await update.message.reply_text("❌ 115 App ID 未配置，请通过Web界面配置")
            return
        config.openapi_115 = OpenAPI115(
            app_id,
            config.bot_config.get('115_user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        )
    
    qrcode_token = config.openapi_115.get_qrcode()
    if qrcode_token:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qrcode_token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        await update.message.reply_photo(
            photo=bio,
            caption="📱 请使用115手机App扫描二维码登录\n\n扫码后请使用 /status 命令检查登录状态"
        )
    else:
        await update.message.reply_text("❌ 获取二维码失败，请检查115 App ID配置或稍后重试")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.id):
        await update.message.reply_text("❌ 您没有权限使用此机器人")
        return
    
    if not config.openapi_115:
        await update.message.reply_text("❌ 115 API未初始化，请先使用 /auth 命令")
        return
    
    is_logged_in = config.openapi_115.check_login()
    messages = config.openapi_115.welcome_message()
    
    status_text = "\n".join(messages)
    if is_logged_in:
        status_text += "\n\n✅ 登录成功！现在可以使用下载功能"
    else:
        status_text += "\n\n⚠️ 尚未登录或登录已过期，请使用 /auth 重新登录"
    
    await update.message.reply_text(status_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_user_allowed(update.effective_user.id):
        await update.message.reply_text("❌ 您没有权限使用此机器人")
        return
    
    await update.message.reply_text(
        "🤖 我是 115 网盘机器人\n\n请使用以下命令：\n/start - 显示帮助信息\n/auth - 115网盘扫码登录\n/status - 查看登录状态"
    )

async def start_bot():
    token = config.bot_config.get('bot_token')
    if not token:
        logger.warning("未配置Bot Token，跳过机器人启动")
        return None
    
    try:
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("auth", auth_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("🤖 Telegram机器人启动成功")
        return application
    except Exception as e:
        logger.error(f"机器人启动失败: {e}")
        return None

# Web界面
app = Flask(__name__)
app.secret_key = 'telegram-115bot-secret-key'

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>登录</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
        h1 { text-align: center; color: #333; }
        form { display: flex; flex-direction: column; }
        input { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007cba; color: white; padding: 10px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #005a87; }
        .error { color: red; text-align: center; }
    </style>
</head>
<body>
    <h1>Telegram-115Bot 登录</h1>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <form method="POST">
        <input type="text" name="username" placeholder="用户名" required>
        <input type="password" name="password" placeholder="密码" required>
        <button type="submit">登录</button>
    </form>
</body>
</html>
'''

INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>管理界面</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }
        .status { background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .config-item { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 4px; }
        a { color: #007cba; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Telegram-115Bot 管理界面</h1>
    
    <div class="status">
        <h3>✅ 系统状态</h3>
        <p>Web界面运行正常！</p>
        <p>当前时间: <span id="currentTime"></span></p>
    </div>

    <div class="config-item">
        <h3>📋 配置信息</h3>
        <p><strong>Bot Token:</strong> {{ '已配置' if config.bot_config.get('bot_token') else '未配置' }}</p>
        <p><strong>115 App ID:</strong> {{ '已配置' if config.bot_config.get('115_app_id') else '未配置' }}</p>
        <p><strong>允许用户数:</strong> {{ config.bot_config.get('allowed_users', [])|length }}</p>
        <p><strong>115登录状态:</strong> {{ '已登录' if config.openapi_115 and config.openapi_115.uid else '未登录' }}</p>
    </div>

    <div class="config-item">
        <h3>🔧 操作指南</h3>
        <ol>
            <li>在Telegram中搜索您的机器人</li>
            <li>使用 <code>/start</code> 命令开始使用</li>
            <li>使用 <code>/auth</code> 命令进行115登录</li>
            <li>使用 <code>/status</code> 命令查看状态</li>
        </ol>
    </div>

    <p><a href="/logout">退出登录</a></p>

    <script>
        // 显示当前时间
        function updateTime() {
            document.getElementById('currentTime').textContent = new Date().toLocaleString();
        }
        updateTime();
        setInterval(updateTime, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template_string(INDEX_HTML, config=config)

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
    """在单独线程中启动Flask服务器"""
    logger.info(f"🌐 启动Web服务器，端口: {config.WEB_PORT}")
    app.run(host='0.0.0.0', port=config.WEB_PORT, debug=False, use_reloader=False)

async def main():
    print("🚀 启动 Telegram-115Bot...")
    
    # 加载配置
    if not config.load_config():
        logger.error("配置加载失败")
        return
    
    # 启动Web界面
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    print(f"🌐 Web管理界面: http://0.0.0.0:{config.WEB_PORT}")
    
    # 检查Bot Token
    token = config.bot_config.get('bot_token')
    if not token:
        print("⚠️  Bot Token未配置，只运行Web界面")
        # 保持程序运行
        while True:
            await asyncio.sleep(10)
    else:
        print("✅ Bot Token已配置，启动Telegram Bot...")
        application = await start_bot()
        if application:
            await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())