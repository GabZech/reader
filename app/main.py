from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import database_path
from app.db import (
    add_source_to_list,
    all_lists,
    all_sources,
    connect,
    count_items_for_source,
    find_list_by_name,
    find_source_by_feed_url,
    format_when,
    get_item,
    get_list,
    get_source,
    init_db,
    insert_list,
    insert_source,
    rename_list,
    delete_list,
    delete_source,
    items_for_list,
    items_for_source,
    lists_with_items,
    membership_label,
    reading_length,
    remove_source_from_list,
    rename_source,
    source_byline,
    source_id_for,
    source_memberships,
)
from app.ingest import (
    discover_feed,
    ingest_all_sources,
    ingest_url,
    normalize_user_url,
)

APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
templates.env.globals["format_when"] = format_when
templates.env.globals["reading_length"] = reading_length

NO_FEED = "We could not find a feed."
TIMED_NOTE = "Timed list · only recent items"
UNTIMED_NOTE = "Not timed"


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


@app.middleware("http")
async def no_cache_static(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


def _sources_view(conn, rows) -> list[dict]:
    result = []
    for row in rows:
        memberships = source_memberships(conn, row["id"])
        result.append(
            {
                **dict(row),
                "byline": source_byline(row["kind"], memberships),
                "unlisted": not memberships,
            }
        )
    return result


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


@app.get("/lists/add")
def add_list(request: Request, error: str | None = None, name: str = ""):
    return templates.TemplateResponse(
        request,
        "add_list.html",
        {
            "nav": "lists",
            "error": error,
            "name": name,
            "back_href": "/lists",
            "form_action": "/lists/add",
            "hidden": {},
        },
    )


@app.post("/lists/add")
async def add_list_submit(request: Request):
    form = await request.form()
    name = str(form.get("name") or "").strip()
    if not name:
        return add_list(request)
    conn = connect()
    try:
        init_db(conn)
        existing = find_list_by_name(conn, name)
        if existing is not None:
            return RedirectResponse(f"/lists/{existing['slug']}", status_code=303)
        insert_list(conn, name)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/lists", status_code=303)


@app.get("/lists/{slug}/edit")
def edit_list(
    request: Request,
    slug: str,
    error: str | None = None,
    name: str | None = None,
):
    conn = connect()
    try:
        init_db(conn)
        named = get_list(conn, slug)
        if named is None:
            raise HTTPException(status_code=404)
        shown = named["name"] if name is None else name
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "edit_list.html",
        {
            "nav": "lists",
            "slug": slug,
            "name": shown,
            "error": error,
        },
    )


@app.post("/lists/{slug}/edit")
async def edit_list_submit(request: Request, slug: str):
    form = await request.form()
    name = str(form.get("name") or "").strip()
    error = None
    shown = name
    conn = connect()
    try:
        init_db(conn)
        named = get_list(conn, slug)
        if named is None:
            raise HTTPException(status_code=404)
        if not name:
            shown = ""
        else:
            existing = find_list_by_name(conn, name)
            if existing is not None and existing["slug"] != slug:
                error = "That name is already used."
            else:
                rename_list(conn, slug, name)
                conn.commit()
                return RedirectResponse(f"/lists/{slug}", status_code=303)
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "edit_list.html",
        {
            "nav": "lists",
            "slug": slug,
            "name": shown,
            "error": error,
        },
    )


@app.post("/lists/{slug}/delete")
async def delete_list_submit(request: Request, slug: str):
    conn = connect()
    try:
        init_db(conn)
        named = get_list(conn, slug)
        if named is None:
            raise HTTPException(status_code=404)
        delete_list(conn, slug)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/lists", status_code=303)


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
        sources = _sources_view(conn, all_sources(conn))
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "sources.html",
        {"nav": "sources", "sources": sources},
    )


@app.get("/sources/add")
def add_source(request: Request, error: str | None = None, url: str = ""):
    return templates.TemplateResponse(
        request,
        "add.html",
        {"nav": "sources", "error": error, "url": url},
    )


