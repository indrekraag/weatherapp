# Madise iPad weather kiosk — session handoff

Last updated: 2026-09-29

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

## ▶ Latest session (2026-09-26 → 29) — design audit, P1+P2 fixes (v1.3.0)

### If something is broken or looks off: undo

Everything below is in 18 commits after the git tag **`pre-audit-fixes`**
(= `bc22574`, the kiosk as it was on 2026-09-19).

- **Undo all of it** — one command, tested (index.html comes back
  byte-identical to the tag; the service worker removes itself ~10 s after
  the iPad reloads):
  ```bash
  cd ~/wa1 && sh scripts/undo-audit-fixes.sh
  ```
  The hero bar then reads `v1.2.0 · 19.09 02:12` again — that is how you
  see on the iPad that the rollback landed. Redo later with
  `git revert <the undo commit> && git push`.
- **Undo one part** — the commits per area are listed below; `git revert
  <hash>` works for most, but the later typography/repair commits touch
  the same lines, so reverting an early commit alone can conflict. Easiest:
  ask Claude "undo the radar changes from the audit" and let it resolve it.

### How it was done

`/impeccable critique` + `/impeccable audit` (the same Impeccable plugin as
Modcranebuilder), plus a rendered-measurement pass (font sizes → physical
legibility distance on the iPad Air 2, contrast, touch targets), a
data-honesty pass and forced states (night, −12 °C, storm, offline, price
extremes, rotation). Every finding went through an adversarial verifier:
105 findings, 0 refuted. Scores before the fixes: **critique 20/40,
audit 9/20**. Snapshot: `.impeccable/critique/2026-09-26T15-18-22Z__index-html.md`
(untracked). The owner chose: wrong data first, reading distance ~1 m (by
the door), map keeps its size, do all P1 then P2.

### What changed (by commit)

| Area | Commits | What |
|---|---|---|
| Calculations | `864bcca` `b90fe06` `cd70a1f` | **Sun times were dated 24 h early from ~23 Sep to ~21 Mar** (equation-of-time wrap in `calcSunTimes`): no sun disc, arc drawn as "past", day treated as night. Hero rain was a **15-min sum shown as mm/h** (4× low) → `currentPrecipRate()`. **"Saju alguseni" was an hour late** (hourly precipitation is the sum over the *preceding* hour) and ignored drizzle; one shared `RAIN_MIN_MM`. Pressure trend from hourly `surface_pressure` over 3 h (was a permanent default "↗ stabiilne" — the history was in memory and the hourly reload wiped it). Hero icon: night variants, port of wa2's `skyIconSVG` guard, one day/night answer for text + icon (`heroIsDay`, `paintHeroSky`). Condition names snow / freezing rain / thunder. |
| Honesty | `27bfc1c` `32e4af1` `7c1e1ed` `6c30470` | No more fake placeholder weather ("14° Pilves selgimistega") when Open-Meteo fails — "—" and an explicit no-data state; cache kept 24 h but shown with its age. **Data age is visible**: `ilm HH:MM` in the hero bar (amber past 45 min), age tags on station chips (EMHI + Kurevere). Kurevere retries no longer multiply (was 1,913 requests / 50 min in an outage) and an error no longer destroys the chip's spans (old open item 0b). Hourly reload only when the site is reachable, plus **`sw.js`** — a network-first app-shell worker (page only, never data), https only, so an offline reload shows the last page instead of Safari's error screen. Empty cards keep their size. 7-day strip drops days that are over. |
| Warnings + road | `a89b1ae` `1a6e7ac` | **Warnings now reach the kiosk**: a banner over the top of the map, only while one is active (costs no layout). One CAP source (the bridge's MeteoAlarm); the direct `hoiatus.php` path was removed — it returns a non-CAP XML the parser could never read. Own alerts fixed (thunder / heavy rain / gusts each register). **Kurevere chip shows road state** (`tee +3° märg`, tarktee's own labels; ICE/FROST/COLD_RAIN go up on the banner). Old open item 0a done. |
| Radar | `68d528b` `b660b02` `ac7ec9e` | One layer per frame switched by opacity (was recreating a tile layer every 500 ms → RainViewer 429 storms that showed "no rain" while the status said OK); back-off with an honest status; legend generated from the real colour scheme (the green "Mõõdukas" never existed on the tiles); holds ~3 s on the newest frame, label `nüüd` / `−40 min`; returns to the preset 60 s after a stray pan; MAP base switched from CARTO (now an "API KEY REQUIRED" watermark) to Esri light grey; autoplay rests at night / hidden / reduced motion; presets `50 KM · 200 KM · EE` match what they show; controls no longer overlap; 32 px hit areas. |
| Readability + colour | `20809b9` `6e16144` `8de4124` `6506f52` | Sized for ~1 m: 14 px floor (12 px only for chart ticks/units), 28 px clock, bigger hero, one shared hour axis for the four 24h charts. `--cold` is a real blue (was the same amber as `--warm`/`--warn`/`--accent`); ordinary temperatures white, ≤0 °C blue, ≥25 °C amber (`tempTone()`). Hero Sadu tile says `vihm ~kl 19` when rain is near. ⟲ now needs **two taps** ("Kinnita?"), ↻/⟲ are 44 px. Contrast failures fixed. The seven `backdrop-filter` layers removed (≈0.2% visual effect, real GPU cost on an A8X). 7-day card is a whole-pixel 148 px (a fractional height put a 1 px seam across the satellite tiles). |
| Rotation, price, night | `c686d90` | Rotating the iPad no longer half-breaks the kiosk (matchMedia listener, init/teardown). Price card: negative prices drawn below zero, cheapest hour tagged (`odavaim`), midnight divider + `homme`, `Elering · HH:MM` age, "homne hind ~14:00" before publication, `Hetkel … tunni keskm.` (the market settles per 15 min; the bridge only keeps hourly). **Night dim** between sunset+1 h and sunrise−30 min (touch lifts it for 60 s). Hidden cards (pollen, aurora, dead NOAA Bz) no longer polled on the kiosk; ↻ also refreshes prices + radar. |
| Follow-ups | `71ca4f4` | Rain start more than 6 h out reads `Sadu: neljapäeval ~kl 13` instead of `~45 h 34 min`; old radar frames in hours; the map's wind arrow no longer waits up to 5 min after a reload (script-order race). |
| Undo tool | `8cd5bfa` | `scripts/undo-audit-fixes.sh` |

