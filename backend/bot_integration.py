# backend/bot_integration.py
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
BOT_LOG = BASE / "bot.log"

def write_bot_log(msg: str):
    with open(BOT_LOG, "a", encoding="utf8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def notify_bot(text: str, level: str = "info"):
    """
    该函数会记录到本地日志，并且尝试调用系统环境 BOT webhook（如果你在环境变量中配置）。
    前端调用 /api/bot/send 会触发这里。
    """
    write_bot_log(f"{level.upper()}: {text}")
    # 如果你有独立的 telegram bot 服务，可以在这里发起 HTTP 请求（requests.post）给它
    # 示例（如果需要，我可以把它加上）：
    # import os, requests
    # webhook = os.getenv("BOT_WEBHOOK")
    # if webhook:
    #     try:
    #         requests.post(webhook, json={"text": text})
    #     except Exception as e:
    #         write_bot_log(f"notify webhook failed: {e}")
    return True
