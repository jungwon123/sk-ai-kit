#!/usr/bin/env python3
"""데이터 폴더(또는 파일)를 점검해 markdown 요약을 출력한다.

사용:
  python3 scripts/profile_data.py data
  python3 scripts/profile_data.py data/a.csv data/b.xlsx --out out/profile.md

점검 항목: 행/열 수, 컬럼 타입, 결측, 완전 중복 행, ID·범주 컬럼의 고유값과
표기 변형(대소문자·공백·하이픈·언더스코어만 다른 값), 단위로 보이는 컬럼,
수치 범위(0·음수 개수), 날짜 범위, 반복되는 키.
원본 데이터는 수정하지 않는다. 필요 패키지: pandas (xlsx는 openpyxl).
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    sys.exit("pandas가 필요합니다: pip install pandas openpyxl")

EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".json", ".parquet"}
UNIT_HINT = re.compile(r"(unit|단위|uom)", re.I)
ID_HINT = re.compile(r"(^id$|_id$|id_|code|코드|번호|eqp|lot|wafer|chamber|tool|line|sku|product)", re.I)


def load(path: Path) -> dict:
    s = path.suffix.lower()
    if s == ".csv":
        return {path.name: pd.read_csv(path, low_memory=False)}
    if s == ".tsv":
        return {path.name: pd.read_csv(path, sep="\t", low_memory=False)}
    if s in (".xlsx", ".xls"):
        sheets = pd.read_excel(path, sheet_name=None)
        return {f"{path.name}#{k}": v for k, v in sheets.items()}
    if s == ".json":
        try:
            return {path.name: pd.read_json(path)}
        except ValueError:
            return {path.name: pd.read_json(path, lines=True)}
    if s == ".parquet":
        return {path.name: pd.read_parquet(path)}
    return {}


PREFIX = re.compile(r"^(CHAMBER|CH|EQP|EQ|TOOL|LINE|NO|NUM|#)(?=[A-Z0-9])")


def norm_key(v: str) -> str:
    """대소문자·공백·하이픈·언더스코어·점을 무시하고, 흔한 접두어(CH-, EQP- 등)를 뗀 비교용 키."""
    k = re.sub(r"[\s\-_.]", "", str(v)).upper()
    return PREFIX.sub("", k) or k


def variants(series: "pd.Series", limit: int = 5):
    """표기만 다른 값 묶음을 찾는다."""
    vals = series.dropna().astype(str)
    if vals.nunique() > 5000:
        return [], 0
    groups = {}
    for raw in vals.unique():
        groups.setdefault(norm_key(raw), set()).add(raw)
    out = [sorted(g) for g in groups.values() if len(g) > 1]
    out.sort(key=len, reverse=True)
    return out[:limit], len(out)


def is_text(series: "pd.Series") -> bool:
    return series.dtype == object or pd.api.types.is_string_dtype(series)


def looks_date(series: "pd.Series") -> bool:
    if not is_text(series):
        return False
    sample = series.dropna().astype(str).head(50)
    if sample.empty:
        return False
    return sample.str.match(r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}").mean() > 0.8


def profile(name: str, df: "pd.DataFrame") -> str:
    L = [f"## {name}", "", f"- 행 {len(df):,} / 열 {df.shape[1]}", f"- 완전 중복 행: {int(df.duplicated().sum()):,}", ""]
    L += ["| 컬럼 | 타입 | 결측 | 고유값 | 요약 |", "| --- | --- | --- | --- | --- |"]
    notes = []
    for c in df.columns:
        s = df[c]
        miss = int(s.isna().sum() + (s.astype(str).str.strip() == "").sum() if is_text(s) else s.isna().sum())
        nun = int(s.nunique(dropna=True))
        if pd.api.types.is_numeric_dtype(s):
            d = s.dropna()
            summ = f"min {d.min():g} / max {d.max():g} / mean {d.mean():.4g}" if len(d) else "-"
            zeros, neg = int((d == 0).sum()), int((d < 0).sum())
            if zeros or neg:
                summ += f" / 0값 {zeros}, 음수 {neg}"
        elif looks_date(s):
            d = pd.to_datetime(s, errors="coerce")
            summ = f"{d.min()} ~ {d.max()} (파싱 실패 {int(d.isna().sum() - s.isna().sum())})"
        else:
            top = s.astype(str).value_counts().head(4)
            summ = ", ".join(f"{k}({v})" for k, v in top.items())
            if len(summ) > 90:
                summ = summ[:87] + "..."
        L.append(f"| {c} | {s.dtype} | {miss:,} | {nun:,} | {summ} |")
        if is_text(s) and (ID_HINT.search(str(c)) or nun <= 200):
            v, n = variants(s)
            if v:
                more = f" 외 {n - len(v)}묶음" if n > len(v) else ""
                notes.append(f"- **표기 변형** `{c}` ({n}묶음): " + "; ".join(" / ".join(f"`{x}`" for x in g) for g in v) + more)
        if UNIT_HINT.search(str(c)):
            notes.append(f"- **단위 컬럼** `{c}`: " + ", ".join(f"{k}({v})" for k, v in s.value_counts().items()))
    # 반복 키: ID처럼 보이는 첫 컬럼의 중복
    key = next((c for c in df.columns if ID_HINT.search(str(c))), None)
    if key is not None:
        dup = int(df[key].duplicated().sum())
        notes.append(f"- 키 후보 `{key}`: 고유 {df[key].nunique():,}, 반복 {dup:,}행 (이력·재작업·조인 시 행 증가 주의)")
    if notes:
        L += ["", "확인할 점:", *notes]
    return "\n".join(L) + "\n"


def join_keys(frames: dict) -> str:
    """여러 파일에 같은 이름으로 있는 컬럼을 조인 키 후보로 보고, 값 겹침과 행 증가 위험을 요약한다."""
    names = list(frames)
    cols = {}
    for n, df in frames.items():
        for c in df.columns:
            cols.setdefault(c, []).append(n)
    shared = {c: ns for c, ns in cols.items() if len(ns) > 1}
    if not shared:
        return ""
    L = ["## 파일 간 공통 컬럼 (조인 키 후보)", "",
         "| 컬럼 | 파일 | 고유값 (파일별) | 값 겹침 | 키당 최대 행 수 (파일별) |", "| --- | --- | --- | --- | --- |"]
    for c, ns in shared.items():
        sets = [set(frames[n][c].dropna().astype(str).map(norm_key)) for n in ns]
        inter = set.intersection(*sets)
        union = set.union(*sets)
        fan = [int(frames[n][c].value_counts().max()) if len(frames[n]) else 0 for n in ns]
        L.append(f"| {c} | {', '.join(ns)} | {' / '.join(str(len(x)) for x in sets)} | "
                 f"{len(inter)}/{len(union)} | {' / '.join(map(str, fan))} |")
    L += ["", "- 키당 최대 행 수가 2 이상인 파일끼리 조인하면 행이 늘어난다(1:N, N:M). 조인 전후 행 수를 확인한다.",
          "- 값 겹침은 표기 정규화(norm_key) 기준이다. 원본 값으로 조인하면 더 적게 맞을 수 있다.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args()
    files = []
    for p in map(Path, a.paths):
        files += sorted(f for f in p.rglob("*") if f.suffix.lower() in EXTS) if p.is_dir() else [p]
    parts = ["# 데이터 점검 결과", ""]
    frames = {}
    for f in files:
        try:
            for name, df in load(f).items():
                frames[name] = df
                parts.append(profile(name, df))
        except Exception as e:  # 읽기 실패도 결과에 남긴다
            parts.append(f"## {f.name}\n\n- 읽기 실패: {e}\n")
    if len(frames) > 1:
        parts.append(join_keys(frames))
    text = "\n".join(parts)
    print(text)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
