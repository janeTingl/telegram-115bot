# backend/organizer.py
import re
from pathlib import Path
from typing import List, Dict, Any
import shutil
import json

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

def list_files(path: str = "."):
    p = Path(path)
    if not p.exists():
        return []
    res = []
    for x in p.iterdir():
        res.append({"name": x.name, "path": str(x), "is_dir": x.is_dir()})
    return res

def preview_organize(rules: Dict[str, Any], src_dir: str):
    """
    rules 示例:
    {
      "type": "movie" or "tv",
      "movie_pattern": "{title} ({year})/{filename}",
      "tv_pattern": "{show}/Season {season}/{show} - S{season:02d}E{episode:02d} - {title}.mkv",
      "regex": "some regex to extract fields token"
    }
    返回将要进行的操作列表，不执行
    """
    p = Path(src_dir)
    ops = []
    for f in p.rglob("*"):
        if f.is_file():
            # 简单示例：如果规则 type==movie 并尝试从文件名提取 (Title.Year)
            if rules.get("type") == "movie":
                m = re.search(r"(?P<title>.+?)[ ._\\-]\\(?P<year>\\d{4})", f.name)
                if m:
                    title = m.group("title").replace(".", " ").replace("_", " ").strip()
                    year = m.group("year")
                    new_rel = rules.get("movie_pattern", "{title} ({year})/{filename}").format(title=title, year=year, filename=f.name)
                    ops.append({"src": str(f), "dst": str(Path(src_dir) / new_rel)})
                else:
                    ops.append({"src": str(f), "dst": None})
            else:
                # 默认：不变
                ops.append({"src": str(f), "dst": None})
    return ops

def run_organize(rules: Dict[str, Any], src_dir: str, dry_run: bool=False):
    ops = preview_organize(rules, src_dir)
    applied = []
    for op in ops:
        src = op["src"]
        dst = op.get("dst")
        if not dst:
            continue
        dst_path = Path(dst)
        if dry_run:
            applied.append({"src": src, "dst": dst, "skipped": False})
            continue
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dst)
        applied.append({"src": src, "dst": dst, "skipped": False})
    return applied
