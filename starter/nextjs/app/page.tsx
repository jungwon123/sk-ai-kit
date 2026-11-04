import { summary } from "@/lib/data";

export const dynamic = "force-dynamic";

export default function Page() {
  const files = summary();
  return (
    <main>
      <h1>데이터 현황</h1>
      {files.length === 0 ? (
        <p>data/ 폴더에 CSV가 없습니다.</p>
      ) : (
        <table style={{ borderCollapse: "collapse", fontVariantNumeric: "tabular-nums" }}>
          <thead><tr><th style={th}>파일</th><th style={th}>행</th></tr></thead>
          <tbody>
            {files.map(f => (
              <tr key={f.file}><td style={td}>{f.file}</td><td style={td}>{f.rows.toLocaleString()}</td></tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}

const th = { textAlign: "left" as const, padding: "6px 10px", background: "#f4f6f9" };
const td = { padding: "6px 10px", borderBottom: "1px solid #e3e6ec" };
