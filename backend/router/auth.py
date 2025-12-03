# backend/router/auth.py
from fastapi import APIRouter, Form
from core.db import get_config, set_config
from typing import Optional

router = APIRouter()

@router.post("/login")
async def login(password: str = Form(...)):
    saved_password = get_config("admin_password") or get_config("password") or "admin"
    
    if password == saved_password:
        return {"code": 0, "msg": "登录成功", "data": {"token": "ok"}}
    else:
        return {"code": 1, "msg": "密码错误"}

@router.post("/api/auth/password")
async def api_set_password(new_password: str = Form(...)):
    if not new_password:
        return {"code": 1, "msg": "新密码不能为空"}
    
    try:
        set_config("admin_password", new_password)
        set_config("password", new_password) 
        return {"code": 0, "msg": "密码修改成功"}
    except Exception as e:
        return {"code": 500, "msg": f"保存失败: {e}"}