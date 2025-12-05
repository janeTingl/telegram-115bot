#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/engine/project/backend')

from main import app

print("=== Testing Backend Routes ===\n")

routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ', '.join(sorted(route.methods))
        routes.append((route.path, methods))

routes.sort()

print("Available API Routes:")
print("-" * 60)
for path, methods in routes:
    if path.startswith('/api/'):
        print(f"{methods:12} {path}")

print("\n=== Key Frontend Requirements ===")
print("-" * 60)

required_routes = [
    "POST /api/auth/login",
    "POST /api/auth/password",
    "GET  /api/auth/2fa/generate",
    "POST /api/auth/2fa/verify",
    "GET  /api/config/load",
    "POST /api/config/save_all",
    "POST /api/config/proxy",
    "GET  /api/file/list",
    "POST /api/file/organize/start",
    "GET  /api/health/report",
]

print("\nRequired routes:")
for req_route in required_routes:
    method, path = req_route.split(' ', 1)
    found = False
    for route_path, route_methods in routes:
        if route_path == path.strip() and method in route_methods:
            found = True
            break
    status = "✓" if found else "✗"
    print(f"{status} {req_route}")

print("\n=== Test Complete ===")
