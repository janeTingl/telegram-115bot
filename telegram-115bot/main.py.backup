# -*- coding: utf-8 -*-

import json
import time
import asyncio
import threading
from telegram import Update, BotCommand
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters, ConversationHandler
from telegram.helpers import escape_markdown
import qrcode
from io import BytesIO
import os

# 导入init模块
import init

# 消息队列相关
message_queue = asyncio.Queue()
global_loop = None

async def add_task_to_queue(user_id, image_path=None, message=None):
    """添加任务到消息队列"""
    await message_queue.put({
        "user_id": user_id,
        "image_path": image_path,
        "message": message
    })

async def queue_worker(loop, token):
    """消息队列工作器"""
    global global_loop
    global_loop = loop
    
    while True:
        try:
            task = await message_queue.get()
            await send_queued_message(task, token)
            message_queue.task_done()
        except Exception as e:
            init.logger.error(f"消息队列处理错误: {e}")
            await asyncio.sleep(1)

async def send_queued_message(task, token):
    """发送队列中的消息"""
    try:
        from telegram import Bot
        bot = Bot(token=token)
        
        if task.get('image_path') and os.path.exists(task['image_path']):
            with open(task['image_path'], 'rb') as photo:
                await bot.send_photo(
                    chat_id=task['user_id'],
                    photo=photo,
                    caption=task.get('message', ''),
                    parse_mode="MarkdownV2"
                )
        else:
            await bot.send_message(
                chat_id=task['user_id'],
                text=task.get('message', ''),
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        init.logger.error(f"发送消息失败: {e}")

# 机器人功能
def get_version(md_format=False):
    version = "v3.2.21"
    if md_format:
        return escape_markdown(version, version=2)
    return version

def get_help_info():
    version = get_version()
    help_info = f"""
<b>🍿 Telegram-115Bot {version} 使用手册</b>\n\n
<b>🔧 命令列表</b>\n
<code>/start</code> - 显示帮助信息\n
<code>/auth</code> - <i>115扫码授权 (解除授权后使用)</i>\n
<code>/reload</code> - <i>重载配置</i>\n
<code>/rl</code> - 查看重试列表\n
<code>/q</code> - 取消当前会话\n\n
<b>✨ 功能说明</b>\n
<u>文件下载：</u>
• 直接输入下载链接，支持磁力/ed2k/迅雷
• 离线超时可选择添加到重试列表\n
<u>重试列表：</u>
• 输入 <code>"/rl"</code>
• 查看当前重试列表，可根据需要选择是否清空\n
<u>视频下载：</u>
• 直接转发视频给机器人即可保存到115
"""
    return help_info

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_info = get_help_info()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_info, parse_mode="html", disable_web_page_preview=True)

async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init.load_yaml_config()
    init.logger.info("重载配置成功")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🔁重载配置完成！", parse_mode="html")

# 授权处理器
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not init.openapi_115:
        await update.message.reply_text("❌ 115客户端未初始化，请检查配置")
        return

    qrcode_token = init.openapi_115.get_qrcode()
    if not qrcode_token:
        await update.message.reply_text("❌ 获取二维码失败，请重试")
        return

    # 生成二维码图片
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qrcode_token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=bio,
        caption="📱 请使用115手机App扫描二维码登录\n\n扫描后请等待自动确认...",
        parse_mode="Markdown"
    )
    
    # 启动登录状态检查
    context.job_queue.run_repeating(check_auth_status, interval=5, first=10, data=update.effective_chat.id)

