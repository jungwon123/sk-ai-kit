# 문제 유형별 오픈소스 레퍼런스 (검증본)

문제 유형별로 "이걸 베이스로 쓴다"를 바로 고르기 위한 표. 모두 설치 후 **오프라인 로컬 실행** 기준.

확인일: 2026-10-31 (PyPI JSON API · npm registry · GitHub 저장소 최신 커밋으로 확인)

## 사용 규칙
- (a) 설치 전에 `DECISIONS.md`에 "왜 이 패키지인가" 한 줄을 기록하고, 버전을 고정한다 (`pip install pkg==x.y.z`, `npm i pkg@x.y.z --save-exact`).
- (b) 과제 데이터는 외부로 보내지 않는다. 클라우드·LLM API, 텔레메트리, CDN 로딩 금지. 모델 파일은 설치 단계에서 미리 받아 두고, 런타임에는 로컬 경로에서 읽는다.
- (c) 레포를 통째로 결과물로 대체하지 않는다. 필요한 함수나 구조만 가져와 쓰고, 출처는 `DECISIONS.md`에 적는다.

> **먼저 pandas·표준 라이브러리로 되는지 본다.** 집계·조인·추이·비교는 대부분 직접 짜는 편이 빠르고 서술형에서 설명하기도 쉽다. 이 표는 예측, 변화 시점, 최적화, 텍스트 검색처럼 더 강한 방법이 필요할 때 쓴다. 도입은 `prompts/codex.md`의 K13 절차로.

> **버전 충돌 주의 (확인됨)**: 최신 pandas는 **3.1.0**이지만 `statsforecast`, `skforecast`는 `pandas<3.0`, `claspy`는 `pandas<2.4`·`scikit-learn<1.8`·`numpy<2.3`를 요구한다. 시계열 계열 패키지를 쓸 거면 **처음부터 `pandas==2.3.*`로 고정**하는 편이 안전하다. duckdb(2.0.0)와 polars(2.1.0)도 최근 메이저 버전이 올라갔으니 버전을 고정할 것.

무게 기준: **light**는 순수 파이썬이거나 의존성 3개 이하, **medium**은 numba/scipy/statsmodels급 의존성이나 시스템 라이브러리가 필요한 경우, **heavy**는 torch, 대형 모델, Docker가 필요한 경우.

---

## 1. 이상 탐지 (tabular / 시계열)
| 후보 | 설치 | 무엇에 쓰나 (한 줄) | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| scikit-learn | `pip install scikit-learn` | IsolationForest, LOF, OneClassSVM, EllipticEnvelope | BSD-3 | 1.9.1 (2026-09-10) | O | medium |
| PyOD | `pip install pyod` | 이상 탐지 알고리즘 수십 종(ECOD, COPOD, IForest 등)을 같은 API로 사용 | BSD-2 | 3.6.7 (2026-10-12), 커밋 2026-10-27 | O | medium (numba) |
| STUMPY | `pip install stumpy` | Matrix Profile로 시계열 discord(이상 구간)와 반복 패턴 탐지 | BSD-3 | 1.14.1 (2026-02-08), 커밋 2026-10-16 | O | medium (numba) |

기본 선택: **PyOD (ECOD/IForest)** — 파라미터가 거의 없어도 바로 돌아가고 점수를 0~1로 정규화하기 쉽다. 시계열 구간 이상이면 STUMPY.
제외: `adtk`는 마지막 릴리스가 2020-04-17이라 유지보수되지 않는 것으로 판단했다.

## 2. 변화 시점 탐지 (change point)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| ruptures | `pip install ruptures` | PELT, BinSeg, Window 방식으로 평균·분산 변화 시점 탐지 | BSD-2 | 1.1.10 (2025-09-10), 커밋 2026-05-26 | O | light |
| ClaSPy | `pip install claspy` | ClaSP 기반 시계열 분할(파라미터 거의 없음) | BSD-3 | 0.2.8 (2026-03-19) | O | medium (aeon, numba, **pandas<2.4**) |
| statsmodels / 직접 구현 CUSUM | `pip install statsmodels` | CUSUM, 구조변화 검정(`breaks_cusumolsresid`) | BSD-3 | 0.15.0 (2026-08-27) | O | medium |

