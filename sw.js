/**
 * AMINA Experience — Service Worker (PWA Offline Support)
 * Cache-First with Stale-While-Revalidate strategy for offline resilience.
 */

const CACHE_NAME = 'amina-pwa-v2';

const STATIC_SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './css/design-system.css',
  './css/player.css',
  './css/reader.css',
  './css/modals.css',
  './js/data/episodes-data.js',
  './js/data/book-data.js',
  './js/state.js',
  './js/audio.js',
  './js/monetization.js',
  './js/player.js',
  './js/reader.js',
  './js/app.js',
  './assets/cover.jpg',
  './episodes/ep-001/audio/bgm_gospel.mp3'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Caching app shell assets');
      return cache.addAll(STATIC_SHELL_ASSETS).catch(err => {
        console.warn('[ServiceWorker] Pre-caching partial assets failed:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache version:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Bypass SW completely for cross-origin URLs (GitHub Releases / redirects / CDN),
  // HTTP 206 Range requests, video/.mp4 streaming, and dynamic videos-manifest.json
  if (
    url.origin !== self.location.origin ||
    event.request.headers.has('range') ||
    event.request.destination === 'video' ||
    url.pathname.endsWith('.mp4') ||
    url.pathname.endsWith('videos-manifest.json')
  ) {
    return;
  }

  // Strategy: Cache-first for static local assets, network fallback
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Return cached and fetch in background for update if http
        if (event.request.url.startsWith('http')) {
          fetch(event.request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, networkResponse.clone());
              });
            }
          }).catch(() => {/* offline */});
        }
        return cachedResponse;
      }

      // If not in cache, fetch from network
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }

        // Cache response for future offline visits
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return networkResponse;
      }).catch(() => {
        // Fallback for HTML documents when completely offline
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
