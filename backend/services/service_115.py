# ... (File: backend/services/service_115.py)

# 导入和类定义部分省略...
# from p115client import P115Client
# class Drive115Service: ...

    def get_file_list(self, cid: str = "0") -> List[Dict[str, Any]]:
        """
        同步方法：调用 p115client 获取文件列表，并格式化数据。
        """
        if not self.client: return []
        try:
            # 假设 p115client 的接口
            resp = self.client.fs_files(cid=cid, limit=100)
            if resp.get("state"):
                # **【连通点：数据格式化，适配前端 FileSelector】**
                return [{
                    "id": str(x.get("cid", x.get("fid"))),
                    "name": x.get("n"),
                    "children": "cid" in x, # 关键字段，前端用它来判断是否可双击进入
                    "date": x.get("te")
                } for x in resp.get("data", [])]
        except Exception as e:
            logger.error(f"115 List Error: {e}")
        return []

# drive_115 = Drive115Service()