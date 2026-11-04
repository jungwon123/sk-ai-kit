import { test } from "node:test";
import assert from "node:assert/strict";
import { generateJson, validate, type Schema } from "./llm.ts";

const schema: Schema = { summary: "string", evidence: "array" };
const rule = (f: Record<string, unknown>) => ({ summary: `값 ${f.v}`, evidence: [] as string[] });

test("validate", () => {
  assert.equal(validate({ summary: "a", evidence: [] }, schema), null);
  assert.equal(validate({ summary: "a" }, schema), "missing:evidence");
});

test("llm 정상 + 코드블록", async () => {
  const r = await generateJson("요약", { v: 3 }, schema, rule, async () => '```json\n{"summary":"좋음","evidence":["v=3"]}\n```');
  assert.equal(r.source, "llm");
});

test("형식 오류 → 대체", async () => {
  const r = await generateJson("요약", { v: 3 }, schema, rule, async () => '{"summary":"x"}');
  assert.equal(r.source, "fallback:missing:evidence");
  assert.equal(r.summary, "값 3");
});

test("기본은 규칙 기반(외부 호출 없음)", async () => {
  const r = await generateJson("요약", { v: 3 }, schema, rule);
  assert.equal(r.source, "fallback:llm_disabled");
  assert.equal(r.summary, "값 3");
});