기본 선택: **ruptures (PELT + `rbf` 또는 `l2` 비용)** — 의존성이 가볍고 결과로 변화 시점 인덱스 리스트가 바로 나온다.
제외: `changefinder`는 마지막 릴리스가 2014년이다.

## 3. 시계열 예측 (경량)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| statsforecast (Nixtla) | `pip install statsforecast` | AutoARIMA, AutoETS, Theta를 빠르게 여러 시리즈에 적용 | Apache-2.0 | 2.1.1 (2026-07-16), 커밋 2026-10-29 | O | medium (**pandas<3.0**) |
| statsmodels | `pip install statsmodels` | ExponentialSmoothing, SARIMAX, STL 분해 | BSD-3 | 0.15.0 (2026-08-27) | O | medium |
| skforecast | `pip install skforecast` | sklearn/LightGBM 회귀기를 lag 피처 기반 예측기로 감싸서 사용 | BSD-3 | 0.26.0 (2026-10-08) | O | medium (optuna, **pandas<3.0**) |

기본 선택: **statsforecast (AutoETS + SeasonalNaive 베이스라인)** — 빠르고 결과가 DataFrame으로 나온다. pandas 3을 써야 하는 상황이면 statsmodels를 쓴다.
참고: darts와 prophet은 유지보수 중이지만 무겁거나(torch, cmdstan) 설치 시간이 길어서 제외했다.

## 4. SPC / 관리도 (반도체 핵심)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| pyControlCharts | `pip install pycontrolcharts` | XmR, X̄-R, X̄-S, p/np/c/u 관리도와 **Nelson rule** 위반 결과를 DataFrame으로 반환, 단계별 관리한계, 규격한계 지원 | MIT | 0.1.2 (2026-03-06) | O | light (pandas만 필요, plotly는 옵션) |
| pyshewhart | `pip install pyshewhart` | X̄-R, X̄-S, CUSUM, p 관리도와 **Western Electric rule** 판정(matplotlib 플롯 중심) | MIT | 1.1.0 (2026-07-20), 커밋 2026-07-19 | O | light |
| 직접 구현 (numpy/pandas) | — | I-MR 관리한계 `CL ± 2.66·MR̄`, WE rule 1~4, Cpk = min(USL−μ, μ−LSL)/3σ | — | — | O | light |

기본 선택: **pyControlCharts** — 결과가 DataFrame이라 FastAPI로 JSON을 넘기고 프론트에서 그리기 쉽다. 패키지가 아직 초기 버전(0.1.x)이므로, 위반 판정 로직은 직접 구현한 결과와 한 번 교차 검증할 것.
주의: PyPI의 `qcc`는 SPC가 아니라 **Claude Code 설정 도구**다. 이름이 같은 R 패키지와 혼동하지 말 것. `pyspc`(2016 릴리스, GPLv3)는 오래되어 제외했다.

## 5. 데이터 검증 / 스키마
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| pandera | `pip install pandera` | DataFrame 컬럼의 타입, 범위, 결측, 커스텀 체크 검증 (pandas/polars 모두 지원) | MIT | 0.35.0 (2026-10-25) | O | light |
| pydantic | `pip install pydantic` | API 요청/응답과 레코드 단위 검증 (FastAPI에 내장) | MIT | 2.14.2 (2026-10-29) | O | light |
| frictionless | `pip install frictionless` | CSV 파일 자체의 구조 오류 리포트 (헤더, 행 길이, 타입) | MIT | 5.21.0 (2026-10-15) | O | medium |

기본 선택: **pandera + pydantic** — 데이터 테이블 검증은 pandera, API 경계 검증은 pydantic으로 나눈다.
참고: great-expectations(1.24.1)는 활발히 유지되지만 무거워서 짧은 작업용으로는 과하다.

