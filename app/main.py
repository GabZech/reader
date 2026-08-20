from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import database_path, skeleton_feed_url
from app.db import (
    all_lists,
    all_sources,
    connect,
    format_when,
    get_item,
    get_list,
    init_db,
    items_for_list,
    lists_with_items,
    reading_length,
)
from app.ingest import ingest_url

APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
templates.env.globals["format_when"] = format_when
templates.env.globals["reading_length"] = reading_length

@asynccontextmanager
async def lifespan(_app: FastAPI):
    conn = connect()
    try:
        init_db(conn)
        conn.commit()
    finally:
        conn.close()
    yield


app = FastAPI(title="Reader", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


@app.get("/")
def home(request: Request):
    conn = connect()
    try:
        init_db(conn)
        lists = lists_with_items(conn, limit_per_list=6)
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"nav": "home", "lists": lists},
    )


@app.get("/lists")
def lists_page(request: Request):
    conn = connect()
    try:
        init_db(conn)
        lists = all_lists(conn)
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "lists.html",
        {"nav": "lists", "lists": lists},
    )


@app.get("/lists/{slug}")
def list_page(request: Request, slug: str):
    conn = connect()
    try:
        init_db(conn)
        named = get_list(conn, slug)
        if named is None:
            raise HTTPException(status_code=404)
        items = items_for_list(conn, slug)
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "list.html",
        {
            "nav": "lists",
            "list_name": named["name"],
            "slug": slug,
            "items": items,
        },
    )


@app.get("/sources")
def sources_page(request: Request):
    conn = connect()
    try:
        init_db(conn)
        sources = all_sources(conn)
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "sources.html",
        {"nav": "sources", "sources": sources},
    )


@app.get("/items/{item_id}")
def item_page(request: Request, item_id: int):
    conn = connect()
    try:
        init_db(conn)
        item = get_item(conn, item_id)
    finally:
        conn.close()
    if item is None:
        raise HTTPException(status_code=404)
    back = f"/lists/{item['list_slug']}" if item["list_slug"] else "/"
    return templates.TemplateResponse(
        request,
        "item.html",
        {"nav": "home", "item": item, "back": back},
    )


@app.post("/sync")
def sync():
    conn = connect()
    try:
        init_db(conn)
        result = ingest_url(conn, skeleton_feed_url())
        conn.commit()
    finally:
        conn.close()
    return result


@app.get("/sw.js")
def service_worker():
    return FileResponse(
        APP_DIR / "static" / "sw.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(
        APP_DIR / "static" / "manifest.webmanifest",
        media_type="application/manifest+json",
    )


@app.get("/health")
def health():
    database_path()
    return {"ok": True}


@app.get("/favicon.ico")
def favicon():
    return RedirectResponse("/static/favicon.svg")
