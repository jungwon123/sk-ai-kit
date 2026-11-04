#!/usr/bin/env python3
"""서술형 브리핑용 근거 수집. 코드·테스트·커밋에서 사실만 모아 out/evidence.md에 쓴다(토큰 절약: 에이전트가 저장소를 통째로 읽지 않게).

사용: python3 scripts/evidence.py [--out out/evidence.md]
모으는 것:
  1. 커밋 흐름 (시각, 메시지, 바뀐 파일 수)
  2. 소스 지도: 파일별 함수·클래스·API 경로 (Python / JS·TS), 줄 번호 포함
  3. 테스트: 테스트 이름 목록과 pytest 실행 결과(통과·실패·건너뜀 수, 시간)
  4. 설정·배포 단서: Dockerfile, .env.example 키, 헬스체크 경로, 포트
  5. 문서 존재 여부
kit/, node_modules 등은 제외한다. 원본은 수정하지 않는다.
"""
import argparse
import re
import subprocess
from pathlib import Path

SKIP = {"kit", "node_modules", ".git", ".venv", "venv", "__pycache__", ".next", "out", "dist", "build", ".codex"}
PY_DEF = re.compile(r"^(\s*)(async\s+def|def|class)\s+(\w+)")
PY_ROUTE = re.compile(r"@\w+\.(get|post|put|delete|patch)\(\s*[\"']([^\"']+)")
JS_DEF = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\(|class\s+(\w+))")
JS_ROUTE = re.compile(r"(?:app|router)\.(get|post|put|delete|patch)\(\s*[\"'`]([^\"'`]+)")


def sh(cmd: str, timeout=300) -> str:
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except subprocess.TimeoutExpired:
        return "(시간 초과)"


def files(exts):
    for p in sorted(Path(".").rglob("*")):
        if p.is_file() and p.suffix in exts and not (set(p.parts) & SKIP):
            yield p


def source_map() -> list[str]:
    out = []
    for p in files({".py", ".js", ".ts", ".tsx"}):
        if "test" in p.name:
            continue
        items = []
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if p.suffix == ".py":
                m = PY_ROUTE.search(line)
                if m:
                    items.append(f"`{m[1].upper()} {m[2]}`:{i}")
                m = PY_DEF.match(line)
                if m and len(m[1]) <= 4:
                    items.append(f"{m[3]}:{i}")
            else:
                m = JS_ROUTE.search(line)
                if m:
                    items.append(f"`{m[1].upper()} {m[2]}`:{i}")
                m = JS_DEF.match(line)
                if m:
                    items.append(f"{m[1] or m[2] or m[3]}:{i}")
        if items:
            out.append(f"- `{p}` ({sum(1 for _ in open(p, encoding='utf-8', errors='ignore'))}줄): " + ", ".join(items[:40]))
    return out


def tests() -> list[str]:
    names = []
    for p in files({".py", ".js", ".ts"}):
        if "test" not in p.name:
            continue
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"\s*def (test_\w+)", line) or re.match(r"\s*(?:test|it)\(\s*[\"'`]([^\"'`]+)", line)
            if m:
                names.append(f"{p}::{m[1]}")
    res = ""
    if any(Path(".").glob("tests/*.py")) or any(Path(".").glob("*/tests/*.py")):
        res = sh("python3 -m pytest -q --ignore=kit 2>&1 | tail -1")
    return [f"- 실행 결과: {res or '(pytest 대상 없음)'}", f"- 테스트 {len(names)}개:"] + [f"  - {n}" for n in names[:80]]


def deploy() -> list[str]:
    out = []
    for f in ("Dockerfile", "docker-compose.yml", ".env.example"):
        if Path(f).exists():
            text = Path(f).read_text(encoding="utf-8", errors="ignore")
            if f == ".env.example":
                keys = [l.split("=")[0] for l in text.splitlines() if "=" in l and not l.startswith("#")]
                out.append(f"- `.env.example` 키: {', '.join(keys)}")
            else:
                out.append(f"- `{f}` 있음: " + " / ".join(l.strip() for l in text.splitlines() if l.strip().startswith(("FROM", "CMD", "EXPOSE", "HEALTHCHECK")))[:300])
    hits = sh("grep -rnE \"health|0\\.0\\.0\\.0|PORT\" --include=*.py --include=*.ts --include=*.js . "
              "--exclude-dir={kit,node_modules,.git,out,.next} | head -8")
    if hits:
        out.append("- 헬스체크·바인딩·포트 단서:\n" + "\n".join("  - " + h for h in hits.splitlines()))
    return out or ["- (배포 파일 없음)"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/evidence.md")
    a = ap.parse_args()
    log = sh("git log --reverse --date=format:%H:%M --pretty='- %ad %s' 2>/dev/null")
    stat = sh("git log --shortstat --pretty=format: 2>/dev/null | grep -c changed")
    docs = [f"- {d}: {'있음' if Path(d).exists() else '없음'}" for d in
            ("README.md", "HOW_TO_RUN.md", "AI_COLLABORATION.md", "DESIGN.md", "DECISIONS.md", "HANDOFF.md", "REQUIREMENTS.md")]
    parts = ["# 근거 모음 (자동 수집, 사실만)", "",
             "## 1. 커밋 흐름", log or "- (커밋 없음)", f"- 파일을 바꾼 커밋 수: {stat}", "",
             "## 2. 소스 지도 (함수·클래스·API 경로:줄)", *source_map(), "",
             "## 3. 테스트", *tests(), "",
             "## 4. 설정·배포", *deploy(), "",
             "## 5. 문서", *docs, ""]
    text = "\n".join(parts)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="utf-8")
    print(f"{a.out} 작성: {len(text.splitlines())}줄")


if __name__ == "__main__":
    main()
