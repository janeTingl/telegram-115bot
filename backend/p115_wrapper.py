# backend/p115_wrapper.py
import traceback
from pathlib import Path

try:
    # 你的 p115client 库
    import p115client
    HAS_P115 = True
except Exception:
    HAS_P115 = False

class P115Error(Exception):
    pass

class P115Wrapper:
    def __init__(self):
        self.client = None
        if HAS_P115:
            # 尝试常见构造
            try:
                if hasattr(p115client, "P115Client"):
                    self.client = p115client.P115Client()
                else:
                    # fallback: try to import default object
                    self.client = p115client
            except Exception:
                self.client = None

    def ensure_client(self):
        if not HAS_P115 or not self.client:
            raise P115Error("p115client 库未安装或初始化失败")

    def login_with_cookie(self, cookie: str):
        try:
            self.ensure_client()
            if hasattr(self.client, "login_by_cookie"):
                return self.client.login_by_cookie(cookie)
            if hasattr(self.client, "login"):
                return self.client.login(cookie)
            # 可能是设置 cookie 到 client.session
            if hasattr(self.client, "set_cookie"):
                return self.client.set_cookie(cookie)
            raise P115Error("未在 p115client 中找到 login 接口，请告知真实方法名")
        except Exception as e:
            raise P115Error(str(e))

    def upload(self, local_path: str, remote_path: str = "/"):
        try:
            self.ensure_client()
            for name in ("upload_file", "upload", "fs_upload", "files_upload", "fs_files_upload"):
                if hasattr(self.client, name):
                    fn = getattr(self.client, name)
                    # 有些方法需要两个参数
                    try:
                        return fn(local_path, remote_path)
                    except TypeError:
                        return fn(local_path)
            raise P115Error("p115client 未提供已知的上传方法，请告知库中上传函数名称")
        except Exception as e:
            raise P115Error(str(e))

    def create_share(self, file_id: str, passwd: str = None):
        try:
            self.ensure_client()
            for name in ("create_share", "share_create", "share", "fs_create_share"):
                if hasattr(self.client, name):
                    fn = getattr(self.client, name)
                    try:
                        return fn(file_id, passwd)
                    except TypeError:
                        return fn(file_id)
            raise P115Error("p115client 未提供已知的分享方法，请告知库中分享函数名称")
        except Exception as e:
            raise P115Error(str(e))
