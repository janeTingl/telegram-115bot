# backend/api/p115.py
from fastapi import APIRouter, Form
from core.db import get_secret, set_secret
from core.qps_limiter import get_limiter
import importlib

router = APIRouter()

# 尝试导入仓库中的 p115client
try:
    p115client = importlib.import_module("p115client")
except Exception:
    p115client = None

def _get_qps(service):
    # 从 data.db 或 config 获取 qps（后面实现）
    from core.db import get_config
    q = get_config(f"{service}_qps", "3")
    try:
        return int(q)
    except:
        return 3

@router.post("/api/115/login")
def api_115_login(cookie: str = Form(None)):
    # 存 cookie 入 secrets（加密）
    if cookie:
        set_secret("115_cookie", cookie)
        return {"code": 0, "msg": "saved"}
    else:
        return {"code": 1, "msg": "missing cookie"}

@router.post("/api/115/upload")
def api_115_upload(filename: str = Form(...), remote_path: str = Form("/")):
    # 限流
    qps = _get_qps("115")
    limiter = get_limiter("115", qps)
    if not limiter.consume():
        return {"code": 429, "msg": "rate limit"}
    # use p115client to upload
    cookie = get_secret("115_cookie")
    if not p115client:
        return {"code": 1, "msg": "p115client not installed"}
    # the exact API varies — this layer will try common methods
    client = None
    try:
        if hasattr(p115client, "P115Client"):
            client = p115client.P115Client()  # may accept cookie or session load
        else:
            client = p115client
    except Exception as e:
        return {"code": 2, "msg": f"init p115client error: {e}"}
    try:
        # try common upload names
        for name in ("upload_file","upload","fs_upload","files_upload"):
            if hasattr(client, name):
                fn = getattr(client, name)
                # prefer (local, remote) signature
                return {"code": 0, "data": fn(filename, remote_path)}
        return {"code": 3, "msg": "no known upload function in p115client"}
    except Exception as e:
        return {"code": 4, "msg": str(e)}
