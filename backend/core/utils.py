import secrets
import base64
import pyotp
from typing import Optional


def generate_base32_secret(length: int = 32) -> str:
    """生成用于 2FA 的 Base32 编码密钥"""
    random_bytes = secrets.token_bytes(length)
    return base64.b32encode(random_bytes).decode('utf-8').rstrip('=')


def verify_totp(secret: str, code: str, valid_window: int = 1) -> bool:
    """验证 TOTP 验证码
    
    Args:
        secret: Base32 编码的密钥
        code: 用户输入的 6 位验证码
        valid_window: 允许的时间窗口（前后各多少个30秒周期）
    
    Returns:
        bool: 验证是否成功
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)
    except Exception as e:
        print(f"TOTP verification error: {e}")
        return False


def generate_totp_uri(secret: str, issuer: str = "115Bot", account_name: str = "Admin") -> str:
    """生成 TOTP URI，用于生成二维码
    
    Args:
        secret: Base32 编码的密钥
        issuer: 发行者名称
        account_name: 账户名称
    
    Returns:
        str: otpauth:// URI
    """
    return f"otpauth://totp/{issuer}:{account_name}?secret={secret}&issuer={issuer}"
