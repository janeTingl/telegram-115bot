from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import logging
import requests
import time
import yaml
from datetime import datetime

template_dir = '/app/templates'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'telegram-115bot-secret-key-2024'
WEB_PORT = 12808

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function  

@app.route('/')
def index():
    """根路径重定向到登录或主页"""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        web_username = os.getenv('WEB_USERNAME', 'root')
        web_password = os.getenv('WEB_PASSWORD', 'root')
        
        if username == web_username and password == web_password:
            session['logged_in'] = True
            session['username'] = username
            logger.info(f"用户 {username} 登录成功")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"登录失败: 用户名={username}")
            return render_template('login.html', error='用户名或密码错误')
    
    # 如果已登录，重定向到仪表板
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """主仪表板"""
    return render_template('index.html')

@app.route('/api/status')
@login_required
def api_status():
    """获取系统状态"""
    try:
        config_file = '/app/data/config.yaml'
        config_exists = os.path.exists(config_file)
        
        status = {
            'bot_running': False,  # 默认不运行，直到配置完成
            '115_logged_in': False,
            '115_uid': None,
            'config_exists': config_exists,
            'timestamp': datetime.now().isoformat(),
            'web_interface': '正常运行'
        }
        
        if config_exists:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                status['bot_configured'] = bool(config.get('bot_token'))
                status['user_configured'] = bool(config.get('allowed_user'))
                status['115_configured'] = bool(config.get('115_app_id'))
                
                # 如果所有配置都完成，标记Bot为运行中
                if status['bot_configured'] and status['user_configured'] and status['115_configured']:
                    status['bot_running'] = True
                    
            except Exception as e:
                status['config_error'] = str(e)
                
    except Exception as e:
        status = {'bot_running': False, '115_logged_in': False, 'error': str(e)}
    
    return jsonify(status)

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    """配置管理 - 永不停止容器"""
    config_file = '/app/data/config.yaml'
    
    if request.method == 'POST':
        try:
            new_config = request.json
            logger.info(f"收到配置更新")
            
            # 确保数据目录存在
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # 读取现有配置
            existing_config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = yaml.safe_load(f) or {}
            
            # 合并配置
            merged_config = {**existing_config, **new_config}
            merged_config['115_user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            
            # 保存配置
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(merged_config, f, allow_unicode=True, default_flow_style=False)
            
            logger.info("配置保存成功")
            
            return jsonify({
                'success': True, 
                'message': '配置保存成功！',
                'action': 'continue'  # 总是继续运行
            })
            
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
            return jsonify({
                'success': False, 
                'message': f'保存失败: {str(e)}',
                'action': 'continue'
            })
    
    else:
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}
            return jsonify(config)
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/api/proxy/test', methods=['POST'])
@login_required
def api_test_proxy():
    """测试代理连接"""
    try:
        proxy_url = request.json.get('proxy_url', '').strip()
        
        if not proxy_url:
            return jsonify({'success': False, 'message': '请输入代理地址', 'latency': 0})
        
        proxies = {'http': proxy_url, 'https': proxy_url}
        
        start_time = time.time()
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        latency = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            return jsonify({
                'success': True, 
                'message': f'代理连接成功！响应时间: {latency}ms',
                'latency': latency,
                'ip_info': response.json()
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'连接失败，状态码: {response.status_code}',
                'latency': latency
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试失败: {str(e)}', 'latency': 0})

@app.route('/logout')
def logout():
    """退出登录"""
    username = session.get('username', '未知用户')
    session.clear()
    logger.info(f"用户 {username} 退出登录")
    return redirect(url_for('login'))

if __name__ == '__main__':
    logger.info(f"启动Web服务器，端口: {WEB_PORT}")
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False)