@app.post("/sources/add")
async def add_source_submit(request: Request):
    form = await request.form()
    raw = str(form.get("url") or "")
    if not raw.strip():
        return add_source(request)
    target = normalize_user_url(raw)
    if target is None:
        return add_source(request, error=NO_FEED, url=raw)
    discovered = discover_feed(target)
    if discovered is None:
        return add_source(request, error=NO_FEED, url=raw)
    conn = connect()
    try:
        init_db(conn)
        existing = find_source_by_feed_url(conn, discovered.feed_url)
    finally:
        conn.close()
    if existing is not None:
        return RedirectResponse(
            f"/sources/{existing['id']}?already=1", status_code=303
        )
    query = urlencode(
        {
            "feed_url": discovered.feed_url,
            "title": discovered.title,
            "item_count": str(discovered.item_count),
        }
    )
    return RedirectResponse(f"/sources/add/count?{query}", status_code=303)


@app.get("/sources/add/count")
def add_count_page(
    request: Request,
    feed_url: str = "",
    title: str = "RSS",
    item_count: int = 0,
):
    if not feed_url:
        return RedirectResponse("/sources/add", status_code=303)
    return templates.TemplateResponse(
        request,
        "add_count.html",
        {
            "nav": "sources",
            "feed_url": feed_url,
            "title": title,
            "item_count": item_count,
        },
    )


@app.post("/sources/add/count")
async def add_source_count(request: Request):
    form = await request.form()
    feed_url = str(form.get("feed_url") or "")
    title = str(form.get("title") or "RSS")
    item_count = _int_field(form.get("item_count"), 0)
    choice = str(form.get("backfill") or "")
    exact = str(form.get("exact") or "")
    backfill = _backfill_choice(choice, exact, item_count)
    if backfill is False:
        query = urlencode(
            {"feed_url": feed_url, "title": title, "item_count": str(item_count)}
        )
        return RedirectResponse(f"/sources/add/count?{query}", status_code=303)
    query = urlencode(
        {
            "feed_url": feed_url,
            "title": title,
            "item_count": str(item_count),
            "backfill": "" if backfill is None else str(backfill),
        }
    )
    return RedirectResponse(f"/sources/add/list?{query}", status_code=303)


@app.get("/sources/add/list")
def add_list_page(
    request: Request,
    feed_url: str = "",
    title: str = "RSS",
    item_count: int = 0,
    backfill: str = "",
):
    if not feed_url:
        return RedirectResponse("/sources/add", status_code=303)
    conn = connect()
    try:
        init_db(conn)
        lists = _chooser_lists(conn)
    finally:
        conn.close()
    list_query = _feed_query(feed_url, title, item_count, backfill)
    return templates.TemplateResponse(
        request,
        "add_source_list.html",
        {
            "nav": "sources",
            "feed_url": feed_url,
            "title": title,
            "item_count": item_count,
            "backfill": backfill,
            "lists": lists,
            "list_query": list_query,
            "count_query": urlencode(
                {
                    "feed_url": feed_url,
                    "title": title,
                    "item_count": str(item_count),
                }
            ),
        },
    )


@app.post("/sources/add/list")
async def add_source_list(request: Request):
    form = await request.form()
    feed_url = str(form.get("feed_url") or "")
    title = str(form.get("title") or "RSS")
    item_count = _int_field(form.get("item_count"), 0)
    backfill_raw = str(form.get("backfill") or "")
    list_slug = str(form.get("list_slug") or "").strip()
    return _continue_after_list(
        request,
        feed_url=feed_url,
        title=title,
        item_count=item_count,
        backfill_raw=backfill_raw,
        list_slug=list_slug or None,
    )


