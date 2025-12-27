// Service Worker for TradePilot PWA
const CACHE_NAME = 'trading-bot-v2-2024-12'; // Updated version to clear old caches
const urlsToCache = [
  '/',
  '/static/dashboard.html',
  '/static/styles.css',
  '/static/dashboard.js',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing new version', CACHE_NAME);
  event.waitUntil(
    // Delete ALL old caches first
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          console.log('Service Worker: Deleting old cache', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      // Now cache new files
      return caches.open(CACHE_NAME).then((cache) => {
        console.log('Service Worker: Caching new files');
        return cache.addAll(urlsToCache);
      });
    }).catch((error) => {
      console.error('Service Worker: Cache failed', error);
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating and clearing all old caches');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Skip API calls - always fetch from network
  if (url.pathname.includes('/api/')) {
    return;
  }
  
  // Skip hashed filenames that don't exist - return 404 immediately
  if (url.pathname.includes('/static/css/main.') || url.pathname.includes('/static/js/main.')) {
    event.respondWith(new Response('File not found', { status: 404, statusText: 'Not Found' }));
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // For HTML files, always try network first to avoid stale cache
        if (event.request.destination === 'document' || 
            event.request.headers.get('accept')?.includes('text/html')) {
          return fetch(event.request).then((networkResponse) => {
            // If network fails, try cache
            if (!networkResponse || networkResponse.status !== 200) {
              return response || networkResponse;
            }
            // Cache the fresh response
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
            return networkResponse;
          }).catch(() => {
            // Network failed, try cache
            return response || new Response('Offline', { status: 503 });
          });
        }
        
        // For other files, use cache-first strategy
        if (response) {
          return response;
        }
        
        return fetch(event.request).then((networkResponse) => {
          // Don't cache if not a valid response
          if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
            return networkResponse;
          }
          
          // Clone the response
          const responseToCache = networkResponse.clone();
          
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          
          return networkResponse;
        });
      })
      .catch(() => {
        // Return offline page if available
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
        return new Response('Network error', { status: 503 });
      })
  );
});

// Push notification event
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification from TradePilot',
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png',
    vibrate: [200, 100, 200],
    tag: 'trading-bot-notification',
    requireInteraction: false,
    actions: [
      {
        action: 'view',
        title: 'View Dashboard'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('TradePilot', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-trades') {
    event.waitUntil(
      // Sync trades when back online
      fetch('/api/trades')
        .then((response) => response.json())
        .then((data) => {
          console.log('Service Worker: Synced trades', data);
        })
        .catch((error) => {
          console.error('Service Worker: Sync failed', error);
        })
    );
  }
});


