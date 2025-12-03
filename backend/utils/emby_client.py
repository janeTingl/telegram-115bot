import requests
import logging
from urllib.parse import urljoin

# 使用 backend/core/logger 的 logger 或者标准 logger
try:
    from core.logger import logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class EmbyClient:
    """
    Emby API 交互封装类
    """
    def __init__(self, host, api_key=None, user_id=None, timeout=10):
        self.base_url = host.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.timeout = timeout
        self.session = requests.Session()
        
        # 默认 Headers
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            # 这里的 Client 名称可以改为你的应用名
            'X-Emby-Authorization': 'MediaBrowser Client="BackendBot", Device="Server", DeviceId="1", Version="1.0.0"'
        })
        
        # 如果初始化时就有 API Key，直接注入 Header
        if self.api_key:
            self.session.headers.update({'X-Emby-Token': self.api_key})

    def _request(self, method, endpoint, params=None, data=None):
        url = urljoin(self.base_url, endpoint)
        # 如果 params 为空初始化字典，确保 API Key 总是可用 (作为 Query 参数备用)
        if params is None:
            params = {}
        if self.api_key and 'api_key' not in params:
            params['api_key'] = self.api_key
            
        try:
            response = self.session.request(method, url, params=params, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Emby API 请求失败 [{endpoint}]: {e}")
            raise

    def refresh_library(self):
        """触发媒体库扫描"""
        return self._request('POST', '/Library/Refresh')

    def get_system_info(self):
        """获取系统信息 (用于测试连接)"""
        return self._request('GET', '/System/Info').json()

    # 你可以在这里继续添加 get_user_items, search 等方法