@app.get("/sources/add/new-list")
def add_source_new_list_page(
    request: Request,
    feed_url: str = "",
    title: str = "RSS",
    item_count: int = 0,
    backfill: str = "",
    error: str | None = None,
    name: str = "",
):
    if not feed_url:
        return RedirectResponse("/sources/add", status_code=303)
    list_query = _feed_query(feed_url, title, item_count, backfill)
    return templates.TemplateResponse(
        request,
        "add_list.html",
        {
            "nav": "sources",
            "error": error,
            "name": name,
            "back_href": f"/sources/add/list?{list_query}",
            "form_action": "/sources/add/new-list",
            "hidden": {
                "feed_url": feed_url,
                "title": title,
                "item_count": str(item_count),
                "backfill": backfill,
            },
        },
    )


@app.post("/sources/add/new-list")
async def add_source_new_list(request: Request):
    form = await request.form()
    feed_url = str(form.get("feed_url") or "")
    title = str(form.get("title") or "RSS")
    item_count = _int_field(form.get("item_count"), 0)
    backfill_raw = str(form.get("backfill") or "")
    name = str(form.get("name") or "").strip()
    if not feed_url:
        return RedirectResponse("/sources/add", status_code=303)
    if not name:
        return add_source_new_list_page(
            request,
            feed_url=feed_url,
            title=title,
            item_count=item_count,
            backfill=backfill_raw,
            name="",
        )
    conn = connect()
    try:
        init_db(conn)
        existing = find_list_by_name(conn, name)
        if existing is not None:
            slug = existing["slug"]
        else:
            slug = insert_list(conn, name)
            conn.commit()
    finally:
        conn.close()
    return _continue_after_list(
        request,
        feed_url=feed_url,
        title=title,
        item_count=item_count,
        backfill_raw=backfill_raw,
        list_slug=slug,
    )


@app.get("/sources/add/window")
def add_window_page(
    request: Request,
    feed_url: str = "",
    title: str = "RSS",
    item_count: int = 0,
    backfill: str = "",
    list_slug: str = "news",
):
    if not feed_url:
        return RedirectResponse("/sources/add", status_code=303)
    return templates.TemplateResponse(
        request,
        "add_window.html",
        {
            "nav": "sources",
            "feed_url": feed_url,
            "title": title,
            "item_count": item_count,
            "backfill": backfill,
            "list_slug": list_slug,
            "list_query": urlencode(
                {
                    "feed_url": feed_url,
                    "title": title,
                    "item_count": str(item_count),
                    "backfill": backfill,
                }
            ),
        },
    )


@app.post("/sources/add/window")
async def add_source_window(request: Request):
    form = await request.form()
    window = str(form.get("window") or "")
    if window not in {"day", "week"}:
        query = urlencode(
            {
                "feed_url": str(form.get("feed_url") or ""),
                "title": str(form.get("title") or "RSS"),
                "item_count": str(_int_field(form.get("item_count"), 0)),
                "backfill": str(form.get("backfill") or ""),
                "list_slug": "news",
            }
        )
        return RedirectResponse(f"/sources/add/window?{query}", status_code=303)
    return _commit_source(
        request,
        feed_url=str(form.get("feed_url") or ""),
        title=str(form.get("title") or "RSS"),
        list_slug="news",
        window=window,
        backfill_raw=str(form.get("backfill") or ""),
    )


@app.get("/sources/added/{source_id}")
def source_added(request: Request, source_id: str):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        memberships = source_memberships(conn, source_id)
    finally:
        conn.close()
    membership = memberships[0] if memberships else None
    return templates.TemplateResponse(
        request,
        "add_done.html",
        {
            "nav": "sources",
            "title": source["title"],
            "list_name": membership["list_name"] if membership else "",
            "timed": bool(membership) and membership["list_slug"] == "news",
            "unlisted": membership is None,
        },
    )


@app.get("/sources/{source_id}/items")
def source_items_page(request: Request, source_id: str):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        items = items_for_source(conn, source_id)
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "source_items.html",
        {
            "nav": "sources",
            "source": source,
            "items": items,
        },
    )


