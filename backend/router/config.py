# backend/router/config.py

from fastapi import APIRouter
from core.db import get_all_config, set_all_config, set_config
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()


class ProxyConfig(BaseModel):
    enabled: bool
    type: str
    host: str
    port: str


@router.get("/config/load")
async def api_config_load():
    try:
        config_data = get_all_config() 
        return {"code": 0, "msg": "配置加载成功", "data": config_data}
    except Exception as e:
        return {"code": 500, "msg": f"配置读取失败: {e}"}


@router.post("/config/save_all")
async def api_config_save_all(config: Dict[str, Any]):
    try:
        set_all_config(config)
        return {"code": 0, "msg": "配置已保存"}
    except Exception as e:
        return {"code": 500, "msg": f"配置保存失败: {e}"}


@router.post("/config/proxy")
async def api_set_proxy_config(proxy_config: ProxyConfig):
    """保存代理配置"""
    try:
        set_config("proxy.enabled", str(proxy_config.enabled))
        set_config("proxy.type", proxy_config.type)
        set_config("proxy.host", proxy_config.host)
        set_config("proxy.port", proxy_config.port)
        return {"code": 0, "msg": "代理配置已保存"}
    except Exception as e:
        return {"code": 500, "msg": f"保存代理配置失败: {e}"}