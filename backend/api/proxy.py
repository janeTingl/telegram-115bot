# backend/api/proxy.py
from fastapi import APIRouter, Form
import asyncio
import aiohttp
import time

router = APIRouter()

async def _probe_once(session, url, timeout=5, proxy=None):
    try:
        t0 = time.time()
        async with session.get(url, timeout=timeout, proxy=proxy) as r:
            if r.status == 200:
                return True, time.time() - t0
            return False, None
    except Exception:
        return False, None

@router.post("/api/proxy/check")
async def api_proxy_check(url: str = Form(...), proxy: str = Form(None), attempts: int = Form(3)):
    successes = 0
    total_time = 0.0
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(attempts):
            tasks.append(_probe_once(session, url, proxy=proxy))
        results = await asyncio.gather(*tasks, return_exceptions=True)
    for ok, rtt in results:
        if ok:
            successes += 1
            total_time += rtt
    rate = successes / attempts
    avg = (total_time / successes) if successes else None
    return {"code": 0, "data": {"success_rate": rate, "avg_rtt": avg, "attempts": attempts}}
