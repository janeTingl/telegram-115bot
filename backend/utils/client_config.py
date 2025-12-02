# backend/utils/client_config.py

# 常用 115 客户端配置
CLIENTS_115 = {
    "web": {
        "name": "Web 浏览器",
        "app_id": "1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    },
    "android": {
        "name": "Android 客户端",
        "app_id": "600000",
        "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36 115Browser/26.0.4",
    },
    "wechat_applet": {
        "name": "微信小程序",
        "app_id": "600018", # 小程序专属ID
        "user_agent": "MicroMessenger/6.8.0 NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF/0.17",
    },
    "windows_pc": {
        "name": "Windows PC 客户端",
        "app_id": "600010",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 115PC-Client/19.1.1",
    },
    "ios_ipad": {
        "name": "iOS/iPad 客户端",
        "app_id": "600014",
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1 115_iOS/22.0.1",
    },
    # 实际项目中，此列表会更长，但此结构足以提供核心功能
}
