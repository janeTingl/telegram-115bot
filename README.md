# Telegram-115Bot

一个基于 Telegram Bot 的 115 网盘管理工具，支持文件下载、视频保存到115网盘。

### 本项目forks qiqiandfei大佬的Telegram-115Bot项目修改而来。
---

## 🚀 功能特性

- ✅ 115网盘授权 - 扫码登录115账号  
- ✅ 文件下载 - 支持磁力链接、ed2k、迅雷链接  
- ✅ 视频保存 - 直接保存 Telegram 视频到 115 网盘  
- ✅ 任务管理 - 查看和管理下载任务  
- ✅ 多平台支持 - 支持 AMD64 和 ARM64 架构  

---

## 📋 命令列表

| 命令 | 功能 | 说明 |
|------|------|------|
/start | 显示帮助信息 | 查看完整使用说明  
/auth | 115扫码授权 | 首次使用或重新授权  
/reload | 重载配置 | 应用配置变更  
/rl | 查看重试列表 | 管理失败任务  
/q | 取消当前会话 | 退出当前操作  

---

## 🐳 Docker 部署

### 方法 1：Docker Run

```bash
# 创建配置目录
mkdir -p telegram-bot-data
cd telegram-bot-data

# 创建配置文件
cat > config.yaml << EOF
bot_token: "你的Telegram机器人Token"
allowed_user: "你的Telegram用户ID"
115_app_id: "你的115AppID"
115_user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
EOF

# 运行容器
'''
docker run -d \
  --name telegram-115bot \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.yaml:/app/config.yaml \
  yongzz668/telegram-115bot:latest
  '''   
- Docker Compose
'''
version: '3.8'

services:
  telegram-115bot:
    image: yongzz668/telegram-115bot:latest
    container_name: telegram-115bot
    restart: unless-stopped
    volumes:
      - /vol1/1000/telegram-115bot/data:/app/data
      - /vol1/1000/telegram-115bot/config.yaml:/app/config.yaml
    environment:
      - TZ=Asia/Shanghai

      # HTTP 代理
      - HTTP_PROXY=http://127.0.0.1:7890
      - http_proxy=http://127.0.0.1:7890

      # 可选：不经过代理的地址
      - NO_PROXY=localhost,127.0.0.1,192.168.0.0/16
      '''   
      🔧 配置获取

1. 获取 Telegram Bot Token
	1.	Telegram 搜索 @BotFather
	2.	发送 /newbot
	3.	按提示设置名称
	4.	获取 API Token

2. 获取 Telegram 用户ID
	1.	搜索 @userinfobot
	2.	发送任意消息即可获取 ID


⸻

📱 使用流程
	1.	部署后，在 Telegram 中找到你的 Bot
	2.	发送 /auth 获取 115 登录二维码
	3.	用 115 手机 App 扫码登录
	4.	之后即可使用：
	•	发送磁力链接自动下载
	•	转发视频自动保存
	•	/rl 查看失败任务

📄 许可证

MIT License

⸻

🤝 贡献

欢迎提交 Issue 和 Pull Request！

⸻

项目地址： GitHub Repository
Docker 镜像： yongzz668/telegram-115bot:latest