Verified at 1024×768 after every group and again independently (two
verifier agents + a repair pass): no overflow, all four column bottoms at
762 px, map 606×395 and Leaflet in agreement, ES5-only JS, no Safari 15.4+
CSS, phone fallback renders, no new console errors. **Not verified on the
physical iPad** (only desktop Chrome was available) — the service worker
and the scrubber thumb styling are the parts most worth a look there.

### The data bridges now run on a real 15-min clock (VPS timer)

GitHub throttled the `*/15` crons to every ~3–5 h (measured: station
readings 3 h old, tomorrow's prices arriving 14:53 / 18:18 / 18:32). Now
**root's crontab on the Hetzner VPS** (`root@77.42.127.225`) runs
`/opt/wa-dispatch/dispatch.sh` every 15 min, which calls
`workflow_dispatch` for this repo's `kurevere.yml` and wa2's `emhi.yml`
(stations + warnings + prices). Token: fine-grained, Actions read/write on
`weatherapp` + `weatherapp2` only, in `/opt/wa-dispatch/token` (created by
the owner, never in a repo or chat). Log: `/var/log/wa-dispatch.log`
(`kurevere=204 emhi+nps=204` per run; **401 = token expired** — regenerate
and overwrite the file). Verified 2026-09-29 08:28 UTC. Stop it with
`ssh root@77.42.127.225 'crontab -l | grep -v wa-dispatch | crontab -'`.
Also written up in wa2's CLAUDE.md.

### Judgement calls worth revisiting

- `RAIN_MIN_MM = 0.2` (wa2 uses 0.5, chosen 2026-05-31). 0.2 is what makes
  the hourly series and the 15-min current value agree on wet/dry; the
  cost is that a lone 0.2 mm hour counts as rain for the countdown.
- `currentSkyText` still says "Sajab" only from 2 mm/h while the tile says
  "mõõdukas" from 0.5 — pre-existing, left alone.
- Road state uses tarktee's own word "jäine" (not "jäide"); one-word edit in
  `ROAD_STATUS_ET`. `grip_factor` does not exist on the tram layer (always
  null) — only `road_status(_aggregate)` drives the ice logic.
- The app's own gust alert uses EMHI's land criteria (15/23/30 m/s): expect
  a yellow "Tugev tuul" on windy autumn days (~43 days/yr at Madise).
- `EE` preset is now centred on Estonia, not Madise (so it really shows
  Estonia).
- New tunables: `WX_AGE_WARN_MIN` 45, `WX_AGE_DIM_MIN` 120,
  `WX_CACHE_KEEP_MS` 24 h, `STATION_AGE_TAG_MIN` 90,
  `STATION_STALE_AFTER_MIN` 360, `KV_RETRY_MS` 8 s/30 s/2 min,
  `RAIN_SOON_H` 3, `RAIN_TILE_AHEAD_H` 6.

### Still open from the audit (P3, not done)

- Wording: `TÄNA · 24H` → "Järgmised 24 h"; "Öökülm" → "Öö min" unless ≤ +3°;
  one date format (7-day still `30/09`); `mm` on 7-day rain; one sign
  convention; station chips mix rate and amount under "mm".
- Temperature bars from a moving baseline exaggerate (a line/area would be
  honest); the rain row autoscales so a drizzle day looks wet.
- Tile glyphs inconsistent (⌁ ◌ ◐, none on the pills).
- Dead weight: 25 unused CSS classes (`.weather-*`), a 128 KB base64 icon
  (~⅓ of the file), manifest says `portrait` / "Madise Ilmaradar", seven
  old HTML copies in the repo root are publicly served, README is
  boilerplate.
- Moon times 6–8 min early (single-term lunar model).
- `checkAlerts` still skips the current hour, and hourly gusts are also a
  preceding-hour value, so the Puhangud row is shifted like rain was.
- Hard refresh still wipes the weather cache, so ⟲ during an Open-Meteo
  outage shows "Ilmaandmed puuduvad" without "viimati".
- The orange sun-arc path can graze the wind label (labels avoid glyphs,
  not arcs).
- **wa2 has the same bugs** — checked 2026-09-29: the unwrapped `EoT` in
  its `calcSunTimes`, `round1(cur.precipitation)` shown as mm/h, the
  "14° Pilves selgimistega" placeholders, the CARTO light base (and almost
  certainly the rain hour shift). Port when convenient.

## Previous session (2026-09-19) — layout reclaim, build stamp

### Reclaiming the wasted bottom strip (2026-09-19)

Measured at a simulated true 1024×768 budget: the forecast card ended
**83px above** the bottom of its column, and because
`syncRadarToForecast()` pins the radar stack to *that card's bottom*, the
map was shortened to match — leaving **64px of dead screen** under it.
Roughly a tenth of the display was empty.

**The counter-intuitive part, worth remembering before "saving space"
here again:** cutting hero content does NOT give the map room. The stack
height is `forecastCard.bottom − stack.top`, so trimming the hero moves
the forecast card *up* and makes the radar *shorter*. Left-column cuts and
map size are independent.

1. **`.forecast-card { flex: 1 1 auto }`** — the card now fills the
   column, so its bottom lands at the column bottom and the existing sync
   function (unchanged) walks the radar down with it.
   **Map 341px → 405px (+19%).** Both columns now reach the app bottom
   exactly (measured 0px slack, 0px misalignment).
   The reclaimed height is passed down to the bars rather than pooling as
   blank space: `.forecast-row` flexes and `.metric-spark` grows from its
   fixed 14px (**14px → 59px at kiosk size**). `renderSpark()` needed no
   change — it already sizes bars as a percentage of their container.
   `.forecast-row-feels` is pinned `flex: 0 0 auto` so the hidden row
   claims no share.
2. **Second metric row dropped** (`.metric-secondary`, hidden in the media
   query) — **59px**. Two of its three tiles were known-wrong anyway: UV
   renders a fabricated `0`, and the Nähtavus sub-label is hardcoded
   "selge". Humidity survives implicitly via the Kastepunkt pill. Note a
   whole grid row must go — hiding one tile of three reclaims nothing.
3. **`.hero-title` dropped** — **19px**. "HETKEILM MADISEL" is redundant
   when the whole screen is one location. The condition text is kept:
   `initIpadEnhancements()` moves `#wx-cond` into `.hero-main` so it sits
   under the big temperature. Done in JS, not markup, so the phone keeps
   its header; the id is unchanged so `renderWeather()` is untouched.

Verified: no left-column scrolling, Leaflet's size matching the DOM, both
SVG overlays tracking, all five sparklines rendering.

**⚠️ This exposed a real bug** — see open items. With the condition text
now beside the hero icon, they visibly contradict each other.

### Radar card title removed (same session)

`VIHMARADAR` is hidden on the kiosk — `#radar-card .card-header
{ display: none }` in the landscape media query — and the card's top
padding trimmed 12px → 10px to match the bottom now that nothing sits
above the map. On a wall display the map is self-evident; the label cost
map height, which is the one thing on this screen that benefits from
every pixel.

Measured A/B at an identical viewport: **map 402px → 423px (+21px)**, with
`leftColOverflow` and the column-bottom misalignment *byte-identical*
before and after, Leaflet's internal size matching the DOM (no stale-size
grey tiles), and `#map-overlay` / `#wind-particle-overlay` both tracking
the new height with the arcs redrawn.

