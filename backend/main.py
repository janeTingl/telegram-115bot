# backend/main.py
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
dist_path = BASE_DIR / "dist"

app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
# ==================== 基础路径 ====================
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

LOG_PATH = BASE_DIR / "backend.log"
_2FA_SESSIONS_PATH = BASE_DIR / "2fa_sessions.json"


# ==================== 日志工具 ====================
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


# ==================== 模块兜底导入 ====================
try:
    from task_queue import submit_task, get_task, TaskStatus
except Exception as e:
    push_log("WARN", f"task_queue 加载失败: {e}")
    submit_task = get_task = TaskStatus = None

try:
    from organizer import preview_organize, run_organize, list_files as organizer_list_files
except Exception as e:
    push_log("WARN", f"organizer 加载失败: {e}")
    preview_organize = run_organize = organizer_list_files = None

try:
    from strm_generator import generate_strm_for_files
except Exception as e:
    push_log("WARN", f"strm_generator 加载失败: {e}")
    generate_strm_for_files = None

try:
    from p115_wrapper import P115Wrapper, P115Error
except Exception as e:
    push_log("WARN", f"p115_wrapper 加载失败: {e}")
    P115Wrapper = None
    P115Error = Exception

try:
    from bot_integration import notify_bot
except Exception:
    def notify_bot(msg, level="info"): return False

# core helpers
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


# ==================== FastAPI 实例 ====================
app = FastAPI(title="115Bot Backend", version="2.0")

# CORS（开发时全开，生产请改成具体域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ← 重点修复
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 动态挂载子路由 ====================
def _include_router(module_name: str):
    try:
        mod = __import__(module_name, fromlist=["router"])
        if hasattr(mod, "router"):
            app.include_router(mod.router, prefix="/api")
            push_log("INFO", f"成功挂载路由: {module_name}")
    except Exception as e:
        push_log("WARN", f"挂载路由 {module_name} 失败: {e}")
_include_router("router.auth")
_include_router("router.offline")
_include_router("router.file")
_include_router("router.notify")
_include_router("router.tmdb")
_include_router("router.emby")

# 兼容旧版路由（如果有 main_old.py）
try:
    from main_old import app as old_app
    app.mount("/old", old_app)
except Exception:
    pass


# ==================== 2FA 临时会话 ====================
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
    # 优先 X-Forwarded-For → X-Real-IP → remote addr
    return (
        req.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or req.headers.get("x-real-ip", "")
        or (req.client.host if req.client else "unknown")
    )


# ==================== P115 懒加载实例 ====================
_P115_INSTANCE = None
def get_p115() -> Optional[P115Wrapper]:
    global _P115_INSTANCE
    if _P115_INSTANCE is None and P115Wrapper:
        cookie = get_secret("115_cookie")
        if cookie:
            _P115_INSTANCE = P115Wrapper(cookie=cookie)
        else:
            _P115_INSTANCE = False  # 标记已尝试过
    return _P115_INSTANCE if _P115_INSTANCE and _P115_INSTANCE is not False else None


# ==================== Pydantic Models ====================
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


# ==================== 基础接口 ====================
@app.get("/healthz")
async def healthz():
    return "ok"

@app.get("/api/status")
async def status():
    return {"code": 0, "data": {"uptime": time.time(), "version": "backend-2.0"}}

@app.get("/api/version")
async def version():
    return {"code": 0, "data": {"version": "2.0", "name": "telegram-115bot-backend"}}


# ==================== 配置 & 日志 ====================
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
        write_log(f"config/get error: {e}")
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
        write_log(f"config/update error: {e}")
        return {"code": 1, "msg": str(e)}


# ==================== 2FA ====================
@app.post("/api/2fa/verify")
async def api_2fa_verify(req: Request, code: str = Form(...)):
    try:
        # 优先使用独立 2fa 模块
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

        # fallback: 数据库里的 secret
        secret = get_secret("2fa_secret")
        if not secret:
            return {"code": 1, "msg": "2FA not configured"}
        import pyotp
        if pyotp.TOTP(secret).verify(code, valid_window=1):
            _mark_2fa_verified(_client_key(req))
            return {"code": 0, "msg": "verified"}
        return {"code": 2, "msg": "invalid code"}
    except Exception as e:
        write_log(f"2fa verify error: {e}")
        return {"code": 3, "msg": str(e)}

@app.get("/api/secret/get")
async def secret_get(req: Request, key: str):
    if not _is_2fa_verified(_client_key(req)):
        raise HTTPException(401, "2FA required")
    value = get_secret(key)
    return {"code": 0, "data": value or ""}


# ==================== 文件上传与管理 ====================
@app.post("/api/files/upload")
async def filesureq(file: UploadFile = File(...)):
    safe_name = Path(file.filename).name  # 防止目录穿越
    dest = UPLOADS_DIR / safe_name
    content = await file.read()
    dest.write_bytes(content)
    write_log(f"uploaded {safe_name} ({len(content)} bytes)")
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


# ==================== 115 接口 ====================
@app.post("/api/115/login")
async def api_115_login(cookie: Optional[str] = Form(None)):
    if cookie:
        set_secret("115_cookie", cookie.strip())
        global _P115_INSTANCE
        _P115_INSTANCE = None  # 强制重新初始化
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

    src = UPLOADS_DIR / Path(filename).name
    if not src.exists():
        return {"code": 1, "msg": "local file not found"}

    try:
        result = p115.upload(str(src), remote_path)
        write_log(f"115 upload success: {filename} → {remote_path}")
        return {"code": 0, "data": result}
    except P115Error as e:
        write_log(f"115 upload failed: {e}")
        return {"code": 3, "msg": str(e)}
    except Exception as e:
        write_log(f"115 upload exception: {e}")
        return {"code": 4, "msg": str(e)}


# ==================== 整理、改名、生成 strm ====================
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
    write_log(f"organize task submitted: {tid}")
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
    write_log(f"strm generate task {tid} submitted")
    return {"code": 0, "data": {"task_id": tid}}


@app.get("/api/task/status")
async def task_status(task_id: str):
    if not get_task:
        return {"code": 1, "msg": "task system unavailable"}
    t = get_task(task_id)
    if not t:
        return {"code": 2, "msg": "task not found"}
    return {"code": 0, "data": t}


# ==================== 其它 ====================
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


# ==================== 启动 ====================
if __name__ == "__main__":
    cfg_path = BASE_DIR / "config.json"
    host = "0.0.0.0"
    port = 12808
    reload = True

    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            server_cfg = cfg.get("server", {})
            host = server_cfg.get("host", host)
            port = server_cfg.get("port", port)
            reload = server_cfg.get("reload", True)
        except Exception as e:
            push_log("WARN", f"读取 config.json 失败，使用默认配置: {e}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

# ==================== 前端静态文件服务（必须放在文件最外面，不能缩进） ====================
import os
from fastapi.staticfiles import StaticFiles

# 前端 build 输出目录（容器里路径）
FRONTEND_DIR = "/app/frontend/dist"  # <- 根据你 Dockerfile 中的路径修改

# 如果目录不存在，则创建空目录（避免启动报错）
if not os.path.exists(FRONTEND_DIR):
    print(f"⚠️ 目录 '{FRONTEND_DIR}' 不存在，创建空目录")
    os.makedirs(FRONTEND_DIR, exist_ok=True)

# 挂载前端静态文件
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
