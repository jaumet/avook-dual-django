self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", () => {
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Minimal fetch handler to make it PWA-compliant
  event.respondWith(fetch(event.request));
});