The `<h2>` stays in the markup for the phone fallback layout, where the
card is one of several stacked and the label helps scanning.

### Build stamp in the hero bar (same session)

Added `APP_VERSION` + `APP_BUILT`, rendered under the date as
`v1.0.0 · 18.09 21:14` in `.build-stamp` — 0.8em and 34% white against the
clock's 92%, so it cannot be misread as a second clock. See **Deployment**
for the bump rule.

`.hero-bar-date` had to change from `flex-wrap: nowrap; overflow: hidden`
to `flex-wrap: wrap` with `white-space: nowrap` on the children: the stamp
is the widest item in that strip and on the iPad's narrow left column
there is no room for it inline, so with `nowrap` the date broke mid-word
("18. / september"). It now drops to its own line as a whole unit.
Measured after the change: `.ipad-left-col` still not overflowing, body
still not scrolling at 1024×768.

## Latest session (2026-09-18b) — forecast audit: icons that over-promised rain

Audit of the card logic against 194 days of actuals (ERA5, Madise,
2026-03-01 → 09-10). Three fixes shipped; the rest is logged below as
open items.

### 1. The 7-day icon had no amount threshold (the reported symptom)

`renderDaily` drew `weatherCodeToSVG(daily.weathercode[i])`, and
Open-Meteo's daily weathercode is the **maximum hourly code of the day** —
so one hour of light drizzle painted all 24. Measured: the strip showed a
precipitation icon on **116 of 194 days**, and **38 of those delivered
under 1 mm**; 24% had ≤2 precipitation hours. Every false alarm was code
**51/53** (light drizzle, median 0.4 mm) — so the cure is a threshold on
the *amount*, not a remap of codes.

