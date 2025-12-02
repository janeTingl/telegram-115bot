# backend/core/logger.py
# 中文滚动日志管理（最多保留 1000 条）
# 严格禁止写入敏感数据（调用方必须保证不传入 secrets / media_scan 详细内容）

import threading
import time
from collections import deque
from typing import List, Dict

_MAX_LOGS = 1000
_lock = threading.Lock()
_logs = deque(maxlen=_MAX_LOGS)

def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def push_log(level: str, text: str, task_id: str = None) -> None:
    """
    level: INFO / WARN / ERROR
    text: 中文日志文本（调用方请勿包含 secret 或媒体扫描敏感信息）
    task_id: 可选任务 id，用于追踪
    """
    with _lock:
        entry = {"ts": _now(), "level": level, "msg": text}
        if task_id:
            entry["task_id"] = task_id
        _logs.append(entry)

def list_logs(limit: int = 200) -> List[Dict]:
    with _lock:
        l = list(_logs)[-limit:]
        return l

def clear_logs():
    with _lock:
        _logs.clear()
