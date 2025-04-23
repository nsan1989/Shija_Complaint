self.addEventListener('install', function(e) {
    console.log('Service Worker: Installed');
  });
  
  self.addEventListener('activate', function(e) {
    console.log('Service Worker: Activated');
    return self.clients.claim();
  });
  
  self.addEventListener('fetch', function(e) {
    e.respondWith(
      caches.match(e.request).then(function(response) {
        return response || fetch(e.request);
      })
    );
  });
  