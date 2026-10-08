"""Workflow Automation Hub — a local web page of buttons that run your processes.

Run:  python -m hub.app      then open http://127.0.0.1:8765
Uses only the Python standard library. Listens on this PC only (127.0.0.1).
"""

import datetime
import json
import logging
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .actions import ACTIONS, ActionError, load_all

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
CONFIG_PATH = ROOT / "config.json"
LOG_DIR = ROOT / "logs"
PORT = 8765

log = logging.getLogger("hub")


def load_config():
    path = CONFIG_PATH if CONFIG_PATH.exists() else ROOT / "config.example.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def public_actions(config):
    """Action metadata for the page (no functions), with dropdown options filled in."""
    out = []
    for a in ACTIONS.values():
        fields = []
        for f in a["fields"]:
            f = dict(f)
            if "options_from" in f:
                f["options"] = list(config.get(f.pop("options_from"), {}))
            fields.append(f)
        out.append({k: a[k] for k in ("id", "title", "description", "category")} | {"fields": fields})
    return out


def run_action(action_id, inputs, config):
    a = ACTIONS.get(action_id)
    if not a:
        raise ActionError(f"Unknown action: {action_id}")
    for f in a["fields"]:
        if f.get("required") and not str(inputs.get(f["name"], "")).strip():
            raise ActionError(f"'{f['label']}' is required.")
    return a["run"](inputs, config)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/actions":
            config = load_config()
            self._send(200, {"actions": public_actions(config), "links": config.get("quick_links", [])})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        # Block other websites from triggering actions: browsers cannot send this
        # custom header cross-origin without a CORS preflight, which we never approve.
        if self.headers.get("X-Hub-Request") != "1" or not self.path.startswith("/api/run/"):
            self._send(403, {"ok": False, "message": "Forbidden"})
            return
        action_id = self.path.rsplit("/", 1)[-1]
        inputs = {}
        try:
            length = int(self.headers.get("Content-Length", 0))
            inputs = json.loads(self.rfile.read(length) or b"{}")
            result = run_action(action_id, inputs, load_config())
            if not isinstance(result, dict):
                result = {"message": result}
            log.info("OK   %s %s -> %s", action_id, inputs, result["message"])
            self._send(200, {"ok": True, **result})
        except (ActionError, ValueError) as e:
            log.warning("FAIL %s %s -> %s", action_id, inputs, e)
            self._send(400, {"ok": False, "message": str(e)})
        except Exception as e:  # unexpected bug: log full trace, show short message
            log.exception("ERROR %s", action_id)
            self._send(500, {"ok": False, "message": f"Unexpected error: {e}"})

    def log_message(self, *args):  # keep the console quiet
        pass


def main():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / f"hub-{datetime.date.today():%Y-%m}.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    load_all()
    if not CONFIG_PATH.exists():
        print("NOTE: config.json not found - using config.example.json. Copy it to config.json and edit.")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Workflow Hub running at {url}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
