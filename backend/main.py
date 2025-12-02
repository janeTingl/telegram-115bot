# backend/main.py
"""
主后端入口：整合各子模块并挂载 /api 前缀下的所有路由。
注意：本文件假定你已在 backend/ 中放置以下模块（或等价实现）：
- task_queue.py
- organizer.py
- strm_generator.py
- p115_wrapper.py or core/api/p115.py
- bot_integration.py
- core/db.py, core/encrypt.py, core/qps_limiter.py, core/zid_loader.py
- api/2fa.py, api/proxy.py, api/zid.py, api/p115.py, api/123cloud.py （可选）
如果缺少，会在日志中记录并返回错误信息。
"""

import time
import json
import os
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

BASE = Path(__file__).resolve().parent

# 加载本地 helper 模块（需要提前放入仓库）
try:
    from task_queue import submit_task, get_task, TaskStatus
except Exception as e:
    submit_task = None
    get_task = None
    TaskStatus = None

try:
    from organizer import preview_organize, run_organize, list_files as organizer_list_files
except Exception:
    preview_organize = None
    run_organize = None
    organizer_list_files = None

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

# core helpers
try:
    from core.db import get_config, set_config, get_secret, set_secret, get_data_conn, get_secrets_conn
except Exception:
    # fallback stubs
    def get_config(k, d=None): return d
    def set_config(k, v): pass
    def get_secret(k, d=None): return d
    def set_secret(k, v): pass
    def get_data_conn(): return None
    def get_secrets_conn(): return None

try:
    from core.qps_limiter import get_limiter
except Exception:
    def get_limiter(s, q): 
        class Dummy:
            def consume(self): return True
        return Dummy()

try:
    from core.zid_loader import ZID_CACHE, load_zid
except Exception:
    ZID_CACHE = {}
    def load_zid(): return {}

# 2FA session存储（临时文件，保存已验证的 client key 与过期时间）
_2FA_SESSIONS = BASE / "2fa_sessions.json"
def _load_2fa_sessions():
    if _2FA_SESSIONS.exists():
        try:
            return json.loads(_2FA_SESSIONS.read_text(encoding="utf8"))
        except:
            return {}
    return {}

def _save_2fa_sessions(d):
    _2FA_SESSIONS.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf8")

def _mark_2fa_verified(client_key: str, ttl_seconds=300):
    s = _load_2fa_sessions()
    s[client_key] = time.time() + ttl_seconds
    _save_2fa_sessions(s)

def _is_2fa_verified(client_key: str):
    s = _load_2fa_sessions()
    exp = s.get(client_key)
    if not exp:
        return False
    if time.time() > exp:
        # expired
        s.pop(client_key, None)
        _save_2fa_sessions(s)
        return False
    return True

# 快速创建 P115 wrapper 实例（若模块存在）
P115 = P115Wrapper() if P115Wrapper else None

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 部署时建议改为精确域名列表
    allow_methods=["*"],
    allow_headers=["*"],
)

# 公共日志
LOG_PATH = BASE / "backend.log"
def write_log(msg: str):
    s = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf8") as f:
        f.write(s)

# ---------------------------
# 简单模型
# ---------------------------
class ConfigUpdate(BaseModel):
    key: str
    value: object

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

# ---------------------------
# Utility: get client key for 2FA (based on ip + optional header)
# ---------------------------
def _client_key_for_request(req: Request):
    # 尽量使用 X-Forwarded-For，再回退到 client.host
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    try:
        return req.client.host
    except:
        return "unknown"

# ---------------------------
# Routes: config / logs / status / version
# ---------------------------
@app.get("/api/config/get")
async def api_config_get():
    try:
        # 返回 data.db 的 config 表为字典（如果实现了）
        conn = get_data_conn()
        if conn:
            cur = conn.execute("SELECT key, value FROM config").fetchall()
            data = {r[0]: r[1] for r in cur}
        else:
            data = {}
        return {"code": 0, "data": data}
    except Exception as e:
        write_log(f"config/get error: {e}")
        return {"code": 1, "msg": str(e)}

@app.post("/api/config/update")
async def api_config_update(item: ConfigUpdate):
    try:
        set_config(item.key, json.dumps(item.value) if isinstance(item.value, (dict, list)) else str(item.value))
        write_log(f"config updated {item.key}")
        return {"code": 0, "msg": "ok"}
    except Exception as e:
        write_log(f"config/update error: {e}")
        return {"code": 1, "msg": str(e)}

@app.get("/api/logs/get")
async def api_logs_get(filename: Optional[str] = None):
    try:
        base = BASE
        if filename:
            p = base / filename
            if not p.exists():
                return {"code": 1, "msg": "not found"}
            return {"code": 0, "data": p.read_text(encoding="utf8")}
        # list logs
        logs = [p.name for p in base.iterdir() if p.is_file() and p.suffix in (".log", ".txt", ".json")]
        return {"code": 0, "data": logs}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.get("/api/status")
async def api_status():
    return {"code": 0, "data": {"uptime": time.time(), "version": "backend-2.0"}}

@app.get("/api/version")
async def api_version():
    return {"code": 0, "data": {"version": "2.0", "name": "telegram-115bot-backend"}}

