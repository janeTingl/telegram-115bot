# backend/router/config.py

from fastapi import APIRouter
from core.db import get_all_config, set_all_config 
from pydantic import BaseModel
from typing import Optional, Dict, Any

# 假设 AppConfig 定义在其他地方，这里只用一个通用的 BaseModel 代替
class FullAppConfig(BaseModel):
    # 实际项目中，这里是完整的配置结构
    pass 

router = APIRouter()

# ... (现有的 ProxyConfig 和 api_set_proxy_config 接口保持不变) ...

@router.get("/api/config/load")
async def api_config_load():
    try:
        config_data = get_all_config() 
        return {"code": 0, "msg": "配置加载成功", "data": config_data}
    except Exception as e:
        return {"code": 500, "msg": f"配置读取失败: {e}"}

@router.post("/api/config/save_all")
async def api_config_save_all(config: Dict[str, Any]):
    try:
        set_all_config(config)
        return {"code": 0, "msg": "配置已保存"}
    except Exception as e:
        return {"code": 500, "msg": f"配置保存失败: {e}"}