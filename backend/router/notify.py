# backend/router/notify.py
from fastapi import APIRouter, Request, BackgroundTasks
from core.logger import push_log
from core.db import get_config
from core.p115_client import P115Wrapper, P115Error
from task_queue import submit_task
from utils.rename import smart_rename_and_move
from utils.strm import generate_strm_for_files
from utils.events import notify_emby_refresh, notify_telegram
from core.zid_loader import ZID_CACHE
import time

router = APIRouter()

@router.post("/api/notify/115_event")
async def api_notify_115_event(req: Request, background: BackgroundTasks):
    """
    接收 p115 的文件变更事件（示例 payload）
    payload 应包含: { 'event': 'file_added', 'path': '/path/to/dir', 'files': [...] }
    """
    try:
        payload = await req.json()
    except:
        payload = {}
    push_log("INFO", f"收到 115 事件: {payload.get('event','unknown')}")
    # 异步处理事件：整理/重命名/生成 STRM/通知 Emby
    def job():
        try:
            event = payload.get("event")
            files = payload.get("files", [])
            path = payload.get("path", "/")
            # 只处理新增文件事件
            if event not in ("file_added","files_added","new_files"):
                push_log("INFO", "非新增文件事件，忽略")
                return
            # 1) 智能重命名与移动
            moved = smart_rename_and_move(files, path, zid_map=ZID_CACHE)
            push_log("INFO", f"处理完成，移动 {len(moved)} 个文件")
            # 2) 生成 STRM（延迟 3 秒再生成）
            time.sleep(3)
            strms = generate_strm_for_files(moved, target_dir=None, template="{filepath}")
            push_log("INFO", f"生成 {len(strms)} 个 STRM 文件")
            # 3) 通知 Emby 刷新（延迟 4 秒）
            notify_emby_refresh()
            # 4) 发送 TG 通知
            notify_telegram(f"已整理并生成 STRM：{len(moved)} 个文件")
        except Exception as e:
            push_log("ERROR", f"事件处理异常: {e}")
    background.add_task(job)
    return {"code": 0, "msg": "accepted"}
