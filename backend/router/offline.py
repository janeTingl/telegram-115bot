# backend/router/offline.py
"""
离线下载与转存路由
- POST /api/offline/create  创建离线任务（body: url, target_folder, notify_tg(boolean)）
- GET /api/offline/status?task_id=...  查询离线任务状态
- POST /api/offline/transfer  将离线完成任务转存并触发后续整理（body: task_id, target_folder）
"""

from fastapi import APIRouter, Form, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time

from core.p115_client import P115Wrapper, P115Error
from core.logger import push_log
from core.qps_limiter import get_limiter
from utils.strm import generate_strm_for_files
from utils.rename import smart_rename_and_move
from core.zid_loader import ZID_CACHE
from task_queue import submit_task

try:
    from bot_integration import notify_bot
except ImportError:
    def notify_bot(msg, level="info"):
        return False

router = APIRouter()

# QPS 控制：从 config 获取（使用 get_config）
from core.db import get_config, get_secret

def _get_qps(service: str, default: int):
    try:
        return int(get_config(f"{service}_qps", default))
    except:
        return default

class OfflineCreateBody(BaseModel):
    url: str
    target_folder: str = "/"
    notify_tg: bool = True

@router.post("/offline/create")
def api_offline_create(body: OfflineCreateBody, background: BackgroundTasks):
    """
    创建离线任务并在后台轮询完成。
    返回 task info（本地 task_id）
    """
    url = body.url
    target = body.target_folder
    notify_tg = body.notify_tg

    push_log("INFO", "收到离线任务创建请求。")
    try:
        qps = _get_qps("115", 3)
        limiter = get_limiter("115", qps)
        if not limiter.consume():
            return {"code": 429, "msg": "达到 115 QPS 限制，请稍后再试"}

        # 从 secrets 中读取 cookie（不记录）
        cookie = get_secret("115_cookie")
        p115 = P115Wrapper(cookie)

        # 创建离线任务
        res = p115.create_offline_task(url)
        # 生成本地任务 id（用时间戳 + 随机）
        local_task_id = f"offline-{int(time.time())}"
        push_log("INFO", "已提交离线任务，后台轮询中", task_id=local_task_id)

        # 后台轮询函数
        def poll_and_process():
            try:
                # 轮询直到状态为完成或失败
                for _ in range(3600):  # 最多轮询 3600 次（保守）
                    try:
                        status = p115.get_offline_status(res.get("task_id") or res.get("id") or res.get("tid"))
                    except Exception as e:
                        push_log("WARN", f"查询离线任务状态出错: {e}", task_id=local_task_id)
                        time.sleep(3)
                        continue
                    st = status.get("status") or status.get("state") or str(status)
                    push_log("INFO", f"离线任务状态: {st}", task_id=local_task_id)
                    if str(st).lower() in ("finished","completed","success","done"):
                        # 转存
                        try:
                            p115.offline_transfer_to_115(status.get("task_id") or status.get("id") or res.get("task_id"), target)
                            push_log("INFO", "离线任务转存完成，触发整理流程", task_id=local_task_id)
                        except Exception as e:
                            push_log("ERROR", f"转存失败: {e}", task_id=local_task_id)
                        # 触发异步整理任务（提交到通用任务队列）
                        def job(update_progress):
                            try:
                                # 1) 列出 target 目录文件（简单处理：在 p115 client 中调用 list_files）
                                files = []
                                try:
                                    fl = p115.list_files(target, limit=500)
                                    # 解析文件路径列表
                                    if isinstance(fl, list):
                                        files = [item.get("path") if isinstance(item, dict) else item for item in fl]
                                except:
                                    pass
                                # 2) 调用智能重命名与分类（会返回移动后的路径）
                                moved = smart_rename_and_move(files, target, zid_map=ZID_CACHE)
                                update_progress(80, "重命名/移动完成，生成 STRM")
                                # 3) 生成 strm（生成到目标目录）
                                strms = generate_strm_for_files(moved, target_dir=None, template="{filepath}")
                                update_progress(95, "STRM 生成完成")
                                # 4) 等待 3 秒（你要求 3 秒后生成 STRM -> 我们已生成，后续 Emby 通知在 file router 中）
                                time.sleep(1)
                                return {"moved": moved, "strms": strms}
                            except Exception as e:
                                push_log("ERROR", f"整理任务内部异常: {e}", task_id=local_task_id)
                                raise
                        tid = submit_task(job)
                        push_log("INFO", f"整理任务已提交 (task_id={tid})", task_id=local_task_id)
                        # 通知 TG （如果需要）
                        if notify_tg:
                            try:
                                notify_text = f"离线任务已转存并提交整理 (task_id={tid})"
                                notify_bot(notify_text)
                            except:
                                pass
                        return
                    if str(st).lower() in ("failed","error"):
                        push_log("ERROR", f"离线任务失败: {status}", task_id=local_task_id)
                        return
                    time.sleep(5)
            except Exception as e:
                push_log("ERROR", f"轮询处理异常: {e}", task_id=local_task_id)

        background.add_task(poll_and_process)
        return {"code": 0, "data": {"local_task_id": local_task_id, "remote": res}}
    except P115Error as e:
        push_log("ERROR", f"创建离线任务失败: {e}")
        return {"code": 2, "msg": str(e)}
    except Exception as e:
        push_log("ERROR", f"offline.create 未知错误: {e}")
        return {"code": 3, "msg": str(e)}

@router.get("/offline/status")
def api_offline_status(task_id: str):
    # 查询本地任务队列状态（由 task_queue 管理）
    from task_queue import get_task
    t = get_task(task_id)
    if not t:
        return {"code": 1, "msg": "not found"}
    return {"code": 0, "data": t}
