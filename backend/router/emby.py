# backend/router/emby.py
from fastapi import APIRouter, Form, BackgroundTasks
from core.db import get_config, get_secret
from core.logger import push_log
from core.qps_limiter import get_limiter
import requests
import time

router = APIRouter()

def _get_emby_conf():
    host = get_config("emby_host", "")
    api_key = get_secret("emby_api_key", None)
    return host, api_key

@router.post("/api/emby/refresh_and_probe")
def api_emby_refresh_and_probe(item_id: str = Form(None), background: BackgroundTasks = None):
    """
    触发 Emby 刷新库，等待 4 秒；若传入 item_id，则在 1 秒后调用 PlaybackInfo
    """
    host, api_key = _get_emby_conf()
    if not host or not api_key:
        push_log("WARN", "Emby 未配置，跳过刷新")
        return {"code": 1, "msg": "emby not configured"}

    qps = int(get_config("emby_qps", 1))
    limiter = get_limiter("emby", qps)
    if not limiter.consume():
        push_log("WARN", "Emby 请求被限流（QPS）")
        return {"code": 429, "msg": "rate limited"}

    def job():
        try:
            push_log("INFO", "触发 Emby 刷新媒体库")
            requests.post(f"{host.rstrip('/')}/Library/Refresh?api_key={api_key}", timeout=10)
            # 等待 4 秒再做后续处理
            time.sleep(4)
            if item_id:
                # 再等待 1 秒后查询 PlaybackInfo
                time.sleep(1)
                try:
                    url = f"{host.rstrip('/')}/emby/Items/{item_id}/PlaybackInfo?api_key={api_key}"
                    r = requests.get(url, timeout=8)
                    # 不在日志中写入 PlaybackInfo 详细信息（敏感）
                    if r.status_code == 200:
                        push_log("INFO", f"已获取 Item {item_id} 的播放信息（已隐藏详情）")
                    else:
                        push_log("WARN", f"获取 PlaybackInfo 返回状态 {r.status_code}")
                except Exception as e:
                    push_log("ERROR", f"调用 PlaybackInfo 出错: {e}")
        except Exception as e:
            push_log("ERROR", f"Emby 刷新失败: {e}")

    if background:
        background.add_task(job)
    else:
        job()
    return {"code": 0, "msg": "emby refresh triggered"}
