#!/bin/sh
# Put the kiosk back exactly as it was before the 2026-09 design-audit
# fixes (git tag `pre-audit-fixes`), and publish that.
#
#   cd ~/wa1 && sh scripts/undo-audit-fixes.sh
#
# What it does:
#   1. restores index.html from the tag — the build stamp in the hero bar
#      then reads "v1.2.0 · 19.09 02:12", so you can see on the iPad that
#      the rollback has landed;
#   2. replaces sw.js with a "switch-off" worker: the fixed build installed
#      a small offline service worker, the old page doesn't know about it,
#      so this one deletes its cache, unregisters itself and reloads the
#      page once;
#   3. commits and pushes. GitHub Pages serves it within a minute or two;
#      the iPad picks it up on its next hourly reload, or on a manual one.
#
# To redo the fixes afterwards:  git revert HEAD && git push
# Nothing is lost either way — every commit stays in the history.
set -e
cd "$(dirname "$0")/.."

if [ -n "$(git status --porcelain index.html sw.js)" ]; then
  echo "index.html or sw.js has uncommitted changes — commit or discard them first." >&2
  exit 1
fi

git pull --ff-only
git checkout pre-audit-fixes -- index.html

cat > sw.js <<'EOF'
/* Switch-off worker, written by scripts/undo-audit-fixes.sh.
 * The page this site now serves does not use a service worker. This
 * replaces the one the audit-fix build installed: it clears its cache,
 * unregisters itself and reloads open pages once, so nothing stale is
 * left behind. Safe to delete this file a few weeks after the rollback. */
self.addEventListener('install', function(){ self.skipWaiting(); });
self.addEventListener('activate', function(event){
  event.waitUntil(
    caches.keys().then(function(names){
      return Promise.all(names.filter(function(n){
        return n.indexOf('madise-shell-') === 0;
      }).map(function(n){ return caches.delete(n); }));
    }).then(function(){
      return self.registration.unregister();
    }).then(function(){
      return self.clients.matchAll({ type: 'window' });
    }).then(function(clients){
      clients.forEach(function(c){ c.navigate(c.url); });
    })
  );
});
EOF

git add index.html sw.js
git commit -m "Undo the 2026-09 audit fixes: back to pre-audit-fixes

Restores index.html from the tag and replaces sw.js with a worker that
unregisters itself. Redo with: git revert <this commit>."
git push

echo
echo "Done. The kiosk shows 'v1.2.0 · 19.09 02:12' in the hero bar once it has reloaded."
