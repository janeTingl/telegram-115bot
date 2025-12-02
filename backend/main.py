from fastapi.staticfiles import StaticFiles
import os
import json
import logging
import asyncio
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from backend.routers import network

from backend.routers import security
from backend.routers import netdisk


from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import Scope, Receive, Send
from tmdbv3api import Trending
from backend.config.manager import CONFIG

# 引入各个服务模块
from backend.services.service_115 import drive_115
from backend.services.service_123 import drive_123
from backend.services.service_openlist import drive_openlist
from backend.services.service_organizer import organizer
from backend.services.service_strm import strm_gen
from backend.services.service_ai import ai_service
from backend.services.auth_service import auth_service
from backend.utils.proxy import apply_global_proxy
from backend.webdav_server import webdav_manager
from backend.bot import run_bot

# --- 配置与日志 ---
DATA_DIR = "/data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Main")
log_buffer = []

# 配置自定义日志处理器以供前端读取


class MemoryHandler(logging.Handler):
    def emit(self, record):
        entry = {
            "time": record.asctime.split(',')[0],
            "status": record.levelname,
            "task": record.name,
            "result": record.getMessage()
        }
        log_buffer.append(entry)
        if len(log_buffer) > 200: log_buffer.pop(0)


logging.getLogger().addHandler(MemoryHandler())

# --- 工具函数 ---


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    return {}


