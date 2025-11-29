# 临时修复：允许空Token启动Web界面
import re

with open('main.py', 'r') as f:
    content = f.read()

# 在Token检查前添加条件，如果Token为空只启动Web界面
new_content = re.sub(
    r'token = init\.bot_config\[\'bot_token\'\]',
    '''token = init.bot_config.get('bot_token', '')
# 如果Token为空，只启动Web界面不启动Bot
if not token:
    print("⚠️  Bot Token未配置，只启动Web管理界面")
    # 启动Web服务器线程
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    print("🌐 Web管理界面已启动: http://0.0.0.0:12808")
    print("📝 请通过Web界面配置Bot Token")
    # 保持主线程运行
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("程序退出")
    exit(0)''',
    content
)

with open('main.py', 'w') as f:
    f.write(new_content)

print("修复完成")
