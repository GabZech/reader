// Never rename: a new name makes activate delete the old cache, and with it
// every page the reader had stored for offline.
const CACHE = "reader-shell-v4";
// Images from other sites in Read Later articles, downloaded ahead (see
// precache) and pruned to what Read Later still holds.
const IMAGES = "reader-images-v1";
// The fonts, stylesheet and script every page uses: answered from the phone
// and fetched again with each download run, like the pages.
const SHELL = [
  "/static/styles.css",
  "/static/app.js",
  "/static/fonts/fraunces-normal.woff2",
  "/static/fonts/fraunces-italic.woff2",
  "/static/fonts/literata-normal.woff2",
  "/static/fonts/literata-italic.woff2",
  "/static/fonts/figtree-normal.woff2",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(["/", "/lists", "/sources", ...SHELL]))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE && key !== IMAGES).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
  // Download straight away, since the page that asked was still controlled by
  // the worker this one replaces, which ignored the ask. Not inside waitUntil:
  // pages wait for activation to finish, and would wait on every download.
  precache().catch(() => {});
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET") {
    // A reading spot or a breadcrumb changes no page, and may be sent as the
    // page goes away: left to the browser.
    if (url.origin !== location.origin || !changesPages(url.pathname)) return;
    event.respondWith(send(request));
    return;
  }
  if (url.origin !== location.origin) {
    if (request.destination === "image") event.respondWith(answerImage(request));
    return;
  }

  event.respondWith(answer(request, event));
});

const changesPages = (path) => !/\/progress$/.test(path) && path !== "/diag";

// A form or a tap that saves something. Once the server has taken it, the
// stored pages it may touch are out of date (noteChange). When the
// connection is found dead only now (a weak signal), a form says so,
// instead of the browser's own error (a blank screen in the installed app).
async function send(request) {
  const path = new URL(request.url).pathname;
  let response;
  try {
    response = await fetch(request);
  } catch (error) {
    if (request.mode === "navigate") return needsConnectionPage();
    throw error;
  }
  // The form routes answer with a redirect, which a page only sees opaque.
  if (response.ok || response.type === "opaqueredirect" || response.status === 303) {
    await noteChange(path);
  }
  return response;
}

// When this phone last changed something, for every page and per article:
// a stored copy older than that is out of date, and its next visit fetches
// it fresh. Kept in the cache, since the worker can be stopped at any time.
const CHANGES_KEY = new URL("/sw-state/changes", location.origin).href;
// An article's own page, and its highlights' pages under it.
const ITEM_SCOPE = /^\/items\/(\d+)(?:\/|$)/;
let changes = null;
let changesSaved = Promise.resolve();

async function readChanges() {
  if (!changes) {
    const stored = await caches.match(CHANGES_KEY, { cacheName: CACHE }).catch(() => null);
    changes = (stored && (await stored.json().catch(() => null))) || { all: 0, items: {} };
  }
  return changes;
}

function noteChange(path) {
  changesSaved = changesSaved
    .then(async () => {
      const now = Date.now();
      const state = await readChanges();
      const item = ITEM_SCOPE.exec(path);
      if (item) state.items[item[1]] = now;
      // A highlight shows only on its article; anything else may show on
      // Home, the lists and the sources.
      if (!/\/highlights(\/|$)/.test(path)) state.all = now;
      const newest = Object.entries(state.items).sort((a, b) => b[1] - a[1]).slice(0, 300);
      state.items = Object.fromEntries(newest);
      const cache = await caches.open(CACHE);
      await cache.put(CHANGES_KEY, new Response(JSON.stringify(state)));
    })
    .catch(() => {});
  return changesSaved;
}

async function upToDate(stored, path) {
  const state = await readChanges();
  const at = Number(stored.headers.get("X-Stored-At")) || 0;
  const item = ITEM_SCOPE.exec(path);
  return at >= (item ? state.items[item[1]] || 0 : state.all);
}

// Keep a page, marked with when it was asked for: a change made after that
// is not in it.
async function store(cache, key, response, askedAt, version = null) {
  const headers = new Headers(response.headers);
  headers.set("X-Stored-At", String(askedAt));
  if (version) headers.set("X-Article-Version", version);
  const body = await response.blob();
  await cache.put(
    key,
    new Response(body, { status: response.status, statusText: response.statusText, headers })
  );
}

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "precache") {
    event.waitUntil(precache(event.data.keep || null));
  }
});

// One stored copy per page whatever banner an action sent the reader back
// with (?flash=Archived): offline, that address finds the stored page
// without it. An article has a copy per way in (from Home, a list, a
// source), since its Close and buttons differ; offline any of them will do.
function cacheKey(request) {
  const url = new URL(request.url);
  url.searchParams.delete("flash");
  return url.href;
}

