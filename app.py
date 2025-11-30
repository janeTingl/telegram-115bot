#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import threading
import yaml
import logging
from datetime import datetime

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
                'web_password': os.getenv('WEB_PASSWORD', 'root'),
                'http_proxy': os.getenv('HTTP_PROXY', ''),
                'no_proxy': os.getenv('NO_PROXY', '')
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
            import requests
            url = "https://passportapi.115.com/app/1.0/web/1.0/login/qrcode"
            headers = {"User-Agent": self.user_agent, "App-ID": self.app_id}
            
            # 设置代理
            proxies = {}
            if config.bot_config.get('http_proxy'):
                proxies = {
                    'http': config.bot_config.get('http_proxy'),
                    'https': config.bot_config.get('http_proxy')
                }
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
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
            import requests
            url = f"https://passportapi.115.com/app/1.0/web/1.0/login/qrcode/status?qrcode={self.qrcode_token}"
            headers = {"User-Agent": self.user_agent, "App-ID": self.app_id}
            
            proxies = {}
            if config.bot_config.get('http_proxy'):
                proxies = {
                    'http': config.bot_config.get('http_proxy'),
                    'https': config.bot_config.get('http_proxy')
                }
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("status") == 1:
                    self.uid = data["data"]["uid"]
                    self.cookie = data["data"].get("cookie")
                    return True
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
        return False

# 初始化115 API
def init_115_api():
    app_id = config.bot_config.get('115_app_id')
    if app_id:
        config.openapi_115 = OpenAPI115(
            app_id,
            config.bot_config.get('115_user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        )
        logger.info("115 API初始化成功")
    else:
        logger.warning("115 App ID未配置，115功能不可用")

# Web界面
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

# 安全设置
MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME = 3600
AUTO_LOGOUT_TIME = 15 * 60

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        
        last_active = session.get('last_active', 0)
        if time.time() - last_active > AUTO_LOGOUT_TIME:
            session.clear()
            return redirect(url_for('login'))
        
        session['last_active'] = time.time()
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    import time
    if 'locked_until' in session:
        if time.time() < session['locked_until']:
            remaining = int((session['locked_until'] - time.time())/60) + 1
            error = f"登录被锁定，请 {remaining} 分钟后重试"
            return render_template('login.html', error=error)
        else:
            session.pop('locked_until', None)
            session.pop('login_attempts', None)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        web_username = config.bot_config.get('web_username', 'root')
        web_password = config.bot_config.get('web_password', 'root')
        
        session.setdefault('login_attempts', 0)

        if username == web_username and password == web_password:
            session['logged_in'] = True
            session['last_active'] = time.time()
            session.pop('login_attempts', None)
            return redirect(url_for('index'))
        else:
            session['login_attempts'] += 1
            remaining = MAX_LOGIN_ATTEMPTS - session['login_attempts']
            error = f"用户名或密码错误！剩余尝试次数：{remaining}"
            if session['login_attempts'] >= MAX_LOGIN_ATTEMPTS:
                session['locked_until'] = time.time() + LOCK_TIME
                error = "登录失败次数达到上限，账号已锁定1小时"
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# API路由
@app.route('/api/status')
@login_required
def api_status():
    status = {
        'bot_running': config.bot_application is not None,
        '115_logged_in': config.openapi_115.uid is not None if config.openapi_115 else False,
        '115_uid': config.openapi_115.uid if config.openapi_115 else None,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(status)

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    config_file = '/app/data/config.yaml'
    
    if request.method == 'POST':
        try:
            new_config = request.json
            # 合并现有配置
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    existing_config = yaml.safe_load(f) or {}
                existing_config.update(new_config)
                new_config = existing_config
            
            with open(config_file, 'w') as f:
                yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False)
            
            # 重新加载配置
            config.load_config()
            # 重新初始化115 API
            init_115_api()
            
            return jsonify({'success': True, 'message': '配置已更新'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    else:
        try:
            return jsonify(config.bot_config)
        except:
            return jsonify({})

@app.route('/api/proxy/test', methods=['POST'])
@login_required
def api_test_proxy():
    import requests
    import time
    try:
        proxy_url = request.json.get('proxy_url', '').strip()
        if not proxy_url:
            return jsonify({'success': False, 'message': '请输入代理地址', 'latency': 0})
        
        proxies = {'http': proxy_url, 'https': proxy_url}
        start_time = time.time()
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        latency = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': f'代理连接成功！响应时间: {latency}ms',
                            'latency': latency, 'ip_info': response.json()})
        else:
            return jsonify({'success': False, 'message': f'连接失败，状态码: {response.status_code}', 'latency': latency})
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': '代理连接超时', 'latency': 0})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': '代理连接失败，请检查地址和端口', 'latency': 0})
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试失败: {str(e)}', 'latency': 0})

