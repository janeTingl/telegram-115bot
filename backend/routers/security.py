import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pyotp
import uuid
import os # 为了获取 DB_KEY，确保加密的密钥是唯一的

# 假设我们已经可以访问到全局配置管理器
from backend.config.manager import CONFIG 

router = APIRouter(tags=["Security"])

class SetupRequest(BaseModel):
    # 临时密钥和用户输入的验证码
    temp_secret: str
    verification_code: str

# ------------------------------------------------------------------
# 关键 API 接口：验证用户输入的 2FA 代码
# ------------------------------------------------------------------
@router.post("/api/security/verify_2fa")
async def verify_2fa_setup(request: SetupRequest):
    """验证用户扫描二维码后输入的 6 位验证码是否正确。"""
    
    if not request.temp_secret or len(request.verification_code) != 6:
        raise HTTPException(status_code=400, detail="缺少密钥或验证码格式错误")

    # 1. 初始化 TOTP 验证器
    # 注意：pyotp 要求密钥是 Base32 格式，Fernet/DB_KEY 不兼容
    totp = pyotp.TOTP(request.temp_secret)
    
    # 2. 验证用户输入的验证码
    # valid_window=1 允许验证码在前后30秒窗口内有效
    if totp.verify(request.verification_code, valid_window=1):
        # 3. 验证成功，将此密钥持久化到加密数据库
        try:
            CONFIG.set_config("TWO_FACTOR_SECRET", request.temp_secret)
            # 这里的 TWO_FACTOR_SECRET 需要在 ConfigManager 的 ENCRYPTED_KEYS 中定义
            
            return {"success": True, "message": "2FA 验证成功并已启用！"}
        except Exception as e:
            # 如果 DB_KEY 丢失，这里会抛出异常
            print(f"Error saving secret: {e}")
            raise HTTPException(status_code=500, detail="无法保存加密密钥，请检查 DB_KEY")
    else:
        raise HTTPException(status_code=401, detail="验证码错误或已过期，请重试。")


@router.post("/api/security/generate_secret")
async def generate_new_secret():
    """生成一个新的、随机的 2FA 密钥。"""
    # 生成一个安全的 Base32 密钥
    new_secret = pyotp.random_base32()
    
    # 生成 TOTP URL，方便前端生成二维码
    app_name = "115BotAdmin"
    email = f"Admin@{os.environ.get('BOT_USERNAME', 'bot')}" # 可以使用 Bot Username 或其他标识符
    otp_url = pyotp.totp.TOTP(new_secret).provisioning_uri(email, issuer_name=app_name)
    
    return {"secret": new_secret, "otp_url": otp_url}

