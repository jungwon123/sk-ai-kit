#!/usr/bin/env bash
# 키트 적용 한 줄 스크립트. 작업 폴더(과제 저장소 루트)에서 실행한다.
#   git clone --depth 1 https://github.com/jungwon123/sk-ai-kit /tmp/kit && bash /tmp/kit/setup.sh
# 옵션: bash /tmp/kit/setup.sh [fastapi|nextjs] [semi] [skills]
#   fastapi|nextjs  앱 뼈대 복사 (이미 있는 파일은 덮어쓰지 않음)
#   semi            domain/semiconductor.md 복사
#   skills          skills/를 ~/.codex/skills/ 에도 복사 (Codex skill 자동 인식용)
set -u
KIT=$(cd "$(dirname "$0")" && pwd)
HASH=$(git -C "$KIT" rev-parse --short HEAD 2>/dev/null || echo unknown)

if [ "$KIT" = "$(pwd)" ]; then echo "작업 폴더에서 실행하세요 (키트 폴더 아님)"; exit 1; fi
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || git init -q

copy() { # 이미 있으면 건너뜀 (과제 원본 보호)
  for src in "$@"; do
    name=$(basename "$src")
    if [ -e "./$name" ]; then echo "  건너뜀(이미 있음): $name"; else cp -r "$src" ./ && echo "  복사: $name"; fi
  done
}

echo "== 키트 적용 sk-ai-kit@$HASH"
copy "$KIT/AGENTS.md" "$KIT"/templates/*.md "$KIT/skills" "$KIT/scripts" "$KIT/prompts" "$KIT/mcp"

for opt in "$@"; do
  case $opt in
    fastapi|nextjs)
      echo "== 앱 뼈대: $opt"
      (cd "$KIT/starter/$opt" && find . -type f) | while read -r f; do
        if [ -e "$f" ]; then echo "  건너뜀(이미 있음): $f"; else mkdir -p "$(dirname "$f")"; cp "$KIT/starter/$opt/$f" "$f"; fi
      done ;;
    semi) copy "$KIT/domain" ;;
    skills)
      mkdir -p "$HOME/.codex/skills" && cp -r "$KIT"/skills/* "$HOME/.codex/skills/" && echo "  ~/.codex/skills 에 복사 (Codex 재시작 후 /skills 로 확인)" ;;
    *) echo "  알 수 없는 옵션: $opt" ;;
  esac
done

if [ -z "$(git config user.email)" ] || [ -z "$(git config user.name)" ]; then
  echo "!! git 사용자 정보가 없어 커밋하지 못했습니다. 아래 두 줄을 실행한 뒤 커밋하세요:"
  echo '   git config user.name "이름" && git config user.email "메일"'
  echo "   git add -A && git commit -m \"[KIT] 공개 키트 적용 sk-ai-kit@$HASH\""
else
  git add -A && git commit -qm "[KIT] 공개 키트 적용 sk-ai-kit@$HASH" && echo "== 커밋 완료: [KIT] sk-ai-kit@$HASH"
fi
echo "다음: bash scripts/env_check.sh, cp -r $KIT/.codex . (codex 켜기 전), DECISIONS.md 첫 줄에 키트 사용 범위 기록, Codex 업데이트 질문은 거절"
