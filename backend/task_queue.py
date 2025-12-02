# backend/task_queue.py
import threading
import uuid
import json
import time
from pathlib import Path
from typing import Callable, Any

BASE = Path(__file__).resolve().parent
TASK_DIR = BASE / "tasks"
TASK_DIR.mkdir(exist_ok=True)

_tasks = {}
_lock = threading.Lock()

class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

def _save_task(task_id, meta):
    p = TASK_DIR / f"{task_id}.json"
    with open(p, "w", encoding="utf8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

def _load_task(task_id):
    p = TASK_DIR / f"{task_id}.json"
    if not p.exists():
        return None
    with open(p, "r", encoding="utf8") as f:
        return json.load(f)

def submit_task(func: Callable[..., Any], *args, **kwargs) -> str:
    """
    提交任务，返回 task_id
    func: 可调用，接受 (update_progress) 回调用于写日志
    """
    task_id = str(uuid.uuid4())
    meta = {"id": task_id, "status": TaskStatus.PENDING, "progress": 0, "log": [], "result": None, "created_at": time.time()}
    _save_task(task_id, meta)

    def runner():
        try:
            meta = _load_task(task_id)
            meta["status"] = TaskStatus.RUNNING
            _save_task(task_id, meta)

            def update_progress(percent:int, message:str=None):
                m = _load_task(task_id)
                m["progress"] = percent
                if message:
                    m.setdefault("log", []).append({"ts": time.time(), "msg": message})
                _save_task(task_id, m)

            res = func(update_progress, *args, **kwargs)
            m = _load_task(task_id)
            m["status"] = TaskStatus.SUCCESS
            m["result"] = res
            m["progress"] = 100
            _save_task(task_id, m)
        except Exception as e:
            m = _load_task(task_id) or meta
            m["status"] = TaskStatus.FAILED
            m.setdefault("log", []).append({"ts": time.time(), "msg": f"Exception: {str(e)}"})
            _save_task(task_id, m)
    t = threading.Thread(target=runner, daemon=True)
    t.start()
    return task_id

def get_task(task_id):
    return _load_task(task_id)
