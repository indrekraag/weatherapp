# Madise iPad weather kiosk — session handoff

Last updated: 2026-05-22

## What this project is

A second build of the Madise weather PWA tailored to a wall-/stand-mounted
**iPad Air 2 in landscape** (1024 × 768, fullscreen Safari kiosk). Shares
the design language and data wiring of the phone build (`weatherapp2`)
but rearranges the layout around a big always-on radar map.

- **Live URL**: https://indrekraag.github.io/weatherapp/
- **Repo**: https://github.com/indrekraag/weatherapp (branch: `main`)
- **Sibling phone repo**: https://github.com/indrekraag/weatherapp2 — used
  as the stylistic reference and as the upstream for the EMHI bridge
- **Local path**: `/Users/indrekraag/wa1/`

## Current layout (iPad landscape)

```
┌──────────────────┬──────────────────────────────────────────┐
│                  │ 7-day forecast strip (full right col)    │
│ HERO CARD        ├──────────────────────────────────────────┤
│ - big temp       │                                           │
│ - 3 comfort      │                                           │
│   pills          │  VIHMARADAR (RainViewer + Esri sat tiles)│
│ - 6 metric tiles │  - 1 wind streamline through Madise      │
│ - 3 station      │  - sunrise/sunset/current-sun rays       │
│   chips          │    with SVG sun-over-horizon glyphs      │
│                  │  - zoom presets 50 m / 2 km / 10 km /    │
│                  │    80 km (default) / EE                  │
│ FORECAST CARD    │  - MAP / SAT base toggle                  │
│ - Temperatuur    │  - timeline + play (auto-plays on load)  │
│   sparkline      │                                           │
│ - Sadu (mm/h)    │                                           │
│ - Tuul + dirs +  │                                           │
│   Puhangud       │                                           │
└──────────────────┴──────────────────────────────────────────┘
                  (column bottoms aligned via JS at runtime)
```

- Phone build is unchanged — all iPad CSS is inside
  `@media (min-width: 900px) and (orientation: landscape)`.

## What's already done

Day-by-day in the commit history (`git log --oneline`); summary:

- Full visual port from `weatherapp2`: glass cards, single warm-amber
  accent (#e9a76b), SF-system font, weather-driven blob field on body
- iPad-specific landscape grid (left sidebar full height, 7-day on top
  of map, radar below); column-bottom alignment via
  `syncRadarToForecast()`
- Map enhancements: wind streamline + sunrise/sunset/current-sun SVG
  overlay; zoom presets; satellite/light base toggle; auto-play on load
  with `RADAR.userPaused` flag so the 5-min refresh doesn't restart the
  loop after a manual pause
- Forecast card lives in the sidebar with rows thinned to 14 px bars,
  legends hidden, "Tundub kui" row hidden; Sadu defaults to **mm/h**
  (`hulk`), not probability
- `maxNativeZoom: 7` on the RainViewer tile layer (no more "Zoom Level
  Not Supported" placeholder tiles past country level)
- iOS `100vh` clipping fix: `min-height: 100dvh` + `-webkit-fill-available`
  fallback so the radar's bottom controls don't hide behind the URL bar
- Tundub kui forecast row hidden via explicit `.forecast-row-feels`
  class hook (the original `:nth-of-type(2)` selector was wrong — it
  counts divs, not just `.forecast-row` divs)
- Empty warning bar collapses (`.warning-bar-empty` class + iPad
  CSS hides it) so the row doesn't eat vertical room when calm
- Visibility-change listener re-pulls all station feeds when the iPad
  wakes from sleep (`setInterval` pauses on hidden tabs)
- Kurevere fetch errors now show **inside the chip's sub-line**
  ("HTTP 5xx" / "võrgu viga" / "aegus" / "parse error") for visible
  debugging on the iPad without the dev console
- `server.py` — small Python dev server that proxies `/api/kurevere`
  and `/api/emhi` server-side, used when testing on the LAN over HTTP
  (CORS quirks were intermittent there). On the live GitHub-Pages
  origin the JS falls back to the direct tarktee URL (works identically
  to the phone build).

## How to run locally

```bash
cd /Users/indrekraag/wa1
python3 server.py 8765          # custom server with /api/* proxies
# open http://<mac-LAN-ip>:8765/index.html on the iPad
```

Static-only equivalent (`python3 -m http.server 8765`) also works but
without the Kurevere/EMHI proxy fallbacks.

## Open items / next steps

1. **Verify Kurevere on the live URL.** The latest push to `main` ought
   to fix it on `indrekraag.github.io/weatherapp/` since tarktee
   honours CORS for the `*.github.io` origin. If it still shows "—"
   after a hard refresh (⟲ icon in the hero bar) check Safari's Web
   Inspector for the actual fetch error.
2. The PWA manifest still says "Madise Ilmaradar" (inherited from
   weatherapp2). Fine for browser use; rename if this gets installed
   to home screen.
3. No service worker registered yet — purely online. Lift `sw.js` from
   weatherapp2 if offline-tolerance matters for the kiosk.
4. The `wip/ipad-unify` branch now matches `main`; can be deleted once
   you're confident nothing needs to be cherry-picked back.

## Files in the repo

- `index.html` — single-file app (~4700 lines: phone base + iPad
  layout + iPad-specific JS for map overlay, zoom presets, sync)
- `server.py` — dev-only proxy server
- `index_vana.html`, `indexv2..v5.html` — pre-unify iterations,
  kept for archival, not loaded by the live page
- `HANDOFF.md` — this file
- `README.md` — original GitHub Pages publish instructions

## Useful command snippets

```bash
# headless screenshot at iPad viewport
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1024,768 --virtual-time-budget=15000 \
  --screenshot=/tmp/ipad.png http://127.0.0.1:8765/index.html

# verify Kurevere endpoint manually
curl -s "https://tarktee.mnt.ee/tarktee/rest/services/road_weather_stations/MapServer/0/query?where=site_name='Kurevere'&outFields=*&f=json" | head -c 200
```
