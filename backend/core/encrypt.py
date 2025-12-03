from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os

# 密钥文件保存在 backend/secure_key.bin
KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "secure_key.bin")

def _load_key():
    """加载或生成 AES 密钥"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    # 生成新 key（仅在首次使用，32 bytes = AES-256）
    k = get_random_bytes(32)
    with open(KEY_FILE, "wb") as f:
        f.write(k)
    # 设置权限为仅拥有者可读写 (Linux/Mac)
    try:
        os.chmod(KEY_FILE, 0o600)
    except Exception:
        pass
    return k

def encrypt_bytes(plaintext: bytes) -> str:
    """AES-GCM 加密，返回 base64 字符串"""
    key = _load_key()
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    # 拼接 nonce + tag +密文
    payload = nonce + tag + ct
    return base64.b64encode(payload).decode()

def decrypt_bytes(token_b64: str) -> bytes:
    """解密 base64 字符串"""
    key = _load_key()
    try:
        payload = base64.b64decode(token_b64)
        nonce = payload[:12]
        tag = payload[12:28]
        ct = payload[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ct, tag)
    except Exception:
        # 解密失败返回空 bytes，避免程序崩溃
        return b""

def encrypt_str(s: str) -> str:
    """加密字符串接口 (供 db.py 调用)"""
    if not s: return ""
    return encrypt_bytes(s.encode("utf8"))

def decrypt_str(token_b64: str) -> str:
    """解密字符串接口 (供 db.py 调用)"""
    if not token_b64: return ""
    b = decrypt_bytes(token_b64)
    return b.decode("utf8") if b else ""