## 6. 빠른 데이터 처리 / 파일 위 SQL
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| DuckDB | `pip install duckdb` | CSV/Parquet를 바로 SQL로 조회, 메모리보다 큰 데이터 처리, pandas와 상호 변환 | MIT | 2.0.0 (2026-10-21) | O | light (휠 1개) |
| Polars | `pip install polars` | lazy/streaming DataFrame, groupby와 rolling 연산이 빠름 | MIT | 2.1.0 (2026-10-25) | O | light~medium |
| PyArrow | `pip install pyarrow` | Parquet 읽기/쓰기, pandas의 Arrow 백엔드 | Apache-2.0 | 26.0.0 (2026-10-09) | O | medium |

기본 선택: **DuckDB** — 로그나 공정 데이터를 SQL 한 줄로 집계하고 `.df()`로 pandas에 넘긴다.

## 7. 통계 검정·회귀 (원인/요인 분석)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| SciPy | `pip install scipy` | t-test, Mann-Whitney, ANOVA, 카이제곱, 상관계수 | BSD-3 | 1.18.1 (2026-08-21) | O | medium |
| statsmodels | `pip install statsmodels` | OLS/로지스틱 회귀(formula API), ANOVA 표, 다중비교 보정 | BSD-3 | 0.15.0 (2026-08-27) | O | medium |
| pingouin | `pip install pingouin` | 효과크기와 p값이 들어간 검정 결과 표를 한 줄로 생성 (ANOVA, post-hoc, 편상관) | **GPL-3.0** | 0.7.0 (2026-09-26) | O | medium (seaborn 등) |
| SHAP (+sklearn 트리 모델) | `pip install shap` | 수율/불량에 영향을 준 변수 중요도 설명 | MIT | 0.54.1 (2026-10-16) | O | medium |

기본 선택: **statsmodels (OLS + ANOVA) + scipy.stats** — 결과 표준성이 높다. 변수가 많으면 RandomForest와 permutation importance(sklearn)를 먼저 쓰고, 필요할 때 SHAP을 추가한다.

## 8. 텍스트 검색·분류 (외부 API 없이)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| scikit-learn TF-IDF | `pip install scikit-learn` | `TfidfVectorizer`와 LogisticRegression으로 분류, cosine 유사도로 검색 | BSD-3 | 1.9.1 | O | medium |
| bm25s | `pip install bm25s` | 빠른 BM25 키워드 검색 (numpy만 필요) | MIT | 0.3.16 (2026-10-28) | O | light |
| kiwipiepy | `pip install kiwipiepy` | 한국어 형태소 분석 (TF-IDF/BM25 토크나이저로 사용, 모델 내장) | Apache-2.0 | 0.24.1 (2026-10-20) | O | medium |
| model2vec | `pip install model2vec` | 정적 임베딩으로 의미 검색 (torch 불필요). potion-base-8M은 약 30MB(영어), potion-multilingual-128M은 다국어 지원 | MIT | 0.10.0 (2026-10-11) | △ 모델을 HF에서 미리 받아 로컬 경로로 로드 | light~medium |
| fastembed (Qdrant) | `pip install fastembed` | ONNX 임베딩 (기본 모델 bge-small-en-v1.5) | Apache-2.0 | 0.9.1 (2026-10-24) | △ 모델 사전 다운로드 필요 | medium (onnxruntime) |

기본 선택: **TF-IDF(char n-gram 또는 kiwipiepy 토큰) + bm25s** — 모델 다운로드 없이 완전 오프라인으로 동작한다. 임베딩은 HF 다운로드가 허용되는 경우에만 model2vec를 쓴다.
참고: sentence-transformers(6.2.0)는 torch가 필요해서 **heavy**로 분류하고 제외했다. `rank-bm25`는 마지막 릴리스가 2022년이라 bm25s로 대체했다.

