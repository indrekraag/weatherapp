#!/usr/bin/env python3
"""Fetch the Kurevere road-weather station from tarktee.mnt.ee and emit
a JSON snapshot the iPad can read via raw.githubusercontent.com.

Why this script exists:
  The tarktee.mnt.ee ArcGIS REST endpoint does send CORS headers, but
  this particular iPad refuses to reach the host (network error firing
  inside the browser even though curl from the same Wi-Fi works fine —
  probably a content blocker or stricter TLS profile on iPadOS for this
  device). The same iPad successfully reaches GitHub's CDN for the EMHI
  bundle, so we route Kurevere through the same channel: a GH Actions
  cron pulls tarktee server-side every 15 min and writes the snapshot
  to the repo's 'data' orphan branch.

Usage:
    python3 scripts/fetch_kurevere.py --out /tmp/kurevere.json

Exits non-zero on network or parse failure so the workflow can fail
loudly instead of silently committing stale data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

TARKTEE_URL = (
    "https://tarktee.mnt.ee/tarktee/rest/services/road_weather_stations/"
    "MapServer/0/query?where=site_name=%27Kurevere%27&outFields=*&f=json"
)
TIMEOUT_SECONDS = 15

# Only surface the fields the PWA actually reads — keeps the bundle small
# and stops random schema noise from triggering pointless commits.
FIELDS = [
    "site_name",
    "air_temp",
    "road_temp",
    "wind_speed",
    "wind_dir",
    "precipitation_type",
    "precipitation_intensity",
    "air_humidity",
    "visibility",
    "measurement_time",
]


def fetch() -> dict:
    req = urllib.request.Request(
        TARKTEE_URL,
        headers={
            "User-Agent": "weatherapp-kurevere-bridge/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        if resp.status != 200:
            raise RuntimeError(f"tarktee HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def build_snapshot(raw: dict) -> dict:
    features = raw.get("features") or []
    if not features:
        raise RuntimeError("tarktee returned no features for Kurevere")
    attrs_raw = features[0].get("attributes") or {}
    attrs = {k: attrs_raw.get(k) for k in FIELDS}
    return {
        "source": "tarktee.mnt.ee",
        "source_url": TARKTEE_URL,
        "fetched_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        # Wrap as a single-feature collection so renderKurevere() in
        # index.html can read it with the same shape as the direct API.
        "features": [{"attributes": attrs}],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/kurevere.json", help="Output JSON path")
    args = p.parse_args()

    try:
        raw = fetch()
    except urllib.error.URLError as e:
        print(f"ERROR fetching tarktee: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # broad — workflow will surface the message
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    snapshot = build_snapshot(raw)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    print(f"✓ Kurevere snapshot → {out_path}")
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
