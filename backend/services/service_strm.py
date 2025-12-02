import os
import logging
import aiofiles
import asyncio
from functools import partial
# 修正导入路径：从同一个 services 目录导入所有服务模块
from .service_115 import drive_115 
from .service_openlist import drive_openlist 
from .service_123 import drive_123 # <--- 假设 123 云盘服务存在

logger = logging.getLogger("STRM")

class StrmGenerator:
    """
    负责执行 115、123 和 OpenList 的目录遍历，生成 .strm 文件。
    """
    def __init__(self):
        self.config = {}

    def init_config(self, app_config):
        """初始化配置，通常从 ConfigManager 中加载。"""
        self.config = app_config.get("strm", {})

    async def generate_115_strm(self):
        """115 网盘：使用 fs_walk (目录树生成模式)"""
        if not self.config.get("enabled"): return
        cid = self.config.get("sourceCid115", "0")
        out_dir = self.config.get("outputDir", "/data/strm")
        prefix = self.config.get("urlPrefix115", "")
        if not drive_115.client: 
            logger.warning("115 Client not initialized. Skipping.")
            return

        try:
            logger.info(f"Starting 115 directory walk for CID: {cid}")
            loop = asyncio.get_event_loop()
            file_walker = partial(drive_115.client.fs_walk, cid=cid)
            
            for item in await loop.run_in_executor(None, file_walker):
                if "fid" not in item or item.get("path") is None: continue
                
                file_id = item["fid"]
                rel_path = item["path"]
                
                download_url = await loop.run_in_executor(
                    None, drive_115.client.get_download_url, file_id
                )
                
                content = f"{prefix}{download_url}" 
                save_path = os.path.join(out_dir, "115", f"{rel_path.lstrip('/')}.strm")
                
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                async with aiofiles.open(save_path, 'w', encoding='utf-8') as f: 
                    await f.write(content)

            logger.info("115 STRM generation complete.")
        except Exception as e: 
            logger.error(f"115 STRM Error: {e}", exc_info=True)

    async def generate_123_strm(self):
        """123 云盘：使用 fs_walk (目录树生成模式)"""
        if not self.config.get("enabled"): return
        cid = self.config.get("sourceCid123", "0") # <--- 假设配置键是 sourceCid123
        out_dir = self.config.get("outputDir", "/data/strm")
        prefix = self.config.get("urlPrefix123", "") # <--- 假设配置键是 urlPrefix123
        if not drive_123.client: 
            logger.warning("123 Client not initialized. Skipping.")
            return

        try:
            logger.info(f"Starting 123 directory walk for CID: {cid}")
            loop = asyncio.get_event_loop()
            file_walker = partial(drive_123.client.fs_walk, cid=cid)
            
            # 同样使用线程池包装阻塞的目录遍历
            for item in await loop.run_in_executor(None, file_walker):
                if "fid" not in item or item.get("path") is None: continue
                
                file_id = item["fid"]
                rel_path = item["path"]
                
                download_url = await loop.run_in_executor(
                    None, drive_123.client.get_download_url, file_id
                )
                
                content = f"{prefix}{download_url}" 
                save_path = os.path.join(out_dir, "123", f"{rel_path.lstrip('/')}.strm")
                
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                async with aiofiles.open(save_path, 'w', encoding='utf-8') as f: 
                    await f.write(content)

            logger.info("123 STRM generation complete.")
        except Exception as e: 
            logger.error(f"123 STRM Error: {e}", exc_info=True)


    async def generate_openlist_strm(self):
        """Openlist：使用异步递归遍历 (历遍目录模式)"""
        if not self.config.get("enabled"): return
        src = self.config.get("sourcePathOpenList", "/")
        out_dir = self.config.get("outputDir", "/data/strm")
        prefix = self.config.get("urlPrefixOpenList", "")

        try:
            async def traverse(curr):
                files = await drive_openlist.get_file_list(curr)
                for f in files:
                    if f.get('children'): 
                        await traverse(f['id'])
                    else:
                        rel_path = f['id'] 
                        content = f"{prefix}{rel_path}"
                        save_path = os.path.join(out_dir, "OpenList", rel_path.lstrip('/')) + ".strm"
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        async with aiofiles.open(save_path, 'w', encoding='utf-8') as f2: 
                            await f2.write(content)

            await traverse(src)
            logger.info("OpenList STRM generation complete.")
        except Exception as e:
            logger.error(f"OpenList STRM Error: {e}", exc_info=True)

strm_gen = StrmGenerator()
