// 의존성 없는 SVG 선 차트. points: [{x: 라벨, y: 값}]. 여러 선은 series로.
type Pt = { x: string; y: number };
type Series = { name: string; points: Pt[]; color?: string };

export default function LineChart({ series, height = 240, unit = "" }: { series: Series[]; height?: number; unit?: string }) {
  const W = 640, H = height, P = { l: 48, r: 12, t: 12, b: 28 };
  const xs = Array.from(new Set(series.flatMap(s => s.points.map(p => p.x))));
  const ys = series.flatMap(s => s.points.map(p => p.y)).filter(Number.isFinite);
  if (!xs.length || !ys.length) return <p>데이터 없음</p>;
  let lo = Math.min(...ys), hi = Math.max(...ys);
  if (lo === hi) { lo -= 1; hi += 1; }
  const sx = (x: string) => P.l + (xs.indexOf(x) / Math.max(1, xs.length - 1)) * (W - P.l - P.r);
  const sy = (y: number) => P.t + (1 - (y - lo) / (hi - lo)) * (H - P.t - P.b);
  const ticks = [lo, (lo + hi) / 2, hi];
  const colors = ["#2563eb", "#dc2626", "#059669", "#d97706"];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, fontSize: 11 }} role="img">
      {ticks.map(t => (
        <g key={t}>
          <line x1={P.l} x2={W - P.r} y1={sy(t)} y2={sy(t)} stroke="#e5e7eb" />
          <text x={P.l - 6} y={sy(t) + 4} textAnchor="end" fill="#6b7280">{t.toFixed(2)}{unit}</text>
        </g>
      ))}
      {[...new Set([xs[0], xs[Math.floor(xs.length / 2)], xs[xs.length - 1]])].map((x, i, a) => (
        <text key={x} x={sx(x)} y={H - 8} textAnchor={i === 0 ? "start" : i === a.length - 1 ? "end" : "middle"} fill="#6b7280">{x}</text>
      ))}
      {series.map((s, i) => (
        <polyline key={s.name} fill="none" strokeWidth={2} stroke={s.color ?? colors[i % colors.length]}
          points={s.points.filter(p => Number.isFinite(p.y)).map(p => `${sx(p.x)},${sy(p.y)}`).join(" ")} />
      ))}
      {series.length > 1 && series.map((s, i) => (
        <text key={s.name} x={P.l + 8 + i * 110} y={P.t + 10} fill={s.color ?? colors[i % colors.length]}>■ {s.name}</text>
      ))}
    </svg>
  );
}