const ARTICLE = /^\/items\/\d+$/;

// The newest stored copy of an article, whichever way in it was kept for.
async function anyCopy(url) {
  const copies = await (await caches.open(CACHE)).matchAll(url, { ignoreSearch: true });
  const at = (copy) => Number(copy.headers.get("X-Stored-At")) || 0;
  return copies.sort((a, b) => at(b) - at(a))[0];
}

// A highlight's page, or its section or subsection title page.
const HIGHLIGHT_PAGE = /^\/items\/\d+\/highlights\/([^/]+)(?:\/(section|subsection)-title)?$/;

// The empty copy of a highlight page that app.js fills in on the phone (see
// OFFLINE_SHELLS in app/main.py), when the page itself cannot be had.
function highlightShell(request) {
  if (request.mode !== "navigate") return null;
  const found = HIGHLIGHT_PAGE.exec(new URL(request.url).pathname);
  if (!found) return null;
  const path = found[2] ? `/offline/highlight-title/${found[2]}` : "/offline/highlight";
  return { pending: found[1].startsWith("p"), path };
}

// Another site's image: the downloaded copy if there is one, so an article
// reads the same offline, else the network as before.
async function answerImage(request) {
  const cached = await caches.match(request, { cacheName: IMAGES });
  return cached || fetch(request);
}

let precaching = null;
let precachedAt = 0;
// Pages ask each time the app is opened; switching away and straight back
// needs no second run.
const PRECACHE_GAP_MS = 10 * 1000;
// A few downloads at once: one at a time took longer than an iPhone keeps
// the worker running.
const DOWNLOADS_AT_ONCE = 4;

// What happens each time the app opens: bring in what is new from the
// sources, then fetch every stored page again, then download every Read
// Later article not stored yet or changed since, and its images, so a saved
// article opens offline without having been opened first. Between runs,
// pages answer from what this stored. Open pages hear when a run starts and
// ends, to turn Home's cog meanwhile.
// `keep` names the articles with saves still waiting on the phone, which
// the worker cannot see; without it, nothing is cleared out.
function precache(keep = null) {
  if (precaching) {
    announce(true);
    return precaching;
  }
  // Nothing to do: say so, which also stops a cog still turning because a
  // "done" went astray.
  if (Date.now() - precachedAt < PRECACHE_GAP_MS) {
    announce(false);
    return Promise.resolve();
  }
  announce(true);
  precaching = updateEverything(keep).finally(() => {
    precaching = null;
    precachedAt = Date.now();
    announce(false);
  });
  return precaching;
}

// Every open page, not only those this worker controls: during an update the
// page passes to the new worker while this one is still downloading.
function announce(running) {
  tell("downloading", null, { running });
}

async function eachAtOnce(things, work) {
  const queue = [...things];
  const worker = async () => {
    while (queue.length) {
      try {
        await work(queue.shift());
      } catch {
        /* the next run tries again */
      }
    }
  };
  await Promise.all(Array.from({ length: DOWNLOADS_AT_ONCE }, worker));
}

// How many items the sources brought in, or null when the sync failed.
async function syncSources() {
  try {
    const response = await fetch("/sync", { method: "POST" });
    if (!response.ok) throw new Error(`status ${response.status}`);
    const result = await response.json();
    return (result.created || 0) + ((result.mail && result.mail.created) || 0);
  } catch (error) {
    tell("sw-sync", `failed ${error}`);
    return null;
  }
}