## 9. 최적화·일정 배정 (LP/MIP/스케줄링)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| OR-Tools | `pip install ortools` | CP-SAT으로 작업·장비 스케줄링, 라우팅, 할당 | Apache-2.0 | 9.15 (2026-01-14), 커밋 2026-09-17 | O | medium (휠 약 20MB 이상) |
| PuLP | `pip install pulp` | LP/MIP 모델을 읽기 쉽게 작성 (CBC 솔버 번들) | MIT | 4.2.0 (2026-10-22) | O | light |
| highspy (HiGHS) | `pip install highspy` | 빠른 LP/MIP 솔버 (scipy `linprog` 백엔드와 같음) | MIT | 1.15.1 (2026-07-02) | O | light |
| scipy.optimize | `pip install scipy` | `linear_sum_assignment`(1:1 할당), `linprog`, `milp` | BSD-3 | 1.18.1 | O | medium |

기본 선택: **OR-Tools CP-SAT** — 시간 구간, 순서, 자원 제약이 들어가는 스케줄링에 가장 강하다. 단순 1:1 할당이면 `scipy.optimize.linear_sum_assignment`를 쓴다.

## 10. 그래프·네트워크 분석
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| NetworkX | `pip install networkx` | 최단경로, 중심성, 연결요소, DAG(공정 흐름) 분석 | BSD-3 | 3.7 (2026-09-21) | O | light |
| python-igraph | `pip install igraph` | 대형 그래프와 커뮤니티 탐지가 빠름 | **GPL-2.0+** | 1.0.0 (2025-10-23), 커밋 2026-10-06 | O | medium |
| React Flow (프론트) | `npm i @xyflow/react` | 공정 흐름도, 노드 그래프 UI | MIT | 12.12.0 (2026-09-24) | O | light |
| Cytoscape.js (프론트) | `npm i cytoscape` | 네트워크 시각화와 레이아웃 | MIT | 3.34.4 (2026-10-15) | O | light |

기본 선택: **NetworkX + @xyflow/react** — 분석은 NetworkX에서 하고, 결과를 nodes/edges JSON으로 넘겨 React Flow로 그린다.

## 11. 차트 라이브러리
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| Recharts (React) | `npm i recharts` | 선·막대·영역 차트, `ReferenceLine`으로 관리한계선(UCL/LCL) 표시 | MIT | 3.10.1 (2026-07-25) | O | light |
| ECharts (+React 래퍼) | `npm i echarts echarts-for-react` | 대용량 시계열, 확대/축소(dataZoom), markLine/markArea로 이상 구간 강조 | Apache-2.0 / MIT | 6.1.0 (2026-05-19) / 3.0.6 (2026-01-21) | O | medium |
| Chart.js (plain JS) | `npm i chart.js` (HTML이면 node_modules에서 로컬 파일로 복사) | 순수 HTML/JS에서 가장 간단 | MIT | 4.6.1 (2026-10-22) | O | light |
| Plotly | `npm i plotly.js-dist-min` / `pip install plotly` | Python에서 바로 인터랙티브 HTML 차트 생성 | MIT | 4.2.0 (2026-10-29) / 7.1.0 (2026-09-15) | O (CDN 대신 `include_plotlyjs=True`) | medium~heavy (JS 약 3MB 이상) |
| uPlot | `npm i uplot` | 수십만 포인트 시계열을 초경량으로 그림 | MIT | npm 1.6.32 (2025-03-14), 커밋 2026-10-27 | O | light |

기본 선택: **Next.js면 ECharts(echarts-for-react)** — 포인트가 많은 센서 데이터, 관리도 markLine, dataZoom이 모두 기본 제공된다. 간단한 KPI 차트는 Recharts, plain HTML이면 Chart.js를 쓴다.

## 12. 데이터 그리드 / 표 UI (React)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| TanStack Table | `npm i @tanstack/react-table` | headless 표 (정렬, 필터, 페이지네이션), shadcn DataTable의 기반 | MIT | 9.3.1 (2026-10-12) | O | light |
| AG Grid Community | `npm i ag-grid-react ag-grid-community` | 정렬·필터·가상 스크롤이 기본 제공되는 대용량 그리드 | MIT (Enterprise 기능은 별도 라이선스) | 36.2.0 (2026-09-16) | O | medium |

기본 선택: **AG Grid Community** — 시간이 부족한 작업에서 대용량 표, 필터, CSV 내보내기를 설정만으로 바로 쓸 수 있다. 디자인 일관성이 중요하면 TanStack과 shadcn 조합을 쓴다.
주의: TanStack Table은 최근 v9로 메이저 버전이 올라갔다. 예제 코드가 v8 기준인지 확인할 것.

