import os
import logging

logger = logging.getLogger("ProxyMgr")

def apply_global_proxy(config: dict):
    """
    应用全局代理设置
    原理: 修改环境变量，影响所有基于 urllib/requests/httpx 的库
    """
    # 从配置中读取 proxy 字段
    proxy_conf = config.get("proxy", {})
    
    if proxy_conf.get("enabled"):
        scheme = proxy_conf.get("type", "http")
        host = proxy_conf.get("host", "127.0.0.1")
        port = proxy_conf.get("port", "7890")
        
        # 构造代理 URL，例如 http://192.168.1.5:7890
        proxy_url = f"{scheme}://{host}:{port}"
        
        # 设置环境变量
        # 注意: 大写是标准约定，httpx/requests 会自动读取这些变量
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        os.environ["ALL_PROXY"] = proxy_url
        os.environ["http_proxy"] = proxy_url
        os.environ["https_proxy"] = proxy_url
        
        logger.info(f"🌍 Global Proxy Enabled: {proxy_url}")
    else:
        # 如果禁用，务必清除环境变量，防止之前设置的残留影响后续请求
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("ALL_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
        
        logger.info("🚫 Global Proxy Disabled")