@app.post("/sources/{source_id}/rename")
async def source_rename(request: Request, source_id: str):
    form = await request.form()
    name = str(form.get("name") or "")
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        rename_source(conn, source_id, name)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/sources/{source_id}?flash=Saved", status_code=303)


@app.post("/sources/{source_id}/delete")
def source_delete(source_id: str):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        delete_source(conn, source_id)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/sources", status_code=303)


@app.get("/sources/{source_id}")
def source_page(
    request: Request,
    source_id: str,
    already: str = "",
    flash: str = "",
):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        memberships = source_memberships(conn, source_id)
        item_count = count_items_for_source(conn, source_id)
    finally:
        conn.close()
    membership_views = [
        {"list_slug": m["list_slug"], "label": membership_label(m)}
        for m in memberships
    ]
    return templates.TemplateResponse(
        request,
        "source.html",
        {
            "nav": "sources",
            "source": {
                **dict(source),
                "byline": source_byline(source["kind"], memberships),
            },
            "memberships": membership_views,
            "item_count": item_count,
            "already": already == "1",
            "flash": flash,
        },
    )


@app.get("/sources/{source_id}/list")
def source_list_page(request: Request, source_id: str):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        joined = {m["list_slug"] for m in source_memberships(conn, source_id)}
        lists = [entry for entry in _chooser_lists(conn) if entry[0] not in joined]
    finally:
        conn.close()
    return templates.TemplateResponse(
        request,
        "source_list.html",
        {"nav": "sources", "source": source, "lists": lists},
    )


@app.post("/sources/{source_id}/list")
async def source_list_submit(request: Request, source_id: str):
    form = await request.form()
    list_slug = str(form.get("list_slug") or "").strip()
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
    finally:
        conn.close()
    if not list_slug:
        return RedirectResponse(f"/sources/{source_id}/list", status_code=303)
    return _apply_source_list(source_id, list_slug)


@app.post("/sources/{source_id}/lists/{list_slug}/remove")
def source_list_remove(source_id: str, list_slug: str):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        remove_source_from_list(conn, source_id, list_slug)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/sources/{source_id}?flash=Removed", status_code=303)


@app.get("/sources/{source_id}/new-list")
def source_new_list_page(
    request: Request, source_id: str, error: str | None = None, name: str = ""
):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
    finally:
        conn.close()
    if source is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "add_list.html",
        {
            "nav": "sources",
            "error": error,
            "name": name,
            "back_href": f"/sources/{source_id}/list",
            "form_action": f"/sources/{source_id}/new-list",
            "hidden": {"source_id": source_id},
        },
    )


@app.post("/sources/{source_id}/new-list")
async def source_new_list_submit(request: Request, source_id: str):
    form = await request.form()
    name = str(form.get("name") or "").strip()
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
    finally:
        conn.close()
    if not name:
        return source_new_list_page(request, source_id, name="")
    conn = connect()
    try:
        init_db(conn)
        existing = find_list_by_name(conn, name)
        if existing is not None:
            slug = existing["slug"]
        else:
            slug = insert_list(conn, name)
            conn.commit()
    finally:
        conn.close()
    return _apply_source_list(source_id, slug)


@app.get("/sources/{source_id}/window")
def source_window_page(request: Request, source_id: str):
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
    finally:
        conn.close()
    if source is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request, "source_window.html", {"nav": "sources", "source": source}
    )


@app.post("/sources/{source_id}/window")
async def source_window_submit(request: Request, source_id: str):
    form = await request.form()
    window = str(form.get("window") or "")
    if window not in {"day", "week"}:
        return RedirectResponse(f"/sources/{source_id}/window", status_code=303)
    conn = connect()
    try:
        init_db(conn)
        source = get_source(conn, source_id)
        if source is None:
            raise HTTPException(status_code=404)
        add_source_to_list(conn, source_id, "news", window)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/sources/{source_id}?flash=Saved", status_code=303)


