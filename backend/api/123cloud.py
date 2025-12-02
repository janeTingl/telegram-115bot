# backend/api/123cloud.py
from fastapi import APIRouter, Form
from core.qps_limiter import get_limiter
from core.db import get_secret, set_secret, get_config

router = APIRouter()

def _get_qps(service):
    q = get_config(f"{service}_qps", "2")
    try:
        return int(q)
    except:
        return 2

@router.post("/api/123/login")
def api_123_login(token: str = Form(...)):
    set_secret("123_token", token)
    return {"code": 0, "msg": "ok"}

@router.post("/api/123/upload")
def api_123_upload(filename: str = Form(...), remote_path: str = Form("/")):
    limiter = get_limiter("123", _get_qps("123"))
    if not limiter.consume():
        return {"code": 429, "msg": "rate limit"}
    # TODO: 调用你实际的 123 SDK（如果存在）
    return {"code": 0, "msg": "simulated upload (implement SDK call)"}
