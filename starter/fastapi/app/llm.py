"""해석 문장 생성 래퍼: JSON 형식 검증 + 규칙 기반 대체. **외부 API를 호출하지 않는다.**

- 외부 LLM·외부 API 호출은 금지다. 이 모듈에는 네트워크 코드가 없다.
- 기본 동작은 규칙 기반(fallback) 결과다. 과제가 허용된 호출 수단을 명시적으로 제공할 때만
  그 함수를 caller로 넘긴다(그 경우에도 입력은 집계 결과만).
- caller가 실패하거나 형식이 틀리면 예외를 밖으로 던지지 않고 fallback 결과를 돌려준다. 결과에는 source가 붙는다.

사용 예:
    schema = {"summary": str, "evidence": list, "risk_level": str}
    def rule_based(facts): return {"summary": f"수율 {facts['yield']}%", "evidence": [], "risk_level": "unknown"}
    result = generate_json("다음 집계를 요약해 ...", facts, schema, rule_based)
    result["source"]  # 기본 "fallback:llm_disabled"
"""
from __future__ import annotations

import json
from typing import Any, Callable

Schema = dict[str, type]


def validate(obj: Any, schema: Schema) -> str | None:
    """형식이 맞으면 None, 틀리면 사유 문자열."""
    if not isinstance(obj, dict):
        return "not_object"
    for key, typ in schema.items():
        if key not in obj:
            return f"missing:{key}"
        if not isinstance(obj[key], typ):
            return f"type:{key}"
    return None


def _extract_json(text: str) -> Any:
    """응답에서 JSON 객체 부분만 꺼낸다(코드블록·앞뒤 설명 허용)."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no_json")
    return json.loads(text[start:end + 1])


def generate_json(instruction: str, facts: dict, schema: Schema,
                  fallback: Callable[[dict], dict],
                  caller: Callable[[str], str] | None = None) -> dict:
    prompt = (f"{instruction}\n\n"
              f"아래 집계 결과만 근거로 사용하고, 숫자를 인용할 때는 그대로 쓴다.\n"
              f"집계 결과(JSON): {json.dumps(facts, ensure_ascii=False)}\n\n"
              f"반드시 다음 키를 가진 JSON 객체 하나만 출력: {list(schema)}")
    if caller is None:
        return {**fallback(facts), "source": "fallback:llm_disabled"}
    reason = None
    try:
        obj = _extract_json(caller(prompt))
        reason = validate(obj, schema)
        if reason is None:
            return {**obj, "source": "llm"}
    except Exception as e:  # 네트워크·파싱·키 없음 등 전부 대체 경로로
        reason = str(e) or type(e).__name__
    out = fallback(facts)
    return {**out, "source": f"fallback:{reason}"}
