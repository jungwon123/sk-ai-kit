// 의존성 없는 SVG 차트 헬퍼. CDN 없이 동작한다.
// drawLine(el, [{name, points:[{x, y}]}], {unit})  /  drawBars(el, [{label, value}], {unit})
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const COLORS = ["#2563eb", "#dc2626", "#059669", "#d97706"];
  const mk = (tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  };
  function frame(el, W, H) {
    el.innerHTML = "";
    const svg = mk("svg", { viewBox: `0 0 ${W} ${H}`, style: `width:100%;max-width:${W}px;font:11px system-ui` });
    el.appendChild(svg);
    return svg;
  }
  function yScale(vals, top, bottom) {
    let lo = Math.min(...vals), hi = Math.max(...vals);
    if (lo === hi) { lo -= 1; hi += 1; }
    return { lo, hi, f: v => top + (1 - (v - lo) / (hi - lo)) * (bottom - top) };
  }
  window.drawLine = function (el, series, opt = {}) {
    const W = 640, H = opt.height || 240, P = { l: 70, r: 12, t: 26, b: 28 };
    const xs = [...new Set(series.flatMap(s => s.points.map(p => String(p.x))))];
    const ys = series.flatMap(s => s.points.map(p => p.y)).filter(Number.isFinite);
    if (!xs.length || !ys.length) { el.textContent = "데이터 없음"; return; }
    const svg = frame(el, W, H), y = yScale(ys.concat((opt.hlines || []).map(h => h.y).filter(Number.isFinite)), P.t, H - P.b);
    const sx = x => P.l + (xs.indexOf(String(x)) / Math.max(1, xs.length - 1)) * (W - P.l - P.r);
    [y.lo, (y.lo + y.hi) / 2, y.hi].forEach(t => {
      svg.appendChild(mk("line", { x1: P.l, x2: W - P.r, y1: y.f(t), y2: y.f(t), stroke: "#e5e7eb" }));
      svg.appendChild(mk("text", { x: P.l - 6, y: y.f(t) + 4, "text-anchor": "end", fill: "#6b7280" }, t.toFixed(2) + (opt.unit || "")));
    });
    [...new Set([xs[0], xs[Math.floor(xs.length / 2)], xs[xs.length - 1]])].forEach((x, i, a) =>
      svg.appendChild(mk("text", { x: sx(x), y: H - 8, "text-anchor": i === 0 ? "start" : i === a.length - 1 ? "end" : "middle", fill: "#6b7280" }, x)));
    (opt.hlines || []).forEach(h => svg.appendChild(mk("line", { x1: P.l, x2: W - P.r, y1: y.f(h.y), y2: y.f(h.y), stroke: h.color || "#9ca3af", "stroke-dasharray": "4 3" })));
    series.forEach((s, i) => {
      const c = s.color || COLORS[i % COLORS.length];
      svg.appendChild(mk("polyline", { fill: "none", "stroke-width": 2, stroke: c,
        points: s.points.filter(p => Number.isFinite(p.y)).map(p => `${sx(p.x)},${y.f(p.y)}`).join(" ") }));
      if (series.length > 1) svg.appendChild(mk("text", { x: P.l + 8 + i * 110, y: 12, fill: c }, "■ " + s.name));
    });
  };
  window.drawBars = function (el, items, opt = {}) {
    const W = 640, row = 22, P = { l: 140, r: 60 }, H = items.length * row + 8;
    if (!items.length) { el.textContent = "데이터 없음"; return; }
    const svg = frame(el, W, H), max = Math.max(...items.map(d => d.value), 0) || 1;
    items.forEach((d, i) => {
      const w = (d.value / max) * (W - P.l - P.r), yy = 4 + i * row;
      svg.appendChild(mk("text", { x: P.l - 6, y: yy + 14, "text-anchor": "end", fill: "#374151" }, d.label));
      svg.appendChild(mk("rect", { x: P.l, y: yy + 3, width: Math.max(0, w), height: row - 8, fill: d.color || COLORS[0], rx: 2 }));
      svg.appendChild(mk("text", { x: P.l + w + 6, y: yy + 14, fill: "#374151" }, d.value.toLocaleString() + (opt.unit || "")));
    });
  };
})();
