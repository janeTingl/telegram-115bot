# backend/core/tmdb_client.py
import requests
import time
from typing import Optional, Dict, Any, List
from core.db import get_secret, get_config
from core.logger import push_log

TMDB_API_URL = "https://api.themoviedb.org/3"

def _get_tmdb_key() -> Optional[str]:
    # 从 secrets 中读取 TMDB API Key（密文存储）
    return get_secret("tmdb_api_key", None)

def search_movie_by_name(name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
    key = _get_tmdb_key()
    if not key:
        push_log("WARN", "TMDB API Key 未配置，search_movie_by_name 返回空")
        return []
    params = {"api_key": key, "query": name, "include_adult": False}
    if year:
        params["year"] = year
    r = requests.get(f"{TMDB_API_URL}/search/movie", params=params, timeout=8)
    if r.status_code != 200:
        push_log("WARN", f"TMDB 搜索失败: {r.status_code}")
        return []
    data = r.json()
    return data.get("results", [])

def get_movie_details(tmdb_id: int) -> Dict[str, Any]:
    key = _get_tmdb_key()
    if not key:
        push_log("WARN", "TMDB API Key 未配置，get_movie_details 返回空")
        return {}
    r = requests.get(f"{TMDB_API_URL}/movie/{tmdb_id}", params={"api_key": key}, timeout=8)
    if r.status_code != 200:
        push_log("WARN", f"TMDB 获取详情失败: {r.status_code}")
        return {}
    return r.json()

def search_tv_by_name(name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
    key = _get_tmdb_key()
    if not key:
        push_log("WARN", "TMDB API Key 未配置，search_tv_by_name 返回空")
        return []
    params = {"api_key": key, "query": name}
    r = requests.get(f"{TMDB_API_URL}/search/tv", params=params, timeout=8)
    if r.status_code != 200:
        push_log("WARN", f"TMDB TV 搜索失败: {r.status_code}")
        return []
    return r.json().get("results", [])

def get_tv_details(tmdb_id: int) -> Dict[str, Any]:
    key = _get_tmdb_key()
    if not key:
        push_log("WARN", "TMDB API Key 未配置，get_tv_details 返回空")
        return {}
    r = requests.get(f"{TMDB_API_URL}/tv/{tmdb_id}", params={"api_key": key}, timeout=8)
    if r.status_code != 200:
        push_log("WARN", f"TMDB 获取 TV 详情失败: {r.status_code}")
        return {}
    return r.json()

# 可选：AI 辅助识别占位（如果配置了 OPENAI_KEY，可调用）
def ai_assist_identify(name: str, candidates: List[Dict[str,Any]]) -> Optional[Dict[str,Any]]:
    """
    占位：若你配置 OPENAI_KEY 并希望使用大模型帮助匹配，可以实现此函数调用 OpenAI API
    这里仅做最小实现提示，不直接调用模型（避免在未配置 KEY 时失效）。
    """
    openai_key = get_secret("openai_api_key", None)
    if not openai_key:
        return None
    # 若需要我可以把实际请求实现写入（需你允许在 Docker 中包含 openai 或直接使用 requests）
    push_log("INFO", "AI 辅助识别已启用（占位）")
    # 简单返回第一个候选作为占位
    return candidates[0] if candidates else None