New `dailyPrecipIcon(daily, i, hourly)` + `dominantSkyCode()`:
- show precipitation from **≥1.0 mm**, or **≥0.3 mm if it lasts ≥3 h**
- **snow** gets a lower bar (0.3 mm water ≈ 3 mm snow)
- **thunder and freezing rain are never suppressed** at any amount —
  0.2 mm of ice is the entire point
- below threshold, fall back to the day's **dominant daylight sky**
  (mode of the hourly cloud codes), not to a blank

Replayed through the shipped function: false alarms **38 → 12**, real rain
days missed **0** (precision 67% → 87%, recall stays 100%). 26 days
reclassified: 12 → clear, 13 → overcast, 1 → mainly clear.
`&daily=` now also requests `precipitation_hours` and
`precipitation_probability_max` (the latter is not rendered yet — see
open items).

### 2. The probability colour ramp was compressed into its bottom eighth

`rainBarColor` borrowed the mm stops through the mapping
`[0,1,3,12,30,55,100]`. A **10%** chance was painted the same violet as
**2 mm/h** of real rain; **30%** came out the heavy-5mm purple; **50%**
read as very-heavy-10mm. Replaced with a proper likelihood scale,
`RAIN_STOPS_PROB` (0/20/40/60/80/100), topping out at purple-red rather
than the 20mm/h extreme red. `RAIN_LEGEND_PROB` is now **generated from
that same array**, so the strip can never again disagree with the bars —
the hand-written version had drifted 2–3 tiers (it labelled 30% light blue
while the bar drew heavy purple).

**Scope note:** the iPad forces `setRainMode('mm')` in
`initIpadEnhancements()`, and the legend is `display:none` in the
landscape media query — so on *this* build the ramp is only visible after
tapping TÕENÄOSUS, and the legend never is. Both matter much more on the
phone build (`wa2`), where probability is the default and the legend
shows. **Not yet ported to wa2.**

