#!/usr/bin/env python3
"""API nhỏ để làm lab L4/L7. Cả 3 bản sao chạy cùng code, khác nhau ở biến NAME."""
import json, os, socket, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

NAME = os.environ.get("NAME") or socket.gethostname()
BIND = os.environ.get("BIND", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))


def log(msg):
    now = time.time()
    print(f"{time.strftime('%H:%M:%S', time.localtime(now))}.{int(now * 1000) % 1000:03d} [{NAME}] {msg}", flush=True)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"   # cho phép keep-alive
    server_version = "tinyapi/1.0"

    def log_message(self, *args):   # tắt log mặc định, tự log bên dưới
        pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Served-By", NAME)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        t0 = time.time()
        u = urlparse(self.path)
        q = parse_qs(u.query)
        rid = self.headers.get("X-Request-ID", "-")

        if u.path == "/health":                       # health check: không log cho đỡ ồn
            return self._json(200, {"status": "ok", "replica": NAME})

        if u.path.startswith("/ai/stream"):           # SSE: giả lập chat AI trả từng token
            n = int(q.get("n", ["10"])[0])
            interval_ms = int(q.get("interval", ["300"])[0])
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Served-By", NAME)
            self.send_header("Connection", "close")   # không có Content-Length -> đóng kết nối khi xong
            self.end_headers()
            self.close_connection = True
            try:
                for i in range(n):
                    self.wfile.write(f"data: token-{i} from {NAME}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(interval_ms / 1000)
                self.wfile.write(b"event: done\ndata: end\n\n")
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                log(f"rid={rid} client ngắt giữa chừng khi stream")
            log(f"rid={rid} GET {self.path} stream xong {int((time.time() - t0) * 1000)}ms")
            return

        if u.path.startswith("/ai/slow"):             # giả lập inference mất ms mili-giây
            ms = int(q.get("ms", ["300"])[0])
            time.sleep(ms / 1000)
            self._json(200, {"replica": NAME, "path": u.path, "slept_ms": ms})
        elif u.path.startswith("/api/") or u.path.startswith("/ai/"):
            self._json(200, {
                "replica": NAME,
                "path": u.path,
                "peer": self.client_address[0],                       # IP mà backend NHÌN THẤY
                "x_forwarded_for": self.headers.get("X-Forwarded-For"),
                "request_id": rid,
            })
        else:
            self._json(404, {"error": "not found", "replica": NAME})
        log(f"rid={rid} GET {self.path} peer={self.client_address[0]} {int((time.time() - t0) * 1000)}ms")


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128


if __name__ == "__main__":
    log(f"listening on {BIND}:{PORT}")
    Server((BIND, PORT), Handler).serve_forever()
