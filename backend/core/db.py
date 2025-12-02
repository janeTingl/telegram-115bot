# backend/core/db.py
import sqlite3
import os
from pathlib import Path
from core.encrypt import encrypt_str, decrypt_str

BASE = Path(__file__).resolve().parent.parent
DATA_DB = BASE / "data.db"
SECRETS_DB = BASE / "secrets.db"

def _ensure_db(path: Path, schema_sql: str = None):
    init = not path.exists()
    conn = sqlite3.connect(str(path))
    if init and schema_sql:
        conn.executescript(schema_sql)
        conn.commit()
    return conn

# data.db 简单表（可扩展）
DATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS config (
  key TEXT PRIMARY KEY,
  value TEXT
);
CREATE TABLE IF NOT EXISTS qps_config (
  service TEXT PRIMARY KEY,
  qps INTEGER
);
"""

# secrets.db 存密保，字段 value 存加密过的 base64
SECRETS_SCHEMA = """
CREATE TABLE IF NOT EXISTS secrets (
  key TEXT PRIMARY KEY,
  value TEXT
);
"""

def get_data_conn():
    return _ensure_db(DATA_DB, DATA_SCHEMA)

def get_secrets_conn():
    return _ensure_db(SECRETS_DB, SECRETS_SCHEMA)

# helpers
def set_config(key: str, value: str):
    conn = get_data_conn()
    conn.execute("REPLACE INTO config(key,value) VALUES(?,?)", (key, value))
    conn.commit()

def get_config(key: str, default=None):
    conn = get_data_conn()
    r = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    return r[0] if r else default

def set_secret(key: str, plaintext: str):
    enc = encrypt_str(plaintext)
    conn = get_secrets_conn()
    conn.execute("REPLACE INTO secrets(key,value) VALUES(?, ?)", (key, enc))
    conn.commit()

def get_secret(key: str, default=None):
    conn = get_secrets_conn()
    r = conn.execute("SELECT value FROM secrets WHERE key=?", (key,)).fetchone()
    if not r:
        return default
    try:
        return decrypt_str(r[0])
    except Exception:
        return default
