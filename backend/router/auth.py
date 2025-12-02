# backend/router/auth.py
from fastapi import APIRouter, Form
from core.db import get_config   # 你原来存密码用的就是这个吧

router = APIRouter()

@router.post("/login")
async def login(password: str = Form(...)):
    # 从 data.db 或 config.json 里读取你设置的密码
    saved_password = get_config("admin_password") or get_config("password") or "admin"
    
    if password == saved_password:
        return {"code": 0, "msg": "登录成功", "data": {"token": "ok"}}
    else:
        return {"code": 1, "msg": "密码错误"}