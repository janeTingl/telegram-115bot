import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from services.service_115 import drive_115

logger = logging.getLogger("TGBot")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>115-Bot 管理员已上线</b>\n\n"
        "直接发送磁力链接、Ed2k 或 HTTP 链接，我将自动添加到 115 离线任务。",
        parse_mode='HTML'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 <b>指令列表</b>:\n"
        "/start - 检查状态\n"
        "/quota - 查看 115 空间配额\n"
        "/magnet <link> - 手动添加任务",
        parse_mode='HTML'
    )

async def check_quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = drive_115.get_storage_info()
    if not info:
        await update.message.reply_text("❌ 无法获取 115 信息，请检查 Cookie。")
        return
    
    total = info.get('total', 0) / 1024**4
    used = info.get('used', 0) / 1024**4
    await update.message.reply_text(f"📊 <b>空间使用:</b>\n{used:.2f} TB / {total:.2f} TB", parse_mode='HTML')

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # 提取多行链接
    urls = [line.strip() for line in text.splitlines() if "magnet:?" in line or "http" in line or "ed2k://" in line]
    
    if not urls:
        await update.message.reply_text("⚠️ 未识别到有效链接")
        return

    await update.message.reply_text(f"📥 正在添加 {len(urls)} 个任务到 115...")
    # 默认添加到根目录，或者你可以读取配置中的 downloadPath
    res = drive_115.add_offline_task(urls)
    
    if res.get("status") == "success":
        await update.message.reply_text("✅ 任务添加成功！")
    else:
        await update.message.reply_text(f"❌ 添加失败: {res.get('msg')}")

async def run_bot(token: str):
    if not token: return
    try:
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("quota", check_quota))
        app.add_handler(CommandHandler("magnet", add_task))
        # 捕获所有文本消息
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_task))
        
        logger.info("🤖 Telegram Bot Started Polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
    except Exception as e:
        logger.error(f"Bot Start Error: {e}")
