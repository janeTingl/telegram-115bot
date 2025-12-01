import logging
import time
import httpx
from typing import Dict, Any, List

logger = logging.getLogger("123Service")

class Drive123Service:
    def __init__(self):
        self.base_url = "https://open-api.123pan.com"
        self.client_id = ""
        self.client_secret = ""
        self.token = ""
        self.token_expire = 0

    def init_config(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def get_token(self) -> str:
        if self.token and time.time() < self.token_expire: return self.token
        url = f"{self.base_url}/api/v1/access_token"
        payload = {"clientID": self.client_id, "clientSecret": self.client_secret}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload)
                data = resp.json()
                if data.get("code") == 200:
                    self.token = data["data"]["accessToken"]
                    self.token_expire = time.time() + data["data"]["expiresIn"] - 60
                    return self.token
        except Exception as e: logger.error(f"123 Token Error: {e}")
        return ""

    async def add_offline_task(self, url: str, filename: str = "") -> Dict[str, Any]:
        token = await self.get_token()
        if not token: return {"status": "error", "msg": "Auth failed"}
        api_url = f"{self.base_url}/api/v1/offline/download"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"url": url}
        if filename: payload["filename"] = filename
        async with httpx.AsyncClient() as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            return resp.json()

    async def get_file_list(self, parent_id: str = "0") -> List[Dict[str, Any]]:
        token = await self.get_token()
        if not token: return []
        url = f"{self.base_url}/api/v1/file/list"
        params = {"parentFileId": parent_id, "limit": 100}
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers)
            data = resp.json()
            if data.get("code") == 0:
                return [{
                    "id": str(f["fileId"]),
                    "name": f["fileName"],
                    "children": f["type"] == 1,
                    "date": f["updateTime"]
                } for f in data.get("data", {}).get("fileList", [])]
        return []

drive_123 = Drive123Service()