async function updateEverything(keep) {
  const arrived = await syncSources();
  let listed;
  let lists;
  try {
    const response = await fetch("/offline/articles", { cache: "no-store" });
    if (!response.ok) throw new Error(`status ${response.status}`);
    ({ articles: listed, pages: lists } = await response.json());
  } catch (error) {
    tell("sw-precache", `failed ${error}`);
    return;
  }
  // A start with no matching end in Diagnostics means the run was cut short.
  tell("sw-precache", `start ${listed.length} articles`);
  const pages = await caches.open(CACHE);
  const images = await caches.open(IMAGES);
  let pagesAdded = 0;
  let imagesAdded = 0;

  // Home and the lists first: they are what the reader sees on opening.
  // The one from last time is kept when fetching fails.
  await eachAtOnce([...lists, ...SHELL], async (path) => {
    const askedAt = Date.now();
    const response = await fetch(path, { cache: "no-store" });
    if (response.ok) await store(pages, new URL(path, location.origin).href, response, askedAt);
  });
  // Home shows what the sync brought in once its new copy is stored.
  tell("refreshed", null, { arrived });

  // Each article for each way in to it (from the Read later list and from
  // Home), when not stored yet or changed since (a highlight, a reading
  // spot): the listing says which version each is at.
  const ways = listed.flatMap((article) =>
    article.urls.map((path) => ({ path, version: article.version }))
  );
  const downloaded = await readDownloaded();
  await eachAtOnce(ways, async ({ path, version }) => {
    const key = new URL(path, location.origin).href;
    const stored = await pages.match(key);
    if (stored && stored.headers.get("X-Article-Version") === version) {
      downloaded[key] = true;
      return;
    }
    const askedAt = Date.now();
    const response = await fetch(path, { headers: { "X-Reader-Prefetch": "1" } });
    if (response.ok) {
      await store(pages, key, response, askedAt, version);
      downloaded[key] = true;
      pagesAdded++;
    }
  });
  const removed = await clearOut(pages, downloaded, ways, keep);

  const wanted = new Set(
    listed.flatMap((article) => article.images.map((src) => new URL(src, location.origin).href))
  );
  await eachAtOnce(wanted, async (src) => {
    if (await images.match(src)) return;
    // Other sites rarely allow reading their images, so take them opaque:
    // enough for an <img> to show.
    const response = await fetch(src, { mode: "no-cors" });
    if (response.ok || response.type === "opaque") {
      await images.put(src, response);
      imagesAdded++;
    }
  });
  for (const request of await images.keys()) {
    if (!wanted.has(request.url)) await images.delete(request);
  }
  tell(
    "sw-precache",
    `pages+${pagesAdded} -${removed} images+${imagesAdded} of ${listed.length}/${wanted.size}`
  );
}

// The article copies this download stored, by address: only these are ever
// cleared out, never one the reader opened themselves.
const DOWNLOADED_KEY = new URL("/sw-state/downloaded", location.origin).href;

async function readDownloaded() {
  const stored = await caches.match(DOWNLOADED_KEY, { cacheName: CACHE }).catch(() => null);
  return (stored && (await stored.json().catch(() => null))) || {};
}

// A downloaded article no longer wanted (read, archived, gone from its list,
// or its list switched off) leaves the phone, unless a save for it still
// waits to be sent: a highlight is never lost with it. Only after a listing
// fetched from the server just now, so only online.
async function clearOut(pages, downloaded, ways, keep) {
  const wanted = new Set(ways.map(({ path }) => new URL(path, location.origin).href));
  const waiting = new Set((keep || []).map(String));
  let removed = 0;
  for (const key of Object.keys(downloaded)) {
    if (wanted.has(key)) continue;
    const item = ITEM_SCOPE.exec(new URL(key).pathname);
    if (!keep || (item && waiting.has(item[1]))) continue;
    await pages.delete(key);
    delete downloaded[key];
    removed++;
  }
  await pages.put(DOWNLOADED_KEY, new Response(JSON.stringify(downloaded)));
  return removed;
}

async function refetch(address) {
  const askedAt = Date.now();
  const response = await fetch(address);
  if (response.ok) await store(await caches.open(CACHE), cacheKey(new Request(address)), response, askedAt);
}

const BOOTED = Date.now();
let pagesServed = 0;

// Tell every open page what happened, so it lands in the phone's breadcrumb log
// (see base.html); the worker itself has nowhere to keep one. With a `type`
// other than "log" (and no breadcrumb), it is news for app.js instead.
function tell(e, d, news = null) {
  const message = news ? { type: e, ...news } : { type: "log", e, d };
  self.clients
    .matchAll({ includeUncontrolled: true })
    .then((pages) => pages.forEach((page) => page.postMessage(message)))
    .catch(() => {});
}

// Pages that are only ever fetched fresh: those that only make sense with
// the server, a page with a banner (it carries the banner in its markup),
// and a highlight's page (offline it is built on the phone instead).
function onlyFresh(url) {
  return NEEDS_SERVER.test(url.pathname) || url.searchParams.has("flash") || HIGHLIGHT_PAGE.test(url.pathname);
}

