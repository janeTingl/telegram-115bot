import logging
import asyncio
from functools import partial
import re # <-- 新增：用于正则表达式匹配分享链接
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from services.service_115 import drive_115

logger = logging.getLogger("TGBot")

# ----------------------------------------------------------------------
# 异步 Bot Handler
# ----------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>115-Bot 管理员已上线</b>\n\n"
        "直接发送：\n"
        "1. 磁力/Ed2k/HTTP 链接，自动添加离线任务。\n"
        "2. <b>115 分享链接 + 提取码</b>，自动转存资源。",
        parse_mode='HTML'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 <b>指令列表</b>:\n"
        "/start - 检查状态\n"
        "/quota - 查看 115 空间配额\n"
        "/magnet <link> - 手动添加离线任务\n"
        "/move <file_ids> <target_cid> - 移动文件（转存）",
        parse_mode='HTML'
    )

async def check_quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 修复：使用 asyncio.to_thread 包装同步调用，防止阻塞
    try:
        info = await asyncio.to_thread(drive_115.get_storage_info)
    except Exception as e:
        logger.error(f"Failed to get 115 quota: {e}")
        await update.message.reply_text("❌ 无法获取 115 信息，客户端或 Cookie 错误。", parse_mode='HTML')
        return

    if not info:
        await update.message.reply_text("❌ 无法获取 115 信息，请检查 Cookie。", parse_mode='HTML')
        return
    
    total = info.get('total', 0) / 1024**4
    used = info.get('used', 0) / 1024**4
    await update.message.reply_text(f"📊 <b>空间使用:</b>\n{used:.2f} TB / {total:.2f} TB", parse_mode='HTML')


async def add_offline_tasks(update: Update, urls: list):
    """处理离线下载任务"""
    await update.message.reply_text(f"📥 正在添加 {len(urls)} 个离线任务到 115...")
    
    task_func = partial(drive_115.add_offline_task, urls=urls)
    try:
        res = await asyncio.to_thread(task_func)
    except Exception as e:
        logger.error(f"Error during add_offline_task: {e}")
        await update.message.reply_text("❌ 离线服务调用失败，请检查日志。", parse_mode='HTML')
        return
    
    
    if res and res.get("status") == "success":
        await update.message.reply_text("✅ 离线任务添加成功！")
    else:
        await update.message.reply_text(f"❌ 离线任务添加失败: {res.get('msg', '未知API错误')}", parse_mode='HTML')


async def transfer_shared_files(update: Update, share_link: str, pickcode: str = None):
    """新增函数：处理 115 分享链接转存"""
    await update.message.reply_text(f"🔗 正在尝试转存分享资源...")
    
    # 目标文件夹 CID：假设转存到根目录 '0' 或从配置中读取
    TARGET_CID = '0' 
    
    # 假设 drive_115.client 有 save_share_to_drive 同步方法
    share_task_func = partial(
        drive_115.save_share_to_drive, 
        share_link=share_link, 
        pickcode=pickcode, 
        target_cid=TARGET_CID
    )

    try:
        res = await asyncio.to_thread(share_task_func)
    except Exception as e:
        logger.error(f"Error during share transfer: {e}")
        await update.message.reply_text("❌ 分享转存服务调用失败，请检查日志。", parse_mode='HTML')
        return

    if res and res.get("status") == "success":
        await update.message.reply_text("✅ 分享资源转存成功！")
    else:
        await update.message.reply_text(f"❌ 分享转存失败: {res.get('msg', '链接或提取码可能错误或已失效。')}", parse_mode='HTML')


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    统一处理所有非命令文本消息，自动区分：分享链接 or 离线链接
    """
    text = update.message.text
    
    # 1. 尝试匹配 115 分享链接
    # 匹配 https://115.com/s/xxxxxx 格式的链接
    share_link_match = re.search(r'https?://(?:www\.)?115\.com/s/[a-zA-Z0-9]+', text)
    
    if share_link_match:
        share_link = share_link_match.group(0)
        
        # 提取提取码：简单地认为最后一个 4 位字符串是提取码 (通常是 115 分享的格式)
        pickcode_match = re.search(r'([a-zA-Z0-9]{4})$', text.strip())
        pickcode = pickcode_match.group(1) if pickcode_match else None
        
        await transfer_shared_files(update, share_link, pickcode)
        return

    # 2. 如果不是分享链接，则按离线任务处理
    urls = [line.strip() for line in text.splitlines() if "magnet:?" in line or "http" in line or "ed2k://" in line]
    
    if urls:
        await add_offline_tasks(update, urls)
        return
        
    await update.message.reply_text("⚠️ 未识别到有效链接。请发送磁力/HTTP链接，或 115 分享链接+提取码。")

# ----------------------------------------------------------------------
# Bot 启动入口
# ----------------------------------------------------------------------

# 重命名并添加了 /move 命令，用于文件转存
async def move_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文件移动/转存命令： /move <文件ID,文件ID,...> <目标文件夹CID>"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("⚠️ 格式错误。\n用法: /move <文件ID1,ID2> <目标CID>", parse_mode='HTML')
        return

    file_ids_str = context.args[0]
    target_cid = context.args[1]
    
    file_ids = [fid.strip() for fid in file_ids_str.split(',') if fid.strip()]
    if not file_ids:
        await update.message.reply_text("⚠️ 未识别到有效文件 ID。")
        return

    await update.message.reply_text(f"🚚 正在转存 {len(file_ids)} 个文件到 CID: {target_cid}...")

    # 核心修复：使用 asyncio.to_thread 包装同步调用
    task_func = partial(drive_115.move_files, file_ids=file_ids, target_cid=target_cid)
    try:
        # 假设 drive_115.move_files 是同步的
        res = await asyncio.to_thread(task_func)
    except Exception as e:
        logger.error(f"Error during move_files: {e}")
        await update.message.reply_text("❌ 后端转存服务调用失败。", parse_mode='HTML')
        return
    
    if res and res.get("status") == "success":
        await update.message.reply_text("✅ 文件转存成功！")
    else:
        await update.message.reply_text(f"❌ 转存失败: {res.get('msg', '未知API错误')}", parse_mode='HTML')

async def run_bot(token: str):
    if not token: 
        logger.warning("Bot Token is empty. Telegram Bot task skipped.")
        return
        
    try:
        app = ApplicationBuilder().token(token).build()
        
        # 注册 CommandHandler
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("quota", check_quota))
        app.add_handler(CommandHandler("magnet", add_offline_tasks))
        app.add_handler(CommandHandler("move", move_file)) # <-- 注册文件移动/转存命令
        
        # 注册 MessageHandler (处理所有非命令文本)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        logger.info("🤖 Telegram Bot Started Polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling() 
    except Exception as e:
        logger.error(f"Bot Start Fatal Error: {e}", exc_info=True)
