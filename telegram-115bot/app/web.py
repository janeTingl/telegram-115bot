from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import time
from datetime import datetime

import init  # 调用你的 init.py

app = Flask(__name__)
app.secret_key = os.urandom(24)

WEB_PORT = 12808

# 登录限制设置
MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME = 3600  # 登录失败锁定时间（秒）
AUTO_LOGOUT_TIME = 15 * 60  # 15分钟无操作自动退出

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查登录状态
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        # 检查无操作自动退出
        last_active = session.get('last_active', 0)
        if time.time() - last_active > AUTO_LOGOUT_TIME:
            session.pop('logged_in', None)
            session.pop('last_active', None)
            return redirect(url_for('login'))

        # 更新最后操作时间
        session['last_active'] = time.time()
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'locked_until' in session:
        if time.time() < session['locked_until']:
            remaining = int((session['locked_until'] - time.time())/60) + 1
            error = f"登录被锁定，请 {remaining} 分钟后重试"
            return render_template('login.html', error=error)
        else:
            # 解锁
            session.pop('locked_until')
            session.pop('login_attempts', None)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        web_username = os.getenv('WEB_USERNAME', 'admin')
        web_password = os.getenv('WEB_PASSWORD', 'admin123')
        
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
                error = "登录失败次数达到上限，服务已锁定，需要重启才能登录"
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('last_active', None)
    return redirect(url_for('login'))

# -------------------------- API --------------------------

@app.route('/api/status')
@login_required
def api_status():
    try:
        status = {
            'bot_running': True,
            '115_logged_in': init.openapi_115.uid is not None if init.openapi_115 else False,
            '115_uid': init.openapi_115.uid if init.openapi_115 else None,
            'timestamp': datetime.now().isoformat()
        }
    except:
        status = {'bot_running': False, '115_logged_in': False}
    
    return jsonify(status)

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    config_file = '/app/data/config.yaml'
    
    if request.method == 'POST':
        try:
            import yaml
            new_config = request.json
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False)
            return jsonify({'success': True, 'message': '配置已更新'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    else:
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            return jsonify(config)
        except:
            return jsonify({})

@app.route('/api/proxy/test', methods=['POST'])
@login_required
def api_test_proxy():
    import requests
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

@app.route('/api/tasks')
@login_required
def api_tasks():
    tasks = [
        {'id': 1, 'name': '示例任务', 'status': 'completed', 'progress': 100},
        {'id': 2, 'name': '下载任务', 'status': 'downloading', 'progress': 75},
    ]
    return jsonify(tasks)

# -------------------------- 运行 --------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False)