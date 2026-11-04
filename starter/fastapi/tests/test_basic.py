import pandas as pd
from fastapi.testclient import TestClient

from app import data
from app.main import app


def test_health():
    assert TestClient(app).get("/api/health").json() == {"ok": True}


def test_summary_counts(tmp_path, monkeypatch):
    pd.DataFrame({"a": [1, 2, 3]}).to_csv(tmp_path / "x.csv", index=False)
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    data.load_csv.cache_clear()
    body = TestClient(app).get("/api/summary").json()
    assert body["files"] == [{"file": "x.csv", "rows": 3, "cols": 1}]


def test_static_chart_served():
    r = TestClient(app).get("/static/chart.js")
    assert r.status_code == 200 and "drawLine" in r.text
