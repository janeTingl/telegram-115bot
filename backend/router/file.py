# backend/router/file.py
from fastapi import APIRouter, Form, BackgroundTasks
from typing import Optional
import time
import requests

from core.p115_client import P115Wrapper, P115Error
from core.db import get_config, get_secret
from core.logger import push_log
from core.qps_limiter import get_limiter
from core.zid_loader import ZID_CACHE
from core.organizer import start_organize_job 

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
        for name in ("move","file_move","mv","fs_move"):
            if hasattr(p.client, name):
                fn = getattr(p.client, name)
                try:
                    r = fn(src, dst)
                    push_log("INFO", f"移动文件: {src} -> {dst}")
                    return {"code": 0, "data": r}
                except Exception:
                    continue
        return {"code": 2, "msg": "p115client 未实现移动接口"}
    except Exception as e:
        push_log("ERROR", f"move error: {e}")
        return {"code": 3, "msg": str(e)}

@router.post("/api/file/rename")
def api_file_rename(path: str = Form(...), new_name: str = Form(...)):
    dst = "/".join(path.split("/")[:-1] + [new_name])
    return api_file_move(src=path, dst=dst)

@router.post("/api/file/notify_emby")
def api_notify_emby(path: str = Form(...), background: BackgroundTasks = None):
    host, api_key = _get_emby_info()
    if not host or not api_key:
        push_log("WARN", "Emby 配置未设置，跳过刷新")
        return {"code": 1, "msg": "emby not configured"}
    push_log("INFO", "触发 Emby 刷新媒体库")
    try:
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

@router.post("/api/file/organize/start")
async def api_organize_start():
    push_log("INFO", "接收到前端请求，开始启动网盘整理任务...")
    
    try:
        job_id = await start_organize_job() 
        
        if job_id:
            push_log("INFO", f"网盘整理任务已成功启动，Job ID: {job_id}")
            return {"code": 0, "msg": "整理任务已在后台启动", "data": {"job_id": job_id}}
        else:
            return {"code": 1, "msg": "整理任务启动失败或配置未启用"}
            
    except Exception as e:
        push_log("ERROR", f"启动整理任务时发生错误: {e}")
        return {"code": 500, "msg": f"服务器内部错误: {e}"}