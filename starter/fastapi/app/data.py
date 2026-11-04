"""데이터 로드 계층. 원본(data/)은 수정하지 않는다.

과제에 맞게 load_* 와 clean_* 함수를 추가하고, 각 함수에 단위 테스트를 붙인다.
"""
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))


@lru_cache(maxsize=None)
def load_csv(name: str) -> pd.DataFrame:
    """서버 시작 후 처음 한 번만 읽고 메모리에 둔다(요청마다 다시 읽지 않음)."""
    return pd.read_csv(DATA_DIR / name, low_memory=False)


def list_files() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return sorted(p.name for p in DATA_DIR.glob("*.csv"))


def summary() -> list[dict]:
    """파일별 행·열 수. 정제 전후 건수 화면의 출발점."""
    out = []
    for name in list_files():
        df = load_csv(name)
        out.append({"file": name, "rows": int(len(df)), "cols": int(df.shape[1])})
    return out