// A page, or the stylesheet, script and fonts, answer from the phone when
// it has an up-to-date copy, online too: stored pages are fetched again
// each time the app opens (precache), and a change made from this phone
// puts the copies it touches out of date (noteChange). Anything else goes
// to the network first, then the copy from the last visit. A page that is
// neither reachable nor stored gets a retry page: answering with nothing
// shows as a blank white screen in an installed iPhone app, with no way out.
async function answer(request, event) {
  const started = Date.now();
  const page = request.mode === "navigate";
  const where = new URL(request.url).pathname;
  const note = (what) => {
    if (!page) return;
    const up = Math.round((Date.now() - BOOTED) / 1000);
    tell("sw-nav", `${where} ${what} ${Date.now() - started}ms #${++pagesServed} up=${up}s`);
  };
  // A highlight still waiting to sync has no page on the server yet.
  const shell = highlightShell(request);
  if (shell && shell.pending) {
    const filled = await caches.match(new URL(shell.path, location.origin).href);
    if (filled) {
      note("shell");
      return filled;
    }
  }
  const url = new URL(request.url);
  const shellFile = SHELL.includes(url.pathname) && !url.search;
  if ((page && !onlyFresh(url)) || shellFile) {
    const stored = await caches.match(cacheKey(request), { cacheName: CACHE });
    if (stored && (shellFile || (await upToDate(stored, url.pathname)))) {
      note("stored");
      // Asking for an article is how the server learns it was opened; the
      // answer refreshes the copy for next time.
      if (ARTICLE.test(url.pathname)) event.waitUntil(refetch(request.url).catch(() => {}));
      return stored;
    }
  }
  const askedAt = Date.now();
  try {
    const response = await fetch(request);
    // A page with a banner carries it in its markup: only the plain page is kept.
    if (response.ok && !url.searchParams.has("flash")) {
      const copy = response.clone();
      caches
        .open(CACHE)
        .then((cache) => store(cache, cacheKey(request), copy, askedAt))
        .catch(() => {});
    }
    note(`net ${response.status}`);
    return response;
  } catch (error) {
    // Offline a highlight's page is always built on the phone: a copy kept
    // from an earlier visit would miss edits made since.
    const filled = shell && (await caches.match(new URL(shell.path, location.origin).href));
    if (filled) {
      note(`shell after ${error}`);
      return filled;
    }
    // An article's newest copy, whichever way in it was stored for: one
    // fetched again after a highlight carries it, the others may not.
    const cached = ARTICLE.test(url.pathname)
      ? await anyCopy(request.url)
      : await caches.match(cacheKey(request));
    if (cached) {
      note(`cache after ${error}`);
      return cached;
    }
    note(`retry-page after ${error}`);
    if (page) return unavailablePage(request.url);
    return Response.error();
  }
}

// Pages that only make sense with the server (adding things, Diagnostics):
// never stored, so offline they say what they need.
const NEEDS_SERVER =
  /^\/(lists\/add|home\/edit|diagnostics|sources\/add(\/.*)?|sources\/added\/[^/]+|sources\/[^/]+\/(list|window|new-list))$/;

// What a page that cannot load says: an article not downloaded, a page that
// needs the server, or (for anything else) just to try again.
function unavailablePage(url) {
  const path = new URL(url).pathname;
  if (/^\/items\/\d+$/.test(path)) {
    return messagePage(
      "This article isn't saved for offline",
      "It opens once you are back online. Read later articles are always kept."
    );
  }
  if (NEEDS_SERVER.test(path)) return needsConnectionPage();
  return retryPage(url);
}

function needsConnectionPage() {
  return messagePage("This needs a connection", "It will work again once you are back online.");
}

// A short screen with a way back, in the app's colours, like retryPage.
function messagePage(title, text) {
  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Reader</title>
<style>
  body { margin: 0; min-height: 100dvh; display: grid; place-items: center; padding: 1.5rem; box-sizing: border-box;
    background: #17120e; color: #f5ead9; font: 1rem/1.4 system-ui, sans-serif; text-align: center; }
  h1 { margin: 0 0 0.6rem; font-size: 1.1875rem; font-weight: 600; }
  p { margin: 0 auto 1.4rem; max-width: 20rem; color: #bfae96; }
  a { display: inline-block; padding: 0.7rem 1.4rem; border-radius: 999px; background: #f5a524; color: #17120e;
    font-weight: 650; text-decoration: none; }
</style></head>
<body><main><h1>${title}</h1><p>${text}</p>
<a href="/" onclick="if (history.length > 1) { history.back(); return false; }">Go back</a></main></body></html>`;
  return new Response(html, {
    status: 503,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

function retryPage(url) {
  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Reader</title>
<style>
  body { margin: 0; min-height: 100dvh; display: grid; place-items: center; padding: 1.5rem; box-sizing: border-box;
    background: #17120e; color: #f5ead9; font: 1rem/1.4 system-ui, sans-serif; text-align: center; }
  p { margin: 0 0 1rem; font-size: 1.1875rem; }
  a { display: inline-block; padding: 0.7rem 1.4rem; border-radius: 999px; background: #f5a524; color: #17120e;
    font-weight: 650; text-decoration: none; }
</style></head>
<body><main><p>Couldn't load this page.</p><a href="${url}">Try again</a></main>
<script>try{var k="reader-log",l=JSON.parse(localStorage.getItem(k)||"[]"),t=Date.now();l.push({s:t,t:t,e:"retry-page",p:location.pathname,d:"",n:"sw",l:""});localStorage.setItem(k,JSON.stringify(l.slice(-150)))}catch(_){}</script>
</body></html>`;
  return new Response(html, {
    status: 503,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}
