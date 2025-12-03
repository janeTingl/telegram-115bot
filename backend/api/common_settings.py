from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.db import get_all_config, save_all_config
from utils.emby_client import EmbyClient # 确保 backend/utils/emby_client.py 存在

router = APIRouter(tags=["Settings"])

# --- Pydantic 数据模型 (用于验证前端发来的 JSON) ---
class Cloud115Config(BaseModel):
    cookies: str
    uid: str

class EmbyConfig(BaseModel):
    host: str
    api_key: str
    qps: int

class TgConfig(BaseModel):
    bot_token: str
    chat_id: str

# 对应前端 AppConfig 接口的总结构
class AppConfigModel(BaseModel):
    cloud115: Cloud115Config
    emby: EmbyConfig
    telegram: TgConfig

# Emby 测试请求模型
class EmbyTestRequest(BaseModel):
    host: str
    api_key: str

# --- 路由定义 ---

@router.get("/api/config", response_model=AppConfigModel)
def get_config_api():
    """
    获取当前后端存储的所有配置
    """
    try:
        config = get_all_config()
        # 构造符合前端要求的嵌套结构
        return {
            "cloud115": {
                "cookies": config.get("115_cookies", ""),
                "uid": config.get("115_uid", "")
            },
            "emby": {
                "host": config.get("emby_host", ""),
                "api_key": config.get("emby_api_key", ""),
                "qps": int(config.get("emby_qps", 1))
            },
            "telegram": {
                "bot_token": config.get("tg_bot_token", ""),
                "chat_id": config.get("tg_chat_id", "")
            }
        }
    except Exception as e:
        # 如果数据库读取失败，返回一个空结构防止前端报错
        print(f"Error loading config: {e}")
        return {
            "cloud115": {"cookies": "", "uid": ""},
            "emby": {"host": "", "api_key": "", "qps": 1},
            "telegram": {"bot_token": "", "chat_id": ""}
        }

@router.post("/api/config")
def update_config_api(data: AppConfigModel):
    """
    保存配置到数据库/文件
    """
    try:
        # 将嵌套对象扁平化，存入 key-value 数据库
        updates = {
            "115_cookies": data.cloud115.cookies,
            "115_uid": data.cloud115.uid,
            "emby_host": data.emby.host,
            "emby_api_key": data.emby.api_key,
            "emby_qps": str(data.emby.qps), # 存为字符串通用性更好
            "tg_bot_token": data.telegram.bot_token,
            "tg_chat_id": data.telegram.chat_id
        }
        save_all_config(updates)
        return {"code": 0, "message": "Configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")

@router.post("/api/emby/test")
def test_emby(req: EmbyTestRequest):
    """
    测试 Emby 连接
    """
    if not req.host or not req.api_key:
        return {"success": False, "error": "Host or API Key is missing"}

    try:
        # 使用我们之前写的 EmbyClient 进行测试
        client = EmbyClient(host=req.host, api_key=req.api_key, timeout=5)
        info = client.get_system_info()
        
        return {
            "success": True,
            "serverName": info.get('ServerName', 'Unknown'),
            "version": info.get('Version', 'Unknown')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}