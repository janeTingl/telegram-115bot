# backend/core/classify.py
"""
基于 zid.yml 做简单二级分类匹配
提供 match_category(title, metadata) -> (primary, secondary)
"""

from core.zid_loader import ZID_CACHE
from core.logger import push_log

def match_category(name: str, metadata: dict = None):
    """
    根据名称与可选 metadata 尝试匹配 zid.yml 中的二级分类
    返回 (primary, secondary)（如果找不到则返回 (None, None)）
    """
    metadata = metadata or {}
    name_low = name.lower()
    # 简单匹配：遍历 zid map 的 values，尝试关键字出现
    for primary, subs in (ZID_CACHE or {}).items():
        if not isinstance(subs, dict):
            continue
        for sub_key, pattern in subs.items():
            # pattern 可以是字符串或 list
            if isinstance(pattern, str):
                if pattern.lower() in name_low:
                    return (primary, sub_key)
            elif isinstance(pattern, list):
                for token in pattern:
                    if token.lower() in name_low:
                        return (primary, sub_key)
    # 无法匹配
    return (None, None)
