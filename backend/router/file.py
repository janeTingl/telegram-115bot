import asyncio
from fastapi import APIRouter, Form, BackgroundTasks, HTTPException, Query
from typing import Optional, Dict, Any, List
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

# ----------------------------------------------------------------------
# 文件列表 API (适配 FileSelector)
# ----------------------------------------------------------------------

# 将 path 视为 115 的 CID
@router.get("/file/list")
async def api_file_list(path: str = Query("0"), limit: int = 200): 
    cookie = get_secret("115_cookie")
    if not cookie:
        # 如果未登录，返回 401
        raise HTTPException(status_code=401, detail="115 Cookie 未设置")
        
    try:
        p = P115Wrapper(cookie)
        
        # 定义同步函数，负责调用 p115client 和数据格式化
        def sync_list_files(cid: str, limit: int) -> List[Dict[str, Any]]:
            # 假设 p.list_files 接受 CID 并返回原始数据
            raw_files = p.list_files(cid, limit=limit) 
            
            # **【连通性核心：数据格式化】**
            # 转换为前端 FileSelector 期望的格式：{ id, name, children, date }
            formatted_files = []
            for x in raw_files:
                # 假设 raw_files 包含 n(name), cid/fid(id), te(time/date)
                is_dir = x.get("cid") is not None and x.get("cid") != "" # 检查是否为目录
                formatted_files.append({
                    "id": str(x.get("cid", x.get("fid"))),
                    "name": x.get("n"),
                    "children": is_dir,
                    "date": x.get("te") # 假设 'te' 是日期字段
                })
            return formatted_files

        # **【异步包装】**：使用 asyncio.to_thread 安全地调用同步函数
        files = await asyncio.to_thread(sync_list_files, path, limit)
        
        # 返回适配前端 FileSelector 的格式: { code: 0, data: [...] }
        return {"code": 0, "data": files} 

    except P115Error as e:
        push_log("ERROR", f"115 client error: {e}")
        raise HTTPException(status_code=500, detail=f"115 客户端错误: {e}")
    except Exception as e:
        push_log("ERROR", f"list files error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------
# 其他原有 API 保持不变 (move, rename, notify_emby, organize/start)
# ----------------------------------------------------------------------

@router.post("/file/move")
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

@router.post("/file/rename")
def api_file_rename(path: str = Form(...), new_name: str = Form(...)):
    dst = "/".join(path.split("/")[:-1] + [new_name])
    return api_file_move(src=path, dst=dst)

@router.post("/file/notify_emby")
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

@router.post("/file/organize/start")
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