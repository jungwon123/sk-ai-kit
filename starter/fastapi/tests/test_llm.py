from app.llm import generate_json, validate

SCHEMA = {"summary": str, "evidence": list}


def rule(facts):
    return {"summary": f"값 {facts['v']}", "evidence": []}


def test_validate():
    assert validate({"summary": "a", "evidence": []}, SCHEMA) is None
    assert validate({"summary": "a"}, SCHEMA) == "missing:evidence"
    assert validate({"summary": 1, "evidence": []}, SCHEMA) == "type:summary"


def test_llm_ok_with_codeblock():
    caller = lambda p: '설명\n```json\n{"summary": "좋음", "evidence": ["v=3"]}\n```'
    r = generate_json("요약해", {"v": 3}, SCHEMA, rule, caller=caller)
    assert r["source"] == "llm" and r["summary"] == "좋음"


def test_fallback_on_bad_format():
    r = generate_json("요약해", {"v": 3}, SCHEMA, rule, caller=lambda p: '{"summary": "x"}')
    assert r["source"] == "fallback:missing:evidence" and r["summary"] == "값 3"


def test_default_is_rule_based_no_network():
    r = generate_json("요약해", {"v": 3}, SCHEMA, rule)
    assert r["source"] == "fallback:llm_disabled" and r["summary"] == "값 3"


def test_no_network_code():
    import inspect
    import app.llm as m
    src = inspect.getsource(m)
    assert "urllib" not in src and "requests" not in src and "http://" not in src and "https://" not in src
