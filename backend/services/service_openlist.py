import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger("OpenList")

class OpenListService:
    def __init__(self):
        self.url = ""
        self.username = ""
        self.password = ""
        self.token = ""

    def init_config(self, url: str, username: str = "", password: str = ""):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.token = ""

    async def _get_token(self) -> str:
        if self.token: return self.token
        auth_url = f"{self.url}/api/auth/login"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(auth_url, json={"username": self.username, "password": self.password})
                data = resp.json()
                if data.get("code") == 200:
                    self.token = data.get("data", {}).get("token")
                    return self.token
        except: pass
        return ""

    async def get_file_list(self, path: str = "/") -> List[Dict[str, Any]]:
        if path == "0": path = "/"
        token = await self._get_token()
        headers = {"Authorization": token} if token else {}
        api_url = f"{self.url}/api/fs/list"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(api_url, json={"path": path}, headers=headers)
                data = resp.json()
                if data.get("code") == 200:
                    return [{
                        "id": f"{path.rstrip('/')}/{item['name']}",
                        "name": item['name'],
                        "children": item['is_dir'],
                        "date": item['modified']
                    } for item in data.get("data", {}).get("content", [])]
        except Exception as e:
            logger.error(f"OpenList Error: {e}")
        return []

drive_openlist = OpenListService()
