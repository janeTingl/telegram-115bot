import os
import yaml
import re
import logging
import httpx
from typing import Dict, Any
from tmdbv3api import TMDb, Movie, TV, Search
from services.service_115 import drive_115
from services.service_ai import ai_service

logger = logging.getLogger("Organizer")

class MediaOrganizer:
    def __init__(self):
        self.tmdb = TMDb()
        self.tmdb_search = Search()
        self.tmdb_movie = Movie()
        self.tmdb_tv = TV()
        self.rules = {}
        self.organize_conf = {}
        self.emby_conf = {}
        self.load_rules()

    def init_config(self, app_config: Dict[str, Any]):
        tmdb_conf = app_config.get("tmdb", {})
        self.tmdb.api_key = tmdb_conf.get("apiKey")
        self.tmdb.language = tmdb_conf.get("language", "zh-CN")
        self.organize_conf = app_config.get("organize", {})
        self.emby_conf = app_config.get("emby", {})
        ai_service.init_config(app_config)

    def load_rules(self):
        path = "zid.yml"
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: self.rules = yaml.safe_load(f)

    def parse_filename(self, filename: str):
        name = os.path.splitext(filename)[0]
        year_match = re.search(r'[\(\.](\d{4})[\)\.]', name)
        year = year_match.group(1) if year_match else None
        clean_name = re.split(r'[\(\.]1080|[\(\.]2160', name, flags=re.IGNORECASE)[0].replace(".", " ").strip()
        return clean_name, year

    def get_tmdb_info(self, keyword, year, is_movie=True):
        if not self.tmdb.api_key: return None
        try:
            res = self.tmdb_search.movies(term=keyword, year=year) if is_movie else self.tmdb_search.tv_shows(term=keyword, first_air_date_year=year)
            if res:
                media_id = res[0].id
                return self.tmdb_movie.details(media_id) if is_movie else self.tmdb_tv.details(media_id)
        except Exception as e: logger.warning(f"TMDB Error: {e}")
        return None

    def match_category(self, info, media_type='movie'):
        if media_type not in self.rules: return "未分类"
        for cat, conds in self.rules[media_type].items():
            if not conds: continue
            match = True
            
            # Genre
            if 'genre_ids' in conds:
                target = str(conds['genre_ids']).split(',')
                info_genres = [str(g['id']) for g in getattr(info, 'genres', [])]
                if not any(t in info_genres for t in target): match = False
            
            # Country
            if match and ('origin_country' in conds or 'production_countries' in conds):
                target = conds.get('origin_country', conds.get('production_countries')).split(',')
                info_c = getattr(info, 'origin_country', [])
                if not info_c and hasattr(info, 'production_countries'):
                    info_c = [c['iso_3166_1'] for c in info.production_countries]
                
                exclude = any(t.startswith('!') for t in target)
                cleant = [t.replace('!', '') for t in target]
                has_inter = any(c in cleant for c in info_c)
                if exclude and has_inter: match = False
                if not exclude and not has_inter: match = False
            
            if match: return cat
        return "未分类"

    async def run_organize(self):
        if not self.organize_conf.get("enabled"): return
        src_cid = self.organize_conf.get("sourceCid", "0")
        tgt_cid = self.organize_conf.get("targetCid", "0")
        
        files = drive_115.get_file_list(src_cid)
        for file in files:
            if file['children']: continue
            filename = file['name']
            
            # AI 优先
            parsed = await ai_service.parse_filename(filename)
            if parsed and parsed.get("title"):
                kw, yr = parsed['title'], parsed.get('year')
                is_tv = parsed.get('season') is not None
            else:
                kw, yr = self.parse_filename(filename)
                is_tv = bool(re.search(r'S\d+E\d+', filename, re.IGNORECASE))
            
            info = self.get_tmdb_info(kw, yr, not is_tv)
            if not info: continue
            
            cat = self.match_category(info, 'tv' if is_tv else 'movie')
            logger.info(f"Matched {filename} -> {cat}")
            
            # 移动文件逻辑
            try:
                # 1. 确保目录
                res = drive_115.client.fs_mkdir(name=cat, pid=tgt_cid)
                real_tgt = res.get('id') or res.get('cid')
                # 2. 移动
                drive_115.client.fs_move(file['id'], pid=real_tgt)
                logger.info(f"✅ Moved: {filename}")
            except Exception as e:
                logger.error(f"Move Error: {e}")

        # 刷新 Emby
        if self.emby_conf.get("refreshAfterOrganize"):
             url = self.emby_conf.get("serverUrl")
             key = self.emby_conf.get("apiKey")
             if url and key:
                 try:
                     async with httpx.AsyncClient() as c:
                         await c.post(f"{url.rstrip('/')}/Library/Refresh", params={"api_key": key})
                 except: pass

organizer = MediaOrganizer()
