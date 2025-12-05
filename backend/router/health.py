"""Health and API coverage report router.

This router exposes `/api/health/report`, which inspects the FastAPI
application at runtime and produces a structured report describing:

1. All registered backend routes (method + path).
2. The list of business-critical endpoints that should exist according to the
   product design docs (mirrors the ticket checklist).
3. The frontend service functions that currently call backend endpoints.
4. A synthesized status (`ok`, `backend_only`, `frontend_only`, `missing`) for
   each expected endpoint so product owners can immediately see the gaps.

The endpoint is intentionally lightweight and does not execute downstream
requests. It operates purely on in-memory metadata so it can be called from
CI, observability dashboards, or by administrators via curl/Postman.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Tuple

from fastapi import APIRouter, Request

router = APIRouter()

# ---------------------------------------------------------------------------
# Expected backend endpoints (taken from the ticket checklist)
# ---------------------------------------------------------------------------
EXPECTED_ENDPOINTS: List[Dict[str, str]] = [
    {"category": "auth", "name": "用户登录", "method": "POST", "path": "/api/auth/login", "description": "用户登陆"},
    {"category": "auth", "name": "二步验证", "method": "POST", "path": "/api/2fa/verify", "description": "二步认证验证"},
    {"category": "auth", "name": "修改密码", "method": "POST", "path": "/api/auth/password", "description": "修改管理员密码"},
    {"category": "auth", "name": "生成 2FA 密钥", "method": "GET", "path": "/api/auth/2fa/generate", "description": "生成 2FA 密钥"},
    {"category": "config", "name": "加载配置", "method": "GET", "path": "/api/config/load", "description": "加载配置"},
    {"category": "config", "name": "保存配置", "method": "POST", "path": "/api/config/save_all", "description": "保存全部配置"},
    {"category": "config", "name": "获取配置", "method": "GET", "path": "/api/config", "description": "获取配置（统一接口）"},
    {"category": "config", "name": "设置配置", "method": "POST", "path": "/api/config", "description": "设置配置（统一接口）"},
    {"category": "config", "name": "保存代理配置", "method": "POST", "path": "/api/config/proxy", "description": "保存代理配置"},
    {"category": "file", "name": "列出文件", "method": "GET", "path": "/api/file/list", "description": "列出 115 网盘文件"},
    {"category": "file", "name": "移动文件", "method": "POST", "path": "/api/file/move", "description": "移动文件"},
    {"category": "file", "name": "重命名文件", "method": "POST", "path": "/api/file/rename", "description": "重命名文件"},
    {"category": "file", "name": "通知 Emby", "method": "POST", "path": "/api/file/notify_emby", "description": "通知 Emby 更新"},
    {"category": "file", "name": "启动整理任务", "method": "POST", "path": "/api/file/organize/start", "description": "启动网盘整理任务"},
    {"category": "offline", "name": "创建离线任务", "method": "POST", "path": "/api/offline/create", "description": "创建离线下载任务"},
    {"category": "offline", "name": "查询任务状态", "method": "GET", "path": "/api/offline/status", "description": "查询离线任务状态"},
    {"category": "tmdb", "name": "TMDB 搜索", "method": "POST", "path": "/api/tmdb/search", "description": "搜索电影/电视剧"},
    {"category": "tmdb", "name": "TMDB 详情", "method": "POST", "path": "/api/tmdb/details", "description": "获取 TMDB 详情"},
    {"category": "tmdb", "name": "TMDB 识别", "method": "POST", "path": "/api/tmdb/identify", "description": "AI 识别媒体"},
    {"category": "emby", "name": "刷新并探测", "method": "POST", "path": "/api/emby/refresh_and_probe", "description": "刷新并探测 Emby"},
    {"category": "emby", "name": "测试 Emby 连接", "method": "POST", "path": "/api/emby/test", "description": "测试 Emby 连接"},
    {"category": "notification", "name": "115 事件通知", "method": "POST", "path": "/api/notify/115_event", "description": "115 事件通知"},
    {"category": "meta", "name": "健康检查", "method": "GET", "path": "/healthz", "description": "健康检查"},
    {"category": "meta", "name": "运行状态", "method": "GET", "path": "/api/status", "description": "运行状态"},
    {"category": "meta", "name": "版本信息", "method": "GET", "path": "/api/version", "description": "版本信息"},
    {"category": "meta", "name": "健康报告", "method": "GET", "path": "/api/health/report", "description": "健康报告"},
]

# ---------------------------------------------------------------------------
# Frontend service coverage table (mirrors frontend/src/services/*)
# ---------------------------------------------------------------------------
FRONTEND_SERVICES: List[Dict[str, str]] = [
    {"name": "AuthService.login", "file": "src/services/auth.ts", "method": "POST", "path": "/api/auth/login"},
    {"name": "AuthService.verify2FA", "file": "src/services/auth.ts", "method": "POST", "path": "/api/2fa/verify"},
    {"name": "AuthService.saveAdminPassword", "file": "src/services/config.ts", "method": "POST", "path": "/api/auth/password"},
    {"name": "ConfigService.loadGlobalConfig", "file": "src/services/config.ts", "method": "GET", "path": "/api/config/load"},
    {"name": "ConfigService.saveGlobalConfig", "file": "src/services/config.ts", "method": "POST", "path": "/api/config/save_all"},
    {"name": "ConfigService.loadSettings", "file": "src/services/config.ts", "method": "GET", "path": "/api/config"},
    {"name": "ConfigService.saveSettings", "file": "src/services/config.ts", "method": "POST", "path": "/api/config"},
    {"name": "ConfigService.testEmbyConnection", "file": "src/services/config.ts", "method": "POST", "path": "/api/emby/test"},
    {"name": "ConfigService.saveProxyConfig", "file": "src/services/config.ts", "method": "POST", "path": "/api/config/proxy"},
    {"name": "ConfigService.generate2FASecret", "file": "src/services/config.ts", "method": "GET", "path": "/api/auth/2fa/generate"},
    {"name": "ConfigService.verifyAndSave2FA", "file": "src/services/config.ts", "method": "POST", "path": "/api/auth/2fa/verify"},
    {"name": "FileService.listFiles", "file": "src/services/file.ts", "method": "GET", "path": "/api/file/list"},
    {"name": "FileService.moveFile", "file": "src/services/file.ts", "method": "POST", "path": "/api/file/move"},
    {"name": "FileService.renameFile", "file": "src/services/file.ts", "method": "POST", "path": "/api/file/rename"},
    {"name": "FileService.notifyEmby", "file": "src/services/file.ts", "method": "POST", "path": "/api/file/notify_emby"},
    {"name": "OfflineService.createTask", "file": "src/services/offline.ts", "method": "POST", "path": "/api/offline/create"},
    {"name": "OfflineService.getTaskStatus", "file": "src/services/offline.ts", "method": "GET", "path": "/api/offline/status"},
    {"name": "TmdbService.search", "file": "src/services/tmdb.ts", "method": "POST", "path": "/api/tmdb/search"},
    {"name": "TmdbService.getDetails", "file": "src/services/tmdb.ts", "method": "POST", "path": "/api/tmdb/details"},
    {"name": "TmdbService.identify", "file": "src/services/tmdb.ts", "method": "POST", "path": "/api/tmdb/identify"},
    {"name": "EmbyService.refreshAndProbe", "file": "src/services/emby.ts", "method": "POST", "path": "/api/emby/refresh_and_probe"},
    {"name": "HealthService.getReport", "file": "src/services/health.ts", "method": "GET", "path": "/api/health/report"},
    {"name": "HealthService.getVersion", "file": "src/services/health.ts", "method": "GET", "path": "/api/version"},
    {"name": "HealthService.getStatus", "file": "src/services/health.ts", "method": "GET", "path": "/api/status"},
    {"name": "HealthService.check", "file": "src/services/health.ts", "method": "GET", "path": "/healthz"},
    {"name": "TaskService.startOrganizeTask", "file": "src/services/task.ts", "method": "POST", "path": "/api/file/organize/start"},
]


def _collect_backend_routes(request: Request) -> Tuple[List[Dict[str, str]], Dict[Tuple[str, str], Dict[str, str]]]:
    """Return the list of backend routes and a map for quick lookups."""
    backend_routes: List[Dict[str, str]] = []
    route_map: Dict[Tuple[str, str], Dict[str, str]] = {}

    for route in request.app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not path or not methods:
            continue
        filtered_methods = sorted(m for m in methods if m not in {"HEAD", "OPTIONS"})
        for method in filtered_methods:
            item = {
                "method": method,
                "path": path,
                "name": getattr(route, "name", None),
                "summary": getattr(route, "summary", None),
            }
            backend_routes.append(item)
            route_map[(method, path)] = item

    backend_routes.sort(key=lambda x: (x["path"], x["method"]))
    return backend_routes, route_map


def _build_expected_checks(route_map: Dict[Tuple[str, str], Dict[str, str]]) -> List[Dict[str, object]]:
    checks: List[Dict[str, object]] = []
    for spec in EXPECTED_ENDPOINTS:
        key = (spec["method"], spec["path"])
        frontend_coverage = [svc["name"] for svc in FRONTEND_SERVICES if svc["path"] == spec["path"] and svc["method"] == spec["method"]]
        has_backend = key in route_map
        has_frontend = len(frontend_coverage) > 0

        if has_backend and has_frontend:
            status = "ok"
        elif has_backend and not has_frontend:
            status = "backend_only"
        elif has_frontend and not has_backend:
            status = "frontend_only"
        else:
            status = "missing"

        checks.append({
            **spec,
            "status": status,
            "has_backend": has_backend,
            "frontend_services": frontend_coverage,
        })
    return checks


def _build_frontend_status(route_map: Dict[Tuple[str, str], Dict[str, str]]) -> List[Dict[str, object]]:
    frontend = []
    for svc in FRONTEND_SERVICES:
        key = (svc["method"], svc["path"])
        frontend.append({**svc, "backend_available": key in route_map})
    frontend.sort(key=lambda x: (x["path"], x["name"]))
    return frontend


@router.get("/health/report")
async def api_health_report(request: Request):
    """Return a structured report describing API coverage and health."""
    backend_routes, route_map = _collect_backend_routes(request)
    expected_checks = _build_expected_checks(route_map)
    frontend_status = _build_frontend_status(route_map)

    missing_or_incomplete = [c for c in expected_checks if c["status"] in {"missing", "frontend_only"}]
    backend_only = [c for c in expected_checks if c["status"] == "backend_only"]

    expected_available = sum(1 for c in expected_checks if c["has_backend"])
    total_expected = len(expected_checks)
    health_score = round((expected_available / total_expected) * 100, 2) if total_expected else 100.0

    summary = {
        "total_registered_routes": len(backend_routes),
        "expected_endpoint_total": total_expected,
        "expected_available": expected_available,
        "missing_or_incomplete": len(missing_or_incomplete),
        "backend_only": len(backend_only),
        "frontend_services_total": len(frontend_status),
        "frontend_without_backend": sum(1 for svc in frontend_status if not svc["backend_available"]),
        "health_score": health_score,
    }

    return {
        "code": 0,
        "msg": "ok",
        "data": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "expected_endpoints": expected_checks,
            "backend_routes": backend_routes,
            "frontend_services": frontend_status,
            "missing_endpoints": missing_or_incomplete,
            "backend_only_endpoints": backend_only,
        },
    }
