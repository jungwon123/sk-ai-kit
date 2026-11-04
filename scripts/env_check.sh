#!/usr/bin/env bash
# 시작 직후 1분 환경 점검. 결과는 몇 줄만 출력하고, 문제는 [!!]로 표시한다.
# 사용: bash scripts/env_check.sh
set -u
ok() { printf '  [OK] %s\n' "$1"; }
ng() { printf '  [!!] %s\n' "$1"; }
echo "== 환경 점검"
py=$(python3 -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])' 2>/dev/null)
if [ -n "$py" ]; then ok "Python $py"; else ng "python3 없음"; fi
python3 - <<'PY' 2>/dev/null
import importlib, sys
from datetime import datetime
mods = ["pandas", "numpy", "fastapi", "uvicorn", "yaml", "pytest", "httpx", "sklearn", "playwright"]
have, miss = [], []
for m in mods:
    try:
        v = getattr(importlib.import_module(m), "__version__", "?")
        have.append(f"{m} {v}")
    except Exception:
        miss.append(m)
print("  [OK] 설치됨: " + ", ".join(have) if have else "  [!!] 주요 패키지 없음")
if miss:
    print("  [..] 없음: " + ", ".join(miss) + "  (필요한 것만 pip install -q)")
try:
    datetime.fromisoformat("2026-10-01T00:00:00Z")
    print("  [OK] fromisoformat이 'Z' 시각을 읽음")
except ValueError:
    print("  [!!] 이 Python의 fromisoformat은 'Z'로 끝나는 시각을 못 읽음 → pd.to_datetime 또는 replace('Z','+00:00')")
try:
    import pandas as pd
    if int(pd.__version__.split(".")[0]) >= 3:
        print("  [..] pandas 3.x: 시계열 예측 패키지(statsforecast 등)와 충돌 가능 (kit/refs/REPOS.md 참고)")
except Exception:
    pass
PY
node -v >/dev/null 2>&1 && ok "node $(node -v), npm $(npm -v 2>/dev/null)" || echo "  [..] node 없음 (Next.js 쓸 때만 필요)"
if [ -r /proc/meminfo ]; then
  mem=$(awk '/MemAvailable/{printf "%.1f", $2/1048576}' /proc/meminfo); ok "사용 가능 메모리 ${mem}GB (큰 데이터는 나눠 읽기)"
fi
df -h . 2>/dev/null | awk 'NR==2{print "  [OK] 디스크 여유 "$4}'
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  [ -n "$(git config user.email)" ] && ok "git 사용자: $(git config user.name) <$(git config user.email)>" || ng "git 사용자 정보 없음 → git config user.name / user.email"
  grep -qx "kit/" .git/info/exclude 2>/dev/null && ok "kit/ 제외 등록됨" || echo "  [..] kit/가 .git/info/exclude에 없음"
else
  ng "git 저장소 아님 → git init"
fi
for p in 3000 8000; do
  (exec 3<>/dev/tcp/127.0.0.1/$p) 2>/dev/null && echo "  [..] 포트 $p 사용 중" || ok "포트 $p 비어 있음"
done