### 3. Öökülm showed a minimum that had usually already happened

The pill read `daily.temperature_2m_min[0]` — *today's* min, which after
~09:00 is behind you. Evaluated at 14:00 across 193 days: off by ≥2 °C on
**33%** of days, and the frost colour band was **wrong on 11%**. The
errors run optimistic, the harmful direction: **17 April showed +4.8 °C
green "safe" while the night ahead reached +0.1 °C**; 5 March showed amber
"caution" for a night that hit −2.2 °C. New `tonightMinTemp(hourly)` takes
the minimum over **now → 09:00 tomorrow**, and returns null (falling back
to the daily figure) rather than inventing a number.

## Previous session (2026-09-18) — tarktee froze again; found the live path

**Kurevere was dead again — and the June fix had only been half the story.**

- **Symptom:** the chip showed a plausible reading that never changed. The
  bridge looked healthy: green cron runs, `fetched_at` minutes old.
- **Cause:** `measurement_time` was **2026-06-04T18:00Z** — 105 days old.
  On the day tarktee moved host (mnt.ee → transpordiamet.ee) it *also*
  stopped updating every **root-level** ArcGIS service. All 116 weather
  stations, the road cameras and the traffic detectors are frozen at that
  one instant and still answer **HTTP 200**. June's fix pointed at the new
  host but the same dead layer, so it fixed the hop and not the data.
- **The live data is in the `tram/` folder** of the same ArcGIS server —
  `/tarktee/rest/services/**tram**/road_weather_stations/MapServer/0/query`.
  Found by watching what tarktee.ee's own map requests. Verified: root path
  105 days stale, tram path 15 min old. Both hosts serve it.
- **Bonus fields** on the tram layer: `road_status` (DRY/MOIST/WET/ICE…),
  `road_status_aggregate`, `grip_factor`. Now carried in the snapshot,
  not yet rendered — a chip could show road state with no bridge change.
- **Closed the open follow-up** from June ("surface a hard failure after N
  consecutive misses"), which is precisely what would have caught this:
  - `fetch_kurevere.py` now checks the reading's age against
    `MAX_MEASUREMENT_AGE` (6 h) and splits two failure modes: a *transient*
    error still soft-fails silently, but a *frozen feed* is published with
    `stale: true` **and** sets a `stale` step output.
  - The workflow gained a **`Fail if the feed is frozen`** step that runs
    *after* the push — the kiosk still gets the flagged data, and the run
    goes red so a human hears about it the same day.
  - Snapshot now also carries `measured_at` + `age_minutes`, so the
    fossil-vs-fresh question is answerable by reading the JSON.
- **Display-side guard** (`index.html`): `markStationStale()` dims the chip,
  greys the temperature and appends an amber `106 p vana` age tag when a
  reading is older than 6 h. It appends its own element rather than
  rewriting `.station-sub` — the existing `status()` error path *does*
  overwrite that node and destroys the `#kv-wind` / `#kv-precip` spans
  permanently (pre-existing bug, see open items). Verified both ways:
  fossil → dimmed + tagged, fresh → class and tag removed cleanly.
- **Lesson, sharpened:** a 200 is not evidence of live data, and neither is
  a fresh `fetched_at` — that only says *we* ran. Only the upstream's own
  measurement timestamp proves anything. Every bridge that republishes a
  third-party feed should assert on it.

## Previous session (2026-06-22) — tarktee domain fix + 7-day dates

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

### Radar overlay: fixes brought back from wa2 (same session)

While porting the overlay to `wa2` several bugs surfaced and were fixed in
BOTH builds (`drawOverlay` / `updateWindParticles` / moon block):

- **Wind stripes were invisible** — `#wind-particle-overlay` sat at z-index
  399, *below* Leaflet's `.leaflet-map-pane` (which is z-index 400 via its
  transform stacking context), so the tiles covered them. Raised to 410
  (particles) / 420 (arcs). The map-overlay arcs only showed because they
  were z-index 400 AND later in the DOM.
- **Wind stripes flowed 90° off** — SVG `rotate(θ)` aligns the drift axis
  with screen angle θ from EAST; a compass azimuth is `rotate(θ−90)`. Fixed
  the group rotation to `blowDeg−90` (verified: drift bearing matches wind
  to 0.0° at all directions).
- **Field rescaled** to the map diagonal (travel via `--wind-travel`, even
  perpendicular spread), denser (24) + brighter so the stream actually fills
  the map.
- **Moon arc rewritten** — was sampling a ±12 h window whose two edges fall
  at the same clock time, producing a bogus duplicate "rise == set" label.
  Now draws the current (or next) above-horizon pass with rise/set markers
  from the real `findMoonRiseSet()` crossings, in **gray**, just inside the
  sun ring; later **brightened** (thicker, denser dashes) for visibility.
- **`placeText` anti-overlap** nudges each value label radially so sun/moon
  values never stack.
- 7-day strip titles → `DD/MM` (no weekday name; `TÄNA` for today).

### Electricity price card (ported from wa2)

Added an **"Elektri hind"** card in the right column **under the radar**.

- Reads the **same `nps.json`** the wa2 GH Actions bridge publishes to
  weatherapp2's `data` branch (wa1 already cross-reads that branch for
  EMHI) — **no separate bridge** for the iPad. Source: Elering / Nord Pool
  day-ahead EE spot price; `fetchNps()` (local `data/nps.json` then the
  weatherapp2 raw URL), `renderNps()`, `PRICE_STOPS`/`priceBarColor`,
  `priceSnt` (÷10 ×(1+VAT)).
- **Layout:** radar-card + price-card wrapped in `.ipad-radar-stack`
  (display:contents on phone; flex column on iPad as grid row 3). Radar is
  `flex:1` (fills), price card `flex:0 0 113px`. `syncRadarToForecast` now
  sizes the **stack** so its bottom aligns with the forecast card — the
  radar shrinks to make room; the price card sits directly under the map.
  First-test height ≈ the puhangud/Tuul row (~113px); tune later.
- Same gridded chart as wa2: Y-axis + gridlines, color tiers
  (green→orange@10→red@18→purple@50, s/kWh incl 24% VAT), rolling 3h-past
  (dimmed) → onwards, hour label under each bar, "Hetkel:" current price.
- **Value tags:** the highest bar and the current-hour bar show their
  price as a figure on top (`.bar-val`); the Y-scale adds headroom so the
  peak tag isn't clipped.
- Rollback snapshots (all gitignored, local-only):
  `index_backup_pre_price_ipad_20260622.html` (no price card),
  `index_backup_ipad_pre_valuetags_20260622.html` (price card, pre value
  tags). Or `git checkout d9bf060 -- index.html` for the pre-price build.

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
  *(2026-09-26 audit: it is effectively a no-op now — the grid itself
  aligns the columns, and hero size does not affect the map height)*
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
- Tarktee ArcGIS REST for Kurevere — via the GH Actions bridge only
  (see below; there is no direct-URL fallback in the code, whatever older
  notes said)
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
- **Endpoint (2026-09-18):** must be the **`tram/`** folder —
  `…/rest/services/tram/road_weather_stations/MapServer/0/query`. The
  root-level service of the same name is a frozen 2026-06-04 snapshot that
  still returns 200. Same URL in `fetch_kurevere.py` and `server.py`.
- **Staleness gate (2026-09-18):** a reading older than 6 h is published
  with `stale: true` and fails the workflow run on purpose.
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
  and unregisters `sw.js` — **two taps** since 2026-09-29 (first tap shows
  "Kinnita?", confirm within 3 s)
- Hourly reload only when the page is reachable; `sw.js` (network-first,
  page only) paints the last page if a reload happens offline
- Night dim between sunset+1 h and sunrise−30 min; a touch lifts it for 60 s

## What's currently disabled / pending

| | Status | Notes |
|---|---|---|
| Warning bar (`#warning-bar`) | **replaced 2026-09-29** | The row stays hidden on the iPad; warnings now show as a banner over the top of the radar map, only while one is active (see Latest session). |
| PILV cloud overlay (RainViewer IR) | **removed** | RainViewer's `satellite.infrared` array comes back empty too often |
| PILV cloud overlay (OpenWeatherMap) | **gated** | Button hidden until `window.OWM_KEY` is set in the `<script>` near the top of `<body>`. Get a free key from https://openweathermap.org/api and paste it. |
| Lightning strikes | **not started** | Free CORS-friendly source TBD — Blitzortung WS needs proxying, NASA GIBS has no Europe IR, OWM requires a paid plan for strikes |

## Deployment — and the build stamp

Push to `main` → GitHub Pages serves it. **Before you push a change to
`index.html`, bump the build stamp at the top of the main `<script>`:**

```js
var APP_VERSION = 'v1.0.0';      // bump for a real change
var APP_BUILT   = '18.09 21:15'; // dd.mm HH:MM, local, when you pushed
```

It renders in the hero bar under the date, small and dim (`.build-stamp`,
34% white vs the clock's 92%) so it reads as a version marker rather than
a second clock. Its whole job is to answer, at a glance at the kiosk,
*"is the iPad showing my latest push or a cached older page?"* — which is
why it is baked into the file rather than fetched. Asking GitHub for the
newest commit would always return the newest, which is precisely the
question it cannot answer; only a value carried inside the file tells you
which file you are looking at.

**A stale stamp is worse than no stamp** — it makes a successful deploy
look like it never landed. If this gets forgotten twice, automate it (a
GH Action on `push: paths: [index.html]` that rewrites `APP_BUILT` and
commits back with a marker in the message to break the trigger loop).

To force the iPad to pick up a new build: the **⟲** button in the hero bar
clears localStorage + service-worker caches in place (tap twice — the
first tap asks "Kinnita?").

`sw.js` sits next to `index.html` and must be deployed with it. It is
network-first for the page only, so a push is picked up on the next load
exactly as before; bump `SHELL_CACHE` in it only if its own logic changes.

## How to run locally

```bash
cd /Users/indrekraag/wa1
python3 server.py 8765          # custom server with /api/* proxies
# open http://<mac-LAN-ip>:8765/index.html on the iPad
```

`python3 -m http.server 8765` works too, but you'll lose the
`/api/kurevere` and `/api/emhi` proxies.

## Files

- `index.html` — single-file app (~8500 lines since the 2026-09 audit)
- `sw.js` — network-first app-shell service worker (page only; deploy with index.html)
- `server.py` — dev-only Python proxy server
- `scripts/fetch_kurevere.py` — GH Actions cron worker
- `scripts/undo-audit-fixes.sh` — one-command rollback to tag `pre-audit-fixes`
- `.github/workflows/kurevere.yml` — nominal 15-min cron (GitHub runs it
  every ~3–5 h) + `workflow_dispatch`, which the VPS timer calls every 15 min
- `index_vana.html`, `indexv2..v5.html` — pre-unify iterations
  (archived, not loaded by the live page)
- `HANDOFF.md` — this file
- `README.md` — GitHub Pages publish instructions

## Open items / next steps

**Status 2026-09-29:** the items below are kept as history. Fixed by the
audit work (see Latest session): the hero icon/text contradiction, -2
(night icon), -1b (pressure trend — note its claim that `surface_pressure`
was already fetched was wrong), -1a for the hero + 24h card (not
`checkAlerts`), 0a (road state), 0b (Kurevere spans), 1 (warnings — as a
map banner), 6 (service worker), and the `code 1` night glyph from -1d.
-1 (wa2 tram fix) was done 2026-09-18. -5 (port to wa2) is now a bigger
job — see "Still open". Still open: -4/-3 (hidden on the kiosk), -1c,
remaining -1d, 2–5.

### Found 2026-09-19 — hero icon contradicts the hero text

Moving the condition line next to the icon (above) made a pre-existing
bug obvious. At 02:10 the card read **"SELGE"** beside an icon **drawing
raindrops**, from the same data:

- text: `currentSkyText(cloud_cover=16, precipitation=0)` → "Selge"
- icon: `hourly.weathercode[curIdx]` = **51 (drizzle)** → drizzle glyph

Cloud cover 16% with zero precipitation says the text is right and the
WMO code is the outlier. This is the **same disease as the 7-day strip** —
a code asserting precipitation the amount does not support — and the cure
already exists: `wa2` guards its hero with
`skyIconSVG(code, precipAmt, isDay)`, which suppresses the glyph below
`RAIN_MIN_MM`. **wa1 has no `skyIconSVG` at all** and calls
`weatherCodeToSVG()` directly, so it has no guard. Port it, or gate the
hero icon on `current.precipitation`.

### From the 2026-09-18 forecast audit — found, NOT fixed

These were measured and left alone deliberately; 1–3 above were the ones
asked for.

-5. **Port the audit fixes to `wa2`.** Fix #2 (probability ramp) matters
   *more* there: the phone defaults to probability and shows the legend,
   both of which the iPad hides. #1 and #3 apply identically.
-4. **UV tile can show a fabricated `0`.** `models=ecmwf_ifs` returns
   `uv_index: null` for every hour; `round1(null)` is **0**, not null, so
   the `uv !== null` guard passes and the tile renders a confident
   "0 · puudub". It only looks right because EMHI Haapsalu usually
   supplies `uvindex` — whenever that is missing you get a false zero.
   Verified: `ecmwf_ifs` → None, default blend → 1.4. Fix = drop the
   forced model, or test for null properly and show "—".
-3. **Nähtavus sub-label is hardcoded.** `<div class="metric-sub">selge</div>`
   (no id, nothing writes to it) — the tile read "5.7 km · selge", and
   5.7 km is haze. Either drive it from `visText` or delete the line.
-2. **Hero icon is always the daytime variant.** `is_day` is not in the
   `current=` request, so `curIsDay` falls back to `1`: a bright sun at
   23:00 on a clear night. `hourly.is_day` is already fetched.
-1a. **Five different precipitation thresholds** across the app (icon: none
   → now amount-based; dry dash 0.1 mm/day; `currentSkyText` 0.1 / 2;
   `updateRainStart` 0.2 mm/h; `checkAlerts` 3 mm/h **and** code ∈
   {65,67,82}). The last is effectively dead — that conjunction almost
   never occurs in a 25 km model, so the *icon* fires on 0.1 mm while the
   actual warning needs a cloudburst. There is also an `else if` there
   that stops a heavy-rain hour registering once a thunder hour is found.
-1b. **Pressure trend default is `'↗ stabiilne'`** — a rising arrow next to
   the word "stable". `PRESSURE_HISTORY` is in-memory, so after every
   reload the kiosk claims this for 2 h before a real trend exists.
   Hourly `surface_pressure` is already fetched; a real 3 h tendency is
   computable immediately.
-1c. **Show `precipitation_probability_max` on the 7-day strip.** Already
   requested as of this session, not rendered. Commercial strips print the
   PoP next to the icon so the reader can calibrate; ours shows mm only.
-1d. Minor: duplicate SVG gradient `id`s across repeated icons;
   `SPARK_RAIN_DATA` fabricates a flat 50% if probability is ever missing;
   `visibilitychange` re-fetches weather/stations but not NPS/pollen/
   aurora; `round1(null) → 0` used throughout; code 1 renders
   sun-behind-cloud by day but a plain moon at night.

   Checked and found **clean**: a precipitation icon next to a "—" mm value
   (0 occurrences in 194 days) and the heavier rain/thunder icon on a
   sub-1 mm day (0 occurrences). The over-promising was entirely drizzle.

### Older

-1. **`wa2` needs the same tram fix.** The phone build shares this bridge
   pattern and is almost certainly pointed at the frozen root endpoint too
   — check its `fetch_kurevere.py` equivalent. **Do this first**; it is the
   same one-line change plus the staleness gate.
0a. **Render `road_status` / `grip_factor`.** The tram layer supplies road
   state (DRY / MOIST / WET / ICE / SNOW) and a grip factor, both already
   carried in the snapshot. On a winter wall display "tee: jäide" is worth
   more than road temperature alone. No bridge change needed — only
   `renderKurevere()` plus a line in the chip.
0b. **`status()` destroys the Kurevere chip's value spans.** The error path
   in `fetchKurevere()` sets `.station-sub`'s `textContent`, which deletes
   `#kv-wind` and `#kv-precip` for good — after one transient failure those
   two values stay blank until a reload. Pre-existing, unrelated to this
   session, but it undermines the same chip. Fix by writing to a child
   element (`markStationStale()` shows the shape).
0. **Electricity price card (shipped `e0298e5`).** Live under the
   radar. Follow-ups: tune the card **height/density** (currently ≈113 px /
   puhangud row; with tomorrow published it shows ~37 hourly bars — could
   cap the look-ahead, e.g. now-3h → +18h, for chunkier bars); optional
   "cheapest upcoming window" highlight. The peak + current-hour value tags
   are iPad-only; the mobile `wa2` card hasn't got them yet (sync TODO).
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
