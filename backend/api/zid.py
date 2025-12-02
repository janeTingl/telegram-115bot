# backend/api/zid.py
from fastapi import APIRouter
from core.zid_loader import ZID_CACHE, load_zid
router = APIRouter()

@router.get("/api/zid/list")
def api_zid_list():
    return {"code": 0, "data": ZID_CACHE}

@router.post("/api/zid/reload")
def api_zid_reload():
    global ZID_CACHE
    ZID_CACHE = load_zid()
    return {"code": 0, "msg": "reloaded"}