# Telegram Bot功能（使用v20.x）
async def start_bot():
    token = config.bot_config.get('bot_token')
    if not token:
        logger.warning("未配置Bot Token，跳过机器人启动")
        return None
    
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        from telegram import Update
        
        # Bot命令处理函数
        async def start_command(update: Update, context):
            await update.message.reply_text("🤖 欢迎使用 115 网盘机器人！\n\n可用命令：\n/start - 显示帮助\n/auth - 115扫码登录\n/status - 查看状态")
        
        async def auth_command(update: Update, context):
            if not config.openapi_115:
                await update.message.reply_text("❌ 115 API未初始化，请先配置115 App ID")
                return
            
            qrcode_token = config.openapi_115.get_qrcode()
            if qrcode_token:
                import qrcode
                from io import BytesIO
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
                await update.message.reply_text("❌ 获取二维码失败，请检查网络或代理设置")
        
        async def status_command(update: Update, context):
            if not config.openapi_115:
                await update.message.reply_text("❌ 115 API未初始化")
                return
            
            is_logged_in = config.openapi_115.check_login()
            messages = config.openapi_115.welcome_message()
            status_text = "\n".join(messages)
            
            if is_logged_in:
                status_text += "\n\n✅ 登录成功！现在可以使用下载功能"
            else:
                status_text += "\n\n⚠️ 尚未登录或登录已过期，请使用 /auth 重新登录"
            
            await update.message.reply_text(status_text)
        
        # 创建Bot应用
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("auth", auth_command))
        application.add_handler(CommandHandler("status", status_command))
        
        logger.info("🤖 Telegram机器人启动成功")
        return application
        
    except Exception as e:
        logger.error(f"机器人启动失败: {e}")
        return None

async def run_bot():
    application = await start_bot()
    if application:
        config.bot_application = application
        try:
            await application.run_polling()
        except Exception as e:
            logger.error(f"机器人运行错误: {e}")
        finally:
            config.bot_application = None

def start_web_server():
    """启动Web服务器"""
    logger.info(f"🌐 启动Web服务器，端口: {config.WEB_PORT}")
    app.run(host='0.0.0.0', port=config.WEB_PORT, debug=False, use_reloader=False)

async def main():
    print("🚀 启动 Telegram-115Bot...")
    
    # 加载配置
    if not config.load_config():
        logger.error("配置加载失败")
        return
    
    # 初始化115 API
    init_115_api()
    
    # 启动Web界面
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    print(f"🌐 Web管理界面: http://0.0.0.0:{config.WEB_PORT}")
    
    # 检查并启动Telegram Bot
    token = config.bot_config.get('bot_token')
    if not token:
        print("⚠️  Bot Token未配置，只运行Web界面")
        # 保持程序运行
        while True:
            await asyncio.sleep(10)
    else:
        print("✅ Bot Token已配置，启动Telegram Bot...")
        await run_bot()

if __name__ == '__main__':
    import time
    asyncio.run(main())