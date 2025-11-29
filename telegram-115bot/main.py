#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import asyncio
import threading
import sys
import os
import yaml
import logging
import requests
import qrcode
from io import BytesIO
from telegram import Update, BotCommand
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters, ConversationHandler
from telegram.helpers import escape_markdown
from telegram.error import TelegramError

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    import init
    from init import init as init_app, initialize_115open, bot_config, openapi_115, IMAGE_PATH
    print("✅ init模块导入成功")
except ImportError as e:
    print(f"❌ init模块导入失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_web_server():
    """启动Web服务器"""
    from app.web import app
    logger.info("🌐 启动Web服务器，端口: 12808")
    try:
        app.run(host='0.0.0.0', port=12808, debug=False)
    except Exception as e:
        logger.error(f"Web服务器错误: {e}")

def main():
    """主函数 - 永不退出"""
    print("=" * 60)
    print("🚀 Telegram-115Bot 启动中...")
    print("=" * 60)
    
    # 初始化配置
    if not init_app():
        logger.error("配置初始化失败，但继续运行Web界面")
    
    # 启动Web服务器（在主线程中运行）
    print("📊 Web管理界面: http://0.0.0.0:12808")
    print("👤 用户名: root")
    print("🔑 密码: root")
    print("")
    print("💡 使用说明:")
    print("   1. 访问上述地址登录Web界面")
    print("   2. 在'基本配置'中填写必要信息")
    print("   3. 保存配置后系统会自动应用")
    print("=" * 60)
    
    # 直接启动Web服务器（阻塞运行）
    start_web_server()

if __name__ == '__main__':
    main()
