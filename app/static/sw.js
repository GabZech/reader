const CACHE = "reader-shell-v4";

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
      Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== location.origin) return;

  event.respondWith(answer(request));
});

// Network first, then the copy from the last visit. A page that is neither
// reachable nor cached gets a retry page: answering with nothing shows as a
// blank white screen in an installed iPhone app, with no way out.
async function answer(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const copy = response.clone();
      caches
        .open(CACHE)
        .then((cache) => cache.put(request, copy))
        .catch(() => {});
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    if (request.mode === "navigate") return retryPage(request.url);
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
<body><main><p>Couldn't load this page.</p><a href="${url}">Try again</a></main></body></html>`;
  return new Response(html, {
    status: 503,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}
