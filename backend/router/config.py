# backend/router/config.py
from fastapi import APIRouter
from core.db import set_config 
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProxyConfig(BaseModel):
    enabled: bool
    type: str
    host: str
    port: str # 使用 str 兼容前端 input

@router.post("/api/config/proxy")
async def api_set_proxy_config(config: ProxyConfig):
    try:
        set_config("proxy", config.model_dump()) 
        return {"code": 0, "msg": "代理配置保存成功"}
    except Exception as e:
        return {"code": 500, "msg": f"保存失败: {e}"}