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

  // Signed out (revoked, or the password changed). Nothing is lost: what
  // waits in the outbox stays there, and is sent once signed in again.
  const goToLogin = () => {
    if (location.pathname === "/login") return;
    location.assign(`/login?next=${encodeURIComponent(location.pathname + location.search)}`);
  };

  // A reply that means "stop sending, try again later": the server failing,
  // or no longer letting this phone in.
  const holdsBack = (response) => {
    if (response.status === 401) {
      goToLogin();
      return true;
    }
    return response.status >= 500;
  };

  const registerWorker = async () => {
    if (!("serviceWorker" in navigator)) return;
    try {
      await navigator.serviceWorker.register("/sw.js");
    } catch {
      /* offline cache is best-effort */
    }
  };

  // The Settings cog on Home turns inside two thin arrows while the app
  // brings itself up to date on opening; it stops once that is done.
  const busy = { downloading: false };
  const showBusy = () => {
    const status = document.getElementById("sync-status");
    if (!status) return;
    const on = busy.downloading;
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

  // Articles with something still to send (a highlight, a move, an opening,
  // a reading spot): the worker must not clear their stored copy out.
  const itemsWaiting = () => {
    const ids = new Set();
    const idIn = (path) => (/^\/items\/(\d+)/.exec(path || "") || [])[1];
    outbox.now().forEach((entry) => {
      const id = entry.item != null ? String(entry.item) : idIn(entry.article);
      if (id) ids.add(id);
    });
    Object.entries(readProgress()).forEach(([path, spot]) => {
      if (spot.unsent && idIn(path)) ids.add(idIn(path));
    });
    return [...ids];
  };

  // Each time the app is opened (launched, or come back to), ask the service
  // worker to bring everything up to date: sync the sources, fetch the
  // stored pages again and download Read Later ahead. In between, pages open
  // from what it stored. Moving from page to page is not opening the app.
  // Asking again when a new worker takes over (the one that got the first
  // ask may be the older worker it replaced), and on getting the network
  // back, so a run cut short gets finished. The worker spaces out the runs.
  const OPENED_FLAG = "reader-synced";
  const updateOnOpen = async () => {
    if (!("serviceWorker" in navigator)) return;
    const ask = () => {
      if (!navigator.onLine) return;
      const worker = navigator.serviceWorker.controller;
      if (worker) worker.postMessage({ type: "precache", keep: itemsWaiting() });
    };
    navigator.serviceWorker.addEventListener("message", (event) => {
      if (!event.data) return;
      if (event.data.type === "downloading") setDownloading(event.data.running);
      if (event.data.type === "signed-out") goToLogin();
      // Home shows what the sync brought in, now stored.
      if (event.data.type === "refreshed" && event.data.arrived && location.pathname === "/") {
        location.reload();
      }
    });
    navigator.serviceWorker.addEventListener("controllerchange", ask);
    window.addEventListener("online", ask);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") ask();
    });
    if (sessionStorage.getItem(OPENED_FLAG) === "1") return;
    sessionStorage.setItem(OPENED_FLAG, "1");
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
      // Straight away, for the pages that apply what waits as they open.
      now: () => {
        try {
          return read();
        } catch {
          return [];
        }
      },
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

  // Archiving, moving back to Library, marking read or unread and saving to
  // Read later work without a connection. Each is a "move" in the outbox,
  // sent in order with the highlights; meanwhile the stored pages show it
  // done (applyMoves), and it goes on showing after a reload.
  const MOVE_GIVE_UP_MS = 15 * 1000;
  // Where the item lands: the tab of its list, by name.
  const MOVE_TO = { archive: "archive", unarchive: "library", later: "library", read: "read", unread: "unread" };
  const MOVE_FLASH = {
    archive: "Archived",
    unarchive: "Moved to Library",
    later: "Saved to Read later",
    read: "Read",
    unread: "Unread",
  };
  // Moves the server answered with an error, by outbox key: a tap that just
  // got one is a failed save, not one waiting for a connection.
  const refused = new Map();
  const secondTab = (list) => (list === "later" ? "archive" : "read");
  const firstTab = (list) => (list === "later" ? "library" : "unread");
  // Every stored page that shows the item: Home, the lists, both tabs.
  const pagesAround = (list) => ["/", "/lists", `/lists/${list}`, `/lists/${list}?view=${secondTab(list)}`];

  // What a row offers once it has moved: its swipe, and the tab it is on.
  const AFTER_MOVE = {
    read: (id, list) => ({ swipe: `/items/${id}/unread?from_list=${list}`, label: "Mark as unread", view: "read" }),
    unread: (id, list) => ({ swipe: `/items/${id}/read?from_list=${list}`, label: "Mark as read", view: "" }),
    archive: (id) => ({ swipe: `/items/${id}/unarchive`, label: "Move to Library", view: "archive" }),
    library: (id) => ({ swipe: `/items/${id}/archive?from_list=later`, label: "Archive", view: "" }),
  };

  // The row as it reads on the tab the item moves to, made from the one just
  // swiped: the same row with its link and swipes pointing the other way.
  const rowAfterMove = (row, list, to) => {
    const id = row.dataset.itemId;
    const next = AFTER_MOVE[to](id, list);
    const copy = row.cloneNode(true);
    copy.classList.remove("is-leaving", "is-more", "is-swiping-left", "is-swiping-right");
    ["hidden", "style", "data-busy"].forEach((name) => copy.removeAttribute(name));
    const link = copy.querySelector("a.item");
    ["style", "hidden"].forEach((name) => link.removeAttribute(name));
    link.classList.remove("is-more");
    const view = next.view ? `&view=${next.view}` : "";
    link.setAttribute("href", `/items/${id}?from_list=${list}${view}`);
    copy.dataset.swipeAction = next.swipe;
    copy.dataset.deleteAction = `/items/${id}/delete?from_list=${list}${view}`;
    const label = copy.querySelector(".swipe-move");
    if (label) label.textContent = next.label;
    return copy.outerHTML;
  };

  // Done at once and sent when it can be: queued behind whatever already waits
  // (a highlight must reach the server before the archive that exports it).
  // Resolves "sent" or "queued". Waits for this move only, not for the pages
  // refreshed after it.
  const sendMove = async (move) => {
    const key = await outbox.add({ kind: "move", body: "", at: Date.now(), ...move });
    const gone = () => !outbox.now().some((entry) => entry.key === key);
    return new Promise((resolve, reject) => {
      const check = () => {
        if (!gone()) return;
        document.removeEventListener("reader:outbox-changed", check);
        resolve("sent");
      };
      const giveUp = () => {
        document.removeEventListener("reader:outbox-changed", check);
        if (gone()) return resolve("sent");
        if (!refused.has(key)) return resolve("queued");
        outbox.remove(key).then(() => reject(new Error(`status ${refused.get(key)}`)));
      };
      document.addEventListener("reader:outbox-changed", check);
      const run = flushOutbox();
      if (!run) return giveUp();
      run.then(() => {
        // A run already going may have started before this was added.
        const again = !gone() && !refused.has(key) && navigator.onLine ? flushOutbox() : null;
        if (again) again.then(giveUp);
        else giveUp();
      });
    });
  };

  const queuedFlash = (action) => `${MOVE_FLASH[action]} · will sync`;

  // The moves still waiting, one per item and list: the last said wins, so
  // read and then unread leaves it unread.
  const waitingMoves = () => {
    const latest = new Map();
    outbox
      .now()
      .filter((entry) => entry.kind === "move")
      .forEach((entry) => latest.set(`${entry.item} ${entry.list}`, entry));
    return [...latest.values()];
  };

  // How many more items each list's first tab holds than the stored pages say,
  // from the first and last thing done to each item still waiting.
  const unreadChanges = () => {
    const byItem = new Map();
    outbox
      .now()
      .filter((entry) => entry.kind === "move")
      .forEach((entry) => {
        const key = `${entry.item} ${entry.list}`;
        byItem.set(key, [...(byItem.get(key) || []), entry]);
      });
    const changes = {};
    byItem.forEach((moves) => {
      const [first, last] = [moves[0], moves[moves.length - 1]];
      const was = first.action === "read" || first.action === "archive" ? 1 : 0;
      const now = last.to === firstTab(last.list) ? 1 : 0;
      changes[last.list] = (changes[last.list] || 0) + now - was;
    });
    return changes;
  };

  // A row that left the tab on show, or arrived on it, moves the counts in
  // the tab labels; `arrived` is 1 or -1.
  const shiftTabCounts = (arrived) => {
    document.querySelectorAll(".actions a").forEach((tab) => {
      const delta = tab.classList.contains("is-active") ? arrived : -arrived;
      tab.textContent = tab.textContent.replace(/\((\d+)\)/, (_, n) => `(${Math.max(0, Number(n) + delta)})`);
    });
  };

  // Make the page show the moves still waiting. Safe to run on a page that
  // already shows them: a row not there is not taken away, one there is not added.
  const applyMoves = () => {
    const moves = waitingMoves();
    const found = /^\/lists\/([^/]+)$/.exec(location.pathname);
    if (found && moves.length) {
      const list = found[1];
      const view = new URLSearchParams(location.search).get("view");
      const tab = view === secondTab(list) ? view : firstTab(list);
      const section = document.querySelector("section.list");
      if (section) {
        moves
          .filter((move) => move.list === list)
          .forEach((move) => {
            const row = section.querySelector(`.item-swipe[data-item-id="${move.item}"]`);
            if (move.to !== tab) {
              if (!row) return;
              row.remove();
              shiftTabCounts(-1);
            } else if (!row && move.row) {
              section.insertAdjacentHTML("afterbegin", move.row);
              shiftTabCounts(1);
            }
          });
      }
    }
    // Home shows only what is unread, so a moved item only ever leaves it.
    document.querySelectorAll("section[data-list]").forEach((section) => {
      const list = section.dataset.list;
      let left = 0;
      moves
        .filter((move) => move.list === list && move.to !== firstTab(list))
        .forEach((move) => {
          const row = section.querySelector(`.item-swipe[data-item-id="${move.item}"]`);
          if (!row) return;
          row.remove();
          left++;
        });
      const count = section.querySelector(".count");
      if (!left || !count) return;
      count.textContent = String(Math.max(0, Number(count.textContent) - left));
      if (count.textContent === "0") section.remove();
      else layoutHomeList(section);
    });
    // The Lists page counts what is unread (in the Library, for Read later).
    if (location.pathname === "/lists") {
      Object.entries(unreadChanges()).forEach(([list, change]) => {
        const count = document.querySelector(`a.list-row[href="/lists/${list}"] .count`);
        if (count && change) count.textContent = String(Math.max(0, Number(count.textContent) + change));
      });
    }
    // Opened offline, or since the stored page was made: dimmed like any
    // opened title.
    const seen = new Set([
      ...outbox.now().filter((entry) => entry.kind === "seen").map((entry) => String(entry.item)),
      ...openedHere(),
    ]);
    if (seen.size) {
      document.querySelectorAll("a.item[data-item-id]").forEach((link) => {
        if (seen.has(link.dataset.itemId)) link.classList.add("is-seen");
      });
    }
  };

  // Articles opened on this phone, newest last: the stored lists may be
  // older than the opening, so they dim them here.
  const OPENED_KEY = "reader-opened";
  const openedHere = () => {
    try {
      return JSON.parse(localStorage.getItem(OPENED_KEY) || "[]");
    } catch {
      return [];
    }
  };

  // An article opened without a connection is not marked opened on the
  // server; it is told once the connection returns.
  const initSeen = () => {
    const found = /^\/items\/(\d+)$/.exec(location.pathname);
    if (!found) return;
    try {
      const opened = openedHere().filter((id) => id !== found[1]);
      localStorage.setItem(OPENED_KEY, JSON.stringify([...opened, found[1]].slice(-500)));
    } catch {
      /* best-effort */
    }
    if (navigator.onLine) return;
    const item = Number(found[1]);
    if (outbox.now().some((entry) => entry.kind === "seen" && entry.item === item)) return;
    outbox.add({ kind: "seen", item, url: `/items/${item}` }).catch(() => {});
  };

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
        // Opened offline: the server learns it by being asked for the page.
        if (entry.kind === "seen") {
          try {
            const response = await fetch(entry.url);
            if (holdsBack(response)) return;
          } catch {
            return;
          }
          await outbox.remove(entry.key);
          continue;
        }
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
        // A connection that hangs must not hold up the taps waiting on it.
        const controller = new AbortController();
        const timer = entry.kind === "move" ? setTimeout(() => controller.abort(), MOVE_GIVE_UP_MS) : 0;
        try {
          // The edit and move routes answer with a redirect: that is
          // success, and nothing else needs to load.
          response = await fetch(url, {
            method: "POST",
            body: new URLSearchParams(entry.body),
            redirect: "manual",
            signal: controller.signal,
          });
        } catch {
          return;
        } finally {
          clearTimeout(timer);
        }
        if (holdsBack(response)) {
          if (entry.kind === "move" && response.status !== 401) {
            refused.set(entry.key, response.status);
          }
          return;
        }
        if (response.ok || response.type === "opaqueredirect") {
          if (entry.kind === "move") {
            // The pages that showed the item where it was are out of date.
            pagesAround(entry.list).forEach((path) => markStale(path, true));
          } else if (isEdit(entry)) {
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
          if (entry.kind !== "move") markStale(entry.article, true);
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
        if (holdsBack(response)) return;
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
      .then((entries) => entries.filter((entry) => entry.kind !== "seen").length + spots)
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
      if (response.status === 401) goToLogin();
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

    const failed = (row, message = "Couldn't save") => {
      setX(row, 0, true);
      delete row.dataset.busy;
      showToast(message);
    };

    // What the swipe does, written down before the row starts to slide.
    const swipeMove = (row) => {
      const url = row.dataset.swipeAction;
      const action = new URL(url, location.origin).pathname.split("/").pop();
      const list = row.dataset.listSlug;
      const to = MOVE_TO[action];
      return { item: Number(row.dataset.itemId), list, action, to, url, row: rowAfterMove(row, list, to) };
    };

    const runMove = async (row) => {
      row.dataset.busy = "1";
      const move = swipeMove(row);
      setX(row, -row.offsetWidth, true);
      let outcome;
      try {
        outcome = await sendMove(move);
      } catch {
        failed(row);
        return;
      }
      if (outcome === "queued") showToast(queuedFlash(move.action));
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
        } catch (error) {
          // Deleting is the one thing not kept for later: it cannot be undone.
          failed(row, error instanceof TypeError ? "Delete needs a connection" : undefined);
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

  // The article's Read later, Archive and Mark as read buttons. Pressed
  // offline they are kept and the page moves on as if they had been sent.
  const initItemActions = () => {
    const bind = (form, spec) => {
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = form.querySelector("button");
        if (button) button.disabled = true;
        const template = document.getElementById(spec.row);
        let outcome;
        try {
          outcome = await sendMove({
            item: spec.item,
            list: spec.list,
            action: spec.action,
            to: MOVE_TO[spec.action],
            url: spec.url,
            row: template ? template.innerHTML.trim() : "",
          });
        } catch {
          if (button) button.disabled = false;
          showToast("Couldn't save");
          return;
        }
        if (outcome === "queued" && spec.action === "later") {
          // Stay on the article: it now says it is saved.
          showSaved(form, spec);
          if (button) button.disabled = false;
          showToast(queuedFlash("later"));
          return;
        }
        const next = new URL(spec.then, location.origin);
        if (outcome === "queued") next.searchParams.set("flash", queuedFlash(spec.action));
        location.assign(next.pathname + next.search);
      });
    };

    // Read later pressed: the button says so and Archive appears.
    const showSaved = (form, spec) => {
      const button = form.querySelector("button");
      button.textContent = "Saved to Read later";
      button.classList.add("is-active");
      if (!spec.archive || document.querySelector(".act-archive")) return;
      const archive = document.createElement("form");
      archive.method = "post";
      archive.action = spec.archive.url;
      archive.innerHTML = '<button type="submit" class="act-archive">Archive</button>';
      form.after(archive);
      bind(archive, spec.archive);
    };

    const waiting = waitingMoves();
    document.querySelectorAll("form[data-move]").forEach((form) => {
      const spec = JSON.parse(form.dataset.move);
      bind(form, spec);
      if (spec.action === "later" && waiting.some((m) => m.item === spec.item && m.list === "later")) {
        showSaved(form, spec);
      }
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
    // The page's own spot is the server's as it stood when the page was
    // made; a stored copy can be older than where the reader got to on
    // this phone.
    const mine = readProgress()[location.pathname];
    const renderedAt = Number(body.dataset.renderedAt) || 0;
    const resumeIndex =
      mine && (!navigator.onLine || mine.unsent || mine.at > renderedAt)
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
        // Signed out: keep the highlight like one made offline, and sign in.
        if (r.status === 401) {
          keep();
          return null;
        }
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
  const flash = new URL(location.href).searchParams.get("flash");
  // A page the phone had stored carries no banner of its own: show the one
  // in its address.
  if (flash && !toast) showToast(flash);
  if (toast || flash) {
    if (window.history && window.history.replaceState) {
      const url = new URL(location.href);
      if (url.searchParams.has("flash")) {
        url.searchParams.delete("flash");
        window.history.replaceState({}, "", url);
      }
    }
  }
  if (toast) setTimeout(() => toast.classList.add("is-hidden"), 5000);

  // Anything else a form sends needs the server. Offline, say so rather than
  // let the browser fail; forms that handle offline themselves have already
  // called preventDefault by now.
  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (event.defaultPrevented || navigator.onLine) return;
    if (!(form instanceof HTMLFormElement) || form.method !== "post") return;
    event.preventDefault();
    showToast("This needs a connection");
  });

  initThemeToggle();
  applyMoves();
  initSwipe();
  initItemActions();
  initSeen();
  initReadingProgress();
  initHighlights();
  initRestorePosition();
  initHighlightPage();
  initHighlightDetail();
  registerWorker();
  initOutbox();
  updateOnOpen();
})();
