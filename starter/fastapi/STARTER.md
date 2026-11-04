# starter/fastapi

최소 뼈대: FastAPI(API) + 정적 HTML 화면 + pytest. 과제 폴더 루트에 복사해서 쓴다.

```bash
pip install -r requirements.txt          # 필요하면 python3 -m venv .venv && . .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
python3 -m pytest -q
```

- 데이터 위치: `DATA_DIR` 환경변수(기본 `data`). 원본은 수정하지 않는다.
- 계산 로직은 `app/` 아래 모듈로 나누고 `tests/`에 테스트를 붙인다.
- `app/llm.py`: 해석 문장 래퍼(JSON 형식 검증 + 규칙 기반 대체). **외부 API 호출 없음**, 기본은 규칙 기반 결과. 사용법은 파일 상단 주석.
- `static/chart.js`: 의존성 없는 SVG 차트 `drawLine(el, series, {unit, hlines})`, `drawBars(el, items)`. `hlines`로 관리한계선 같은 기준선을 그린다.
- 화면을 키우려면 `static/index.html`에 표·차트를 추가하거나 프론트엔드를 따로 둔다.
