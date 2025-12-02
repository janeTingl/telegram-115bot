import os
import sqlite3
from typing import Any

# 假设需要加密的敏感字段
ENCRYPTED_KEYS = ["BOT_TOKEN", "API_SECRET"]

def decrypt_value(encrypted: str) -> str:
    """解密函数示例，这里可以替换为你实际的解密逻辑"""
    return encrypted  # 这里简单返回原值作为示例

class ConfigManager:
    def __init__(self, secrets_db_path: str = "secrets.db", data_db_path: str = "data.db"):
        # 初始化数据库连接
        self.secrets_db = sqlite3.connect(secrets_db_path, check_same_thread=False)
        self.data_db = sqlite3.connect(data_db_path, check_same_thread=False)

        # 延迟加载 BOT_TOKEN，不在这里读取
        # self.bot_token = None

        # 初始化表（如果不存在）
        self._init_tables()

    def _init_tables(self):
        # 敏感数据表
        self.secrets_db.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # 普通配置表
        self.data_db.execute("""
            CREATE TABLE IF NOT EXISTS bot_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.secrets_db.commit()
        self.data_db.commit()

    def get_config(self, key: str) -> str:
        """获取配置值，敏感数据自动解密，BOT_TOKEN 支持 ENV 回退"""
        db_value = ""
        if key in ENCRYPTED_KEYS:
            cursor = self.secrets_db.execute("SELECT value FROM credentials WHERE key=?", (key,))
            row = cursor.fetchone()
            db_value = decrypt_value(row[0]) if row else ""
        else:
            cursor = self.data_db.execute("SELECT value FROM bot_config WHERE key=?", (key,))
            row = cursor.fetchone()
            db_value = row[0] if row else ""

        # 数据库有值优先返回
        if db_value:
            return db_value

        # 延迟回退环境变量，仅在请求 BOT_TOKEN 时读取
        if key == "BOT_TOKEN":
            return os.environ.get("BOT_TOKEN", "")

        return ""

    def set_config(self, key: str, value: str):
        """设置配置值，敏感信息存 secrets_db，普通配置存 data_db"""
        if key in ENCRYPTED_KEYS:
            self.secrets_db.execute(
                "INSERT OR REPLACE INTO credentials (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.secrets_db.commit()
        else:
            self.data_db.execute(
                "INSERT OR REPLACE INTO bot_config (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.data_db.commit()

# 全局实例，方便导入使用
CONFIG = ConfigManager()