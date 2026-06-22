# Madise iPad weather kiosk — session handoff

Last updated: 2026-06-22

## What this project is

A second build of the Madise weather PWA tailored to a wall-/stand-mounted
**iPad Air 2 in landscape** (1024 × 768, fullscreen Safari kiosk). Shares
the design language and data wiring of the phone build (`weatherapp2`)
but rearranges the layout around a big always-on radar map.

- **Live URL**: https://indrekraag.github.io/weatherapp/
- **Repo**: https://github.com/indrekraag/weatherapp (branch: `main`)
- **Sibling phone repo**: https://github.com/indrekraag/weatherapp2 — used
  as the stylistic reference and as the upstream for the EMHI station
  bridge
- **Local path**: `/Users/indrekraag/wa1/`

## Latest session (2026-06-22) — tarktee domain fix + 7-day dates

- **Kurevere bridge was silently broken for ~18 days.** tarktee migrated
  `tarktee.mnt.ee → tarktee.transpordiamet.ee` (~2026-06-04). The old host
  301-redirects; the GH Actions runner couldn't complete the cross-domain
  hop, so the cron hit its soft-fail path every 15 min — **green runs, no
  data pushed** (the 2026-06-08 "don't email on transient outages" hardening
  masked a permanent break). Data branch was frozen at 2026-06-04.
  **Fix (`54cfd29`):** point `fetch_kurevere.py` + `server.py` directly at
  the new canonical URL (no longer rely on the redirect). Verified end-to-end:
  push-triggered run pushed a fresh snapshot; cron is live again.
- **7-day strip:** day names now carry the date — `TÄNA` (today, no date),
  then `TEIS 23`, `KOLM 24`, … (`renderDaily`, abbreviation + `d.getDate()`).
- Added `.gitignore` (`__pycache__`).
- **Lesson:** a soft-fail that swallows *all* errors can hide a permanent
  outage behind green checkmarks. Open follow-up: make the cron surface a
  hard failure / staleness flag after N consecutive misses.
- Sibling note: the phone build (`wa2`) got the same tarktee domain fix the
  same day, plus a port of this kiosk's radar overlay (sun/moon arcs, wind).

## Current layout (iPad landscape)

```
┌──────────────────┬──────────────────────────────────────────┐
│                  │ 7-day forecast strip (full right col)    │
│ HERO CARD        ├──────────────────────────────────────────┤
│ - big temp       │                                           │
│ - 3 comfort      │  VIHMARADAR (RainViewer + Esri sat tiles)│
│   pills          │  + sun ARC across the sky                │
│ - 6 metric tiles │  + moon ARC (when above horizon)         │
│ - 3 station      │  + 1 wind arrow at Madise + label        │
│   chips          │  + faint drifting wind particles         │
│                  │  + Sadu colour legend top-right          │
│ FORECAST CARD    │  + zoom presets / MAP·SAT / [PILV opt'l] │
│ - Temperatuur    │  + timeline (auto-plays, time on right)  │
│ - Sadu (mm/h)    │                                           │
│ - Tuul + dirs +  │                                           │
│   Puhangud       │                                           │
└──────────────────┴──────────────────────────────────────────┘
                  (column bottoms aligned at runtime via JS)
```

- Phone build untouched — all iPad CSS is inside
  `@media (min-width: 900px) and (orientation: landscape)`.

## What's done

### Layout
- Glass cards, warm-amber accent (`#e9a76b`), SF system font, weather-blob
  body background — all ported from `weatherapp2`
- 3-row landscape grid: warning row (currently disabled) ・ hero + 7-day
  ・ forecast continues + radar
- Left wrapper (`.ipad-left-col`) so hero + forecast share one grid cell
  with `overflow-y: auto`; `display: contents` on phone so the wrapper
  vanishes there
- `syncRadarToForecast()` JS aligns the radar's bottom with the forecast
  card's bottom on init + resize so both columns end at the same line
- iOS `100dvh` + `-webkit-fill-available` so the radar's bottom controls
  don't disappear behind Safari's URL bar
- Tundub kui forecast row hidden via `.forecast-row-feels` class hook
  (`:nth-of-type` was a footgun — counts divs not just `.forecast-row`)

### Forecast card
- 14 px bar height, axis labels, wind-direction arrows under Tuul, gusts
  sub-row, colour-ramp legends hidden to save vertical room
- Sadu defaults to **mm/h** (`hulk`), not probability — when staring at
  a radar the relevant question is amount

### Radar map
- `maxNativeZoom: 7` on RainViewer tiles so no more "Zoom Level Not
  Supported" placeholders at country level
- Default zoom 80 km (level 8); presets 50 m / 2 km / 10 km / 80 km / EE
- MAP / SAT base toggle (Esri World Imagery as the sat layer)
- Auto-plays on load; manual pause sets `RADAR.userPaused` so the 5-min
  refresh doesn't restart the loop
- Timeline: play btn ・ slider stretching middle ・ time pinned to right

### Map overlays (SVG layer)
- **Sun arc** across the sky for today, sampled every 4 min from
  `solarPosition()`; past portion (rise → now) solid amber, future
  (now → set) dashed amber. Sun-over-horizon glyphs + time labels at
  both endpoints. Glowing sun disc + altitude° label at the current
  position
- **Moon arc** — same treatment, cool blue, only drawn when the moon
  is above the horizon at some point in a ±12 h window
- **Wind arrow** — single line with head pointing AT Madise from the
  direction wind is FROM (meteorology convention). Speed/gust label
  at the upwind tail end
- **Wind particles** — persistent `#wind-particle-overlay` SVG with 14
  faint cyan dashes drifting downwind via CSS keyframes; group rotation
  + animation-duration set per redraw. Hidden when wind < 0.4 m/s