## 13. UI 컴포넌트 / 대시보드 템플릿
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| shadcn/ui | `npx shadcn@latest init` / `add <component>` | Tailwind 기반 컴포넌트를 소스 코드로 복사해서 사용 | MIT | CLI 4.23.0 (2026-10-27) | △ CLI가 개발 시점에 레지스트리에서 받아옴, 런타임은 오프라인 | light |
| Mantine | `npm i @mantine/core @mantine/hooks` (+`@mantine/charts`) | 컴포넌트와 차트가 한 번에 들어 있는 올인원 | MIT | 9.7.4 (2026-10-25) | O | medium |
| next-shadcn-dashboard-starter (템플릿 레포) | `git clone https://github.com/Kiranism/next-shadcn-dashboard-starter` | Next.js와 shadcn 대시보드 레이아웃 참고용 (사이드바, 표, 차트) | MIT (레포 확인 필요) | 커밋 2026-10-21 | △ 인증 등 외부 연동 부분은 제거 필요 | medium |
| full-stack-fastapi-template (템플릿 레포) | `git clone https://github.com/fastapi/full-stack-fastapi-template` | FastAPI와 React 프로젝트 구조, 라우터·스키마 분리 참고 | MIT | 커밋 2026-10-26 | O (단, Docker와 Postgres 전제) | heavy |

기본 선택: **Next.js + shadcn/ui (필요한 컴포넌트만 add)** — 템플릿 레포는 구조만 참고하고 통째로 쓰지 않는다(규칙 c). FastAPI 쪽은 `main.py`, `routers/`, `schemas.py` 정도로만 나눈다.
참고: `@tremor/react`는 npm 마지막 릴리스가 2025-01이고 레포 커밋도 2025-10에서 멈춰서 제외했다.

## 14. 보고서 생성 (HTML / PDF / Excel)
| 후보 | 설치 | 무엇에 쓰나 | 라이선스 | 최근 활동 | 오프라인 | 무게 |
|---|---|---|---|---|---|---|
| Jinja2 (+plotly `to_html`) | `pip install jinja2` | HTML 리포트 템플릿에 표와 차트를 삽입 | BSD-3 | 3.1.6 (2025-03-05), 안정판 | O | light |
| XlsxWriter | `pip install xlsxwriter` | 서식, 조건부서식, 차트가 들어간 Excel 생성 (`df.to_excel(engine="xlsxwriter")`) | BSD-2 | 3.3.1 (2026-10-28) | O | light |
| openpyxl | `pip install openpyxl` | 기존 xlsx 읽기와 수정 | MIT | 3.1.5 (2024-06-28), 안정판 | O | light |
| WeasyPrint | `pip install weasyprint` | HTML/CSS를 PDF로 변환 | BSD-3 | 70.0 (2026-09-08) | O | medium (**시스템 Pango 라이브러리 필요**) |
| ReportLab | `pip install reportlab` | 코드로 PDF를 직접 구성 | BSD | 5.1.0 (2026-10-22) | O | light~medium |

기본 선택: **Jinja2 HTML 리포트 + XlsxWriter** — PDF는 브라우저의 `window.print()`(인쇄용 CSS)로 처리하는 것이 가장 안전하다. WeasyPrint는 시스템 라이브러리 설치가 가능한 환경일 때만 쓴다.

---

