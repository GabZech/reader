"""Which browser engine the browser tests run on.

WebKit by default: it is Safari's engine, the one the installed iPhone app
runs on. Chromium on top before a pull request:

    uv run pytest --browsers=webkit,chromium

or set READER_BROWSERS the same way (CI does for pull requests).
"""

from __future__ import annotations

import os


def pytest_addoption(parser):
    parser.addoption(
        "--browsers",
        default=os.environ.get("READER_BROWSERS", "webkit"),
        help="comma-separated engines for the browser tests: webkit, chromium",
    )


def pytest_generate_tests(metafunc):
    # Any browser fixture that asks for `engine` runs once per chosen engine.
    if "engine" in metafunc.fixturenames:
        engines = [e.strip() for e in metafunc.config.getoption("browsers").split(",") if e.strip()]
        metafunc.parametrize("engine", engines)