@app.get("/items/{item_id}")
def item_page(
    request: Request,
    item_id: int,
    from_source: str | None = None,
    from_list: str | None = None,
):
    conn = connect()
    try:
        init_db(conn)
        item = get_item(conn, item_id)
    finally:
        conn.close()
    if item is None:
        raise HTTPException(status_code=404)
    if from_source and item["source_id"] == from_source:
        back = f"/sources/{from_source}/items"
    elif from_list:
        back = f"/lists/{from_list}"
    else:
        back = "/"
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
        result = ingest_all_sources(conn)
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


def _feed_query(
    feed_url: str, title: str, item_count: int, backfill: str = ""
) -> str:
    return urlencode(
        {
            "feed_url": feed_url,
            "title": title,
            "item_count": str(item_count),
            "backfill": backfill,
        }
    )


def _chooser_lists(conn) -> list[tuple[str, str, str]]:
    return [
        (
            row["slug"],
            row["name"],
            TIMED_NOTE if row["slug"] == "news" else UNTIMED_NOTE,
        )
        for row in all_lists(conn)
    ]


def _continue_after_list(
    request: Request,
    *,
    feed_url: str,
    title: str,
    item_count: int,
    backfill_raw: str,
    list_slug: str | None,
):
    if not list_slug:
        return _commit_source(
            request,
            feed_url=feed_url,
            title=title,
            list_slug=None,
            window=None,
            backfill_raw=backfill_raw,
        )
    conn = connect()
    try:
        init_db(conn)
        named = get_list(conn, list_slug)
    finally:
        conn.close()
    if named is None:
        return RedirectResponse(
            f"/sources/add/list?{_feed_query(feed_url, title, item_count, backfill_raw)}",
            status_code=303,
        )
    if list_slug == "news":
        query = urlencode(
            {
                "feed_url": feed_url,
                "title": title,
                "item_count": str(item_count),
                "backfill": backfill_raw,
                "list_slug": list_slug,
            }
        )
        return RedirectResponse(f"/sources/add/window?{query}", status_code=303)
    return _commit_source(
        request,
        feed_url=feed_url,
        title=title,
        list_slug=list_slug,
        window=None,
        backfill_raw=backfill_raw,
    )


def _apply_source_list(source_id: str, list_slug: str):
    if list_slug == "news":
        return RedirectResponse(f"/sources/{source_id}/window", status_code=303)
    conn = connect()
    try:
        init_db(conn)
        add_source_to_list(conn, source_id, list_slug, None)
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/sources/{source_id}?flash=Saved", status_code=303)


def _int_field(value, default: int) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _backfill_choice(choice: str, exact: str, item_count: int):
    if choice == "all":
        return None
    if choice == "5":
        return 5
    if choice == "1":
        return 1
    if choice == "exact":
        if not exact.strip():
            return False
        try:
            count = int(exact)
        except ValueError:
            return False
        if count < 1:
            return False
        if item_count:
            return min(count, item_count)
        return count
    return False


def _commit_source(
    request: Request,
    *,
    feed_url: str,
    title: str,
    list_slug: str | None,
    window: str | None,
    backfill_raw: str,
):
    backfill = int(backfill_raw) if backfill_raw else None
    conn = connect()
    try:
        init_db(conn)
        existing = find_source_by_feed_url(conn, feed_url)
        if existing is not None:
            conn.commit()
            return RedirectResponse(
                f"/sources/{existing['id']}?already=1", status_code=303
            )
        source_id = source_id_for(feed_url)
        insert_source(
            conn,
            source_id=source_id,
            kind="rss",
            title=title or "RSS",
            feed_url=feed_url,
            backfill=backfill,
            auto_title=title or "RSS",
        )
        if list_slug:
            add_source_to_list(conn, source_id, list_slug, window)
        ingest_url(conn, feed_url, source_id, limit=backfill)
        conn.commit()
    except Exception:
        conn.rollback()
        return add_source(request, error=NO_FEED, url=feed_url)
    finally:
        conn.close()
    return RedirectResponse(f"/sources/added/{source_id}", status_code=303)
