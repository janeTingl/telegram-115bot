# backend/router/tmdb.py
from fastapi import APIRouter, Form
from core.tmdb_client import search_movie_by_name, search_tv_by_name, get_movie_details, get_tv_details, ai_assist_identify
from core.logger import push_log

router = APIRouter()

@router.post("/api/tmdb/search")
def api_tmdb_search(q: str = Form(...), typ: str = Form("movie"), year: int = None):
    try:
        if typ == "movie":
            res = search_movie_by_name(q, year)
        else:
            res = search_tv_by_name(q, year)
        return {"code": 0, "data": res}
    except Exception as e:
        push_log("ERROR", f"TMDB search 错误: {e}")
        return {"code": 1, "msg": str(e)}

@router.post("/api/tmdb/details")
def api_tmdb_details(tmdb_id: int = Form(...), typ: str = Form("movie")):
    try:
        if typ == "movie":
            d = get_movie_details(tmdb_id)
        else:
            d = get_tv_details(tmdb_id)
        return {"code": 0, "data": d}
    except Exception as e:
        push_log("ERROR", f"TMDB details 错误: {e}")
        return {"code": 1, "msg": str(e)}

@router.post("/api/tmdb/identify")
def api_tmdb_identify(name: str = Form(...), typ: str = Form("movie")):
    try:
        if typ == "movie":
            cands = search_movie_by_name(name)
        else:
            cands = search_tv_by_name(name)
        # 可选 AI 协助
        ai_choice = ai_assist_identify(name, cands)
        return {"code": 0, "data": {"candidates": cands, "ai_choice": ai_choice}}
    except Exception as e:
        push_log("ERROR", f"TMDB identify 错误: {e}")
        return {"code": 1, "msg": str(e)}
