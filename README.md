# sk-ai-kit

> **두 세션 운영**: 터미널 T1은 구현 Codex, T2는 보조 Codex(서버·검증·문서). 사람은 시작 4줄 외에는 터미널을 조작하지 않는다. 역할과 충돌 방지 규칙은 `AGENTS.md` 7-2, 순서는 `PLAYBOOK.md`.

코딩 에이전트(Codex 등)와 함께 짧은 시간 안에 데이터 기반 과제를 수행하기 위한 **범용 작업 키트**입니다.
특정 과제의 정답이나 완성된 결과물은 포함하지 않으며, 문서 템플릿·작업 절차서·데이터 점검 스크립트·최소 앱 뼈대만 담고 있습니다.

- 작성일: 2026-10-30
- 작성자: 이정원
- 구성: `PLAYBOOK.md`, `refs/`, `START.md`, `setup.sh`, `AGENTS.md`, `templates/`, `prompts/`, `skills/`, `scripts/`, `mcp/`, `.codex/agents/`, `starter/`, `domain/`

## 구성

| 경로 | 내용 |
| --- | --- |
| `AGENTS.md` | 코딩 에이전트 작업 규칙. 작업 폴더 루트에 복사하면 에이전트가 매 작업마다 따른다 |
| `templates/DESIGN.md` | 한 장 설계: 범위, 아키텍처·데이터 파이프라인·서빙 표, 데이터 모델, 알고리즘과 트레이드오프, 기준값, 비기능 |
| `templates/DESIGN_SHORT.md` | 구현용 설계 요약(40줄 이내). T1은 이것만 읽고, 자세한 DESIGN은 T2와 서술형이 쓴다 |
| `templates/` | REQUIREMENTS · PLAN · DECISIONS · DATA_NOTES · HANDOFF · INTERVIEW 문서 틀 |
| `prompts/codex.md` | 단계별 프롬프트 모음 (K0~K14, K2-1, K3-1, K6-1, K8-1, K14-1, 키트가 없을 때의 대체 프롬프트 P2·P7, 담당자 DM D1·D1-1·D2·D3) |
| `PLAYBOOK.md` | 사람이 보는 180분 작업 순서표: 타임라인, 서브에이전트·비용 관리, 승인 규칙, 복습, 안 될 때 |
| `START.md` | 시작 절차: clone 후 Codex에게 `kit/START.md 읽고 그대로 해.` 한 줄로 키트 적용 + 과제 요약 |
| `setup.sh` | 키트 적용 한 줄 스크립트 (복사 + git 커밋, 기존 파일은 덮어쓰지 않음) |
| `skills/` | 에이전트가 따르는 절차서 (Codex skill 형식 `이름/SKILL.md`): `handoff`, `review`, `data-check`, `edge-cases`(예외·엣지 케이스 체크리스트·처리 방식), `essay-brief`(서술형 브리핑 + 질문 은행 50개), `fluent-korean`(한국어 문장 교정, 외부 MIT: snflkd/fluent-korean) |
| `.codex/agents/` | Codex 서브에이전트 정의: `data_scout`(데이터 점검), `reviewer`(읽기 전용 점검), `doc_sync`(문서 동기화). 모두 추론 강도 low |
| `mcp/` | MCP 기준: 기본은 미사용(Context7·Playwright 등 미채택 이유), 필요해질 때의 도입 절차 |
| `scripts/ui_check.py` | 화면 동작 점검: 응답·콘솔 에러·실패 요청·선택자·클릭 후 결과를 몇 줄로 출력 (Playwright 없으면 HTTP만) |
| `scripts/profile_data.py` | CSV/XLSX/JSON 자동 점검: 행 수, 타입, 결측, 중복, ID 표기 변형(접두어 포함), 단위 컬럼, 수치·날짜 범위, 파일 간 조인 키 |
| `scripts/evidence.py` | 서술형 근거 자동 수집: 커밋 흐름, 소스 지도(함수·API 경로:줄), 테스트 목록·결과, 배포 단서 → `out/evidence.md` |
| `scripts/env_check.sh` | 시작 직후 1분 환경 점검: Python·패키지 버전, 'Z' 시각 파싱, pandas 3 충돌 주의, 메모리·디스크, git 사용자, 포트 |
| `scripts/check.sh` | 테스트 판정(**실행 0건·건너뜀은 미검증으로 경고**) + git 상태 + 서버 응답 + 외부 호출·키 하드코딩 + 문서 존재 검사 |
| `refs/REPOS.md` | 문제 유형별 오픈소스 후보 14종 (2026-10-31 확인, 오프라인 동작·라이선스·버전 충돌 포함) |
| `starter/fastapi/` | 최소 뼈대: FastAPI + pandas + 정적 HTML 화면 + pytest, `app/llm.py`(해석 문장 래퍼: 기본 규칙 기반, 외부 호출 없음, JSON 검증), `static/chart.js`(SVG 선·막대 차트) |
| `starter/nextjs/` | 최소 뼈대: Next.js(App Router, TypeScript) + API route, `lib/llm.ts`(해석 문장 래퍼: 기본 규칙 기반, 외부 호출 없음), `components/LineChart.tsx`(SVG 차트) |
| `domain/semiconductor.md` | 반도체 공정 데이터 용어와 일반적인 분석 패턴 (공개 일반 지식) |

