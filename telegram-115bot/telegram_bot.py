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

# Web界面
app = Flask(__name__)
app.secret_key = 'telegram-115bot-secret-key'

# 简单的HTML模板
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
        # 保持程序运行
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("程序退出")
    else:
        print("✅ Bot Token已配置，准备启动Telegram Bot...")
        # 这里可以添加Telegram Bot的启动代码
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("程序退出")

if __name__ == '__main__':
    main()
