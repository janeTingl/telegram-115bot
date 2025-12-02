# backend/utils/strm.py
"""
根据给定文件路径生成 .strm 文件。
对于网盘文件，我们直接在同目录下生成 .strm（如果允许）。
template 参数可设置 STRM 内写法，例如 file://{filepath} 或 http://.../{filepath}
"""

from typing import List
from pathlib import Path
from core.logger import push_log
import os

def generate_strm_for_files(file_paths: List[str], target_dir: str = None, template: str = "{filepath}") -> List[str]:
    out = []
    for fp in file_paths:
        try:
            # 目标 path
            p = Path(fp)
            if target_dir:
                target = Path(target_dir)
                target.mkdir(parents=True, exist_ok=True)
                name = p.stem + ".strm"
                out_path = target / name
            else:
                out_path = p.with_suffix(".strm")
                out_path.parent.mkdir(parents=True, exist_ok=True)
            content = template.format(filepath=str(fp))
            # 如果 out_path 代表远程网盘（字符串路径），这里尝试本地写入到 backend/strms 目录并记录映射
            # 通常网盘上写文件需要调用 p115 API；为简单起见我们在后端本地生成 strm 文件供前端下载/查看
            with open(out_path, "w", encoding="utf8") as fh:
                fh.write(content)
            out.append(str(out_path))
        except Exception as e:
            push_log("ERROR", f"生成 STRM 失败: {e}")
    push_log("INFO", f"生成 {len(out)} 个 STRM 文件")
    return out
