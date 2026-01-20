const CACHE_NAME = 'dual-cat-cache-v1';
const urlsToCache = [
  '/',
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
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
