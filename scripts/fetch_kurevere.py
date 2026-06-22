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

Network/connection hiccups are retried (3 attempts with backoff). If
every attempt fails, the script exits 0 *without* writing the output
file and sets the GitHub Actions step output ``wrote=false``, so the
workflow skips the push and the data branch keeps its last good
snapshot — a transient outage no longer emails a cron-failure alert.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# NOTE: tarktee migrated from mnt.ee → transpordiamet.ee around 2026-06-04.
# The old host still 301-redirects, but the cron silently soft-failed for
# weeks against it (GitHub runner couldn't complete the cross-domain hop),
# so we hit the canonical new URL directly instead of relying on a redirect.
TARKTEE_URL = (
    "https://tarktee.transpordiamet.ee/tarktee/rest/services/road_weather_stations/"
    "MapServer/0/query?where=site_name=%27Kurevere%27&outFields=*&f=json"
)
TIMEOUT_SECONDS = 15

# Retry policy. tarktee is occasionally slow/unreachable from GitHub's
# runners; retrying a few times with a short backoff clears most transient
# failures. Backoff applies *between* attempts, so 3 attempts sleep twice.
FETCH_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = (5, 15)

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
        "source": "tarktee.transpordiamet.ee",
        "source_url": TARKTEE_URL,
        "fetched_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        # Wrap as a single-feature collection so renderKurevere() in
        # index.html can read it with the same shape as the direct API.
        "features": [{"attributes": attrs}],
    }


def set_action_output(name: str, value: str) -> None:
    """Expose a step output when running under GitHub Actions (no-op
    locally). The workflow gates its push step on ``wrote == 'true'`` so a
    soft failure leaves the data branch untouched."""
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(f"{name}={value}\n")


def fetch_snapshot_with_retries(attempts: int = FETCH_ATTEMPTS):
    """Fetch tarktee + build the snapshot, retrying transient failures.

    A single attempt must clear every hazard: the HTTP fetch (timeouts,
    5xx), the JSON parse, and the "has a Kurevere feature" check (an empty
    feature list is treated as a miss and retried). Returns the snapshot
    dict, or None if every attempt failed."""
    last_err = None
    for i in range(1, attempts + 1):
        try:
            return build_snapshot(fetch())
        except Exception as exc:  # noqa: BLE001 — catch-all is intentional for retry
            last_err = exc
            print(f"Kurevere fetch attempt {i}/{attempts} failed: {exc}", file=sys.stderr)
            if i < attempts:
                delay = RETRY_BACKOFF_SECONDS[min(i - 1, len(RETRY_BACKOFF_SECONDS) - 1)]
                print(f"  retrying in {delay}s…", file=sys.stderr)
                time.sleep(delay)
    print(
        f"Kurevere fetch failed after {attempts} attempts; last error: {last_err}",
        file=sys.stderr,
    )
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/kurevere.json", help="Output JSON path")
    args = p.parse_args()

    snapshot = fetch_snapshot_with_retries()
    if snapshot is None:
        # Soft failure: every attempt hit a transient error. Write nothing
        # and tell the workflow not to push, so the data branch keeps its
        # last good snapshot. Exit 0 so the cron doesn't email on a blip.
        print(
            "Soft failure: tarktee unreachable after retries — keeping the "
            "previous snapshot (no file written, no push)."
        )
        set_action_output("wrote", "false")
        return 0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    print(f"✓ Kurevere snapshot → {out_path}")
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    set_action_output("wrote", "true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
