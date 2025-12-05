# API Health Report & Integrity Checklist

This repository now exposes a dedicated runtime audit endpoint that inspects
both the FastAPI backend and the React service layer to highlight integration
gaps in a single JSON payload.

```
GET /api/health/report
```

## What the endpoint provides

- **Registered backend routes** – every method/path pair that FastAPI knows
  about at runtime (after all routers are mounted).
- **Expected endpoints** – a canonical list that mirrors the ticket checklist
  (auth, config, file, offline, TMDB, Emby, STRM, notification, meta). Each
  entry is annotated with `status`:
  - `ok`: backend route exists and a frontend service uses it.
  - `backend_only`: implemented on the backend but no frontend caller yet.
  - `frontend_only`: frontend expects it but the backend is missing it.
  - `missing`: neither side currently implements it.
- **Frontend service coverage** – every function under `frontend/src/services/*`
  together with whether the backend route it calls is available.
- **Summary metrics** – total routes, coverage counts, missing endpoints, and a
  simple health score (percentage of expected endpoints that exist on the
  backend).

## Example usage

```bash
curl -s http://localhost:8000/api/health/report | jq
```

Sample (truncated) response:

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "generated_at": "2024-03-05T08:32:10.123456+00:00",
    "summary": {
      "total_registered_routes": 27,
      "expected_endpoint_total": 29,
      "expected_available": 12,
      "missing_or_incomplete": 17,
      "backend_only": 3,
      "frontend_services_total": 9,
      "frontend_without_backend": 0,
      "health_score": 41.38
    },
    "expected_endpoints": [
      {
        "category": "auth",
        "name": "用户登录",
        "method": "POST",
        "path": "/api/auth/login",
        "status": "ok",
        "frontend_services": ["AuthService.login"]
      },
      {
        "category": "config",
        "name": "获取所有配置",
        "method": "GET",
        "path": "/api/config/all",
        "status": "missing",
        "frontend_services": []
      }
    ],
    "backend_routes": [
      {"method": "GET", "path": "/api/status"},
      {"method": "POST", "path": "/api/file/move"}
    ]
  }
}
```

## When to use it

- **During development** – quickly verify whether newly added routers are being
  picked up, and whether the frontend has been wired up.
- **In CI or health dashboards** – a failing health score (or any `missing`
  entry) is an early warning that the product checklist is not fully covered.
- **For manual audits** – the JSON already lists discrepancies, so PMs and QA
  can align on priorities without digging through code.

No additional authentication is required right now because the endpoint only
surfaces metadata. If that ever changes, wrap it with the same auth guards used
for other administrative APIs.