def save_config_disk(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f: json.dump(data, f, indent=2)


def reload_services(config):
    # 1. 应用代理 (最优先)
    apply_global_proxy(config)

    # 2. 重载各网盘服务
    c115 = config.get("cloud115", {})
    if c115.get("cookies"):
        drive_115.init_client(c115["cookies"], c115.get("loginApp", "web"))

    c123 = config.get("cloud123", {})
    if c123.get("clientId"):
        drive_123.init_config(c123["clientId"], c123["clientSecret"])

    ol = config.get("openList", {})
    if ol.get("url"):
        drive_openlist.init_config(
    ol["url"],
    ol.get("username"),
    ol.get("password"))

# --- WebDAV 动态代理中间件 ---
# 用于将 /dav 请求转发给动态生成的 WebDAV App


class DynamicWebDAVProxy:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if webdav_manager.asgi_app:
            await webdav_manager.asgi_app(scope, receive, send)
        else:
            await send({
                "type": "http.response.start",
                "status": 503,
                "headers": [(b"content-type", b"text/plain")],
            })
            await send({
                "type": "http.response.body",
                "body": b"WebDAV service is disabled or initializing...",
            })

# --- 生命周期管理 ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("System: Backend Starting...")
    config = load_config()

    # 初始化所有业务服务
    reload_services(config)
    organizer.init_config(config)
    strm_gen.init_config(config)
    ai_service.init_config(config)

    # 初始化 WebDAV App
    strm_conf = config.get("strm", {}).get("webdav", {})
    if strm_conf.get("enabled"):
        webdav_manager.get_asgi_app(
            username=strm_conf.get("username", "admin"),
            password=strm_conf.get("password", "password")
        )

    # 启动 Telegram Bot
    # 1. 从配置管理器中获取解密后的 BOT_TOKEN
    bot_token = CONFIG.get_config("BOT_TOKEN")

    if bot_token:
    # 2. 使用获取到的 Token 启动 Bot 任务
        asyncio.create_task(run_bot(bot_token))

    yield

    logger.info("System: Shutting down...")

app = FastAPI(lifespan=lifespan)

# CORS 配置
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# --- 挂载 WebDAV 子应用 ---
# 访问地址: http://IP:12808/dav
app.mount("/dav", DynamicWebDAVProxy())

# --- API 接口 ---

# 1. 登录鉴权 (含锁定机制)


@app.post("/api/login")
async def login(credentials: Dict[str, str]):
    username = credentials.get("username")
    password = credentials.get("password")
    config = load_config()
    # 读取用户配置的密码，默认为 'password'
    saved_pass = config.get("user", {}).get("password")

    result = auth_service.check_login(username, password, saved_pass)

    if not result["success"]:
        status = 403 if result.get("locked") else 401
        raise HTTPException(status_code=status, detail=result)
    return result

# 2. 获取壁纸 (后端代理抓取 TMDB)


@app.get("/api/wallpaper/trending")
async def get_trending_wallpapers():
    config = load_config()
    tmdb_key = config.get("tmdb", {}).get("apiKey")
    if not tmdb_key: return {"images": []}

    try:
        trending = Trending()
        trending.api_key = tmdb_key
        # 请求会自动走全局代理
        results = trending.all_week()
        images = [
            f"https://image.tmdb.org/t/p/original{item.backdrop_path}" for item in results if hasattr(item, 'backdrop_path')][:8]
        return {"images": images}
    except Exception as e:
        logger.error(f"Wallpaper fetch failed: {e}")
        return {"images": []}

# 3. 配置管理 (含热重载)


@app.get("/api/config")
async def get_config_api():
    return load_config()


@app.post("/api/config")
async def save_config_api(data: Dict[str, Any]):
    save_config_disk(data)

    # 重载所有服务
    reload_services(data)
    organizer.init_config(data)
    strm_gen.init_config(data)
    ai_service.init_config(data)

    # WebDAV 热重载
    w_conf = data.get("strm", {}).get("webdav", {})
    if w_conf.get("enabled"):
        webdav_manager.get_asgi_app(
            username=w_conf.get("username", "admin"),
            password=w_conf.get("password", "password")
        )
    else:
        webdav_manager.asgi_app = None

    return {"status": "success"}

# 4. 系统状态 (Dashboard)


@app.get("/api/status")
async def get_status():
    import time
    ping = "Timeout"
    try:
        t0 = time.time()
        # 简单请求一次 115 接口测速
        if drive_115.client:
            drive_115.get_storage_info()
            ping = f"{int((time.time() - t0) * 1000)}ms"
    except: pass

    return {
        "active": True,
        "uptime": "Running",
        "connection_115": {
            "status": "Connected" if drive_115.client else "Disconnected",
            "ping": ping
        },
        "tasks": {"running": 0, "queue": 0}
    }

# 5. 日志接口


@app.get("/api/logs")
async def get_logs():
    return log_buffer

# --- 115 专属接口 ---


@app.get("/api/115/qrcode/token")
async def get_qr(): return await drive_115.get_qrcode_token()


@app.get("/api/115/qrcode/status")
async def check_qr(uid: str, time: int, sign: str):
    res = await drive_115.check_qrcode_status(uid, time, sign)
    if res["status"] == "success":
        # 扫码成功自动保存
        conf = load_config()
        if "cloud115" not in conf: conf["cloud115"] = {}
        conf["cloud115"]["cookies"] = res["cookies"]
        save_config_disk(conf)
        reload_services(conf)
    return res


@app.get("/api/115/files")
async def list_115(cid: str = "0"): return drive_115.get_file_list(cid)


@app.post("/api/trigger/115_offline")
async def dl_115(d: Dict[str, Any]): return drive_115.add_offline_task(
    d.get("urls", []), d.get("cid", "0"))

# --- 123 & OpenList 接口 ---


@app.get("/api/123/files")
async def list_123(
    parent_id: str = "0"): return await drive_123.get_file_list(parent_id)


@app.post("/api/trigger/123_offline")
async def dl_123(d: Dict[str, Any]): return await drive_123.add_offline_task(
    d.get("url"), d.get("filename"))


@app.get("/api/openlist/files")
async def list_ol(
    path: str = "/"): return await drive_openlist.get_file_list(path)

# --- 触发器接口 ---


@app.post("/api/trigger/organize")
async def trig_org():
        asyncio.create_task(organizer.run_organize())
        return {"status": "started", "msg": "整理任务已在后台启动"}

@app.post("/api/trigger/strm")
async def trig_strm():
        asyncio.create_task(strm_gen.generate_115_strm())
        asyncio.create_task(strm_gen.generate_openlist_strm())
#     return {"status": "started", "msg": "STRM 生成任务已在后台启动"}
# 
# # --- 静态文件托管 (必须放在最后) ---
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

# ==========================================
# 下面是自动添加的前端挂载代码
# ==========================================
import os
from fastapi.staticfiles import StaticFiles

# 获取根目录下的 dist 文件夹位置
dist_path = os.path.join(os.getcwd(), 'dist')

# 如果 dist 存在，就挂载它
if os.path.exists(dist_path):
    print(f"✅ 发现前端构建文件，正在挂载: {dist_path}")
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
else:
    print(f"⚠️ 未找到 {dist_path} 文件夹，仅运行后端模式")