## 사용법 (작업 시작 5분)

**기본: 작업 폴더에 clone하고 Codex에게 맡기기** (`START.md`)

```bash
git clone --depth 1 https://github.com/jungwon123/sk-ai-kit kit
echo "kit/" >> .git/info/exclude   # 키트가 과제 저장소 커밋에 섞이지 않게 (.gitignore는 그대로)
cp -r kit/.codex .             # 서브에이전트 정의 (codex 켜기 전에)
codex                          # 첫 문장: kit/START.md 읽고 그대로 해.
```

**대안: 스크립트로 적용** (작업 폴더 밖에 clone)

```bash
git clone --depth 1 https://github.com/jungwon123/sk-ai-kit /tmp/kit && bash /tmp/kit/setup.sh
# 옵션: fastapi | nextjs (앱 뼈대), semi (반도체 용어), skills (~/.codex/skills 에 복사)
# 예: bash /tmp/kit/setup.sh fastapi semi skills
```

이어서 (두 방식 공통):
1. `codex`를 켤 때 **업데이트 질문이 나오면 거절**합니다(권한 오류로 실패하고 시간만 씁니다).
2. `/subagents`로 서브에이전트 3종이 보이는지 확인합니다. 스크립트 방식이면 `cp -r /tmp/kit/.codex .`를 codex 켜기 전에 합니다. MCP는 붙이지 않습니다(`mcp/README.md`).

수동으로 할 때:

```bash
git status || git init
git clone --depth 1 https://github.com/jungwon123/sk-ai-kit.git /tmp/kit
git -C /tmp/kit rev-parse --short HEAD          # 사용한 키트 버전(커밋 해시) 확인
cp /tmp/kit/AGENTS.md ./
cp -r /tmp/kit/templates/. ./
cp -r /tmp/kit/skills /tmp/kit/scripts /tmp/kit/prompts /tmp/kit/mcp ./
git add -A && git commit -m "[KIT] 공개 키트 적용 sk-ai-kit@<해시>"
```

- 앱 뼈대가 필요하면 과제 스택에 맞는 것만 복사합니다: `cp -r /tmp/kit/starter/fastapi/. ./` 또는 `cp -r /tmp/kit/starter/nextjs/. ./`
- 반도체 데이터 과제면 `cp -r /tmp/kit/domain ./`
- 과제 안내(README 등)가 파일명·양식을 정해 두었다면 **과제 안내가 우선**입니다. 템플릿은 그 양식으로 옮겨 씁니다.
- 키트를 쓴 사실과 범위는 `DECISIONS.md` 첫 줄에 기록합니다.

## 원칙

1. 키트는 작업 방식(문서 틀·절차·점검 도구)만 제공하고, 과제의 도메인 로직은 작업 중에 새로 만든다.
2. 판정·집계·계산은 코드로 한다. 앱은 외부 API(외부 LLM 포함)를 호출하지 않고, 해석 문장도 규칙 기반으로 만든다.
3. 요구사항 하나 = 구현 → 테스트 → 커밋. 결정은 근거와 함께 기록한다.
4. 문서와 코드·커밋이 일치해야 한다. 안 된 것은 안 됐다고 쓴다.
