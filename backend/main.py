import json
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles  # ⚠️ 保留 import，但未使用

from pydantic import BaseModel

# --- 可选路由导入 ---
try:
    from api.common_settings import router as settings_router
    from api.cloud115_qr import router as cloud115_qr_router
except ImportError:
    settings_router = None
    cloud115_qr_router = None

# --- 核心路径配置 ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

LOG_PATH = DATA_DIR / "backend.log"
_2FA_SESSIONS_PATH = DATA_DIR / "2fa_sessions.json"

# --- 日志辅助函数 ---
def write_log(msg: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

try:
    from core.logger import push_log
except Exception:
    def push_log(level: str, msg: str):
        write_log(f"[{level}] {msg}")

# --- 其他模块导入 ---
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
_include_router("router.config")
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

# --- 2FA 会话管理 ---
def _load_2fa_sessions() -> Dict[str, float]:
    if _2FA_SESSIONS_PATH.exists():
        try:
            return json.loads(_2FA_SESSIONS_PATH.read_text(encoding="utf-8"))
        except:
            return {}
    return {}

def _save_2fa_sessions(data: Dict[str, float]):
    _2FA_SESSIONS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _mark_2fa_verified(client_key: str, ttl: int = 300):
    sessions = _load_2fa_sessions()
    sessions[client_key] = time.time() + ttl
    _save_2fa_sessions(sessions)

def _is_2fa_verified(client_key: str) -> bool:
    sessions = _load_2fa_sessions()
    exp = sessions.get(client_key)
    if not exp or time.time() > exp:
        sessions.pop(client_key, None)
        _save_2fa_sessions(sessions)
        return False
    return True

def _client_key(req: Request) -> str:
    return (
        req.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or req.headers.get("x-real-ip", "")
        or (req.client.host if req.client else "unknown")
    )

# --- 115 Wrapper 单例 ---
_P115_INSTANCE = None
def get_p115() -> Optional[P115Wrapper]:
    global _P115_INSTANCE
    if _P115_INSTANCE is None and P115Wrapper:
        cookie = get_secret("115_cookie")
        if cookie:
            _P115_INSTANCE = P115Wrapper(cookie=cookie)
        else:
            _P115_INSTANCE = False
    return _P115_INSTANCE if _P115_INSTANCE and _P115_INSTANCE is not False else None

# --- Pydantic 模型 ---
class ConfigUpdate(BaseModel):
    key: str
    value: Any

class OrgRules(BaseModel):
    rules: dict
    src_dir: str
    dry_run: bool = True

class RenameRules(BaseModel):
    pattern: str
    replace: str
    files: List[str]

class StrmBody(BaseModel):
    files: List[str]
    target_dir: Optional[str] = None
    template: str = "{filepath}"

# --- 健康检查 / 基础路由 ---
@app.get("/healthz")
async def healthz():
    return "ok"

@app.get("/api/status")
async def status():
    return {"code": 0, "data": {"uptime": time.time(), "version": "backend-2.1"}}

@app.get("/api/version")
async def version():
    return {"code": 0, "data": {"version": "2.1", "name": "telegram-115bot-backend"}}

# --- 配置 / Secret / 文件上传等接口 ---
@app.get("/api/config/get")
async def config_get():
    try:
        conn = get_data_conn()
        data = {}
        if conn:
            cur = conn.execute("SELECT key, value FROM config").fetchall()
            data = {r[0]: r[1] for r in cur}
        return {"code": 0, "data": data}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.post("/api/config/update")
async def config_update(item: ConfigUpdate):
    try:
        val = item.value
        if isinstance(val, (dict, list)):
            val = json.dumps(val, ensure_ascii=False)
        set_config(item.key, val)
        return {"code": 0, "msg": "ok"}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.post("/api/2fa/verify")
async def api_2fa_verify(req: Request, code: str = Form(...)):
    try:
        try:
            from api import _2fa as mod_2fa
            if hasattr(mod_2fa, "api_2fa_verify"):
                result = mod_2fa.api_2fa_verify(code=code)
                if result.get("ok"):
                    _mark_2fa_verified(_client_key(req))
                    return {"code": 0, "msg": "verified"}
                return {"code": 2, "msg": "invalid"}
        except Exception:
            pass

        secret = get_secret("2fa_secret")
        if not secret:
            return {"code": 1, "msg": "2FA not configured"}
        import pyotp
        if pyotp.TOTP(secret).verify(code, valid_window=1):
            _mark_2fa_verified(_client_key(req))
            return {"code": 0, "msg": "verified"}
        return {"code": 2, "msg": "invalid code"}
    except Exception as e:
        return {"code": 3, "msg": str(e)}

@app.get("/api/secret/get")
async def secret_get(req: Request, key: str):
    if not _is_2fa_verified(_client_key(req)):
        raise HTTPException(401, "2FA required")
    value = get_secret(key)
    return {"code": 0, "data": value or ""}

@app.post("/api/files/upload")
async def filesureq(file: UploadFile = File(...)):
    safe_name = Path(file.filename).name
    dest = UPLOADS_DIR / safe_name
    content = await file.read()
    dest.write_bytes(content)
    return {"code": 0, "data": {"filename": safe_name, "path": str(dest)}}

@app.get("/api/files/list")
async def files_list(path: str = "."):
    try:
        if organizer_list_files:
            return {"code": 0, "data": organizer_list_files(path)}
        p = Path(path).resolve()
        if not p.is_dir():
            return {"code": 1, "msg": "not directory"}
        items = [{"name": x.name, "path": str(x), "is_dir": x.is_dir()} for x in p.iterdir()]
        return {"code": 0, "data": items}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

# --- 后续接口略（保持你最早的原始版本） ---
# 包含 /api/115/login、/api/115/upload、/api/organize/run 等
# 包含 /api/rename/run、/api/strm/generate、/api/task/status、/api/bot/send
# /api/zid/list、/api/zid/reload 等
# ⭐ 前端静态资源挂载（必须位于所有 API 之后）
app.mount("/", StaticFiles(directory="dist", html=True), name="static")
# --- 启动 ---
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