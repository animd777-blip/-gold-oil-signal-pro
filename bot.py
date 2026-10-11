import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
PORT = int(os.environ.get("PORT", "10000"))


def telegram(method, data=None):
    if not BOT_TOKEN:
        return {"ok": False, "description": "Bot token is not configured"}

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    body = json.dumps(data or {}).encode()

    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())


def reply(chat_id, text):
    telegram("sendMessage", {
        "chat_id": chat_id,
        "text": text
    })


def handle_update(update):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip().lower()

    if not chat_id:
        return

    if text in ("/start", "/help"):
        reply(
            chat_id,
            "Welcome to Gold Oil Signal Pro!\n\n"
            "Markets: XAUUSD (Gold) and USOIL (US Oil)\n"
            "Trading approach: 4H trend -> 1H structure -> "
            "15M confirmation\n\n"
            "Commands:\n"
            "/status - check bot setup status\n"
            "/signals - check signal-engine status\n\n"
            "IMPORTANT: Live market data is not connected yet. "
            "No live BUY or SELL signals are being issued."
        )

    elif text == "/status":
        reply(
            chat_id,
            "Bot service code is running if this message is received.\n"
            "Market feed: not connected\n"
            "Signal engine: not active\n"
            "Risk preference: $2 per trade; target minimum 1:2 R:R."
        )

    elif text == "/signals":
        reply(
            chat_id,
            "WAIT - no verified live signal is available yet.\n"
            "A market-price feed and tested strategy are required "
            "before signals can be generated."
        )

    else:
        reply(chat_id, "Use /start, /status, or /signals.")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gold Oil Signal Pro service is running.")

    def do_POST(self):
        if self.path != "/telegram-webhook":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            update = json.loads(self.rfile.read(length).decode())
            handle_update(update)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print("Gold Oil Signal Pro service started")
    server.serve_forever()
