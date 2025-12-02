import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sys # 用于在密钥缺失时退出系统

# --- 1. Key Derivation and Initialization ---

# 从环境变量中读取 DB_KEY 作为加密主密钥
MASTER_SECRET_KEY: Optional[str] = os.environ.get("DB_KEY")

def _derive_fernet_key(master_key: str) -> bytes:
    """使用 PBKDF2HMAC 从主密钥派生出 Fernet 密钥。"""
    # 固定的盐值，确保派生密钥稳定
    salt = b'115bot_salt' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000, # 迭代次数越高越安全
    )
    return base64.urlsafe_b64encode(kdf.derive(master_key.encode()))

# 初始化加密器
try:
    if not MASTER_SECRET_KEY:
        # 安全警告：如果密钥丢失，应用必须立即停止运行
        raise ValueError("FATAL: DB_KEY environment variable is not set. Cannot initialize crypto.")
        
    FERNET_KEY = _derive_fernet_key(MASTER_SECRET_KEY)
    CRYPTOR = Fernet(FERNET_KEY)
except ValueError as e:
    print(f"FATAL: {e}")
    # 强制退出，防止应用在不安全状态下运行
    sys.exit(1)
except Exception as e:
    print(f"FATAL: Error initializing cryptography: {e}")
    sys.exit(1)

# --- 2. Public Encryption/Decryption Functions ---

def encrypt_value(value: str) -> str:
    """加密字符串值，并返回 URL 安全的 Base64 字符串。"""
    # 由于我们在 try 块中已经保证了 CRYPTOR 存在，这里无需重复检查
    
    # 确保输入是字符串
    if not isinstance(value, str):
        value = str(value)
        
    token = CRYPTOR.encrypt(value.encode('utf-8'))
    return token.decode('utf-8')

def decrypt_value(token: str) -> str:
    """解密字符串值。"""
    # 如果密钥错误或数据被篡改，解密会失败
    try:
        decrypted_value = CRYPTOR.decrypt(token.encode('utf-8'))
        return decrypted_value.decode('utf-8')
    except Exception as e:
        # 如果解密失败，打印警告，并返回空字符串，阻止敏感信息泄漏
        print(f"WARNING: Decryption failed for token starting with: {token[:10]}... Error: {e}")
        return "" 
