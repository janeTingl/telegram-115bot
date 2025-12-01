import logging
import os
from wsgidav.wsgidav_app import WsgiDAVApp
from wsgidav.fs_dav_provider import FilesystemProvider
from a2wsgi import WSGIMiddleware

logger = logging.getLogger("WebDAV")

class WebDAVManager:
    def __init__(self):
        self.root_path = "/data/strm"
        self.asgi_app = None
        self._current_config = {}

    def get_asgi_app(self, username="admin", password="password", read_only=True):
        """
        创建并返回一个适配 FastAPI 的 ASGI 应用
        """
        # 确保目录存在
        os.makedirs(self.root_path, exist_ok=True)

        # WsgiDAV 配置
        config = {
            "provider_mapping": {"/": FilesystemProvider(self.root_path)},
            "simple_dc": {
                "user_mapping": {
                    "*": {username: {"password": password}}
                }
            },
            "verbose": 1,
            "http_authenticator": {
                "domain_controller": None,
                "accept_basic": True,
                "accept_digest": True,
                "default_to_digest": True,
            },
            # 关键：告诉 WsgiDAV 它被挂载在 /dav 下，否则生成的链接会少 /dav 前缀
            # 但 WsgiDAV 4.x 通常能自动识别 SCRIPT_NAME，如果不行需手动指定 mount_path
        }

        # 创建 WSGI 应用
        wsgi_app = WsgiDAVApp(config)
        
        # 转换为 ASGI
        self.asgi_app = WSGIMiddleware(wsgi_app)
        logger.info(f"WebDAV App initialized (User: {username})")
        return self.asgi_app

# 单例
webdav_manager = WebDAVManager()