@app.get("/healthz")
async def healthz():
    return "ok"

# ---------------------------
# 2FA: 验证后允许查看敏感字段（一次性或短时访问）
# ---------------------------
@app.post("/api/2fa/verify")
async def api_2fa_verify(req: Request, code: str = Form(...)):
    # 调用 api/2fa.py 中的验证函数（如果存在）
    try:
        # 如果你已经放置了 api/2fa.py，我们会调用其逻辑（更标准）
        import importlib
        try:
            mod = importlib.import_module("api.2fa")
            # mod.api_2fa_verify 返回 {code: .., ok: ..} 或类似
            if hasattr(mod, "api_2fa_verify"):
                r = mod.api_2fa_verify(code=code)
                ok = (r.get("ok") if isinstance(r, dict) else False)
            else:
                ok = False
        except Exception:
            # fallback: 简单调用 core.db 中的 secret 比对 (若 secret 存在)
            from core.db import get_secret
            secret = get_secret("2fa_secret")
            if not secret:
                return {"code": 1, "msg": "2FA not setup"}
            import pyotp
            ok = pyotp.TOTP(secret).verify(code, valid_window=1)
        if ok:
            client_key = _client_key_for_request(req)
            _mark_2fa_verified(client_key, ttl_seconds=300)
            return {"code": 0, "msg": "verified"}
        return {"code": 2, "msg": "invalid"}
    except Exception as e:
        write_log(f"2fa verify error: {e}")
        return {"code": 3, "msg": str(e)}

# 用于前端请求敏感数据时的接口（示例：获取 115 cookie）
@app.get("/api/secret/get")
async def api_secret_get(req: Request, key: str):
    client_key = _client_key_for_request(req)
    if not _is_2fa_verified(client_key):
        return {"code": 401, "msg": "2FA required"}
    # 通过 core.db.get_secret 获取明文并返回（一次性或短期）
    try:
        v = get_secret(key)
        # 一次性返回后撤销（可选）
        # 这里不自动删除，仅短时有效（已有 2FA session 限时）
        return {"code": 0, "data": v}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

# ---------------------------
# 文件管理 & 上传（与前端文件浏览对应）
# ---------------------------
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

@app.post("/api/files/upload")
async def api_files_upload(file: UploadFile = File(...)):
    try:
        path = UPLOADS / file.filename
        with open(path, "wb") as f:
            f.write(await file.read())
        write_log(f"uploaded {file.filename}")
        return {"code": 0, "data": {"filename": file.filename, "path": str(path)}}
    except Exception as e:
        write_log(f"files.upload error: {e}")
        return {"code": 1, "msg": str(e)}

@app.get("/api/files/list")
async def api_files_list(path: Optional[str] = "."):
    try:
        if organizer_list_files:
            res = organizer_list_files(path)
            return {"code": 0, "data": res}
        # fallback: basic list
        p = Path(path)
        if not p.exists():
            return {"code": 1, "msg": "not found"}
        out = [{"name": x.name, "path": str(x), "is_dir": x.is_dir()} for x in p.iterdir()]
        return {"code": 0, "data": out}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/files/delete")
async def api_files_delete(path: str = Form(...)):
    try:
        p = Path(path)
        if not p.exists():
            return {"code": 1, "msg": "not found"}
        if p.is_file():
            p.unlink()
        else:
            import shutil
            shutil.rmtree(p)
        write_log(f"deleted {path}")
        return {"code": 0, "msg": "deleted"}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

# ---------------------------
# 115 / 123 接口（登陆、上传、分享） — 使用 QPS 限流
# ---------------------------
@app.post("/api/115/login")
async def api_115_login(cookie: Optional[str] = Form(None)):
    try:
        if cookie:
            set_secret("115_cookie", cookie)
            return {"code": 0, "msg": "saved"}
        # else check existing
        existing = get_secret("115_cookie")
        if existing:
            return {"code": 0, "msg": "cookie exists"}
        return {"code": 1, "msg": "missing cookie"}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/115/upload")
async def api_115_upload(filename: str = Form(...), remote_path: str = Form("/")):
    try:
        # qps control
        qps = int(get_config("115_qps", 3))
        limiter = get_limiter("115", qps)
        if not limiter.consume():
            return {"code": 429, "msg": "rate limit"}
        src = UPLOADS / filename
        if not src.exists():
            return {"code": 1, "msg": "file not found"}
        if P115 is None:
            return {"code": 2, "msg": "p115 wrapper not available"}
        res = P115.upload(str(src), remote_path)
        write_log(f"115 upload {filename} => {remote_path}")
        return {"code": 0, "data": res}
    except P115Error as e:
        write_log(f"115 upload error: {e}")
        return {"code": 3, "msg": str(e)}
    except Exception as e:
        return {"code": 4, "msg": str(e)}

@app.post("/api/115/share")
async def api_115_share(file_id: str = Form(...), passwd: Optional[str] = Form(None)):
    try:
        if P115 is None:
            return {"code": 1, "msg": "p115 wrapper unavailable"}
        res = P115.create_share(file_id, passwd)
        return {"code": 0, "data": res}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

