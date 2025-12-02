# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json, os, time
from pathlib import Path

from task_queue import submit_task, get_task, TaskStatus
from organizer import preview_organize, run_organize, list_files
from strm_generator import generate_strm_for_files
from p115_wrapper import P115Wrapper, P115Error
from bot_integration import notify_bot, write_bot_log

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
CONFIG_FILE = BASE / "config.json"
LOG_FILE = BASE / "backend.log"

p115 = P115Wrapper()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def write_log(msg: str):
    with open(LOG_FILE, "a", encoding="utf8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def load_config():
    if not CONFIG_FILE.exists():
        cfg = {"115": {}, "server": {"base_path": "/api"}}
        with open(CONFIG_FILE, "w", encoding="utf8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return cfg
    return json.loads(CONFIG_FILE.read_text(encoding="utf8"))

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf8")

# -----------------------
# small models
# -----------------------
class UpdateCfg(BaseModel):
    key: str
    value: object

class OrgRules(BaseModel):
    rules: dict
    src_dir: str
    dry_run: bool = True

class RenameRules(BaseModel):
    pattern: str
    replace: str
    files: list

class StrmBody(BaseModel):
    files: list
    target_dir: str = None
    template: str = "{filepath}"

# -----------------------
# routes
# -----------------------
@app.get("/api/config/get")
def api_config_get():
    return {"code": 0, "data": load_config()}

@app.post("/api/config/update")
def api_config_update(req: UpdateCfg):
    cfg = load_config()
    cfg[req.key] = req.value
    save_config(cfg)
    write_log(f"config updated {req.key}")
    return {"code": 0, "msg": "ok"}

@app.get("/api/logs/get")
def api_logs(filename: str = None):
    if not filename:
        # return list
        logs = [p.name for p in BASE.iterdir() if p.suffix in (".log", ".txt", ".json") or "log" in p.name]
        return {"code": 0, "data": logs}
    p = BASE / filename
    if not p.exists():
        return {"code": 1, "msg": "not found"}
    return {"code": 0, "data": p.read_text(encoding="utf8")}

@app.post("/api/files/upload")
async def api_files_upload(file: UploadFile = File(...)):
    UPLOADS.mkdir(exist_ok=True)
    path = UPLOADS / file.filename
    with open(path, "wb") as f:
        f.write(await file.read())
    write_log(f"uploaded {file.filename}")
    return {"code": 0, "data": {"filename": file.filename, "path": str(path)}}

@app.get("/api/files/list")
def api_files_list(path: str = "."):
    try:
        res = list_files(path)
        return {"code": 0, "data": res}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.post("/api/files/delete")
def api_files_delete(path: str = Form(...)):
    p = Path(path)
    if not p.exists():
        return {"code": 1, "msg": "not found"}
    try:
        if p.is_file():
            p.unlink()
        else:
            import shutil
            shutil.rmtree(p)
        write_log(f"deleted {path}")
        return {"code": 0, "msg": "deleted"}
    except Exception as e:
        return {"code": 2, "msg": str(e)}

# ---------- 115 ----------
@app.post("/api/115/login")
def api_115_login(cookie: str = Form(None)):
    try:
        if cookie:
            ok = p115.login_with_cookie(cookie)
        else:
            # try default config cookie
            cfg = load_config()
            cookie = cfg.get("115", {}).get("cookie")
            if not cookie:
                return {"code": 1, "msg": "missing cookie"}
            ok = p115.login_with_cookie(cookie)
        write_log("115 login called")
        return {"code": 0, "msg": "login success"} if ok else {"code": 2, "msg": "login failed"}
    except P115Error as e:
        write_log(f"115 login error: {e}")
        return {"code": 2, "msg": str(e)}

@app.post("/api/115/upload")
def api_115_upload(filename: str = Form(...), target_path: str = Form("/")):
    src = UPLOADS / filename
    if not src.exists():
        return {"code": 1, "msg": "file not found"}
    try:
        res = p115.upload(str(src), target_path)
        write_log(f"uploaded to 115 {filename}")
        return {"code": 0, "data": res}
    except P115Error as e:
        write_log(f"115 upload error: {e}")
        return {"code": 2, "msg": str(e)}

@app.post("/api/115/share")
def api_115_share(file_id: str = Form(...), passwd: str = Form(None)):
    try:
        res = p115.create_share(file_id, passwd)
        write_log(f"create share {file_id}")
        return {"code": 0, "data": res}
    except P115Error as e:
        write_log(f"115 share error: {e}")
        return {"code": 2, "msg": str(e)}

# ---------- organize ----------
@app.post("/api/organize/preview")
def api_organize_preview(body: OrgRules):
    try:
        ops = preview_organize(body.rules, body.src_dir)
        return {"code": 0, "data": ops}
    except Exception as e:
        return {"code": 1, "msg": str(e)}

@app.post("/api/organize/run")
def api_organize_run(body: OrgRules):
    # 提交异步任务
    tid = submit_task(lambda update, r, s, d: run_organize(r, s, d), body.rules, body.src_dir, not body.dry_run)
    write_log(f"organize task submitted {tid}")
    return {"code": 0, "data": {"task_id": tid}}

# ---------- rename (轻量实现，前端会传 files & pattern/replace) ----------
@app.post("/api/rename/preview")
def api_rename_preview(body: RenameRules):
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
def api_rename_run(body: RenameRules):
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

# ---------- strm ----------
@app.post("/api/strm/generate")
def api_strm_generate(body: StrmBody):
    def job(update_progress):
        out = generate_strm_for_files(body.files, body.target_dir, body.template)
        return out
    tid = submit_task(job)
    write_log(f"strm task submitted {tid}")
    return {"code": 0, "data": {"task_id": tid}}

# ---------- task status ----------
@app.get("/api/task/status")
def api_task_status(task_id: str):
    t = get_task(task_id)
    if not t:
        return {"code": 1, "msg": "not found"}
    return {"code": 0, "data": t}

# ---------- bot ----------
@app.post("/api/bot/send")
def api_bot_send(text: str = Form(...)):
    ok = notify_bot(text)
    return {"code": 0 if ok else 1, "msg": "sent" if ok else "failed"}

# ---------- misc ----------
@app.get("/api/status")
def api_status():
    return {"code": 0, "data": {"uptime": time.time(), "version": "backend-1.0"}}

@app.get("/api/version")
def api_version():
    return {"code": 0, "data": {"version": "1.0", "name": "telegram-115bot-backend"}}

@app.get("/healthz")
def healthz():
    return "ok"
