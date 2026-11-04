#!/usr/bin/env bash
# 제출 전·중간 점검: 테스트, git 상태, 서버 응답, 키 하드코딩.
# 사용: bash scripts/check.sh [포트]   (포트 생략 시 3000, 8000 순서로 확인)
set -u
ok() { printf '  [OK] %s\n' "$1"; }
ng() { printf '  [!!] %s\n' "$1"; }

echo "== 0. 과제 README 보존"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1 && [ -f README.md ]; then
  first=$(git rev-list --max-parents=0 HEAD 2>/dev/null | tail -1)
  if [ -n "$first" ] && git cat-file -e "$first:README.md" 2>/dev/null; then
    if git diff --quiet "$first" -- README.md; then ok "README.md가 첫 커밋과 같음"
    else ng "README.md가 첫 커밋(과제 원본)과 다름 → git checkout $first -- README.md"; fi
  else echo "  [..] 첫 커밋에 README.md가 없어 비교하지 않음"; fi
fi

echo "== 1. 테스트 (검증 0건은 통과가 아니다)"
ran=0
LOG=${TMPDIR:-/tmp}
if ls tests/*.py >/dev/null 2>&1 || ls test_*.py >/dev/null 2>&1 || ls */tests/*.py >/dev/null 2>&1; then
  ran=1
  python3 -m pytest -q --ignore=kit >$LOG/pytest.log 2>&1; rc=$?
  passed=$(grep -oE "[0-9]+ passed" $LOG/pytest.log | tail -1 | grep -oE "[0-9]+" || echo 0)
  if [ $rc -eq 5 ] || { [ $rc -eq 0 ] && [ "${passed:-0}" = "0" ]; }; then ng "pytest가 테스트를 하나도 실행하지 않음 (검증 0건 = 미검증)"
  elif [ $rc -eq 0 ]; then ok "pytest 통과: $(tail -1 $LOG/pytest.log)"
  else ng "pytest 실패 (전체 로그 $LOG/pytest.log)"; grep -E "FAILED|Error" $LOG/pytest.log | head -8; fi
  skipped=$(grep -oE "[0-9]+ skipped" $LOG/pytest.log | tail -1)
  [ -n "$skipped" ] && ng "건너뛴 테스트 있음: $skipped (건너뛴 것은 검증이 아님)"
fi
if [ -f package.json ] && grep -q '"test"' package.json; then
  ran=1
  if npm test --silent >$LOG/npmtest.log 2>&1; then
    n=$(grep -oE "# pass [0-9]+|[0-9]+ (passed|passing)" $LOG/npmtest.log | grep -oE "[0-9]+" | tail -1)
    [ "${n:-0}" = "0" ] && ng "npm test가 통과했지만 실행된 테스트 수를 확인하지 못함 (0건이면 미검증)" || ok "npm test 통과 (${n}건)"
  else ng "npm test 실패 (전체 로그 $LOG/npmtest.log)"; tail -8 $LOG/npmtest.log; fi
fi
[ $ran -eq 0 ] && ng "테스트를 찾지 못함 (tests/*.py 또는 package.json test 스크립트) = 미검증"

echo "== 2. git"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ch=$(git status --porcelain | wc -l | tr -d ' ')
  [ "$ch" = "0" ] && ok "커밋 안 된 변경 없음" || { ng "커밋 안 된 변경 ${ch}개"; git status --short | head -10; }
  git log --oneline -8
else
  ng "git 저장소가 아님 (git init 필요)"
fi

echo "== 3. 서버 응답"
ports=${1:-"3000 8000"}
for p in $ports; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "http://0.0.0.0:$p/" || true)
  if [ "$code" != "000" ] && [ -n "$code" ]; then ok "포트 $p 응답 $code"; else ng "포트 $p 응답 없음"; fi
done

echo "== 4. 키·토큰 하드코딩 검사"
hits=$(grep -rInE "(sk-[A-Za-z0-9]{16,}|api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}|secret\s*[:=]\s*['\"][^'\"]{8,})" \
  --exclude-dir={.git,node_modules,.venv,venv,__pycache__,.next,out} . 2>/dev/null | head -5)
[ -z "$hits" ] && ok "의심 문자열 없음" || { ng "확인 필요:"; echo "$hits"; }

echo "== 4-1. 외부 호출 코드 검사 (앱은 외부 API 호출 금지)"
ext=$(grep -rInE "(requests\.(get|post)|urllib\.request|httpx\.|fetch\(['\"\`]https?://|https?://[a-zA-Z0-9.-]+\.(com|io|ai|net|org)/)" \
  --include=*.py --include=*.ts --include=*.tsx --include=*.js \
  --exclude-dir={.git,node_modules,.venv,venv,__pycache__,.next,out,kit,scripts} . 2>/dev/null | grep -v "localhost\|0\.0\.0\.0\|127\.0\.0\.1\|www\.w3\.org" | head -5)
[ -z "$ext" ] && ok "외부 호출로 보이는 코드 없음" || { ng "외부 호출 의심:"; echo "$ext"; }

echo "== 5. 문서"
for f in REQUIREMENTS.md PLAN.md DECISIONS.md HANDOFF.md; do
  [ -f "$f" ] && ok "$f" || ng "$f 없음 (과제가 다른 파일명을 요구하면 무시)"
done
