# START — 키트 적용 절차 (Codex가 읽고 그대로 수행)

## 사람이 먼저 할 것 (터미널, 작업 폴더 루트에서)

```bash
git clone --depth 1 https://github.com/jungwon123/sk-ai-kit kit
echo "kit/" >> .git/info/exclude    # 제출물에 키트가 섞이지 않게 (.gitignore는 건드리지 않음)
cp -r kit/.codex .                 # 서브에이전트 정의(data_scout·reviewer·doc_sync). codex 켜기 전에
codex
```

T1 Codex에 보낼 첫 문장: `너는 T1 구현 세션이다. kit/START.md 읽고 그대로 해.`
`[KIT]` 커밋 뒤 두 번째 터미널(T2)에서 `codex`를 켜고 보낼 첫 문장:
```
너는 T2 보조 세션이다. AGENTS.md 7-2를 읽고 지켜: 코드·테스트·설정은 절대 고치지 않고, 문제는 "T1에 보낼 문장"으로 보고해. 커밋은 git add <자기 파일>로 [DOCS]만. 준비되면 역할을 2줄로 요약하고 기다려.
```
커밋이 멈추면 T1에: `git user 설정하고 다시 커밋해.`
(업데이트 질문이 나오면 거절. MCP는 붙이지 않는다: `kit/mcp/README.md`)

---

## Codex가 할 것

`kit/`는 공개 키트(https://github.com/jungwon123/sk-ai-kit)다. **과제 기준은 루트 `README.md`이고, `kit/README.md`는 무시한다.**

1. 작업 폴더가 git 저장소가 아니면 `git init`. `.git/info/exclude`에 `kit/`가 없으면 추가한다(`.gitignore`는 과제 파일이므로 건드리지 않는다).
2. `bash kit/scripts/env_check.sh`로 환경을 점검하고 [!!] 항목만 보고한다(Python·패키지 버전, 시각 파싱, 메모리, git 사용자, 포트).
3. `kit/AGENTS.md`, `kit/templates/`의 문서들, `kit/scripts/`, `kit/skills/`, `kit/prompts/`, `kit/mcp/`를 루트로 복사한다. `.codex/agents/`가 없으면 `kit/.codex/`도 복사한다(이 경우 서브에이전트는 Codex 재시작 후 인식된다고 알린다). **이미 있는 파일은 덮어쓰지 않는다.**
4. 루트에 `AGENTS.md`가 이미 있으면 덮지 말고, 그 아래에 `kit/AGENTS.md` 내용을 `## 개인 작업 규칙(키트)`으로 덧붙인다. **과제 규칙이 우선이다.**
5. `DECISIONS.md` 첫 줄에 키트 사용을 기록한다: 주소, 커밋 해시(`git -C kit rev-parse --short HEAD`), 쓴 범위(문서 틀·절차서·점검 스크립트, 과제 로직은 새로 작성).
6. `[KIT] 공개 키트 적용 sk-ai-kit@<해시>`로 커밋한다. git 사용자 정보가 없어 실패하면 멈추고 알린다.
7. `AGENTS.md` 규칙을 3줄로 요약한다.
8. 사용자에게 "이제 T2를 열어 T2-0을 보내세요"라고 한 줄 알린다.
9. 루트 `README.md`로 과제를 요약한다: 목표, 필수·선택 조건, 제출물과 파일명, 제약, **이용 조건**(업로드 금지 등), **양식이 주어진 파일**(예: HOW_TO_RUN.md, AI_COLLABORATION.md, 내보내기 스키마). 데이터는 파일별 행 수·컬럼만. **README는 수정하지 않고, 코드는 아직 쓰지 않는다.**

필요할 때만 (사용자가 지시하면):
- 앱 뼈대 (덮어쓰기 금지): `kit/starter/fastapi/`(Python API + 정적 화면) 또는 `kit/starter/nextjs/`(TypeScript). 과제 로직은 직접 구현
- 오픈소스 후보: `kit/refs/REPOS.md`
- 반도체 데이터: `kit/domain/semiconductor.md` 참고
- 프롬프트 모음: `kit/prompts/codex.md`
