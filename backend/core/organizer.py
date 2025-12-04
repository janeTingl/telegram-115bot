import asyncio
import uuid
from typing import Optional
from core.db import get_config, get_secret
from core.logger import push_log


async def start_organize_job() -> Optional[str]:
    """启动网盘整理任务
    
    Returns:
        str: 任务 ID，如果启动失败则返回 None
    """
    try:
        # 检查整理功能是否启用
        organize_enabled = get_config("organize.enabled", "false")
        if organize_enabled.lower() not in ("true", "1", "yes"):
            push_log("WARN", "网盘整理功能未启用")
            return None
        
        # 生成任务 ID
        job_id = str(uuid.uuid4())
        push_log("INFO", f"正在启动整理任务，Job ID: {job_id}")
        
        # 获取配置
        source_cid = get_config("organize.sourceCid", "0")
        target_cid = get_config("organize.targetCid", "0")
        
        if source_cid == "0" or target_cid == "0":
            push_log("ERROR", "整理任务配置不完整：sourceCid 或 targetCid 未设置")
            return None
        
        # 启动后台任务
        asyncio.create_task(_run_organize_task(job_id, source_cid, target_cid))
        
        return job_id
        
    except Exception as e:
        push_log("ERROR", f"启动整理任务失败: {e}")
        return None


async def _run_organize_task(job_id: str, source_cid: str, target_cid: str):
    """实际执行整理任务的后台函数"""
    try:
        push_log("INFO", f"[{job_id}] 开始执行整理任务")
        push_log("INFO", f"[{job_id}] 源目录 CID: {source_cid}")
        push_log("INFO", f"[{job_id}] 目标目录 CID: {target_cid}")
        
        # 尝试导入并使用 organizer 服务
        try:
            from services.service_organizer import organizer
            push_log("INFO", f"[{job_id}] 加载 organizer 模块成功")
            
            # 获取完整配置
            from core.db import get_all_config
            app_config = get_all_config()
            
            # 初始化配置
            organizer.init_config(app_config)
            
            # 运行整理
            await organizer.run_organize()
            push_log("INFO", f"[{job_id}] 整理任务完成")
            
        except ImportError as ie:
            push_log("WARN", f"[{job_id}] 无法导入 organizer 模块: {ie}")
            push_log("INFO", f"[{job_id}] 使用简化版整理逻辑")
            
            # 简化版：仅记录任务信息
            await asyncio.sleep(2)
            push_log("INFO", f"[{job_id}] 简化版整理任务完成（实际整理逻辑待实现）")
            
    except Exception as e:
        push_log("ERROR", f"[{job_id}] 整理任务执行失败: {e}")
        import traceback
        push_log("ERROR", f"[{job_id}] {traceback.format_exc()}")
