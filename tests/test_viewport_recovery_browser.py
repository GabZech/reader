from __future__ import annotations

import pytest
from test_service_worker_browser import _live_server

# On an iPhone, closing the in-app browser that Original opens can leave the
# installed app's window short, so the bottom bar rides above the screen's
# bottom edge until the app is reopened (seen in the phone's Diagnostics as an
# innerHeight of 626 against the usual 762). The page cannot resize the window,
# so it asks iOS to measure again, a few times at most, and logs each try.

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

BREADCRUMBS = """() => JSON.parse(localStorage.getItem("reader-log") || "[]")
  .filter((entry) => entry.e === "viewport")
  .map((entry) => entry.d)"""


def _installed_phone(phone):
    phone.add_init_script(AS_INSTALLED_APP)
    return phone


def _open(phone, url):
    # The page records the window's normal height shortly after it loads;
    # the return from the in-app browser comes long after.
    phone.goto(url)
    phone.wait_for_function("() => sessionStorage.getItem('reader-tall') !== null")


def _come_back(phone):
    # What iOS does when the in-app browser closes: the app becomes visible again.
    phone.evaluate("document.dispatchEvent(new Event('visibilitychange'))")


def _notes(phone):
    return phone.evaluate(BREADCRUMBS)


def test_a_window_left_short_after_coming_back_is_noticed_and_nudged_a_few_times(
    phone, monkeypatch, tmp_path
):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        _come_back(phone)

        phone.wait_for_function(
            "() => JSON.parse(localStorage.getItem('reader-log') || '[]')"
            ".some((entry) => entry.e === 'viewport' && entry.d.startsWith('stuck'))",
            timeout=8000,
        )
        notes = _notes(phone)
        assert notes[0].startswith(f"short ih={SHORT} tall={TALL}")
        assert notes[-1].startswith(f"stuck ih={SHORT} after 3")
        assert len(notes) == 2


def test_a_page_opened_while_the_window_is_still_short_is_noticed_too(
    phone, monkeypatch, tmp_path
):
    # Pages opened after the return load at the short height; what the window
    # measured earlier in the launch is kept for them.
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        phone.goto(f"{origin}/sources")

        phone.wait_for_function(
            "() => JSON.parse(localStorage.getItem('reader-log') || '[]')"
            ".some((entry) => entry.e === 'viewport' && entry.d.startsWith('short'))",
            timeout=8000,
        )
        assert _notes(phone)[0].startswith(f"short ih={SHORT} tall={TALL}")


def test_a_window_that_comes_back_to_full_height_is_logged_as_fixed(
    phone, monkeypatch, tmp_path
):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        _come_back(phone)
        phone.wait_for_function(
            "() => JSON.parse(localStorage.getItem('reader-log') || '[]')"
            ".some((entry) => entry.e === 'viewport' && entry.d.startsWith('short'))",
            timeout=8000,
        )
        phone.set_viewport_size({"width": 390, "height": TALL})

        phone.wait_for_function(
            "() => JSON.parse(localStorage.getItem('reader-log') || '[]')"
            ".some((entry) => entry.e === 'viewport' && entry.d.startsWith('ok'))",
            timeout=8000,
        )
        assert _notes(phone)[-1].startswith(f"ok ih={TALL}")


def test_a_full_height_window_is_left_alone(phone, monkeypatch, tmp_path):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        _come_back(phone)
        phone.wait_for_timeout(1500)
        assert _notes(phone) == []


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
        assert _notes(phone) == []


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
        assert _notes(phone) == []


@pytest.mark.parametrize("trigger", ["pageshow", "focus"])
def test_other_ways_of_coming_back_are_noticed_too(phone, monkeypatch, tmp_path, trigger):
    phone = _installed_phone(phone)
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        _open(phone, f"{origin}/lists")
        phone.set_viewport_size({"width": 390, "height": SHORT})
        phone.evaluate(f"window.dispatchEvent(new Event('{trigger}'))")

        phone.wait_for_function(
            "() => JSON.parse(localStorage.getItem('reader-log') || '[]')"
            ".some((entry) => entry.e === 'viewport' && entry.d.startsWith('short'))",
            timeout=8000,
        )
