# backend/main.py
import json
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 统一在这里导入
from pydantic import BaseModel

# ==================== 基础配置 ====================
# 获取当前文件所在的目录 (即 backend 目录)
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
# ... (保持你原有的 try/except 导入逻辑不变，为了节省篇幅我略过了中间未修改的 import 部分) ...
# 请保留你原始代码中 task_queue, organizer, strm_generator, p115_wrapper 等模块的导入部分
# ... 

# 为了代码完整性，这里简写几个关键的 dummy 导入，实际使用请保留你原来的代码
try:
    from task_queue import submit_task, get_task
except: submit_task = get_task = None
try:
    from organizer import preview_organize, run_organize, list_files as organizer_list_files
except: preview_organize = run_organize = organizer_list_files = None
try:
    from strm_generator import generate_strm_for_files
except: generate_strm_for_files = None
try:
    from p115_wrapper import P115Wrapper, P115Error
except: P115Wrapper = None; P115Error = Exception
try:
    from bot_integration import notify_bot
except: notify_bot = lambda m: False
try:
    from core.db import get_config, set_config, get_secret, set_secret, get_data_conn
except: 
    get_config = lambda k, d=None: d
    set_config = lambda k, v: None
    get_secret = lambda k, d=None: d
    set_secret = lambda k, v: None
    get_data_conn = lambda: None
try:
    from core.qps_limiter import get_limiter
except: get_limiter = lambda s, q: type('D',(),{'consume':lambda s:True})()

# ==================== FastAPI 实例初始化 ====================
app = FastAPI(title="115Bot Backend", version="2.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 动态挂载 API 路由 ====================
def _include_router(module_name: str):
    try:
        mod = __import__(module_name, fromlist=["router"])
        if hasattr(mod, "router"):
            app.include_router(mod.router, prefix="/api")
            push_log("INFO", f"成功挂载路由: {module_name}")
    except Exception as e:
        push_log("WARN", f"挂载路由 {module_name} 失败: {e}")

# 挂载你的 routers
_include_router("router.auth")
_include_router("router.offline")
_include_router("router.file")
_include_router("router.notify")
_include_router("router.tmdb")
_include_router("router.emby")

# ==================== 业务逻辑函数 (保持不变) ====================
# 这里保留你原来代码中的:
# _load_2fa_sessions, _save_2fa_sessions, _mark_2fa_verified, _is_2fa_verified, _client_key
# get_p115
# Pydantic Models (ConfigUpdate, OrgRules 等)
# 以及所有的 API 接口 (@app.get/post ...)
# ... (为了篇幅，这里假设你原来的业务逻辑代码都在这里) ...
# 请直接把你原文件从 "_load_2fa_sessions" 开始 到 "if __name__ == '__main__':" 之前的内容粘贴在这里

# ==================== 【关键修改】前端静态文件挂载 ====================
# 必须在 uvicorn.run 之前执行！

# 1. 定义可能的路径：优先 Docker 路径，其次本地开发路径
DOCKER_FRONTEND_DIR = Path("/app/frontend/dist")
LOCAL_FRONTEND_DIR = BASE_DIR.parent / "frontend/dist" # 假设在 backend 的上一级

if DOCKER_FRONTEND_DIR.exists():
    static_dir = DOCKER_FRONTEND_DIR
    push_log("INFO", f"使用 Docker 前端目录: {static_dir}")
elif LOCAL_FRONTEND_DIR.exists():
    static_dir = LOCAL_FRONTEND_DIR
    push_log("INFO", f"使用本地开发前端目录: {static_dir}")
else:
    # 如果都不存在（比如第一次启动），创建一个空目录防止报错，但页面会是 404
    static_dir = DOCKER_FRONTEND_DIR
    push_log("WARN", f"⚠️ 前端目录不存在，创建空目录: {static_dir}")
    os.makedirs(static_dir, exist_ok=True)

# 2. 挂载静态文件
# html=True 表示访问 / 时自动寻找 index.html
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# ==================== 启动入口 ====================
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

    print(f"🚀 服务启动中: http://{host}:{port}")
    print(f"📂 前端静态资源目录: {static_dir}")

    uvicorn.run(
        "main:app",  # 注意这里引用的是字符串，对应文件名 main.py 和变量 app
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )