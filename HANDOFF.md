# Session handoff — 2026-05-22

## What was done

Unified the iPad version (`weatherapp`) with the design language and feature
set of the phone version (`weatherapp2`), keeping the iPad's large radar map
as the centrepiece.

**Visual:**
- Glass cards (28px backdrop blur + hairline borders + noise overlay)
- Single warm-amber accent (`#e9a76b`) replacing the cyan/blue
- System font (`-apple-system, SF Pro Display`) with mono only for numerics
- Weather-driven blob field as body background (drift changes with sky)

**Layout (≥900px landscape only — phone fallback untouched):**
- 5-row grid: warning bar → hero+radar → 7-day → sun-moon+pollen-aurora → footer
- Left column ~420px (hero card, scrollable if content overflows)
- Right column = big radar map with SVG wind/sun overlays
- Top-right of the map carries a 24h sparkline forecast overlay (cloned from
  the now-hidden phone forecast card via MutationObserver)

**Features ported from the phone:**
- 3 nearby weather stations (Kurevere · Lääne-Nig · Haapsalu) via
  `raw.githubusercontent.com/indrekraag/weatherapp2/data/emhi.json`
- Live CAP warnings (Lääne maakond) from EMHI XML feed with severity colours
- Pollen (Üldine · Kask · Hein · Lepp)
- Aurora (Kp 24h · Tõenäosus · Bz) + 72h Kp sparkline
- UV, humidity, visibility, snow depth
- Hard refresh button (clears localStorage + service-worker cache)
- 24h sparkline forecast (temp · feels · rain · wind+gusts)

**iPad-only additions on top of the phone:**
- Wind streamline arrows (7 dashed lines) over the radar centred on Madise
- Sunrise / sunset / current-sun direction lines with timestamps
- Zoom presets: 50m / 2km / 10km / 80km / EE
- MAP / SAT base-map toggle (defaults to satellite via Esri World Imagery)
- `maxNativeZoom: 7` on the radar layer so RainViewer's "Zoom Level Not
  Supported" tiles never appear when zoomed in past country level

## Files

- `index.html` — single-file app, ~4500 lines (phone base + iPad layer)
- `index_vana.html` / `indexv2.html`-`indexv5.html` — old iterations, untouched
- The pre-unify iPad index is now in git history (commit before this one);
  a local backup also sits at `/tmp/wa1_index_pre_unify_backup.html`

## How to verify locally

```bash
cd /Users/indrekraag/wa1
python3 -m http.server 8765
# Then in Safari: open http://127.0.0.1:8765/index.html
# For iPad viewport: Develop → Responsive Design Mode → 1024×768 landscape
```

## Open items / next steps

- Watch for one render cycle to confirm Kp 72h chart and pollen labels
  populate (they default to placeholder labels until the first NOAA + Open-Meteo
  fetch completes — ~3 s after load)
- If the wind streamlines look too dense at narrow zooms (zoom 14+), consider
  reducing the offsets array in `drawOverlay()` from 7 to 5 arrows
- The PWA manifest still says "Madise Ilmaradar" (inherited from phone) —
  fine for now; rename if this version gets installed to home screen
- Consider lifting `weatherapp2`'s service worker (`sw.js`) over too if the
  iPad will be used offline-tolerant
