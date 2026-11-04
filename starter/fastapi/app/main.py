"""최소 FastAPI 뼈대: API + 정적 화면 1개.

실행: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import data

app = FastAPI(title="app")
STATIC = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/summary")
def summary():
    return {"files": data.summary()}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
