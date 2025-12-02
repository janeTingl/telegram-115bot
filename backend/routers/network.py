import time
import os
from fastapi import APIRouter, HTTPException
from httpx import AsyncClient, ConnectTimeout
from backend.config.manager import CONFIG 

router = APIRouter(tags=["Network"])

@router.get("/api/network/latency")
async def get_proxy_latency():
    proxy_config = CONFIG.get_config("PROXY") 
    
    proxies = None
    if proxy_config and proxy_config.get('enabled'):
        proxy_type = proxy_config.get('type', 'http')
        proxy_host = proxy_config.get('host')
        proxy_port = proxy_config.get('port')
        
        if proxy_host and proxy_port:
            proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
            # 假设 CONFIG.get_config("PROXY") 返回的是一个字典，且包含 host/port
            proxies = {"https": proxy_url, "http": proxy_url}

    target_url = "https://api.telegram.org/"
    
    try:
        # 使用 httpx 进行带代理的请求并计算延迟
        async with AsyncClient(proxies=proxies, timeout=5) as client:
            start_time = time.time()
            response = await client.get(target_url)
            end_time = time.time()
            
            latency_ms = round((end_time - start_time) * 1000)

            if response.status_code == 200:
                return {"latency": latency_ms, "status": "success"}
            else:
                return {"latency": "N/A", "status": "failed", "detail": f"Target returned {response.status_code}"}

    except ConnectTimeout:
        raise HTTPException(status_code=503, detail="代理连接超时，请检查代理地址或端口。")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"网络错误：{str(e)}")