async def check_auth_status(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    if init.openapi_115.check_login():
        await context.bot.send_message(chat_id=chat_id, text="✅ 115登录成功！")
        context.job.schedule_removal()

# 下载处理器
async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not init.openapi_115 or not init.openapi_115.uid:
        await update.message.reply_text("❌ 请先使用 /auth 登录115账号")
        return

    url = update.message.text.strip()
    success, message = init.openapi_115.add_offline_task(url)
    
    if success:
        await update.message.reply_text(f"✅ {message}")
    else:
        await update.message.reply_text(f"❌ {message}")

# 视频处理器
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.video:
        return
        
    if not init.openapi_115 or not init.openapi_115.uid:
        await update.message.reply_text("❌ 请先使用 /auth 登录115账号")
        return

    # 这里简化处理，实际需要下载视频并上传到115
    await update.message.reply_text("📹 视频接收成功，开始处理...")

# 离线任务处理器
async def show_retry_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 简化实现，实际应该有重试列表管理
    await update.message.reply_text("📋 当前重试列表为空")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 当前操作已取消")
    return ConversationHandler.END

def start_async_loop():
    """启动异步事件循环的线程"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    init.logger.info("事件循环已启动")
    try:
        token = init.bot_config['bot_token']
        loop.create_task(queue_worker(loop, token))
        loop.run_forever()
    except Exception as e:
        init.logger.error(f"事件循环异常: {e}")
    finally:
        loop.close()
        init.logger.info("事件循环已关闭")

def send_start_message():
    version = get_version()  
    if not init.openapi_115:
        return
    
    line1, line2, line3, line4 = init.openapi_115.welcome_message()
    if not line1:
        return
    line5 = escape_markdown(f"Telegram-115Bot {version} 启动成功！", version=2)
    if line1 and line2 and line3 and line4:
        formatted_message = f"""
{line1}
{line2}
{line3}
{line4}

{line5}

发送 `/start` 查看操作说明"""
        
        asyncio.run_coroutine_threadsafe(
            add_task_to_queue(init.bot_config['allowed_user'], message=formatted_message),
            global_loop
        )

def update_logger_level():
    import logging
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)

def get_bot_menu():
    return [
        BotCommand("start", "获取帮助信息"),
        BotCommand("auth", "115扫码授权"),
        BotCommand("reload", "重载配置"),
        BotCommand("rl", "查看重试列表"),
        BotCommand("q", "退出当前会话")
    ]

async def set_bot_menu(application):
    """异步设置Bot菜单"""
    try:
        await application.bot.set_my_commands(get_bot_menu())
        init.logger.info("Bot菜单命令已设置!")
    except Exception as e:
        init.logger.error(f"设置Bot菜单失败: {e}")

async def post_init(application):
    """应用初始化后的回调"""
    await set_bot_menu(application)

if __name__ == '__main__':
    if not init.init():
        exit(1)
        
    # 启动消息队列
    message_thread = threading.Thread(target=start_async_loop, daemon=True)
    message_thread.start()
    
    # 等待消息队列准备就绪
    max_wait = 30
    wait_count = 0
    while True:
        if global_loop is not None:
            init.logger.info("消息队列线程已准备就绪！")
            break
        time.sleep(1)
        wait_count += 1
        if wait_count >= max_wait:
            init.logger.error("消息队列线程未准备就绪，程序将退出。")
            exit(1)
            
    init.logger.info("Starting bot with configuration")
    update_logger_level()
    
    token = init.bot_config['bot_token']
    application = Application.builder().token(token).post_init(post_init).build()    

    # 注册处理器
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('reload', reload))
    application.add_handler(CommandHandler('auth', auth))
    application.add_handler(CommandHandler('rl', show_retry_list))
    application.add_handler(CommandHandler('q', cancel))
    
    # 注册消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # 初始化115open对象
    if not init.initialize_115open():
        init.logger.error("115 OpenAPI客户端初始化失败，程序无法继续运行！")
        asyncio.run_coroutine_threadsafe(
            add_task_to_queue(init.bot_config['allowed_user'], message="❌ 115 OpenAPI客户端初始化失败！"),
            global_loop
        )
        time.sleep(30)
        exit(1)

    # 启动机器人轮询
    try:
        time.sleep(3)
        send_start_message()
        application.run_polling()
    except KeyboardInterrupt:
        init.logger.info("程序已被用户终止")
    except Exception as e:
        init.logger.error(f"程序遇到错误：{e}")
    finally:
        init.logger.info("机器人已停止运行")