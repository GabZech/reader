from __future__ import annotations

from test_service_worker_browser import _live_server

# On an iPhone, closing the in-app browser that Original opens can leave the
# installed app's window short, so the bottom bar rides above the screen's
# bottom edge (seen in the phone's Diagnostics as an innerHeight of 626 against
# the usual 762, through every page opened after). iOS keeps the window short
# only while the page is no taller than it, so the page makes itself as tall as
# the window was earlier in the launch. A test browser cannot reproduce iOS
# handing the height back, so these check what the page asks for.

TALL = 844
SHORT = TALL - 136

# Playwright cannot install the app, so stand in for the installed app's
# display mode.
AS_INSTALLED_APP = """
const real = window.matchMedia.bind(window);
window.matchMedia = (query) => {
  const list = real("all");
  if (!query.includes("display-mode: standalone")) return real(query);
  Object.defineProperty(list, "matches", { value: true });
  return list;
};
"""

NOTES = """() => JSON.parse(localStorage.getItem("reader-log") || "[]")
  .filter((entry) => entry.e === "viewport")
  .map((entry) => entry.d)"""

MIN_HEIGHT = "() => document.documentElement.style.minHeight"


def _installed_phone(phone):
    phone.add_init_script(AS_INSTALLED_APP)
    return phone


def _open(phone, url):
    phone.goto(url)
    phone.wait_for_function("() => sessionStorage.getItem('reader-tall') !== null")


def _come_back(phone):
    # What iOS does when the in-app browser closes: the app becomes visible again.
    phone.evaluate("document.dispatchEvent(new Event('visibilitychange'))")


def _wait_for_note(phone, start):
    phone.wait_for_function(
        "(start) => JSON.parse(localStorage.getItem('reader-log') || '[]')"
        ".some((entry) => entry.e === 'viewport' && entry.d.startsWith(start))",
        arg=start,
        timeout=8000,
    )


def test_a_window_left_short_after_coming_back_makes_the_page_full_height(
    phone, monkeypatch, tmp_path
):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        _come_back(phone)

        _wait_for_note(phone, "stuck")
        assert phone.evaluate(MIN_HEIGHT) == f"{TALL}px"
        notes = phone.evaluate(NOTES)
        assert notes[0].startswith(f"short ih={SHORT} tall={TALL}")
        assert notes[-1] == f"stuck ih={SHORT} tall={TALL}"
        # The page itself still does not scroll.
        assert phone.evaluate("document.scrollingElement.scrollTop") == 0


def test_a_page_opened_while_the_window_is_still_short_is_made_full_height_too(
    phone, monkeypatch, tmp_path
):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        phone.goto(f"{origin}/sources")

        _wait_for_note(phone, "short")
        assert phone.evaluate(MIN_HEIGHT) == f"{TALL}px"


def test_once_the_window_is_full_height_again_the_page_lets_go(
    phone, monkeypatch, tmp_path
):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        _come_back(phone)
        _wait_for_note(phone, "short")
        phone.set_viewport_size({"width": 390, "height": TALL})

        _wait_for_note(phone, "ok")
        assert phone.evaluate(NOTES)[-1] == f"ok ih={TALL} tall={TALL}"
        assert phone.evaluate(MIN_HEIGHT) == ""


def test_a_full_height_window_is_left_alone(phone, monkeypatch, tmp_path):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        _come_back(phone)
        phone.wait_for_timeout(1500)
        assert phone.evaluate(NOTES) == []
        assert phone.evaluate(MIN_HEIGHT) == ""


def test_the_keyboard_shortening_the_window_is_left_alone(phone, monkeypatch, tmp_path):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.evaluate(
            "document.body.insertAdjacentHTML('beforeend', '<input id=\"typing\">');"
            "document.getElementById('typing').focus()"
        )
        phone.set_viewport_size({"width": 390, "height": SHORT})
        _come_back(phone)
        phone.wait_for_timeout(1500)
        assert phone.evaluate(NOTES) == []
        assert phone.evaluate(MIN_HEIGHT) == ""


def test_a_browser_tab_is_left_alone(phone, monkeypatch, tmp_path):
    # Safari's own toolbars legitimately change the height of a tab.
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/lists")
        # Given the height an installed app would have remembered, so the
        # display mode is the only reason left for it to do nothing.
        phone.evaluate(f"sessionStorage.setItem('reader-tall', '{{\"p\": {TALL}}}')")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        _come_back(phone)
        phone.wait_for_timeout(1500)
        assert phone.evaluate(NOTES) == []
        assert phone.evaluate(MIN_HEIGHT) == ""
