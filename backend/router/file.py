# backend/router/file.py
"""
网盘文件操作（与前端文件管理交互）
包含：
- /api/file/list
- /api/file/move
- /api/file/rename
- /api/file/notify_emby  (刷新 Emby 并在刮削后获取 PlaybackInfo)
"""

from fastapi import APIRouter, Form, BackgroundTasks
from typing import Optional
import time
import requests

from core.p115_client import P115Wrapper, P115Error
from core.db import get_config, get_secret
from core.logger import push_log
from core.qps_limiter import get_limiter
from core.zid_loader import ZID_CACHE

router = APIRouter()

def _get_emby_info():
    host = get_config("emby_host", "")
    api_key = get_secret("emby_api_key", None)
    return host, api_key

@router.get("/api/file/list")
def api_file_list(path: str = "/", limit: int = 200):
    cookie = get_secret("115_cookie")
    try:
        p = P115Wrapper(cookie)
        files = p.list_files(path, limit=limit)
        return {"code": 0, "data": files}
    except Exception as e:
        push_log("ERROR", f"list files error: {e}")
        return {"code": 1, "msg": str(e)}

@router.post("/api/file/move")
def api_file_move(src: str = Form(...), dst: str = Form(...)):
    cookie = get_secret("115_cookie")
    try:
        p = P115Wrapper(cookie)
        # 尝试常见 move 方法
        for name in ("move","file_move","mv","fs_move"):
            if hasattr(p.client, name):
                fn = getattr(p.client, name)
                try:
                    r = fn(src, dst)
                    push_log("INFO", f"移动文件: {src} -> {dst}")
                    return {"code": 0, "data": r}
                except Exception:
                    continue
        # fallback: 返回 unsupported
        return {"code": 2, "msg": "p115client 未实现移动接口"}
    except Exception as e:
        push_log("ERROR", f"move error: {e}")
        return {"code": 3, "msg": str(e)}

@router.post("/api/file/rename")
def api_file_rename(path: str = Form(...), new_name: str = Form(...)):
    # 直接调用 move 到同目录下新名称
    dst = "/".join(path.split("/")[:-1] + [new_name])
    return api_file_move(src=path, dst=dst)

@router.post("/api/file/notify_emby")
def api_notify_emby(path: str = Form(...), background: BackgroundTasks = None):
    """
    path: 网盘中文件或目录路径（整理完成后调用）
    逻辑：
      - 触发 Emby 刷新（/Library/Refresh）
      - 等待 4 秒
      - 前端/后端会在 Emby 刮削完成后触发回调；如果没有回调，1 秒后调用 Items/{ItemId}/PlaybackInfo（需要前端提供 ItemId）
    """
    host, api_key = _get_emby_info()
    if not host or not api_key:
        push_log("WARN", "Emby 配置未设置，跳过刷新")
        return {"code": 1, "msg": "emby not configured"}
    push_log("INFO", "触发 Emby 刷新媒体库")
    try:
        # 限流
        qps = int(get_config("emby_qps", 1))
        limiter = get_limiter("emby", qps)
        if not limiter.consume():
            return {"code": 429, "msg": "emby rate limited"}

        def do_refresh():
            try:
                url = f"{host.rstrip('/')}/Library/Refresh?api_key={api_key}"
                requests.post(url, timeout=10)
                push_log("INFO", "已触发 Emby 刷新，等待 4 秒")
                time.sleep(4)
                # 发送通知后由 Emby 刮削，1 秒后可查询 PlaybackInfo（需要前端或 webhook 提供 ItemId）
                # 这里仅记录流程，PlaybackInfo 的调用需要 ItemId，由前端/Emby webhook 提供
            except Exception as e:
                push_log("ERROR", f"触发 Emby 刷新失败: {e}")

        if background:
            background.add_task(do_refresh)
        else:
            do_refresh()
        return {"code": 0, "msg": "emby refresh triggered"}
    except Exception as e:
        push_log("ERROR", f"notify emby error: {e}")
        return {"code": 2, "msg": str(e)}
