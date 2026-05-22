#!/usr/bin/env python3
"""Local dev server for the Madise iPad weather kiosk.

Serves static files (like `python3 -m http.server`) PLUS a small set of
API proxy endpoints that forward to upstream weather APIs. The proxies
exist purely so the iPad — hitting this server over HTTP on a LAN IP —
can pull data sources that don't reliably surface CORS headers for
non-public origins.

Routes:
  /                       → index.html  (or any static file)
  /api/kurevere           → tarktee.mnt.ee road weather station JSON
  /api/emhi               → raw.githubusercontent.com/.../emhi.json

Run from /Users/indrekraag/wa1:
    python3 server.py            # binds 0.0.0.0:8765
    python3 server.py 8080       # custom port
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError
import json
import socket
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

KUREVERE_URL = (
    "https://tarktee.mnt.ee/tarktee/rest/services/road_weather_stations/"
    "MapServer/0/query?where=site_name=%27Kurevere%27&outFields=*&f=json"
)
EMHI_URL = "https://raw.githubusercontent.com/indrekraag/weatherapp2/data/emhi.json"

UPSTREAM_TIMEOUT = 12  # seconds


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/kurevere"):
            self._proxy(KUREVERE_URL, label="kurevere")
            return
        if self.path.startswith("/api/emhi"):
            self._proxy(EMHI_URL, label="emhi")
            return
        super().do_GET()

    def _proxy(self, url, label):
        try:
            req = urllib_request.Request(
                url,
                headers={
                    "User-Agent": "Madise-iPad-Kiosk/1.0",
                    "Accept": "application/json,*/*",
                },
            )
            with urllib_request.urlopen(req, timeout=UPSTREAM_TIMEOUT) as resp:
                body = resp.read()
                ctype = resp.headers.get("Content-Type", "application/json")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except HTTPError as e:
            self._err(e.code, f"{label}: upstream HTTP {e.code}")
        except URLError as e:
            self._err(502, f"{label}: {e.reason}")
        except Exception as e:
            self._err(500, f"{label}: {e}")

    def _err(self, code, msg):
        payload = json.dumps({"error": msg}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    host_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
    except OSError:
        pass
    print(f"Serving on http://{host_ip}:{PORT}/  (open this URL on the iPad)")
    print(f"  • static files from {server.RequestHandlerClass.__name__}'s directory")
    print(f"  • /api/kurevere → {KUREVERE_URL[:60]}…")
    print(f"  • /api/emhi     → {EMHI_URL[:60]}…")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
