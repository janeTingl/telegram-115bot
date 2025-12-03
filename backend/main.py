import json
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 可选路由 ---
try:
    from api.common_settings import router as settings_router
    from api.cloud115_qr import router as cloud115_qr_router
except ImportError:
    settings_router = None
    cloud115_qr_router = None

# --- 核心路径 ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

LOG_PATH = DATA_DIR / "backend.log"
_2FA_SESSIONS_PATH = DATA_DIR / "2fa_sessions.json"

def write_log(msg: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

try:
    from core.logger import push_log
except Exception:
    def push_log(level: str, msg: str):
        write_log(f"[{level}] {msg}")

# --- 保留其他模块导入 ---
try:
    from task_queue import submit_task, get_task, TaskStatus
except Exception:
    submit_task = get_task = TaskStatus = None

try:
    from organizer import preview_organize, run_organize, list_files as organizer_list_files
except Exception:
    preview_organize = run_organize = organizer_list_files = None

try:
    from strm_generator import generate_strm_for_files
except Exception:
    generate_strm_for_files = None

try:
    from p115_wrapper import P115Wrapper, P115Error
except Exception:
    P115Wrapper = None
    P115Error = Exception

try:
    from bot_integration import notify_bot
except Exception:
    def notify_bot(msg, level="info"): return False

try:
    from core.db import get_config, set_config, get_secret, set_secret, get_data_conn
except Exception:
    def get_config(k, d=None): return d
    def set_config(k, v): pass
    def get_secret(k, d=None): return d
    def set_secret(k, v): pass
    def get_data_conn(): return None

try:
    from core.qps_limiter import get_limiter
except Exception:
    def get_limiter(service: str, qps: int):
        class Dummy:
            def consume(self): return True
        return Dummy()

try:
    from core.zid_loader import ZID_CACHE, load_zid
except Exception:
    ZID_CACHE: Dict[str, Any] = {}
    def load_zid(): return {}

# --- FastAPI 实例 ---
app = FastAPI(title="115Bot Backend", version="2.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 路由自动加载 ---
def _include_router(module_name: str):
    try:
        mod = __import__(module_name, fromlist=["router"])
        if hasattr(mod, "router"):
            app.include_router(mod.router, prefix="/api")
    except Exception:
        pass

_include_router("router.auth")
_include_router("router.offline")
_include_router("router.file")
_include_router("router.notify")
_include_router("router.tmdb")
_include_router("router.emby")

if settings_router:
    app.include_router(settings_router)
if cloud115_qr_router:
    app.include_router(cloud115_qr_router)

try:
    from main_old import app as old_app
    app.mount("/old", old_app)
except Exception:
    pass

# --- 以下保持原来 2FA / 115 / Organizer / STRM / Task / Bot / ZID 接口 ---
# ... 保留你原来的接口代码，不变 ...

# --- 最后启动入口 ---
if __name__ == "__main__":
    cfg_path = DATA_DIR / "config.json"
    host = "0.0.0.0"
    port = 8000
    reload = True
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            server_cfg = cfg.get("server", {})
            host = server_cfg.get("host", host)
            reload = server_cfg.get("reload", True)
        except Exception:
            pass

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )