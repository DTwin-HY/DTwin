from pathlib import Path
from typing import Any

import tomli

CONFIG_PATH = Path(__file__).parent.resolve() / "config.toml"
with open(CONFIG_PATH, "rb") as f:
    _config = tomli.load(f)


def get(key: str | None = None, default: Any = None) -> Any:
    """
    Get a value from the TOML config.

    - If key is None or empty, returns the whole config dict
    - Supports dotted key paths like "data_generation.rows_to_generate"
    - Returns `default` when the path is missing
    """
    if not key:
        return _config

    parts = key.split(".")
    cur = _config
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur
