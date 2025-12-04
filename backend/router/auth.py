# backend/router/auth.py
from fastapi import APIRouter, Form
from core.db import get_config, set_config
from typing import Optional
from core.utils import generate_base32_secret
from core.utils import verify_totp

router = APIRouter()

@router.post("/auth/login")
async def login(password: str = Form(...)):
    saved_password = get_config("admin_password") or get_config("password") or "admin"
    
    if password == saved_password:
        return {"code": 0, "msg": "登录成功", "data": {"token": "ok"}}
    else:
        return {"code": 1, "msg": "密码错误"}

@router.post("/auth/password")
async def api_set_password(new_password: str = Form(...)):
    if not new_password:
        return {"code": 1, "msg": "新密码不能为空"}
    
    try:
        set_config("admin_password", new_password)
        set_config("password", new_password)
        return {"code": 0, "msg": "密码修改成功"}
    except Exception as e:
        return {"code": 500, "msg": f"保存失败: {e}"}

@router.get("/auth/2fa/generate")
async def api_2fa_generate():
    secret = generate_base32_secret()
    otpauth_url = f"otpauth://totp/115BotAdmin?secret={secret}&issuer=115Bot"
    
    return {
        "code": 0, 
        "msg": "密钥生成成功", 
        "data": {
            "secret": secret,
            "otpauth_url": otpauth_url
        }
    }

@router.post("/auth/2fa/verify")
async def api_2fa_verify(
    secret: str = Form(...),
    code: str = Form(...)
):
    if not secret or not code:
        return {"code": 1, "msg": "密钥和验证码不能为空"}

    is_valid = verify_totp(secret, code)
    
    if is_valid:
        try:
            set_config("twoFactorSecret", secret)
            return {"code": 0, "msg": "2FA 验证成功，已启用"}
        except Exception as e:
            return {"code": 500, "msg": f"保存密钥失败: {e}"}
    else:
        return {"code": 2, "msg": "验证码错误，请检查时间同步"}