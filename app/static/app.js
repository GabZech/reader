(() => {
  const THEME_COLOR = { light: "#f5eee3", dark: "#17120e" };

  const initThemeToggle = () => {
    const buttons = document.querySelectorAll(".theme-toggle [data-theme-value]");
    const meta = document.querySelector('meta[name="theme-color"]');

    const apply = (theme) => {
      document.documentElement.dataset.theme = theme;
      buttons.forEach((button) => {
        const on = button.dataset.themeValue === theme;
        button.classList.toggle("is-active", on);
        button.setAttribute("aria-pressed", String(on));
      });
      if (meta) meta.setAttribute("content", THEME_COLOR[theme]);
    };

    apply(document.documentElement.dataset.theme === "dark" ? "dark" : "light");

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        localStorage.setItem("reader-theme", button.dataset.themeValue);
        apply(button.dataset.themeValue);
      });
    });
  };

  const registerWorker = async () => {
    if (!("serviceWorker" in navigator)) return;
    try {
      await navigator.serviceWorker.register("/sw.js");
    } catch {
      /* offline cache is best-effort */
    }
  };

  // The Settings cog on Home turns inside two thin arrows while Home syncs
  // or Read Later downloads for offline; it stops once both are done.
  const busy = { syncing: false, downloading: false };
  const showBusy = () => {
    const status = document.getElementById("sync-status");
    if (!status) return;
    const on = busy.syncing || busy.downloading;
    status.classList.toggle("is-updating", on);
    status.setAttribute("aria-label", on ? "Settings (updating)" : "Settings");
  };

  // An iPhone can stop the worker mid-download, and then no "done" ever
  // comes: stop turning after a while rather than forever.
  const DOWNLOAD_GIVE_UP_MS = 2 * 60 * 1000;
  let downloadTimer = null;
  const setDownloading = (running) => {
    clearTimeout(downloadTimer);
    busy.downloading = running;
    if (running) downloadTimer = setTimeout(() => setDownloading(false), DOWNLOAD_GIVE_UP_MS);
    showBusy();
  };

  // Ask the service worker to download Read Later ahead, so a saved article
  // opens offline without being opened first. The worker spaces out the runs.
  // Asking again when a new worker takes over (the one that got the first
  // ask may be the older worker it replaced), and on coming back to the app
  // or the network, so a download cut short gets finished.
  const precacheReadLater = async () => {
    if (!("serviceWorker" in navigator)) return;
    const ask = () => {
      if (!navigator.onLine) return;
      const worker = navigator.serviceWorker.controller;
      if (worker) worker.postMessage({ type: "precache" });
    };
    navigator.serviceWorker.addEventListener("message", (event) => {
      if (event.data && event.data.type === "downloading") setDownloading(event.data.running);
    });
    navigator.serviceWorker.addEventListener("controllerchange", ask);
    window.addEventListener("online", ask);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") ask();
    });
    try {
      await navigator.serviceWorker.ready;
      ask();
    } catch {
      /* offline cache is best-effort */
    }
  };

  // Fetch an article again so the stored offline copy carries a highlight
  // just saved; the service worker keeps what comes back.
  const refreshOfflineCopy = (path = location.pathname) =>
    fetch(path, { headers: { "X-Reader-Prefetch": "1" } })
      .then((r) => r.ok)
      .catch(() => false);

  // Articles whose saves reached the server but whose stored copy was not
  // fetched again yet: kept across pages, since leaving a page cuts a run
  // short and an old copy would bring back what was deleted.
  const STALE_KEY = "reader-stale-copies";
  const staleCopies = () => {
    try {
      return new Set(JSON.parse(localStorage.getItem(STALE_KEY) || "[]"));
    } catch {
      return new Set();
    }
  };
  const markStale = (path, stale) => {
    const all = staleCopies();
    if (stale) all.add(path);
    else all.delete(path);
    try {
      localStorage.setItem(STALE_KEY, JSON.stringify([...all]));
    } catch {
      /* best-effort */
    }
  };

  const note = (event, detail) => {
    if (window.readerLog) window.readerLog(event, detail);
  };

  // Highlights made without a connection, and edits to highlights, wait
  // here and go to the server in order once it is back (see flushOutbox).
  // In localStorage, whose writes are done the moment they are made: an
  // IndexedDB write still under way when the reader tapped on to another
  // page was lost, and the highlight with it.
  const outbox = (() => {
    const KEY = "reader-outbox";
    const changed = () => document.dispatchEvent(new Event("reader:outbox-changed"));
    const read = () => {
      try {
        return JSON.parse(localStorage.getItem(KEY) || "[]");
      } catch {
        return [];
      }
    };
    const write = (entries) => localStorage.setItem(KEY, JSON.stringify(entries));
    const nextKey = (entries) => entries.reduce((max, e) => Math.max(max, e.key), 0) + 1;
    // Promises, so callers need not care where the outbox lives.
    const attempt = (work) => {
      try {
        return Promise.resolve(work());
      } catch (error) {
        return Promise.reject(error);
      }
    };
    return {
      all: () => attempt(read),
      add: (entry) =>
        attempt(() => {
          const entries = read();
          const key = nextKey(entries);
          write([...entries, { ...entry, key }]);
          return key;
        }).finally(changed),
      put: (entry) =>
        attempt(() => write(read().map((e) => (e.key === entry.key ? entry : e)))),
      remove: (key) => attempt(() => write(read().filter((e) => e.key !== key))).finally(changed),
    };
  })();

  // Saves queued by an earlier version, which kept them in IndexedDB: moved
  // over once, so none is lost in the update.
  const moveOldOutbox = () => {
    if (!("indexedDB" in window)) return;
    try {
      if (localStorage.getItem("reader-outbox-moved")) return;
    } catch {
      return;
    }
    const request = indexedDB.open("reader", 1);
    request.onupgradeneeded = () =>
      request.result.createObjectStore("outbox", { keyPath: "key", autoIncrement: true });
    request.onsuccess = () => {
      const db = request.result;
      const all = db.transaction("outbox").objectStore("outbox").getAll();
      all.onsuccess = () => {
        const old = all.result || [];
        old
          .reduce((done, entry) => {
            const { key: _old, ...rest } = entry;
            return done.then(() => outbox.add(rest));
          }, Promise.resolve())
          .then(() => {
            localStorage.setItem("reader-outbox-moved", "1");
            db.close();
            indexedDB.deleteDatabase("reader");
            if (old.length) {
              note("outbox", `moved ${old.length} from the old store`);
              flushOutbox();
            }
          })
          .catch(() => {});
      };
    };
  };

  // A highlight saved on this phone but not yet on the server carries a
  // temporary id starting with "p" until it syncs.
  const isPending = (id) => String(id).startsWith("p");
  const newPendingId = () =>
    `p${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
  // Outbox entries are either a new highlight or an edit to one (a title,
  // the key mark, a delete); entries from before edits existed have no kind.
  const isEdit = (entry) => entry.kind === "edit";
  const byStart = (a, b) => a.start_block - b.start_block || a.start_offset - b.start_offset;

  // `action` is the edit route's last part: key, unkey, delete,
  // section-title or subsection-title.
  const queueEdit = (article, highlightId, action, title = null) =>
    outbox.add({
      kind: "edit",
      article,
      highlightId,
      action,
      title,
      body: title == null ? "" : new URLSearchParams({ title }).toString(),
    });

  // An article's highlights as they stand on this phone: what its page was
  // rendered with, then every outbox entry for it in order. A pending
  // highlight that merges saved ones takes their titles and key mark, as
  // the server will. `pending` marks one with anything still to send.
  const highlightsOnPhone = (saved, entries, article) => {
    let list = saved.map((h) => ({ ...h, pending: false }));
    entries
      .filter((e) => e.article === article)
      .forEach((e) => {
        if (isEdit(e)) {
          const h = list.find((x) => String(x.id) === String(e.highlightId));
          if (!h) return;
          if (e.action === "delete") {
            list = list.filter((x) => x !== h);
            return;
          }
          if (e.action === "key" || e.action === "unkey") h.is_key = e.action === "key";
          if (e.action === "section-title") h.section_title = e.title || null;
          if (e.action === "subsection-title") h.subsection_title = e.title || null;
          h.has_title = Boolean(h.section_title || h.subsection_title);
          h.pending = true;
          return;
        }
        const merged = list.filter((x) => e.mergeIds.includes(x.id)).sort(byStart);
        list = list.filter((x) => !merged.includes(x));
        const [startBlock, startOffset, endBlock, endOffset] = e.span;
        const first = (field) => (merged.find((x) => x[field]) || {})[field] || null;
        const section = first("section_title");
        const subsection = first("subsection_title");
        list.push({
          id: e.pendingId,
          start_block: startBlock,
          start_offset: startOffset,
          end_block: endBlock,
          end_offset: endOffset,
          text: new URLSearchParams(e.body).get("text") || "",
          section_title: section,
          subsection_title: subsection,
          has_title: Boolean(section || subsection) || Boolean(e.hasTitle && !merged.length),
          is_key: merged.some((x) => x.is_key) || Boolean(e.isKey && !merged.length),
          merge_ids: e.mergeIds,
          pending: true,
        });
      });
    return list;
  };

  // The last reading spot per article on this phone. Kept in localStorage,
  // not the outbox: it is written as the page goes away, too late for an
  // IndexedDB write to be sure to land. `unsent` marks one still owed to the
  // server.
  const PROGRESS_KEY = "reader-progress";
  const readProgress = () => {
    try {
      return JSON.parse(localStorage.getItem(PROGRESS_KEY) || "{}");
    } catch {
      return {};
    }
  };
  const writeProgress = (all) => {
    try {
      const newest = Object.entries(all)
        .sort((a, b) => b[1].at - a[1].at)
        .slice(0, 100);
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(Object.fromEntries(newest)));
      document.dispatchEvent(new Event("reader:outbox-changed"));
    } catch {
      /* best-effort */
    }
  };

  // Drawn pending highlights must be on the page before any is sent, or
  // one synced meanwhile would be drawn twice; initHighlights replaces this.
  let pendingDrawn = Promise.resolve();
  let flushing = null;

  // Send what was saved offline: queued highlights in the order they were
  // made, then reading spots. A refusal (the article or passage changed on
  // another device meanwhile) is dropped and noted in Diagnostics; no
  // connection, or the server failing, leaves the rest for next time.
  const flushOutbox = () => {
    if (flushing || !navigator.onLine) return flushing;
    flushing = (async () => {
      await pendingDrawn;
      // Real ids for highlights sent in this run, for the edits after them.
      const realIds = {};
      for (const entry of await outbox.all()) {
        let url = entry.url;
        let highlightId = entry.highlightId;
        if (isEdit(entry)) {
          if (isPending(highlightId)) highlightId = realIds[highlightId];
          // Its highlight was refused or never sent: nothing to edit.
          if (highlightId == null) {
            note("outbox-dropped", `${entry.action} ${entry.highlightId} never synced`);
            await outbox.remove(entry.key);
            continue;
          }
          url = `${entry.article}/highlights/${highlightId}/${entry.action}`;
        }
        let response;
        try {
          // The edit routes answer with a redirect back to the article:
          // that is success, and nothing else needs to load.
          response = await fetch(url, {
            method: "POST",
            body: new URLSearchParams(entry.body),
            redirect: "manual",
          });
        } catch {
          return;
        }
        if (response.status >= 500) return;
        if (response.ok || response.type === "opaqueredirect") {
          if (isEdit(entry)) {
            document.dispatchEvent(
              new CustomEvent("reader:edit-synced", { detail: { entry, highlightId } })
            );
          } else {
            const result = await response.json();
            realIds[entry.pendingId] = result.id;
            // Kept in the outbox too, in case this run stops before the
            // edits that follow are sent.
            for (const later of await outbox.all()) {
              if (isEdit(later) && later.highlightId === entry.pendingId) {
                await outbox.put({ ...later, highlightId: result.id });
              }
            }
            document.dispatchEvent(
              new CustomEvent("reader:highlight-synced", { detail: { entry, result } })
            );
          }
          markStale(entry.article, true);
        } else {
          note("outbox-dropped", `${url} ${response.status}`);
        }
        await outbox.remove(entry.key);
      }
      for (const path of staleCopies()) {
        if (await refreshOfflineCopy(path)) markStale(path, false);
      }

      const spots = readProgress();
      for (const [path, spot] of Object.entries(spots)) {
        if (!spot.unsent) continue;
        let response;
        try {
          response = await fetch(`${path}/progress`, {
            method: "POST",
            body: new URLSearchParams({ index: String(spot.index) }),
          });
        } catch {
          return;
        }
        if (response.status >= 500) return;
        const latest = readProgress();
        if (latest[path] && latest[path].at === spot.at) {
          latest[path].unsent = false;
          writeProgress(latest);
        }
      }
    })()
      .catch(() => {})
      .finally(() => (flushing = null));
    return flushing;
  };

  // The article bar's label, only while offline: "Offline", and how many
  // saves wait for the connection. Online they go at once, so no label.
  const showSyncState = () => {
    const label = document.querySelector(".sync-state");
    if (!label) return;
    if (navigator.onLine) {
      label.hidden = true;
      return;
    }
    const spots = Object.values(readProgress()).filter((spot) => spot.unsent).length;
    outbox
      .all()
      .then((entries) => entries.length + spots)
      .catch(() => spots)
      .then((count) => {
        if (navigator.onLine) return;
        label.textContent = count ? `Offline · ${count} to sync` : "Offline";
        label.hidden = false;
      });
  };

  const initOutbox = () => {
    showSyncState();
    window.addEventListener("offline", showSyncState);
    document.addEventListener("reader:outbox-changed", showSyncState);
    moveOldOutbox();
    flushOutbox();
    window.addEventListener("online", showSyncState);
    window.addEventListener("online", flushOutbox);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") flushOutbox();
    });
  };

  const syncHome = async () => {
    if (location.pathname !== "/") return;
    if (!navigator.onLine) return;
    if (sessionStorage.getItem("reader-synced") === "1") return;
    const updating = (on) => {
      busy.syncing = on;
      showBusy();
    };
    updating(true);
    sessionStorage.setItem("reader-synced", "1");
    try {
      const response = await fetch("/sync", { method: "POST" });
      if (response.ok) {
        location.reload();
      } else {
        updating(false);
      }
    } catch {
      updating(false);
    }
  };

  // Home shows three rows per list, the rest behind Show more. Laid out
  // from the rows still present, so a row swiped away lets the next move up.
  const layoutHomeList = (section) => {
    const rows = [...section.querySelectorAll(":scope > .item-swipe, :scope > .item")];
    const button = section.querySelector(".show-more");
    const expanded = section.dataset.expanded === "1";
    rows.forEach((row, index) => {
      row.hidden = !expanded && index >= 3;
    });
    if (button) {
      button.hidden = rows.length <= 3;
      button.textContent = expanded ? "Show less" : "Show more";
    }
  };

  document.querySelectorAll("[data-list]").forEach((section) => {
    const button = section.querySelector(".show-more");
    if (!button) return;
    button.addEventListener("click", () => {
      section.dataset.expanded = section.dataset.expanded === "1" ? "" : "1";
      layoutHomeList(section);
    });
  });

  const initSwipe = () => {
    const rows = document.querySelectorAll(".item-swipe");
    if (rows.length === 0) return;
    const SLIDE = "transform 0.2s ease";

    // A row leaving one tab lands in the other: the active tab's count
    // drops and, when it moved rather than got deleted, the other rises.
    const bumpCounts = (row, moved) => {
      // On Home a row leaves its list whichever way it goes.
      const homeList = row.closest("[data-list]");
      if (homeList) {
        const count = homeList.querySelector(".count");
        if (count) count.textContent = String(Math.max(0, Number(count.textContent) - 1));
        return;
      }
      const tabs = document.querySelectorAll(".actions a");
      tabs.forEach((tab) => {
        const delta = tab.classList.contains("is-active") ? -1 : moved ? 1 : 0;
        if (delta === 0) return;
        tab.textContent = tab.textContent.replace(/\((\d+)\)/, (_, n) => `(${Number(n) + delta})`);
      });
    };

    const post = async (url) => {
      // `manual` keeps the redirect the form routes answer with from being
      // followed: a 303 back to the list is success, and nothing else loads.
      const response = await fetch(url, { method: "POST", redirect: "manual" });
      if (!(response.ok || response.type === "opaqueredirect")) {
        throw new Error(`status ${response.status}`);
      }
    };

    const setX = (row, x, animate) => {
      const link = row.querySelector(".item");
      link.style.transition = animate ? SLIDE : "none";
      link.style.transform = x ? `translateX(${x}px)` : "";
      row.classList.toggle("is-swiping-left", x < 0);
      row.classList.toggle("is-swiping-right", x > 0);
    };

    const removeRow = (row) => {
      row.style.height = `${row.offsetHeight}px`;
      row.classList.add("is-leaving");
      requestAnimationFrame(() => {
        row.style.height = "0px";
        row.style.borderTopColor = "transparent";
      });
      setTimeout(() => {
        const homeList = row.closest("[data-list]");
        row.remove();
        if (!homeList) return;
        const count = homeList.querySelector(".count");
        // Home hides a list with nothing unread; match that without a reload.
        if (count && count.textContent === "0") {
          homeList.remove();
        } else {
          layoutHomeList(homeList);
        }
      }, 220);
    };

    const failed = (row) => {
      setX(row, 0, true);
      delete row.dataset.busy;
      showToast("Couldn't save");
    };

    const runMove = async (row) => {
      row.dataset.busy = "1";
      setX(row, -row.offsetWidth, true);
      try {
        await post(row.dataset.swipeAction);
      } catch {
        failed(row);
        return;
      }
      bumpCounts(row, true);
      removeRow(row);
    };

    const confirmDelete = (row) => {
      row.dataset.busy = "1";
      setX(row, Math.round(row.offsetWidth * 0.4), true);
      const backdrop = document.createElement("div");
      backdrop.className = "swipe-dialog-backdrop";
      backdrop.innerHTML = `
        <div class="swipe-dialog" role="alertdialog" aria-modal="true" aria-labelledby="swipe-dialog-title">
          <div class="swipe-dialog-body">
            <h2 id="swipe-dialog-title">Delete this article?</h2>
            <p></p>
          </div>
          <div class="swipe-dialog-buttons">
            <button type="button">Cancel</button>
            <button type="button">Delete</button>
          </div>
        </div>`;
      backdrop.querySelector("p").textContent =
        `“${row.querySelector(".title").textContent}” will be removed from every list. This can’t be undone.`;
      const [cancel, confirm] = backdrop.querySelectorAll("button");

      const close = () => {
        backdrop.remove();
        document.removeEventListener("keydown", onKey);
      };
      const onCancel = () => {
        close();
        setX(row, 0, true);
        delete row.dataset.busy;
      };
      const onKey = (event) => {
        if (event.key === "Escape") onCancel();
      };

      cancel.addEventListener("click", onCancel);
      backdrop.addEventListener("click", (event) => {
        if (event.target === backdrop) onCancel();
      });
      document.addEventListener("keydown", onKey);
      confirm.addEventListener("click", async () => {
        close();
        try {
          await post(row.dataset.deleteAction);
        } catch {
          failed(row);
          return;
        }
        bumpCounts(row, false);
        removeRow(row);
      });

      document.body.appendChild(backdrop);
      cancel.focus();
    };

    rows.forEach((row) => {
      const link = row.querySelector(".item");
      if (!link) return;
      const canMove = Boolean(row.dataset.swipeAction);
      let startX = 0;
      let startY = 0;
      let dx = 0;
      let dragging = false;
      let deciding = false;
      let justDragged = false;

      const clamp = (value) => {
        const width = row.offsetWidth;
        return Math.max(canMove ? -width : 0, Math.min(width, value));
      };

      // A mouse drag on a link otherwise starts the browser's own link drag,
      // which cancels the pointer mid-swipe.
      link.addEventListener("dragstart", (event) => event.preventDefault());

      link.addEventListener("pointerdown", (event) => {
        if (event.pointerType === "mouse" && event.button !== 0) return;
        if (row.dataset.busy) return;
        startX = event.clientX;
        startY = event.clientY;
        dx = 0;
        dragging = false;
        deciding = true;
      });

      link.addEventListener("pointermove", (event) => {
        if (!deciding && !dragging) return;
        const moveX = event.clientX - startX;
        const moveY = event.clientY - startY;
        if (deciding) {
          if (Math.abs(moveX) < 8 && Math.abs(moveY) < 8) return;
          deciding = false;
          dragging = Math.abs(moveX) > Math.abs(moveY);
          if (dragging) link.setPointerCapture(event.pointerId);
        }
        if (!dragging) return;
        event.preventDefault();
        dx = clamp(moveX);
        setX(row, dx, false);
      });

      const finishDrag = (event) => {
        deciding = false;
        if (!dragging) return;
        dragging = false;
        // A drag release fires a trailing click on this same element; swallow it below.
        justDragged = true;
        const threshold = row.offsetWidth / 3;
        if (event.type === "pointerup" && dx <= -threshold) {
          runMove(row);
        } else if (event.type === "pointerup" && dx >= threshold) {
          confirmDelete(row);
        } else {
          setX(row, 0, true);
        }
      };

      link.addEventListener("pointerup", finishDrag);
      link.addEventListener("pointercancel", finishDrag);

      link.addEventListener("click", (event) => {
        if (justDragged || row.dataset.busy) {
          justDragged = false;
          event.preventDefault();
        }
      });
    });
  };

  const initReadingProgress = () => {
    const body = document.querySelector(".article-body[data-progress-action]");
    if (!body) return;
    const blocks = Array.from(body.children);
    if (blocks.length === 0) return;
    const saveUrl = body.dataset.progressAction;

    let currentIndex = -1;
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              currentIndex = blocks.indexOf(entry.target);
            }
          });
        },
        { rootMargin: "0px 0px -85% 0px" }
      );
      blocks.forEach((block) => observer.observe(block));
    }

    const sendProgress = () => {
      if (currentIndex < 0) return;
      const spots = readProgress();
      spots[location.pathname] = { index: currentIndex, at: Date.now(), unsent: !navigator.onLine };
      writeProgress(spots);
      if (!navigator.onLine) return;
      const data = new URLSearchParams({ index: String(currentIndex) });
      try {
        navigator.sendBeacon(saveUrl, data);
      } catch {
        fetch(saveUrl, { method: "POST", body: data, keepalive: true }).catch(() => {});
      }
    };

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") sendProgress();
    });
    window.addEventListener("pagehide", sendProgress);

  };

  // Put the reader back where they were: on the highlight named by the
  // #highlight-<id> in the address (set when closing a highlight), else at
  // the saved reading spot. Runs once the text is parsed and highlights are
  // drawn, not on "load", which waits for every image and leaves a slow
  // connection stuck at the top. Images arriving later push the text
  // around, so it places again once after "load", unless the reader has
  // touched the page since.
  const initRestorePosition = () => {
    const body = document.querySelector(".article-body[data-progress-action]");
    if (!body) return;
    const blocks = Array.from(body.children);

    const hashMatch = /^#highlight-([a-z0-9]+)$/.exec(location.hash);
    const highlight = hashMatch
      ? body.querySelector(`[data-highlight-id="${hashMatch[1]}"]`)
      : null;
    // The page's own spot is the server's; offline it comes from the stored
    // copy and can be older than where the reader got to on this phone.
    const mine = readProgress()[location.pathname];
    const resumeIndex =
      mine && (!navigator.onLine || mine.unsent)
        ? mine.index
        : parseInt(body.dataset.progressIndex || "", 10);
    const resumeBlock =
      Number.isInteger(resumeIndex) && resumeIndex >= 2 ? blocks[resumeIndex] : null;

    const place = highlight
      ? () => highlight.scrollIntoView({ block: "center" })
      : resumeBlock
        ? () => resumeBlock.scrollIntoView({ block: "start" })
        : null;
    if (!place) return;

    if (!highlight) {
      resumeBlock.classList.add("is-resume");
      showToast("Resumed");
    }
    place();

    let touched = false;
    ["wheel", "touchstart", "keydown", "pointerdown"].forEach((type) => {
      window.addEventListener(type, () => (touched = true), { passive: true, once: true });
    });
    const settle = () => {
      if (!touched) place();
    };
    if (document.readyState === "complete") settle();
    else window.addEventListener("load", settle, { once: true });
  };

  const initHighlights = () => {
    const body = document.querySelector(".article-body[data-highlight-action]");
    if (!body) return;
    const blocks = Array.from(body.children);
    if (blocks.length === 0) return;
    const saveUrl = body.dataset.highlightAction;

    const pointAtOffset = (block, offset) => {
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
      let pos = 0;
      let node = walker.nextNode();
      let last = null;
      while (node) {
        const len = node.textContent.length;
        if (pos + len >= offset) return { node, offset: offset - pos };
        pos += len;
        last = node;
        node = walker.nextNode();
      }
      return last ? { node: last, offset: last.textContent.length } : null;
    };

    // Wraps each text node's covered slice in its own <mark>, so a range
    // crossing element boundaries (list items, links, emphasis) never pulls
    // those elements apart or nests block elements inside an inline mark.
    const wrapBlockRange = (block, from, to) => {
      if (to <= from) return [];
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
      const slices = [];
      let pos = 0;
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const len = node.textContent.length;
        const a = Math.max(from - pos, 0);
        const b = Math.min(to - pos, len);
        // Whitespace beside a block element (between list items, table
        // cells, paragraphs in a quote) is layout, not text.
        const layoutOnly =
          !node.textContent.trim() &&
          [node.previousSibling, node.nextSibling].some(
            (el) =>
              el &&
              el.nodeType === Node.ELEMENT_NODE &&
              !getComputedStyle(el).display.startsWith("inline")
          );
        if (a < b && !layoutOnly) slices.push({ node, a, b });
        pos += len;
        if (pos >= to) break;
      }
      return slices.map(({ node, a, b }) => {
        let target = node;
        if (b < target.textContent.length) target.splitText(b);
        if (a > 0) target = target.splitText(a);
        const mark = document.createElement("mark");
        mark.className = "hl";
        target.before(mark);
        mark.appendChild(target);
        return mark;
      });
    };

    const imagesIn = (block) =>
      block.matches("img") ? [block] : Array.from(block.querySelectorAll("img"));
    const isImageOnly = (block) => !block.textContent.trim() && imagesIn(block).length > 0;

    const wrapHighlight = (
      startBlock,
      startOffset,
      endBlock,
      endOffset,
      highlightId,
      hasTitle = false,
      isKey = false
    ) => {
      const marks = [];
      for (let b = startBlock; b <= endBlock; b++) {
        const block = blocks[b];
        if (!block) continue;
        const from = b === startBlock ? startOffset : 0;
        const to = b === endBlock ? endOffset : block.textContent.length;
        marks.push(...wrapBlockRange(block, from, to));
        // Images have no text to wrap. Outline the ones the highlight
        // covers, by the same rule the server stores and exports them
        // (`images_in_block_range` in app/db.py).
        if ((b > startBlock && b < endBlock) || isImageOnly(block)) {
          imagesIn(block).forEach((img) => {
            img.classList.add("hl-image");
            if (highlightId != null) img.dataset.highlightId = String(highlightId);
          });
        }
      }
      if (highlightId != null) {
        marks.forEach((mark) => {
          mark.dataset.highlightId = String(highlightId);
        });
      }
      // A highlight carrying a section or subsection title gets a small §
      // just before it, and a key highlight a small ★ after that. The
      // elements stay empty (CSS draws the symbols) so they add no text:
      // highlights are stored as character offsets into a block.
      const addMarker = (className) => {
        const marker = document.createElement("span");
        marker.className = className;
        marker.setAttribute("aria-hidden", "true");
        if (highlightId != null) marker.dataset.highlightId = String(highlightId);
        marks[0].before(marker);
      };
      if (marks.length > 0) {
        if (hasTitle) addMarker("hl-title-marker");
        if (isKey) addMarker("hl-key-marker");
      }
      return marks;
    };

    const blockIndexOf = (node) => {
      let el = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
      while (el && el.parentElement !== body) el = el.parentElement;
      return el ? blocks.indexOf(el) : -1;
    };

    const charOffsetWithinBlock = (block, container, offsetInContainer) => {
      const range = document.createRange();
      range.selectNodeContents(block);
      range.setEnd(container, offsetInContainer);
      return range.toString().length;
    };

    const dataEl = document.getElementById("highlights-data");
    let saved = [];
    try {
      saved = dataEl ? JSON.parse(dataEl.textContent || "[]") : [];
    } catch {
      saved = [];
    }
    saved.forEach((h) => {
      wrapHighlight(h.start_block, h.start_offset, h.end_block, h.end_offset, h.id, h.has_title, h.is_key);
    });
    // Live record of what's on the page, kept in sync as saves/merges
    // happen so a second overlapping selection in the same visit (before
    // any reload) still detects correctly.
    const known = saved.map((h) => ({ ...h }));

    // Tuple-less-than for [block, offset] points, matching the server's
    // own (block, offset) comparisons.
    const pointBefore = (a, b) => a[0] < b[0] || (a[0] === b[0] && a[1] < b[1]);

    const textForSpan = (startBlock, startOffset, endBlock, endOffset) => {
      const start = pointAtOffset(blocks[startBlock], startOffset);
      const end = pointAtOffset(blocks[endBlock], endOffset);
      if (!start || !end) return "";
      const range = document.createRange();
      range.setStart(start.node, start.offset);
      range.setEnd(end.node, end.offset);
      return range.toString();
    };

    const unwrapHighlight = (highlightId) => {
      body
        .querySelectorAll(
          `.hl-title-marker[data-highlight-id="${highlightId}"],` +
            `.hl-key-marker[data-highlight-id="${highlightId}"]`
        )
        .forEach((marker) => marker.remove());
      body.querySelectorAll(`mark.hl[data-highlight-id="${highlightId}"]`).forEach((mark) => {
        const parent = mark.parentNode;
        while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
        parent.removeChild(mark);
        parent.normalize();
      });
      body.querySelectorAll(`img.hl-image[data-highlight-id="${highlightId}"]`).forEach((img) => {
        img.classList.remove("hl-image");
        delete img.dataset.highlightId;
      });
    };

    // Draw a highlight from its state (see highlightsOnPhone), replacing the
    // ones it merged, and keep `known` in step.
    const draw = (h, merged = []) => {
      merged.forEach((m) => unwrapHighlight(m.id));
      const span = [h.start_block, h.start_offset, h.end_block, h.end_offset];
      const marks = wrapHighlight(...span, h.id, h.has_title, h.is_key);
      if (h.pending) {
        marks.forEach((mark) => mark.classList.add("is-pending"));
        body
          .querySelectorAll(`img.hl-image[data-highlight-id="${h.id}"]`)
          .forEach((img) => img.classList.add("is-pending"));
      }
      const gone = new Set(merged.map((m) => m.id));
      for (let i = known.length - 1; i >= 0; i--) {
        if (gone.has(known[i].id) || known[i].id === h.id) known.splice(i, 1);
      }
      known.push({ ...h });
    };

    // Save a highlight. Without a connection, or when it merges one still
    // waiting to sync (so the two reach the server in order), it is drawn at
    // once as pending and kept in the outbox. Online, the page changes only
    // once the server confirms: a refused save leaves it exactly as it was.
    const saveHighlight = (span, text, overlapping) => {
      const [startBlock, startOffset, endBlock, endOffset] = span;
      const mergeIds = overlapping.flatMap((h) => (isPending(h.id) ? h.merge_ids : [h.id]));
      const data = new URLSearchParams({
        start_block: String(startBlock),
        start_offset: String(startOffset),
        end_block: String(endBlock),
        end_offset: String(endOffset),
        text,
      });
      mergeIds.forEach((id) => data.append("merge_id", String(id)));

      const keep = () => {
        const id = newPendingId();
        const ordered = [...overlapping].sort(byStart);
        const first = (list, field) => (list.find((h) => h[field]) || {})[field] || null;
        const state = {
          id,
          start_block: startBlock,
          start_offset: startOffset,
          end_block: endBlock,
          end_offset: endOffset,
          text,
          section_title: first(ordered, "section_title"),
          subsection_title: first(ordered, "subsection_title"),
          is_key: ordered.some((h) => h.is_key),
          merge_ids: mergeIds,
          pending: true,
        };
        state.has_title = Boolean(state.section_title || state.subsection_title);
        draw(state, overlapping);

        // The server carries titles and the key mark over only from saved
        // highlights it merges; what came from pending ones is sent as edits.
        const saved = ordered.filter((h) => !isPending(h.id));
        const edits = [];
        if (state.is_key && !saved.some((h) => h.is_key)) edits.push(["key", null]);
        ["section", "subsection"].forEach((level) => {
          const title = state[`${level}_title`];
          if (title && title !== first(saved, `${level}_title`)) {
            edits.push([`${level}-title`, title]);
          }
        });
        const replaced = new Set(overlapping.filter((h) => isPending(h.id)).map((h) => h.id));
        return outbox
          .all()
          .then((entries) =>
            Promise.all(
              entries
                .filter((e) => replaced.has(isEdit(e) ? e.highlightId : e.pendingId))
                .map((e) => outbox.remove(e.key))
            )
          )
          .then(() =>
            outbox.add({
              url: saveUrl,
              article: location.pathname,
              pendingId: id,
              body: data.toString(),
              span,
              mergeIds,
              hasTitle: state.has_title,
              isKey: state.is_key,
            })
          )
          .then(() =>
            edits.reduce(
              (done, [action, title]) =>
                done.then(() => queueEdit(location.pathname, id, action, title)),
              Promise.resolve()
            )
          )
          .then(flushOutbox)
          .catch((error) => note("outbox-failed", `keep ${id} ${error}`));
      };

      if (!navigator.onLine || overlapping.some((h) => isPending(h.id))) {
        keep();
        return;
      }
      fetch(saveUrl, { method: "POST", body: data }).then((r) => {
        if (!r.ok) return null;
        return r.json().then((result) => {
          const ordered = [...overlapping].sort(byStart);
          const first = (field) => (ordered.find((h) => h[field]) || {})[field] || null;
          draw(
            {
              id: result.id,
              start_block: startBlock,
              start_offset: startOffset,
              end_block: endBlock,
              end_offset: endOffset,
              text,
              section_title: first("section_title"),
              subsection_title: first("subsection_title"),
              has_title: result.has_title,
              is_key: result.is_key,
              pending: false,
            },
            overlapping
          );
          refreshOfflineCopy();
        });
      }, keep);
    };

    // What changed on this phone since the page was rendered (or stored):
    // highlights deleted, merged or edited offline, and pending new ones.
    pendingDrawn = outbox
      .all()
      .then((entries) => {
        const now = highlightsOnPhone(saved, entries, location.pathname);
        const byId = new Map(now.map((h) => [String(h.id), h]));
        // Only what the page opened with: a highlight made while this was
        // being read is already right, and is not in `entries` yet.
        const openedWith = new Set(saved.map((h) => String(h.id)));
        [...known]
          .filter((h) => openedWith.has(String(h.id)))
          .forEach((h) => {
            const current = byId.get(String(h.id));
            if (current && !current.pending) return;
            unwrapHighlight(h.id);
            known.splice(known.indexOf(h), 1);
            if (current) draw(current);
          });
        now
          .filter((h) => isPending(h.id) && !known.some((k) => k.id === h.id))
          .forEach((h) => draw(h));
        if (entries.length) note("outbox", `drawn ${now.filter((h) => h.pending).length} of ${entries.length}`);
      })
      .catch((error) => note("outbox-failed", `draw ${error}`));

    // Once sent, a pending highlight takes the id the server gave it.
    document.addEventListener("reader:highlight-synced", ({ detail: { entry, result } }) => {
      if (entry.article !== location.pathname) return;
      const pending = known.find((h) => h.id === entry.pendingId);
      if (!pending) return;
      // Its own edits, if any, follow in this same run.
      draw({ ...pending, id: result.id, pending: false }, [pending]);
    });
    document.addEventListener("reader:edit-synced", ({ detail: { entry, highlightId } }) => {
      if (entry.article !== location.pathname) return;
      body
        .querySelectorAll(`[data-highlight-id="${highlightId}"]`)
        .forEach((el) => el.classList.remove("is-pending"));
    });

    body.addEventListener("click", (event) => {
      const mark = event.target.closest("mark.hl, .hl-title-marker, .hl-key-marker");
      if (!mark || !mark.dataset.highlightId) return;
      location.href = `${location.pathname}/highlights/${mark.dataset.highlightId}`;
    });

    // A double-click/tap on an image highlights just that image, with no
    // text selection needed. Only an image that is its own top-level block
    // (no text alongside it) can be targeted this way - the block/offset
    // model has nothing to point at an inline image sharing a block with
    // real text. An already-highlighted image opens its highlight instead
    // of saving again, matching the click-a-mark behaviour above.
    // Sites like Substack wrap each image in a link to the full-size file;
    // following it on the first tap would leave the page before the second
    // tap can land, so an image never navigates from here.
    body.addEventListener("click", (event) => {
      if (event.target.closest("a img")) event.preventDefault();
    });

    body.addEventListener("dblclick", (event) => {
      const img = event.target.closest("img");
      if (!img || !body.contains(img)) return;
      if (img.dataset.highlightId) {
        location.href = `${location.pathname}/highlights/${img.dataset.highlightId}`;
        return;
      }
      const blockIndex = blockIndexOf(img);
      if (blockIndex < 0 || !isImageOnly(blocks[blockIndex])) return;

      saveHighlight([blockIndex, 0, blockIndex, 0], "", []);
    });

    const handleFinishedSelection = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) return;
      const range = selection.getRangeAt(0);
      if (!body.contains(range.commonAncestorContainer)) return;
      const text = range.toString();
      if (!text.trim()) return;

      let startBlock = blockIndexOf(range.startContainer);
      let endBlock = blockIndexOf(range.endContainer);
      if (startBlock < 0 || endBlock < 0) return;
      let startOffset = charOffsetWithinBlock(
        blocks[startBlock],
        range.startContainer,
        range.startOffset
      );
      let endOffset = charOffsetWithinBlock(
        blocks[endBlock],
        range.endContainer,
        range.endOffset
      );
      selection.removeAllRanges();

      // A boundary in an image-only block counts as covering its image
      // (see `images_in_block_range` in app/db.py). A browser often puts a
      // selection's end at the very start of the next block, touching an
      // image without covering it: move such a boundary onto the
      // neighbouring text so the image stays out.
      const touchesOnly = (block) =>
        isImageOnly(block) && !imagesIn(block).some((img) => range.intersectsNode(img));
      if (endBlock > startBlock && touchesOnly(blocks[endBlock])) {
        endBlock -= 1;
        endOffset = blocks[endBlock].textContent.length;
      }
      if (startBlock < endBlock && touchesOnly(blocks[startBlock])) {
        startBlock += 1;
        startOffset = 0;
      }

      const newStart = [startBlock, startOffset];
      const newEnd = [endBlock, endOffset];
      const overlapping = known.filter(
        (h) =>
          pointBefore(newStart, [h.end_block, h.end_offset]) &&
          pointBefore([h.start_block, h.start_offset], newEnd)
      );

      let unionStart = newStart;
      let unionEnd = newEnd;
      overlapping.forEach((h) => {
        const hStart = [h.start_block, h.start_offset];
        const hEnd = [h.end_block, h.end_offset];
        if (pointBefore(hStart, unionStart)) unionStart = hStart;
        if (pointBefore(unionEnd, hEnd)) unionEnd = hEnd;
      });

      const finalText = overlapping.length
        ? textForSpan(unionStart[0], unionStart[1], unionEnd[0], unionEnd[1])
        : text;
      if (!finalText.trim()) return;

      saveHighlight([...unionStart, ...unionEnd], finalText, overlapping);
    };

    // mouseup covers a fresh press-and-drag selection. On a touch device,
    // refining a selection with the system's drag handles never fires
    // mouseup on the page at all, so selectionchange (debounced until the
    // selection stops moving) is the only signal that works for both.
    body.addEventListener("mouseup", handleFinishedSelection);

    // Dragging a native selection handle slowly (aiming precisely, pausing
    // to reposition a finger) can easily pause longer than the debounce
    // below, which would finalize and mutate the DOM mid-drag — visibly
    // disrupting the OS's own handle UI and leaving only a partial
    // highlight. Tracking whether a touch is actually still down and
    // holding off until it lifts avoids finalizing while the gesture is
    // still in progress, regardless of how long a mid-drag pause lasts.
    let touchActive = false;
    let selectionTimer = null;
    document.addEventListener(
      "touchstart",
      () => {
        touchActive = true;
      },
      { passive: true }
    );
    const onTouchEnd = () => {
      touchActive = false;
      clearTimeout(selectionTimer);
      handleFinishedSelection();
    };
    document.addEventListener("touchend", onTouchEnd, { passive: true });
    document.addEventListener("touchcancel", onTouchEnd, { passive: true });

    document.addEventListener("selectionchange", () => {
      clearTimeout(selectionTimer);
      selectionTimer = setTimeout(() => {
        if (touchActive) return; // still dragging; touchend will finalize
        handleFinishedSelection();
      }, 400);
    });
  };

  // A highlight's page and its title pages. Offline, or for a highlight
  // still waiting to sync, the service worker answers with an empty copy
  // (data-offline-shell) that is filled in here from the stored article and
  // the outbox; and the buttons queue their change instead of posting it.
  const initHighlightPage = () => {
    const found = /^\/items\/(\d+)\/highlights\/([a-z0-9]+)(?:\/(section|subsection)-title)?$/.exec(
      location.pathname
    );
    if (!found) return;
    const [, itemId, highlightId, level] = found;
    const article = `/items/${itemId}`;
    const page = `${article}/highlights/${highlightId}`;
    const back = `${article}#highlight-${highlightId}`;
    const shell = Boolean(document.querySelector("[data-offline-shell]"));

    // Where every link and button leads depends only on this page's own
    // address: set at once, so a tap before the rest is filled in still lands
    // in the right place (Close used to lead Home meanwhile).
    const wire = () => {
      document.querySelector(".top-edit").href = level ? page : back;
      if (level) {
        document.querySelector('[data-highlight-form="title"]').action = `${page}/${level}-title`;
        return;
      }
      const [section, subsection] = document.querySelectorAll("a.item");
      section.href = `${page}/section-title`;
      subsection.href = `${page}/subsection-title`;
      document.querySelector('[data-highlight-form="key"]').action = `${page}/key`;
      document.querySelector('[data-highlight-form="delete"]').action = `${page}/delete`;
    };

    const fill = (h) => {
      document.querySelector("blockquote.quote").textContent = h.text || "";
      if (level) {
        // Never over what the reader already started typing.
        const input = document.getElementById("highlight-title");
        if (!input.dataset.typed) input.value = h[`${level}_title`] || "";
        return;
      }
      const keyForm = document.querySelector('[data-highlight-form="key"]');
      keyForm.action = `${page}/${h.is_key ? "unkey" : "key"}`;
      keyForm.querySelector("button").innerHTML = document.getElementById(
        h.is_key ? "key-on" : "key-off"
      ).innerHTML;
      document.getElementById("copy-highlight").dataset.copyText = h.text || "";
    };

    if (shell) {
      wire();
      const input = document.getElementById("highlight-title");
      if (input) input.addEventListener("input", () => (input.dataset.typed = "1"), { once: true });
      Promise.all([
        fetch(article, { headers: { "X-Reader-Prefetch": "1" } }).then((r) => r.text()),
        outbox.all(),
      ])
        .then(([html, entries]) => {
          const data = new DOMParser()
            .parseFromString(html, "text/html")
            .getElementById("highlights-data");
          const saved = JSON.parse((data && data.textContent) || "[]");
          const h = highlightsOnPhone(saved, entries, article).find(
            (x) => String(x.id) === highlightId
          );
          note(
            "highlight-page",
            `${highlightId} ${h ? "found" : "missing"} saved=${saved.length} outbox=${entries.length}`
          );
          if (h) fill(h);
          else location.replace(article);
        })
        .catch((error) => {
          note("highlight-page", `${highlightId} failed ${error}`);
          location.replace(article);
        });
    }

    // Forgetting a highlight that never reached the server: nothing to send.
    const forgetPending = () =>
      outbox
        .all()
        .then((entries) =>
          Promise.all(
            entries
              .filter((e) => (isEdit(e) ? e.highlightId : e.pendingId) === highlightId)
              .map((e) => outbox.remove(e.key))
          )
        );

    document.querySelectorAll("[data-highlight-form]").forEach((form) => {
      form.addEventListener("submit", (event) => {
        if (!shell && navigator.onLine && !isPending(highlightId)) return;
        event.preventDefault();
        const kind = form.dataset.highlightForm;
        let queued;
        let then = back;
        if (kind === "delete") {
          queued = isPending(highlightId)
            ? forgetPending()
            : queueEdit(article, highlightId, "delete");
          then = article;
        } else if (kind === "key") {
          const action = form.action.endsWith("/unkey") ? "unkey" : "key";
          queued = queueEdit(article, highlightId, action);
        } else {
          const title = document.getElementById("highlight-title").value.trim();
          queued = queueEdit(article, highlightId, `${level}-title`, title);
        }
        // Leave as soon as it is kept: the page we go to sends it (waiting
        // for every queued save made a tap seem to do nothing).
        queued
          .catch((error) => note("outbox-failed", `${kind} ${highlightId} ${error}`))
          .finally(() => (location.href = then));
      });
    });
  };

  const initHighlightDetail = () => {
    const button = document.getElementById("copy-highlight");
    if (!button) return;
    button.addEventListener("click", () => {
      const text = button.dataset.copyText || "";
      navigator.clipboard?.writeText(text)
        .then(() => showToast("Copied"))
        .catch(() => {});
    });
  };

  const showToast = (text) => {
    const el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    el.textContent = text;
    document.body.appendChild(el);
    setTimeout(() => el.classList.add("is-hidden"), 5000);
    setTimeout(() => el.remove(), 5600);
  };

  const toast = document.querySelector(".toast");
  if (toast) {
    if (window.history && window.history.replaceState) {
      const url = new URL(location.href);
      if (url.searchParams.has("flash")) {
        url.searchParams.delete("flash");
        window.history.replaceState({}, "", url);
      }
    }
    setTimeout(() => toast.classList.add("is-hidden"), 5000);
  }

  initThemeToggle();
  initSwipe();
  initReadingProgress();
  initHighlights();
  initRestorePosition();
  initHighlightPage();
  initHighlightDetail();
  registerWorker();
  initOutbox();
  precacheReadLater();
  syncHome();
})();