## Sources
PyPI (각 `https://pypi.org/pypi/<name>/json`으로 버전, 날짜, 라이선스, 의존성 확인)
- https://pypi.org/project/pyod/ · https://pypi.org/project/scikit-learn/ · https://pypi.org/project/stumpy/ · https://pypi.org/project/adtk/
- https://pypi.org/project/ruptures/ · https://pypi.org/project/claspy/ · https://pypi.org/project/changefinder/
- https://pypi.org/project/statsforecast/ · https://pypi.org/project/statsmodels/ · https://pypi.org/project/skforecast/ · https://pypi.org/project/darts/ · https://pypi.org/project/prophet/
- https://pypi.org/project/pycontrolcharts/ · https://pypi.org/project/pyshewhart/ · https://pypi.org/project/qcc/ · https://pypi.org/project/pyspc/
- https://pypi.org/project/pandera/ · https://pypi.org/project/pydantic/ · https://pypi.org/project/frictionless/ · https://pypi.org/project/great-expectations/
- https://pypi.org/project/duckdb/ · https://pypi.org/project/polars/ · https://pypi.org/project/pyarrow/
- https://pypi.org/project/scipy/ · https://pypi.org/project/pingouin/ · https://pypi.org/project/shap/
- https://pypi.org/project/bm25s/ · https://pypi.org/project/rank-bm25/ · https://pypi.org/project/kiwipiepy/ · https://pypi.org/project/model2vec/ · https://pypi.org/project/fastembed/ · https://pypi.org/project/sentence-transformers/
- https://pypi.org/project/ortools/ · https://pypi.org/project/pulp/ · https://pypi.org/project/highspy/
- https://pypi.org/project/networkx/ · https://pypi.org/project/igraph/
- https://pypi.org/project/jinja2/ · https://pypi.org/project/xlsxwriter/ · https://pypi.org/project/openpyxl/ · https://pypi.org/project/weasyprint/ · https://pypi.org/project/reportlab/ · https://pypi.org/project/plotly/ · https://pypi.org/project/pandas/

npm (`https://registry.npmjs.org/<name>`)
- https://www.npmjs.com/package/recharts · https://www.npmjs.com/package/echarts · https://www.npmjs.com/package/echarts-for-react · https://www.npmjs.com/package/chart.js · https://www.npmjs.com/package/plotly.js-dist-min · https://www.npmjs.com/package/uplot
- https://www.npmjs.com/package/@tanstack/react-table · https://www.npmjs.com/package/ag-grid-react
- https://www.npmjs.com/package/shadcn · https://www.npmjs.com/package/@mantine/core · https://www.npmjs.com/package/@tremor/react
- https://www.npmjs.com/package/@xyflow/react · https://www.npmjs.com/package/cytoscape

GitHub (최신 커밋일 확인: shallow clone)
- https://github.com/yzhao062/pyod · https://github.com/stumpy-dev/stumpy · https://github.com/deepcharles/ruptures · https://github.com/ermshaua/claspy
- https://github.com/Nixtla/statsforecast · https://github.com/statsmodels/statsmodels · https://github.com/skforecast/skforecast
- https://github.com/suanto/pycontrolcharts · https://github.com/huft-jonathan/pyshewhart · https://github.com/carlosqsilva/pyspc
- https://github.com/pandera-dev/pandera · https://github.com/duckdb/duckdb-python · https://github.com/pola-rs/polars · https://github.com/raphaelvallat/pingouin
- https://github.com/xhluca/bm25s · https://github.com/dorianbrown/rank_bm25 · https://github.com/MinishLab/model2vec · https://github.com/qdrant/fastembed · https://github.com/bab2min/kiwipiepy
- https://github.com/google/or-tools · https://github.com/coin-or/pulp · https://github.com/ERGO-Code/HiGHS · https://github.com/networkx/networkx · https://github.com/igraph/python-igraph
- https://github.com/recharts/recharts · https://github.com/apache/echarts · https://github.com/hustcc/echarts-for-react · https://github.com/chartjs/Chart.js · https://github.com/plotly/plotly.js · https://github.com/leeoniya/uPlot
- https://github.com/TanStack/table · https://github.com/ag-grid/ag-grid · https://github.com/shadcn-ui/ui · https://github.com/mantinedev/mantine · https://github.com/tremorlabs/tremor · https://github.com/xyflow/xyflow · https://github.com/cytoscape/cytoscape.js
- https://github.com/Kiranism/next-shadcn-dashboard-starter · https://github.com/fastapi/full-stack-fastapi-template
- https://github.com/Kozea/WeasyPrint · https://github.com/jmcnamara/XlsxWriter · https://github.com/pallets/jinja
