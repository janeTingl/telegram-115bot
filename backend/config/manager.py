# 确保在文件顶部有 import os

# ... 其他代码 ...

class ConfigManager:
    # ... __init__ 和 secrets_db/data_db 初始化 ...

    def get_config(self, key: str) -> str:
        """获取配置值，如果是敏感数据则自动解密，并为 BOT_TOKEN 提供 ENV 回退。"""
        
        # 1. 尝试从 secrets.db 或 data.db 中查询
        if key in ENCRYPTED_KEYS:
            cursor = self.secrets_db.execute("SELECT value FROM credentials WHERE key=?", (key,))
            row = cursor.fetchone()
            db_value = decrypt_value(row[0]) if row else ""
        else:
            cursor = self.data_db.execute("SELECT value FROM bot_config WHERE key=?", (key,))
            row = cursor.fetchone()
            db_value = row[0] if row else ""
        
        # 2. 如果数据库有值，直接返回
        if db_value:
            return db_value
        
        # 3. 【关键】如果数据库为空 (首次启动)，从环境变量中获取 Bot Token
        if key == "BOT_TOKEN":
            env_token = os.environ.get("BOT_TOKEN")
            # 注意：这里我们不将 ENV Token 写入 DB，因为它只用于启动时的临时认证。
            return env_token if env_token else ""

        return "" # 数据库中没有，也不是 Bot Token，则返回空值
        
    def set_config(self, key: str, value: str):
        # ... set_config 保持不变 ...
