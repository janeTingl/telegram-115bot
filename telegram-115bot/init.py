import yaml
import logging
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

    # 115相关方法保持原样（get_qrcode, check_login, add_offline_task, welcome_message）

def load_yaml_config():
    global bot_config
    try:
        config_path = "/app/data/config.yaml"
        if not os.path.exists(config_path):
            config_path = "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            bot_config = yaml.safe_load(f)
        logger.info("配置文件加载成功")
        return True
    except Exception as e:
        logger.error(f"配置文件加载失败: {e}")
        bot_config = {
            'bot_token': os.getenv('BOT_TOKEN', ''),
            'allowed_user': os.getenv('ALLOWED_USER', ''),
            '115_app_id': os.getenv('APP_115_APP_ID', ''),
            '115_user_agent': os.getenv('APP_115_USER_AGENT', '')
        }
        return bool(bot_config['bot_token'])

def initialize_115open():
    global openapi_115
    try:
        openapi_115 = OpenAPI115(app_id=bot_config.get('115_app_id', ''),
                                 user_agent=bot_config.get('115_user_agent', ''))
        logger.info("115 OpenAPI客户端初始化成功")
        return True
    except Exception as e:
        logger.error(f"115 OpenAPI客户端初始化失败: {e}")
        return False

def init():
    if not load_yaml_config():
        logger.error("配置加载失败，应用无法启动")
        return False
    os.makedirs(IMAGE_PATH, exist_ok=True)
    return True