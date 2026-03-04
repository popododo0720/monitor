#!/usr/bin/env python3
"""Topology config API — read/write config.json on server."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/api/config":
            return self._resp(404, {"error": "not found"})
        try:
            with open(CONFIG) as f:
                data = f.read()
        except FileNotFoundError:
            data = "{}"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data.encode())

    def do_POST(self):
        if self.path != "/api/config":
            return self._resp(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            json.loads(body)  # validate JSON
        except Exception:
            return self._resp(400, {"error": "invalid json"})
        with open(CONFIG, "w") as f:
            f.write(body.decode())
        self._resp(200, {"ok": True})

    def _resp(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def log_message(self, format, *args):
        pass  # suppress request logs


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8999), Handler)
    print("Topology API listening on 127.0.0.1:8999")
    server.serve_forever()
