# backend/organizer.py
"""
文件整理模块（增强版）
支持：
- 电影 (title.year) 提取并移动到 pattern: {title} ({year})/{filename}
- 电视剧 SxxExx 或 SxEx 格式提取并组织到 pattern: {show}/Season {season}/{show} - S{season:02d}E{episode:02d} - {title}.ext
- 预览（不移动）与执行（移动）
- 可扩展为调用 TMDB 来精确匹配（占位）
"""

import re
from pathlib import Path
from typing import List, Dict, Any
import shutil
import os

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

# helpers for parsing
MOVIE_RE = re.compile(r"(?P<title>.+?)[\.\s_\-]\(?((?P<year>\d{4}))\)?", re.I)
TV_RE = re.compile(r"(?P<show>.+?)[\.\s_\-][Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{1,2})", re.I)
TV_RE_ALT = re.compile(r"(?P<show>.+?)[\.\s_\-](?P<season>\d{1,2})x(?P<episode>\d{1,2})", re.I)

def _normalize_title(s: str):
    return s.replace('.', ' ').replace('_', ' ').strip()

def preview_organize(rules: Dict[str, Any], src_dir: str):
    """
    返回操作预览：列表[{src, dst или None, reason}]
    rules 可包含 movie_pattern, tv_pattern, type (auto/movie/tv)
    """
    p = Path(src_dir)
    ops = []
    if not p.exists():
        return ops
    for f in p.rglob("*"):
        if f.is_file():
            name = f.name
            rel_dst = None
            reason = None
            # try tv first
            m = TV_RE.search(name) or TV_RE_ALT.search(name)
            if m:
                show = _normalize_title(m.group("show"))
                season = int(m.group("season"))
                episode = int(m.group("episode"))
                title_only = name
                pattern = rules.get("tv_pattern", "{show}/Season {season}/{show} - S{season:02d}E{episode:02d} - {title}")
                rel = pattern.format(show=show, season=season, episode=episode, title=title_only, filename=name)
                rel_dst = str(Path(src_dir) / rel)
                reason = "tv_match"
            else:
                # try movie
                m2 = MOVIE_RE.search(name)
                if m2:
                    title = _normalize_title(m2.group("title"))
                    year = m2.group("year")
                    pattern = rules.get("movie_pattern", "{title} ({year})/{filename}")
                    rel = pattern.format(title=title, year=year, filename=name)
                    rel_dst = str(Path(src_dir) / rel)
                    reason = "movie_match"
                else:
                    reason = "no_match"
            ops.append({"src": str(f), "dst": rel_dst, "reason": reason})
    return ops

def run_organize(rules: Dict[str, Any], src_dir: str, dry_run: bool=False):
    """
    执行整理：如果 dry_run True 则不移动，只返回计划动作
    """
    ops = preview_organize(rules, src_dir)
    applied = []
    for op in ops:
        src = op["src"]
        dst = op.get("dst")
        if not dst:
            applied.append({"src": src, "dst": None, "skipped": True, "reason": op.get("reason")})
            continue
        if dry_run:
            applied.append({"src": src, "dst": dst, "skipped": False})
            continue
        try:
            dstp = Path(dst)
            dstp.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            applied.append({"src": src, "dst": dst, "skipped": False})
        except Exception as e:
            applied.append({"src": src, "dst": dst, "error": str(e)})
    return applied

# 可扩展：TMDB 精准匹配（占位）
def enhance_with_tmdb(ops: List[Dict[str, Any]], tmdb_api_key: str = None):
    """
    如果传入 tmdb_api_key，可对 movie 匹配进行 TMDB 校验并返回更准确 title/year。
    目前为占位实现：如果需要我可以实现完整 TMDB 查询流程。
    """
    # TODO: implement TMDB lookup
    return ops
