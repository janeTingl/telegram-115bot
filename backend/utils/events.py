# backend/utils/events.py
"""
事件通知模块：
- 提供 notify_emby_refresh(path) 用于在整理后通知 Emby
- 提供 notify_telegram(text) 用于发送 TG 通知（请在 bot_integration.py 中实现实际发送）
"""

import time
from core.logger import push_log
from core.db import get_config, get_secret
from core.qps_limiter import get_limiter
import requests

def notify_emby_refresh():
    host = get_config("emby_host", "")
    api_key = get_secret("emby_api_key", None)
    if not host or not api_key:
        push_log("WARN", "Emby 未配置，跳过刷新")
        return False
    try:
        qps = int(get_config("emby_qps", 1))
        limiter = get_limiter("emby", qps)
        if not limiter.consume():
            push_log("WARN", "Emby 请求受限（QPS）")
            return False
        url = f"{host.rstrip('/')}/Library/Refresh?api_key={api_key}"
        requests.post(url, timeout=8)
        push_log("INFO", "已触发 Emby 刷新")
        # 等待 4 秒后，前端/系统会处理刮削回调；这里仅触发
        time.sleep(4)
        return True
    except Exception as e:
        push_log("ERROR", f"触发 Emby 刷新失败: {e}")
        return False

def notify_telegram(text: str):
    # 不在这里实现 HTTP，只调用 bot_integration.notify_bot
    try:
        from bot_integration import notify_bot
        notify_bot(text)
        push_log("INFO", "已发送 Telegram 通知")
        return True
    except Exception as e:
        push_log("WARN", f"发送 Telegram 通知失败: {e}")
        return False