- **Precipitation colour legend** inside `#radar-map`, top-right corner,
  same Leaflet-zoom styling as the +/- block on the opposite corner

### Data
- Open-Meteo for weather / hourly / daily / pollen / aurora air quality
- NOAA SWPC for Kp / Ovation / Bz
- Tarktee ArcGIS REST for Kurevere — now via the GH Actions bridge
  (see below); direct URL still used as a last-resort fallback
- EMHI bundle at `raw.githubusercontent.com/indrekraag/weatherapp2/data/
  emhi.json` (Lääne-Nigula 26124 + Haapsalu 26123 + CAP warnings)
- Local astronomy: Meeus simplified for sun, Brown lunar leading-term
  for moon

### Kurevere bridge
- `scripts/fetch_kurevere.py` + `.github/workflows/kurevere.yml` cron
  pulls tarktee server-side every 15 min and writes
  `https://raw.githubusercontent.com/indrekraag/weatherapp/data/
  kurevere.json`
- `fetchKurevere()` reads that URL on the github.io build (this device's
  iPad refuses tarktee directly — likely content blocker / TLS profile;
  Mac + iPhone Safari reach tarktee fine)
- Local `server.py` proxies `/api/kurevere` for LAN HTTP dev testing
- **Hardened 2026-06-08:** the cron retries tarktee **3× with backoff
  (5 s, 15 s)** and **soft-fails** (exit 0, no file, push step skipped) if
  every attempt fails — so a transient tarktee outage leaves the last good
  `kurevere.json` in place instead of emailing a workflow-failure alert.
  `fetch_kurevere.py` signals the Actions output `wrote=true|false`; the
  push step is gated on `wrote == 'true'`. Actions bumped to
  `checkout@v5` / `setup-python@v6` (Node 24); also fixed the deprecated
  `datetime.utcnow()`.
- 7-day strip: daily max-wind values colour-coded with `windBarColor()`
  so windy upcoming days stand out

### Kiosk-friendly behaviour
- `visibilitychange` listener re-pulls Kurevere / EMHI / warnings /
  weather / Kp the moment the iPad wakes from sleep — `setInterval`
  pauses on hidden tabs
- Hard-refresh ⟲ in hero-bar clears localStorage + service-worker caches

## What's currently disabled / pending

| | Status | Notes |
|---|---|---|
| Warning bar (`#warning-bar`) | **disabled on iPad** | CSS comment block in `index.html` next to the `display: none` override has the original styling for easy restore. `renderWarnings()` still runs. Disabled because the row pushed the left column past its vertical budget; needs a layout pass. |
| PILV cloud overlay (RainViewer IR) | **removed** | RainViewer's `satellite.infrared` array comes back empty too often |
| PILV cloud overlay (OpenWeatherMap) | **gated** | Button hidden until `window.OWM_KEY` is set in the `<script>` near the top of `<body>`. Get a free key from https://openweathermap.org/api and paste it. |
| Lightning strikes | **not started** | Free CORS-friendly source TBD — Blitzortung WS needs proxying, NASA GIBS has no Europe IR, OWM requires a paid plan for strikes |

## How to run locally

```bash
cd /Users/indrekraag/wa1
python3 server.py 8765          # custom server with /api/* proxies
# open http://<mac-LAN-ip>:8765/index.html on the iPad
```

`python3 -m http.server 8765` works too, but you'll lose the
`/api/kurevere` and `/api/emhi` proxies.

## Files

- `index.html` — single-file app (~5000 lines)
- `server.py` — dev-only Python proxy server
- `scripts/fetch_kurevere.py` — GH Actions cron worker
- `.github/workflows/kurevere.yml` — 15-min cron + push trigger
- `index_vana.html`, `indexv2..v5.html` — pre-unify iterations
  (archived, not loaded by the live page)
- `HANDOFF.md` — this file
- `README.md` — GitHub Pages publish instructions

## Open items / next steps

1. **Warning bar layout fix.** Re-add `#warning-bar` to the iPad grid
   without breaking column alignment. Options to try: skinnier idle
   state (height: 22 px max), or push it OUTSIDE `.app` into a fixed
   strip above the grid, or just always reserve the row but with
   `min-height: 0`.
2. **PILV / OpenWeatherMap key.** Get the free key, paste into the
   config `<script>` near the top of `<body>`. Button auto-appears.
3. **Lightning strikes.** Pick a data source (Blitzortung community
   feed via small proxy in `server.py` is probably easiest, but
   requires CORS pass-through and the GH Pages build doesn't have a
   server). Alternative: use the same GH Actions cron pattern as
   Kurevere to pull strikes server-side every minute.
4. **Wind particles visibility.** Currently faint enough to be invisible
   in still air or against light tiles. If the user wants them more
   prominent, bump opacity (~0.85) and stroke / width — or drop them.
5. **PWA manifest** still says "Madise Ilmaradar" (inherited from
   weatherapp2). Rename if this version gets installed to home screen.
6. **Service worker** — none registered. Lift `sw.js` from weatherapp2
   if offline-tolerance matters.

## Useful command snippets

```bash
# Headless screenshot at iPad viewport
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1024,768 --virtual-time-budget=15000 \
  --screenshot=/tmp/ipad.png http://127.0.0.1:8765/index.html

# Trigger the Kurevere GH Actions workflow manually
gh workflow run kurevere.yml -R indrekraag/weatherapp

# Check what the Kurevere bridge has cached right now
curl -s https://raw.githubusercontent.com/indrekraag/weatherapp/data/kurevere.json \
  | python3 -m json.tool
```
