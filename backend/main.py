import json
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles # ⚠️ 虽然保留，但静态文件功能被移除

try:
    from api.common_settings import router as settings_router
    from api.cloud115_qr import router as cloud115_qr_router
except ImportError:
    settings_router = None
    cloud115_qr_router = None

# --- 核心路径配置 (数据持久化部分) ---
# BASE_DIR: 代码所在的目录 (例如 /app/backend)
BASE_DIR = Path(__file__).resolve().parent

# DATA_DIR: 数据持久化目录 (例如 /app/data)
# 优先级：环境变量 DATA_DIR > BASE_DIR.parent / data
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. 上传文件 -> /app/data/uploads
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# 2. 日志文件 -> /app/data/backend.log
LOG_PATH = DATA_DIR / "backend.log"

# 3. 2FA 缓存 -> /app/data/2fa_sessions.json
_2FA_SESSIONS_PATH = DATA_DIR / "2fa_sessions.json"


def write_log(msg: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    # 确保日志目录存在
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

try:
    from core.logger import push_log
except Exception:
    def push_log(level: str, msg: str):
        write_log(f"[{level}] {msg}")

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

app = FastAPI(title="115Bot Backend", version="2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/healthz")
async def healthz():
    return "ok"

@app.get("/api/status")
async def status():
    return {"code": 0, "data": {"uptime": time.time(), "version": "backend-2.1"}}

@app.get("/api/version")
async def version():
    return {"code": 0, "data": {"version": "2.1", "name": "telegram-115bot-backend"}}

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
    # 存到 DATA_DIR/uploads 下
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
        items = [
            {"name": x.name, "path": str(x), "is_dir": x.is_dir()}
            for x in p.iterdir()
        ]
        return {"code": 0, "data": items}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/115/login")
async def api_115_login(cookie: Optional[str] = Form(None)):
    if cookie:
        set_secret("115_cookie", cookie.strip())
        global _P115_INSTANCE
        _P115_INSTANCE = None
        return {"code": 0, "msg": "saved"}
    return {"code": 1, "msg": "no cookie provided"}

@app.post("/api/115/upload")
async def api_115_upload(filename: str = Form(...), remote_path: str = Form("/")):
    p115 = get_p115()
    if not p115:
        return {"code": 2, "msg": "115 wrapper not available or cookie invalid"}

    limiter = get_limiter("115", int(get_config("115_qps", 3)))
    if not limiter.consume():
        return {"code": 429, "msg": "rate limited"}

    # 从 UPLOADS_DIR 找文件
    src = UPLOADS_DIR / Path(filename).name
    if not src.exists():
        return {"code": 1, "msg": "local file not found"}

    try:
        result = p115.upload(str(src), remote_path)
        return {"code": 0, "data": result}
    except P115Error as e:
        return {"code": 3, "msg": str(e)}
    except Exception as e:
        return {"code": 4, "msg": str(e)}

@app.post("/api/organize/preview")
async def organize_preview(body: OrgRules):
    if not preview_organize:
        return {"code": 1, "msg": "organizer not available"}
    try:
        ops = preview_organize(body.rules, body.src_dir)
        return {"code": 0, "data": ops}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/organize/run")
async def organize_run(body: OrgRules):
    if not submit_task or not run_organize:
        return {"code": 1, "msg": "task queue or organizer not available"}

    def job(progress_callback):
        return run_organize(
            rules=body.rules,
            src_dir=body.src_dir,
            execute=not body.dry_run,
            update_progress=progress_callback
        )

    tid = submit_task(job)
    return {"code": 0, "data": {"task_id": tid}}

@app.post("/api/rename/run")
async def rename_run(body: RenameRules):
    if not submit_task:
        return {"code": 1, "msg": "task queue unavailable"}

    def create_job(files, pattern, replace):
        def job(progress_callback):
            import os, re
            result = []
            for i, f in enumerate(files):
                new_name = re.sub(pattern, replace, f)
                try:
                    os.rename(f, new_name)
                    result.append({"src": f, "dst": new_name})
                except Exception as e:
                    result.append({"src": f, "dst": None, "error": str(e)})
                progress_callback(int((i + 1) / len(files) * 100))
            return result
        return job

    tid = submit_task(create_job(body.files, body.pattern, body.replace))
    return {"code": 0, "data": {"task_id": tid}}

@app.post("/api/strm/generate")
async def strm_generate(body: StrmBody):
    if not generate_strm_for_files or not submit_task:
        return {"code": 1, "msg": "strm generator or task queue unavailable"}

    def job(progress_callback):
        return generate_strm_for_files(body.files, body.target_dir, body.template)

    tid = submit_task(job)
    return {"code": 0, "data": {"task_id": tid}}

@app.get("/api/task/status")
async def task_status(task_id: str):
    if not get_task:
        return {"code": 1, "msg": "task system unavailable"}
    t = get_task(task_id)
    if not t:
        return {"code": 2, "msg": "task not found"}
    return {"code": 0, "data": t}

@app.post("/api/bot/send")
async def bot_send(text: str = Form(...)):
    ok = notify_bot(text)
    return {"code": 0 if ok else 1, "msg": "sent" if ok else "failed"}

@app.get("/api/zid/list")
async def zid_list():
    return {"code": 0, "data": ZID_CACHE}

@app.post("/api/zid/reload")
async def zid_reload():
    global ZID_CACHE
    try:
        ZID_CACHE = load_zid()
        return {"code": 0, "msg": "reloaded"}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

# --- 清理掉静态文件配置，由 Nginx 负责 ---
# ⚠️ 注意: FileResponse 和 StaticFiles 模块虽然保留 import，但未在路由中使用

# ⚠️ 移除：static_dir = BASE_DIR.parent / "frontend" / "dist"
# ⚠️ 移除：assets_dir = static_dir / "assets"
# ⚠️ 移除：app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# ⚠️ 移除：@app.get("/{full_path:path}") 的 serve_spa 路由

if __name__ == "__main__":
    # 配置文件路径
    cfg_path = DATA_DIR / "config.json"
    
    host = "0.0.0.0"
    # 【关键清理】：端口硬编码为 8000
    # 这是 Supervisor 启动时 Uvicorn 实际监听的端口，供 Nginx 内部反向代理使用。
    port = 8000 
    reload = True

    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            server_cfg = cfg.get("server", {})
            host = server_cfg.get("host", host)
            # 即使配置文件里有 port 字段，Supervisor 启动时也会覆盖为 8000
            # 这里保持不变，以防其他地方用到配置
            reload = server_cfg.get("reload", True)
        except Exception:
            pass

    # ⚠️ 注意：在 Supervisor 模式下，实际启动命令在 supervisord.conf 中，
    # 这里的代码主要用于本地调试或作为 Supervisor 的目标程序。
    uvicorn.run(
        "main:app", 
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )