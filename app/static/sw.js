// Never rename: a new name makes activate delete the old cache, and with it
// every page the reader had stored for offline.
const CACHE = "reader-shell-v4";
// Images from other sites in Read Later articles, downloaded ahead (see
// precache) and pruned to what Read Later still holds.
const IMAGES = "reader-images-v1";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) =>
      cache.addAll([
        "/",
        "/lists",
        "/sources",
        "/static/styles.css",
        "/static/app.js",
        "/static/fonts/fraunces-normal.woff2",
        "/static/fonts/fraunces-italic.woff2",
        "/static/fonts/literata-normal.woff2",
        "/static/fonts/literata-italic.woff2",
        "/static/fonts/figtree-normal.woff2",
      ])
    )
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
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== location.origin) {
    if (request.destination === "image") event.respondWith(answerImage(request));
    return;
  }

  event.respondWith(answer(request));
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "precache") event.waitUntil(precache());
});

// One stored copy per article, whichever list it was opened from: the
// address differs only by where Close leads back to.
function cacheKey(request) {
  const url = new URL(request.url);
  return /^\/items\/\d+$/.test(url.pathname) ? url.origin + url.pathname : request;
}

// Another site's image: the downloaded copy if there is one, so an article
// reads the same offline, else the network as before.
async function answerImage(request) {
  const cached = await caches.match(request, { cacheName: IMAGES });
  return cached || fetch(request);
}

let precaching = null;
let precachedAt = 0;
// Every page open asks; one run a minute is plenty.
const PRECACHE_GAP_MS = 60 * 1000;
// A few downloads at once: one at a time took longer than an iPhone keeps
// the worker running.
const DOWNLOADS_AT_ONCE = 4;

// Download every Read Later article not stored yet, and its images, so a
// saved article opens offline without having been opened first. Open pages
// hear when a run starts and ends, to turn Home's cog meanwhile.
function precache() {
  if (precaching) {
    announce(true);
    return precaching;
  }
  if (Date.now() - precachedAt < PRECACHE_GAP_MS) return Promise.resolve();
  announce(true);
  precaching = downloadReadLater().finally(() => {
    precaching = null;
    precachedAt = Date.now();
    announce(false);
  });
  return precaching;
}

function announce(running) {
  self.clients
    .matchAll()
    .then((pages) => pages.forEach((page) => page.postMessage({ type: "downloading", running })))
    .catch(() => {});
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

async function downloadReadLater() {
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

  // Articles first: they are what the reader cannot get any other way.
  await eachAtOnce(listed, async (article) => {
    const key = new URL(article.url, location.origin).href;
    if (await pages.match(key)) return;
    const response = await fetch(article.url, { headers: { "X-Reader-Prefetch": "1" } });
    if (response.ok) {
      await pages.put(key, response);
      pagesAdded++;
    }
  });

  // Home and the lists change all the time: always store a fresh copy, and
  // keep the one from last time when that fails.
  await eachAtOnce(lists, async (path) => {
    const response = await fetch(path);
    if (response.ok) await pages.put(new URL(path, location.origin).href, response);
  });

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
  tell("sw-precache", `pages+${pagesAdded} images+${imagesAdded} of ${listed.length}/${wanted.size}`);
}

const BOOTED = Date.now();
let pagesServed = 0;

// Tell every open page what happened, so it lands in the phone's breadcrumb log
// (see base.html); the worker itself has nowhere to keep one.
function tell(e, d) {
  self.clients
    .matchAll({ includeUncontrolled: true })
    .then((pages) => pages.forEach((page) => page.postMessage({ type: "log", e, d })))
    .catch(() => {});
}

// Network first, then the copy from the last visit. A page that is neither
// reachable nor cached gets a retry page: answering with nothing shows as a
// blank white screen in an installed iPhone app, with no way out.
async function answer(request) {
  const started = Date.now();
  const page = request.mode === "navigate";
  const where = new URL(request.url).pathname;
  const note = (what) => {
    if (!page) return;
    const up = Math.round((Date.now() - BOOTED) / 1000);
    tell("sw-nav", `${where} ${what} ${Date.now() - started}ms #${++pagesServed} up=${up}s`);
  };
  try {
    const response = await fetch(request);
    if (response.ok) {
      const copy = response.clone();
      caches
        .open(CACHE)
        .then((cache) => cache.put(cacheKey(request), copy))
        .catch(() => {});
    }
    note(`net ${response.status}`);
    return response;
  } catch (error) {
    const cached = await caches.match(cacheKey(request));
    if (cached) {
      note(`cache after ${error}`);
      return cached;
    }
    note(`retry-page after ${error}`);
    if (page) return retryPage(request.url);
    return Response.error();
  }
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
