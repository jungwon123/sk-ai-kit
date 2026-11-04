// 데이터 로드 계층(서버 전용). 원본 data/는 수정하지 않는다.
import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";

export const DATA_DIR = process.env.DATA_DIR ?? path.join(process.cwd(), "data");

/** 아주 단순한 CSV 파서(따옴표 안 쉼표 지원). 큰 데이터나 복잡한 형식이면 Python 처리 후 결과만 읽는다. */
export function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let cur: string[] = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (ch === '"') q = false;
      else cell += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { cur.push(cell); cell = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      cur.push(cell); cell = "";
      if (cur.length > 1 || cur[0] !== "") rows.push(cur);
      cur = [];
    } else cell += ch;
  }
  if (cell !== "" || cur.length) { cur.push(cell); rows.push(cur); }
  const [head, ...body] = rows;
  if (!head) return [];
  return body.map(r => Object.fromEntries(head.map((h, j) => [h, r[j] ?? ""])));
}

const cache = new Map<string, Record<string, string>[]>();

/** 처음 한 번만 읽고 메모리에 둔다. */
export function loadCsv(name: string): Record<string, string>[] {
  if (!cache.has(name)) cache.set(name, parseCsv(readFileSync(path.join(DATA_DIR, name), "utf-8")));
  return cache.get(name)!;
}

export function summary(): { file: string; rows: number }[] {
  if (!existsSync(DATA_DIR)) return [];
  return readdirSync(DATA_DIR).filter(f => f.endsWith(".csv")).sort()
    .map(file => ({ file, rows: loadCsv(file).length }));
}
