# starter/nextjs

최소 뼈대: Next.js(App Router, TypeScript) 서버 컴포넌트 화면 + API route + node 내장 테스트. 과제 폴더 루트에 복사해서 쓴다.

```bash
npm install
npm run dev        # 0.0.0.0:3000 (Browser 미리보기 PORT 3000, 경로 /)
npm test           # lib/*.test.ts
```

- 데이터 위치: `DATA_DIR` 환경변수(기본 `./data`). 원본은 수정하지 않는다.
- CSV 파서는 단순 구현이다. 데이터가 크거나 집계가 복잡하면 Python(pandas)으로 처리하고 결과(JSON/CSV)만 읽는 편이 낫다.
- 집계·판정 로직은 `lib/`에 함수로 두고 `*.test.ts`로 테스트한다.
- `lib/llm.ts`: 해석 문장 래퍼(JSON 형식 검증 + 규칙 기반 대체). **외부 API 호출 없음**, 기본은 규칙 기반 결과.
- `components/LineChart.tsx`: 의존성 없는 SVG 선 차트 (`<LineChart series={[{name, points:[{x, y}]}]} />`).
