from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import logging
import requests
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 配置常量
WEB_PORT = 12808

# 简单的认证装饰器
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    """主面板"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 从环境变量或配置获取认证信息
        web_username = os.getenv('WEB_USERNAME', 'admin')
        web_password = os.getenv('WEB_PASSWORD', 'admin123')
        
        if username == web_username and password == web_password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/api/status')
@login_required
def api_status():
    """获取系统状态"""
    try:
        import init
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
    """配置管理"""
    config_file = '/app/data/config.yaml'
    
    if request.method == 'POST':
        try:
            import yaml
            new_config = request.json
            
            # 保存配置到文件
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
    """测试代理连接"""
    try:
        proxy_url = request.json.get('proxy_url', '').strip()
        
        if not proxy_url:
            return jsonify({'success': False, 'message': '请输入代理地址', 'latency': 0})
        
        # 设置代理
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # 测试连接
        start_time = time.time()
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies=proxies, 
            timeout=10
        )
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
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': '代理连接超时', 'latency': 0})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': '代理连接失败，请检查地址和端口', 'latency': 0})
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试失败: {str(e)}', 'latency': 0})

@app.route('/api/tasks')
@login_required
def api_tasks():
    """获取任务列表"""
    tasks = [
        {'id': 1, 'name': '示例任务', 'status': 'completed', 'progress': 100},
        {'id': 2, 'name': '下载任务', 'status': 'downloading', 'progress': 75},
    ]
    return jsonify(tasks)

@app.route('/logout')
def logout():
    """退出登录"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False)