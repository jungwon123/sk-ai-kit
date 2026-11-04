// 해석 문장 생성 래퍼: JSON 형식 검증 + 규칙 기반 대체. 외부 API를 호출하지 않는다(네트워크 코드 없음).
// - 기본은 규칙 기반 결과(source "fallback:llm_disabled"). 과제가 허용된 호출 수단을 명시할 때만 caller로 넘긴다.
// - 어떤 실패든 예외를 던지지 않고 fallback 결과에 source를 붙여 돌려준다.

export type Schema = Record<string, "string" | "number" | "boolean" | "array" | "object">;
export type Caller = (prompt: string) => Promise<string>;

export function validate(obj: unknown, schema: Schema): string | null {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) return "not_object";
  const o = obj as Record<string, unknown>;
  for (const [k, t] of Object.entries(schema)) {
    if (!(k in o)) return `missing:${k}`;
    const v = o[k];
    const ok = t === "array" ? Array.isArray(v) : t === "object" ? !!v && typeof v === "object" && !Array.isArray(v) : typeof v === t;
    if (!ok) return `type:${k}`;
  }
  return null;
}

function extractJson(text: string): unknown {
  const s = text.indexOf("{"), e = text.lastIndexOf("}");
  if (s < 0 || e <= s) throw new Error("no_json");
  return JSON.parse(text.slice(s, e + 1));
}

export async function generateJson<T extends Record<string, unknown>>(
  instruction: string, facts: Record<string, unknown>, schema: Schema,
  fallback: (facts: Record<string, unknown>) => T, caller: Caller | null = null,
): Promise<T & { source: string }> {
  const prompt = `${instruction}\n\n아래 집계 결과만 근거로 사용하고, 숫자를 인용할 때는 그대로 쓴다.\n` +
    `집계 결과(JSON): ${JSON.stringify(facts)}\n\n반드시 다음 키를 가진 JSON 객체 하나만 출력: ${Object.keys(schema).join(", ")}`;
  if (!caller) return { ...fallback(facts), source: "fallback:llm_disabled" };
  let reason = "unknown";
  try {
    const obj = extractJson(await caller(prompt));
    const bad = validate(obj, schema);
    if (!bad) return { ...(obj as T), source: "llm" };
    reason = bad;
  } catch (e) {
    reason = e instanceof Error ? e.message : String(e);
  }
  return { ...fallback(facts), source: `fallback:${reason}` };
}
