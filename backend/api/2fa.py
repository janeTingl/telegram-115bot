# backend/api/2fa.py
from fastapi import APIRouter, Request, Form
import pyotp
import qrcode
import io
from fastapi.responses import JSONResponse, StreamingResponse
from core.db import set_secret, get_secret

router = APIRouter()

# /api/2fa/setup -> 返回 secret + QR image (base64 optional)
@router.post("/api/2fa/setup")
def api_2fa_setup(name: str = Form("115bot")):
    secret = pyotp.random_base32()
    # 存到 secrets.db，加密保存
    set_secret("2fa_secret", secret)
    otpauth = pyotp.totp.TOTP(secret).provisioning_uri(name, issuer_name="115Bot")
    # 返回 otpauth (前端可以展示二维码)
    return {"code": 0, "data": {"secret": secret, "otpauth": otpauth}}

@router.post("/api/2fa/verify")
def api_2fa_verify(code: str = Form(...)):
    secret = get_secret("2fa_secret")
    if not secret:
        return {"code": 1, "msg": "2FA not setup"}
    totp = pyotp.TOTP(secret)
    ok = totp.verify(code, valid_window=1)
    return {"code": 0 if ok else 2, "ok": bool(ok)}

@router.get("/api/2fa/status")
def api_2fa_status():
    secret = get_secret("2fa_secret")
    return {"code": 0, "data": {"enabled": bool(secret)}}
