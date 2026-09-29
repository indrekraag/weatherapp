/* Madise weather kiosk — app-shell service worker.
 *
 * NETWORK-FIRST, and for the page itself only. Every navigation still goes
 * to the server first, so a new deploy is picked up exactly as it was
 * without a service worker; the copy kept here is used only when that
 * request fails. Then the hourly reload (or any reload) during a Wi-Fi
 * outage paints the last page instead of the browser's "cannot open the
 * page" screen, and the page renders its cached data with age badges.
 *
 * Everything else — Open-Meteo, the data-branch bundles, radar and map
 * tiles, the Leaflet CDN, the page's own reachability check — is never
 * intercepted: no respondWith(), so the browser fetches it exactly as if
 * this file did not exist. The manifest is inline (a data: URI), so the
 * page is the whole shell.
 *
 * Registered from index.html on https only (GitHub Pages). The ⟲ button's
 * hardRefresh() unregisters it and deletes its cache. ES5 on purpose, like
 * index.html: the kiosk is Safari 15 on iPadOS 15.
 */
var SHELL_CACHE = 'madise-shell-v1';

/* One entry per document: '/weatherapp/' and '/weatherapp/index.html' are
   the same page, and a query string never names a different one. */
function shellKey(url){
  var u = new URL(url);
  var path = u.pathname;
  if(path.charAt(path.length - 1) === '/') path += 'index.html';
  return u.origin + path;
}

function keepCopy(key, res){
  return caches.open(SHELL_CACHE).then(function(c){ return c.put(key, res); });
}

self.addEventListener('install', function(event){
  // Take the page that registered us into the cache straight away, so the
  // very first outage after install is already covered. Best effort: a
  // failure here must not block installing.
  var page = new URL('./', self.location.href).href;
  event.waitUntil(
    fetch(page, { cache: 'no-cache', credentials: 'same-origin' }).then(function(res){
      if(res.ok && !res.redirected) return keepCopy(shellKey(page), res);
    }).then(null, function(){}).then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(event){
  event.waitUntil(
    caches.keys().then(function(names){
      return Promise.all(names.filter(function(n){
        return n.indexOf('madise-shell-') === 0 && n !== SHELL_CACHE;
      }).map(function(n){ return caches.delete(n); }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(event){
  var req = event.request;
  if(req.method !== 'GET' || req.mode !== 'navigate') return;
  var key = shellKey(req.url);
  event.respondWith(
    fetch(req).then(function(res){
      // Only a plain same-origin 200 is worth keeping — never an error
      // page or a redirect.
      if(res.ok && res.type === 'basic' && !res.redirected){
        var saving = keepCopy(key, res.clone()).then(null, function(){});
        try { event.waitUntil(saving); } catch(e){}
      }
      return res;
    }, function(err){
      return caches.open(SHELL_CACHE).then(function(c){
        return c.match(key);
      }).then(function(hit){
        if(hit) return hit;
        throw err;
      });
    })
  );
});
