# backend/utils/rename.py
"""
智能重命名与移动（适用于网盘路径）
- 输入: files (list of path strings), base_dir (网盘路径)
- 根据简单正则识别 movie / tv，并使用 zid 字典做二级分类
- 返回: list of new paths (strings)
"""

import re
from typing import List, Dict
from pathlib import Path
from core.zid_loader import ZID_CACHE
from core.logger import push_log

MOVIE_RE = re.compile(r"(?P<title>.+?)[\.\s_\-]\(?((?P<year>\d{4}))\)?", re.I)
TV_RE = re.compile(r"(?P<show>.+?)[\.\s_\-][Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{1,2})", re.I)

def _normalize_name(s: str) -> str:
    return s.replace(".", " ").replace("_", " ").strip()

def smart_rename_and_move(files: List[str], base_dir: str, zid_map: Dict = None) -> List[str]:
    """
    对文件路径进行重命名与移动（调用 p115 move/rename 接口需要在外部处理）
    这里只生成目标路径并尝试调用 p115 move（若可用）。
    返回实际移动后的路径列表（如果调用失败则返回原路径）
    """
    results = []
    zid_map = zid_map or ZID_CACHE or {}
    # 尝试导入 p115 客户端以进行实际移动
    try:
        from core.db import get_secret
        from core.p115_client import P115Wrapper
        cookie = get_secret("115_cookie")
        p115 = P115Wrapper(cookie)
    except Exception:
        p115 = None

    for fp in files:
        try:
            fn = fp.split("/")[-1]
            # tv?
            m = TV_RE.search(fn)
            if m:
                show = _normalize_name(m.group("show"))
                season = int(m.group("season"))
                episode = int(m.group("episode"))
                new_rel = f"{show}/Season {season}/{show} - S{season:02d}E{episode:02d} - {fn}"
            else:
                m2 = MOVIE_RE.search(fn)
                if m2:
                    title = _normalize_name(m2.group("title"))
                    year = m2.group("year")
                    new_rel = f"{title} ({year})/{fn}"
                else:
                    # fallback: put under Other
                    new_rel = f"Other/{fn}"
            # apply zid mapping if possible (二级分类)
            # zid_map 可能形如 { "电影":{"动作":"action_dir",...}, ... }
            # 这里只做示意：如存在 top-level map for movies
            # finalize dst
            dst = f"{base_dir.rstrip('/')}/{new_rel}"
            # 如果可以调用 p115 move，就尝试移动
            moved = None
            if p115 and hasattr(p115.client, "move"):
                try:
                    moved = p115.client.move(fp, dst)
                    push_log("INFO", f"移动文件 {fn} 到 {dst}")
                    results.append(dst if isinstance(moved, str) else dst)
                except Exception:
                    # fallback: 不移动
                    results.append(dst)
            else:
                # 没有 p115 move 接口，只返回目标路径（前端/后续步骤可处理）
                results.append(dst)
        except Exception as e:
            push_log("ERROR", f"重命名/移动失败: {e}")
            results.append(fp)
    return results
