# backend/strm_generator.py
from pathlib import Path
from typing import List
import os

BASE = Path(__file__).resolve().parent
STRM_DIR = BASE / "strms"
STRM_DIR.mkdir(exist_ok=True)

def generate_strm_for_files(file_paths: List[str], target_dir: str = None, template: str = "{filepath}"):
    """
    file_paths: 本地文件绝对或相对路径
    template: strm 中写入内容的模板，例如 'smb://NAS{filepath}' 或 'file://{filepath}' 或 http url.
    target_dir: 生成 .strm 的目录（如果为空则在源文件同目录生成）
    返回生成的 strm 文件路径列表
    """
    out = []
    for fp in file_paths:
        f = Path(fp)
        if not f.exists():
            continue
        if target_dir:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            name = f.stem + ".strm"
            out_path = target / name
        else:
            out_path = f.with_suffix(".strm")
        content = template.format(filepath=str(f))
        with open(out_path, "w", encoding="utf8") as fh:
            fh.write(content)
        out.append(str(out_path))
    return out
