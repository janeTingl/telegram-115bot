import logging
import time
import httpx
from typing import Dict, Any, List, Optional
from p115client import P115Client

logger = logging.getLogger("115Service")

class Drive115Service:
    def __init__(self):
        self.client: Optional[P115Client] = None
        self.cookies: str = ""
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def init_client(self, cookies: str, app_type: str = "web"):
        try:
            self.cookies = cookies
            self.client = P115Client(cookies=cookies, app=app_type)
            if self.client.user_id:
                logger.info(f"115 Client Initialized. UID: {self.client.user_id}")
                return True
        except Exception as e:
            logger.error(f"115 Init Error: {e}")
        return False

    async def get_qrcode_token(self) -> Dict[str, Any]:
        url = "https://qrcodeapi.115.com/api/1.0/web/1.0/token"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            data = resp.json()
            if data.get("state") == 1:
                return data['data']
        return {}

    async def check_qrcode_status(self, uid: str, time_val: int, sign: str) -> Dict[str, Any]:
        url = f"https://qrcodeapi.115.com/api/1.0/web/1.0/status?uid={uid}&time={time_val}&sign={sign}&_={int(time.time()*1000)}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            data = resp.json()
            state = data.get("data", {}).get("status")
            if state == 2:
                cookie_data = data.get("data", {}).get("cookie")
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_data.items()])
                return {"status": "success", "cookies": cookie_str}
            elif state == 1: return {"status": "scanned"}
            elif state == 0: return {"status": "waiting"}
            else: return {"status": "expired"}

    def get_storage_info(self) -> Dict[str, Any]:
        if not self.client: return {}
        try:
            idx = self.client.fs_index_info
            return idx.get("data", {}).get("space_info", {})
        except: return {}

    def get_file_list(self, cid: str = "0") -> List[Dict[str, Any]]:
        if not self.client: return []
        try:
            resp = self.client.fs_files(cid=cid, limit=100)
            if resp.get("state"):
                return [{
                    "id": str(x.get("cid", x.get("fid"))),
                    "name": x.get("n"),
                    "children": "cid" in x,
                    "date": x.get("te")
                } for x in resp.get("data", [])]
        except Exception as e:
            logger.error(f"115 List Error: {e}")
        return []

    def add_offline_task(self, urls: List[str], save_cid: str = "0") -> Dict[str, Any]:
        if not self.client: return {"status": "error", "msg": "未登录"}
        try:
            res = self.client.offline_add_urls(urls, pid=save_cid)
            if res.get("state"):
                return {"status": "success", "data": res}
            return {"status": "fail", "msg": res.get("error_msg")}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

drive_115 = Drive115Service()
