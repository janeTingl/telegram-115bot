# backend/core/p115_client.py
"""
p115client 适配器：以健壮方式调用你仓库的 p115client。
本模块不打印敏感数据（如 cookie），调用方负责保密。
"""

from typing import Optional, Dict, Any, List
import importlib
import time

# 日志
from core.logger import push_log

P115 = None
_loaded = False

def _try_import():
    global P115, _loaded
    if _loaded:
        return
    try:
        P115 = importlib.import_module("p115client")
        _loaded = True
        push_log("INFO", "已导入 p115client 模块")
    except Exception as e:
        P115 = None
        _loaded = True
        push_log("WARN", f"无法导入 p115client: {e}")

_try_import()

class P115Error(Exception):
    pass

class P115Wrapper:
    def __init__(self, cookie: Optional[str] = None):
        """
        cookie: 可选 cookie 字符串（不记录）
        """
        if P115 is None:
            raise P115Error("p115client 模块不可用")
        self.cookie = cookie
        self.client = None
        self._init_client()

    def _init_client(self):
        # 尝试多种构造方式
        try:
            if hasattr(P115, "P115Client"):
                try:
                    # 优先尝试不传敏感参数的构造，然后通过方法注入 cookie
                    self.client = P115.P115Client()
                except Exception:
                    # 有些实现需要 cookie 参数
                    try:
                        self.client = P115.P115Client(self.cookie) if self.cookie else P115.P115Client()
                    except Exception as e:
                        raise
            else:
                # 如果模块本身就是一个 client 实例或提供函数集合
                self.client = P115
        except Exception as e:
            raise P115Error(f"初始化 p115client 失败: {e}")

    def login_with_cookie(self, cookie: str) -> bool:
        # 不记录 cookie
        try:
            if hasattr(self.client, "login_by_cookie"):
                return self.client.login_by_cookie(cookie)
            if hasattr(self.client, "login"):
                # login 可能接受 cookie 或 username/password；我们优先尝试 cookie
                try:
                    return self.client.login(cookie)
                except TypeError:
                    return self.client.login()
            if hasattr(self.client, "set_cookie"):
                self.client.set_cookie(cookie)
                return True
            raise P115Error("p115client 未实现 cookie 登录接口")
        except Exception as e:
            raise P115Error(str(e))

    def list_files(self, path: str = "/", limit: int = 100) -> List[Dict[str, Any]]:
        # 尝试多种常用方法名
        for name in ("list_files", "fs_list", "files_list", "list"):
            if hasattr(self.client, name):
                fn = getattr(self.client, name)
                try:
                    return fn(path, limit) if callable(fn) else []
                except TypeError:
                    try:
                        return fn(path)
                    except Exception as e:
                        continue
        raise P115Error("p115client 未找到 list_files 方法")

    def create_offline_task(self, url: str, params: Dict = None) -> Dict:
        """
        创建离线下载任务（适配 p115client 的不同签名）
        返回任务 info（id/status/message）
        """
        params = params or {}
        for name in ("create_offline_task","offline_task_create","add_offline_task","task_create"):
            if hasattr(self.client, name):
                fn = getattr(self.client, name)
                try:
                    return fn(url, **params)
                except TypeError:
                    try:
                        return fn(url)
                    except Exception:
                        continue
        raise P115Error("p115client 未提供离线任务创建接口")

    def get_offline_status(self, task_id: str) -> Dict:
        for name in ("get_offline_task","offline_task_status","task_status","get_task"):
            if hasattr(self.client, name):
                fn = getattr(self.client, name)
                try:
                    return fn(task_id)
                except TypeError:
                    try:
                        return fn()
                    except Exception:
                        continue
        raise P115Error("p115client 未提供离线任务状态查询接口")

    def offline_transfer_to_115(self, task_id: str, target_folder: str = "/") -> Dict:
        """
        将离线任务转存到网盘。具体函数名视 p115client 版本而定。
        """
        for name in ("transfer_offline","offline_transfer","save_offline","offline_task_transfer"):
            if hasattr(self.client, name):
                fn = getattr(self.client, name)
                try:
                    return fn(task_id, target_folder)
                except TypeError:
                    try:
                        return fn(task_id)
                    except Exception:
                        continue
        # 有些 p115client 将转存作为离线任务自动完成，直接返回 OK
        return {"status": "unknown", "note": "no explicit transfer api found"}

    def upload_file(self, local_path: str, remote_path: str = "/") -> Dict:
        for name in ("upload_file","upload","fs_upload","files_upload"):
            if hasattr(self.client, name):
                fn = getattr(self.client, name)
                try:
                    return fn(local_path, remote_path)
                except TypeError:
                    try:
                        return fn(local_path)
                    except Exception:
                        continue
        raise P115Error("p115client 未提供已知的上传方法")

    def create_share(self, file_id: str, passwd: Optional[str] = None) -> Dict:
        for name in ("create_share","share_create","share","fs_create_share"):
            if hasattr(self.client, name):
                fn = getattr(self.client, name)
                try:
                    return fn(file_id, passwd) if passwd else fn(file_id)
                except TypeError:
                    try:
                        return fn(file_id)
                    except Exception:
                        continue
        raise P115Error("p115client 未提供已知的分享方法")