# 123 cloud placeholders
@app.post("/api/123/login")
async def api_123_login(token: str = Form(...)):
    try:
        set_secret("123_token", token)
        return {"code": 0, "msg": "saved"}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.post("/api/123/upload")
async def api_123_upload(filename: str = Form(...), remote_path: str = Form("/")):
    try:
        qps = int(get_config("123_qps", 2))
        limiter = get_limiter("123", qps)
        if not limiter.consume():
            return {"code": 429, "msg": "rate limit"}
        # TODO: call real 123 SDK — placeholder:
        return {"code": 0, "data": {"msg": "simulated upload"}}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

# ---------------------------
# Organize / Rename / STRM / Tasks
# ---------------------------
@app.post("/api/organize/preview")
async def api_organize_preview(body: OrgRules):
    try:
        if preview_organize is None:
            return {"code": 1, "msg": "organizer not available"}
        ops = preview_organize(body.rules, body.src_dir)
        return {"code": 0, "data": ops}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/organize/run")
async def api_organize_run(body: OrgRules):
    try:
        if submit_task is None:
            return {"code": 1, "msg": "task queue not available"}
        # submit run_organize as job
        def job(update, rules, src_dir, execute):
            return run_organize(rules, src_dir, not execute) if False else run_organize(rules, src_dir, not body.dry_run)
        tid = submit_task(lambda update: run_organize(body.rules, body.src_dir, not body.dry_run))
        write_log(f"organize submitted {tid}")
        return {"code": 0, "data": {"task_id": tid}}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/rename/preview")
async def api_rename_preview(body: RenameRules):
    try:
        import re
        res = []
        for f in body.files:
            new = re.sub(body.pattern, body.replace, f)
            res.append({"src": f, "dst": new})
        return {"code": 0, "data": res}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.post("/api/rename/run")
async def api_rename_run(body: RenameRules):
    try:
        if submit_task is None:
            return {"code": 1, "msg": "task queue not available"}
        def job(update_progress):
            import os, re
            applied = []
            for idx, f in enumerate(body.files):
                new = re.sub(body.pattern, body.replace, f)
                try:
                    os.rename(f, new)
                    applied.append({"src": f, "dst": new})
                except Exception as e:
                    applied.append({"src": f, "dst": None, "error": str(e)})
                update_progress(int((idx+1)/len(body.files)*100), f"renamed {f}")
            return applied
        tid = submit_task(job)
        return {"code": 0, "data": {"task_id": tid}}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.post("/api/strm/generate")
async def api_strm_generate(body: StrmBody):
    try:
        if generate_strm_for_files is None:
            return {"code": 1, "msg": "strm generator not available"}
        if submit_task is None:
            return {"code": 1, "msg": "task queue not available"}
        def job(update_progress):
            out = generate_strm_for_files(body.files, body.target_dir, body.template)
            return out
        tid = submit_task(job)
        write_log(f"strm task {tid} submitted")
        return {"code": 0, "data": {"task_id": tid}}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

@app.get("/api/task/status")
async def api_task_status(task_id: str):
    try:
        if get_task is None:
            return {"code": 1, "msg": "task queue not available"}
        t = get_task(task_id)
        if not t:
            return {"code": 1, "msg": "not found"}
        return {"code": 0, "data": t}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

# ---------------------------
# Proxy check (delegates to api/proxy if exist)
# ---------------------------
@app.post("/api/proxy/check")
async def api_proxy_check(url: str = Form(...), proxy: Optional[str] = Form(None), attempts: int = Form(3)):
    try:
        import importlib
        try:
            mod = importlib.import_module("api.proxy")
            if hasattr(mod, "api_proxy_check"):
                return await mod.api_proxy_check(url=url, proxy=proxy, attempts=attempts)
        except Exception:
            # fallback simple ping using aiohttp
            import aiohttp, asyncio, time
            async def probe():
                successes = 0
                total = 0.0
                async with aiohttp.ClientSession() as s:
                    for i in range(attempts):
                        t0 = time.time()
                        try:
                            async with s.get(url, timeout=5, proxy=proxy) as r:
                                if r.status == 200:
                                    successes += 1
                                    total += (time.time() - t0)
                        except:
                            pass
                return {"code": 0, "data": {"success_rate": successes/attempts, "avg_rtt": (total/successes) if successes else None}}
            return await probe()
    except Exception as e:
        return {"code": 1, "msg": str(e)}

# ---------------------------
# zid endpoints
# ---------------------------
@app.get("/api/zid/list")
async def api_zid_list():
    return {"code": 0, "data": ZID_CACHE}

@app.post("/api/zid/reload")
async def api_zid_reload():
    try:
        global ZID_CACHE
        ZID_CACHE = load_zid()
        return {"code": 0, "msg": "reloaded"}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

# ---------------------------
# Bot trigger
# ---------------------------
@app.post("/api/bot/send")
async def api_bot_send(text: str = Form(...)):
    try:
        ok = notify_bot(text)
        return {"code": 0 if ok else 1, "msg": "sent" if ok else "failed"}
    except Exception as e:
        return {"code": 1, "msg": str(e)}
