# backend/core/encrypt.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os

KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "secure_key.bin")

def _load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    # 生成新 key（仅在首次使用）
    k = get_random_bytes(32)
    with open(KEY_FILE, "wb") as f:
        f.write(k)
    os.chmod(KEY_FILE, 0o600)
    return k

def encrypt_bytes(plaintext: bytes) -> str:
    key = _load_key()
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    payload = nonce + tag + ct
    return base64.b64encode(payload).decode()

def decrypt_bytes(token_b64: str) -> bytes:
    key = _load_key()
    payload = base64.b64decode(token_b64)
    nonce = payload[:12]
    tag = payload[12:28]
    ct = payload[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)

def encrypt_str(s: str) -> str:
    return encrypt_bytes(s.encode("utf8"))

def decrypt_str(token_b64: str) -> str:
    return decrypt_bytes(token_b64).decode("utf8")
