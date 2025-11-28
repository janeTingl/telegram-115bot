# -*- coding: utf-8 -*-

import yaml
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局变量
bot_config = {}
openapi_115 = None
IMAGE_PATH = "/app/data/images"

class OpenAPI115:
    def __init__(self, app_id, user_agent):
        self.app_id = app_id
        self.user_agent = user_agent
        self.qrcode_token = None
        self.uid = None
        self.cookie = None

    def welcome_message(self):
        if self.uid:
            return (
                "✅ 115登录状态：已登录",
                f"🆔 用户ID：{self.uid}",
                "📅 登录时间：最近",
                "💫 状态：正常"
            )
        else:
            return (
                "❌ 115登录状态：未登录",
                "⚠️ 请使用 /auth 命令进行扫码登录",
                "📱 需要使用115手机App扫码",
                "🔐 授权后即可使用下载功能"
            )

    def get_qrcode(self):
        """获取登录二维码"""
        try:
            import requests
            url = "https://passportapi.115.com/app/1.0/web/1.0/login/qrcode"
            headers = {
                "User-Agent": self.user_agent,
                "App-ID": self.app_id
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.qrcode_token = data.get("data", {}).get("qrcode")
                return self.qrcode_token
        except Exception as e:
            logger.error(f"获取二维码失败: {e}")
        return None

    def check_login(self):
        """检查登录状态"""
        if not self.qrcode_token:
            return False
            
        try:
            import requests
            url = f"https://passportapi.115.com/app/1.0/web/1.0/login/qrcode/status?qrcode={self.qrcode_token}"
            headers = {
                "User-Agent": self.user_agent,
                "App-ID": self.app_id
            }
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

    def add_offline_task(self, url, save_path="/"):
        """添加离线下载任务"""
        if not self.uid:
            return False, "未登录，请先使用 /auth 登录"
            
        try:
            import requests
            api_url = "https://115.com/web/lixian/?ct=lixian&ac=add_task_url"
            headers = {
                "User-Agent": self.user_agent,
                "Cookie": self.cookie
            }
            data = {
                "url": url,
                "savepath": save_path
            }
            response = requests.post(api_url, headers=headers, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("state"):
                    return True, "任务添加成功"
                else:
                    return False, result.get("error_msg", "任务添加失败")
        except Exception as e:
            logger.error(f"添加离线任务失败: {e}")
            return False, f"添加失败: {str(e)}"
        
        return False, "未知错误"

def load_yaml_config():
    """加载YAML配置"""
    global bot_config
    try:
        config_path = "/app/config/config.yaml"
        if not os.path.exists(config_path):
            config_path = "config.yaml"
            
        with open(config_path, 'r', encoding='utf-8') as file:
            bot_config = yaml.safe_load(file)
        logger.info("配置文件加载成功")
        return True
    except Exception as e:
        logger.error(f"配置文件加载失败: {e}")
        # 使用环境变量作为备选
        bot_config = {
            'bot_token': os.getenv('BOT_TOKEN', ''),
            'allowed_user': os.getenv('ALLOWED_USER', ''),
            '115_app_id': os.getenv('APP_115_APP_ID', ''),
            '115_user_agent': os.getenv('APP_115_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        }
        return bool(bot_config['bot_token'])

def initialize_115open():
    """初始化115 OpenAPI客户端"""
    global openapi_115
    try:
        openapi_115 = OpenAPI115(
            app_id=bot_config.get('115_app_id', ''),
            user_agent=bot_config.get('115_user_agent', '')
        )
        logger.info("115 OpenAPI客户端初始化成功")
        return True
    except Exception as e:
        logger.error(f"115 OpenAPI客户端初始化失败: {e}")
        return False

def init():
    """初始化应用"""
    if not load_yaml_config():
        logger.error("配置加载失败，应用无法启动")
        return False
    
    # 创建必要目录
    os.makedirs(IMAGE_PATH, exist_ok=True)
    
    return True