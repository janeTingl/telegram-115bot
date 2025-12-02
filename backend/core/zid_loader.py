# backend/core/zid_loader.py
import yaml
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
ZID = BASE / "zid.yml"

def load_zid():
    if not ZID.exists():
        return {}
    with open(ZID, "r", encoding="utf8") as f:
        return yaml.safe_load(f)

# 可在启动时加载并缓存
ZID_CACHE = load_zid()
