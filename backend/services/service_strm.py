import os
import logging
import aiofiles
from services.service_115 import drive_115
from services.service_openlist import drive_openlist

logger = logging.getLogger("STRM")

class StrmGenerator:
    def __init__(self):
        self.config = {}

    def init_config(self, app_config):
        self.config = app_config.get("strm", {})

    async def generate_115_strm(self):
        if not self.config.get("enabled"): return
        cid = self.config.get("sourceCid115", "0")
        out_dir = self.config.get("outputDir", "/data/strm")
        prefix = self.config.get("urlPrefix115", "")
        
        if not drive_115.client: return

        try:
            for item in drive_115.client.fs_walk(cid):
                if "fid" not in item: continue
                fname = item.get("n")
                # 假设 WebDAV 路径与文件名一致，实际需完整相对路径
                # 简化: 直接用文件名
                content = f"{prefix}/{fname}"
                
                save_path = os.path.join(out_dir, "115", f"{fname}.strm")
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                async with aiofiles.open(save_path, 'w') as f: await f.write(content)
            logger.info("115 STRM Done")
        except Exception as e: logger.error(f"115 STRM Error: {e}")

    async def generate_openlist_strm(self):
        if not self.config.get("enabled"): return
        src = self.config.get("sourcePathOpenList", "/")
        out_dir = self.config.get("outputDir", "/data/strm")
        prefix = self.config.get("urlPrefixOpenList", "")

        async def traverse(curr):
            files = await drive_openlist.get_file_list(curr)
            for f in files:
                if f['children']: await traverse(f['id'])
                else:
                    rel_path = f['id'] # /Movie/A.mkv
                    content = f"{prefix}{rel_path}"
                    save_path = os.path.join(out_dir, "OpenList", rel_path.lstrip('/')) + ".strm"
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    async with aiofiles.open(save_path, 'w') as f2: await f2.write(content)

        await traverse(src)
        logger.info("OpenList STRM Done")

strm_gen = StrmGenerator()
