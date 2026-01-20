const CACHE_NAME = 'dual-cat-cache-v1';
const STATIC_ASSETS = [
  '/static/css/index.css',
  '/static/js/main.js',
  '/static/js/theme_switcher.js',
  '/static/imgs/logo-dual-fons-blau.png',
  '/favicon.ico'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(STATIC_ASSETS);
      })
  );
});

self.addEventListener('fetch', event => {
  // Strategy: Network-First for HTML/other, Cache-First for Static Assets
  const url = new URL(event.request.url);

  if (STATIC_ASSETS.includes(url.pathname)) {
    // Cache-First for static assets
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          return response || fetch(event.request);
        })
    );
  } else {
    // Network-First for everything else (especially HTML to avoid CSRF issues)
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return caches.match(event.request);
        })
    );
  }
});
