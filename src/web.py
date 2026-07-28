"""Giao diện web cục bộ cho demo ReAct Agent, không cần API key hay thư viện ngoài."""

import json
import os
import errno
from contextlib import redirect_stdout
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import StringIO
from urllib.parse import urlparse

from app import run_react_agent
from providers import MockProvider


PAGE = """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Demo Trợ lý Đơn hàng</title>
  <style>
    :root { color-scheme: dark; --bg:#0d1322; --panel:#18223a; --line:#304262; --accent:#7dd3fc; --muted:#a8b6ce; }
    * { box-sizing:border-box; } body { margin:0; min-height:100vh; font:16px/1.5 system-ui,sans-serif; background:linear-gradient(135deg,#0d1322,#152c4b); color:#eff6ff; }
    main { width:min(860px,100%); margin:0 auto; padding:32px 18px; } h1 { margin:0; font-size:clamp(1.5rem,5vw,2.25rem); } .sub { color:var(--muted); margin:.35rem 0 1.25rem; }
    .badge { display:inline-block; padding:.2rem .6rem; border:1px solid #2dd4bf; border-radius:999px; color:#99f6e4; font-size:.85rem; }
    #messages { display:grid; gap:12px; min-height:320px; } .message { padding:14px 16px; border:1px solid var(--line); border-radius:14px; white-space:pre-wrap; overflow-wrap:anywhere; }
    .user { background:#213b64; margin-left:12%; } .agent { background:var(--panel); margin-right:4%; } .label { display:block; color:var(--accent); font-size:.8rem; font-weight:700; margin-bottom:4px; }
    .suggestions { display:flex; flex-wrap:wrap; gap:8px; margin:16px 0; } button { cursor:pointer; color:inherit; } .suggestions button { border:1px solid var(--line); background:#172c4b; border-radius:999px; padding:7px 10px; }
    form { display:flex; gap:10px; margin-top:18px; } input { flex:1; min-width:0; padding:13px; border:1px solid var(--line); border-radius:10px; color:inherit; background:#101b30; font:inherit; } form button { border:0; border-radius:10px; padding:0 18px; background:#38bdf8; color:#082f49; font-weight:750; }
    details { margin-top:10px; color:var(--muted); } pre { white-space:pre-wrap; overflow-wrap:anywhere; padding:12px; background:#0b1220; border-radius:10px; font-size:.82rem; }
    .error { color:#fecaca; } @media (max-width:560px) { form { flex-direction:column; } form button { padding:12px; } }
  </style>
</head>
<body><main>
  <span class="badge">Dữ liệu demo · Offline Mock</span>
  <h1>Trợ lý tra cứu đơn hàng</h1>
  <p class="sub">Hỏi về các mã demo bên dưới. Mỗi câu hỏi chạy ReAct với dữ liệu giả lập và hiển thị trace tool.</p>
  <p class="sub"><strong>Đơn đã giao:</strong> HD123, HD234, HD345 · <strong>Đơn bị từ chối đổi trả:</strong> HD456, HD567, HD678, HD789</p>
  <section id="messages" aria-live="polite"><div class="message agent"><span class="label">TRỢ LÝ</span>Xin chào! Tôi có thể tra cứu đơn hàng hoặc hỗ trợ đổi trả trong dữ liệu demo.</div></section>
  <div class="suggestions">
    <button type="button" data-question="Kiểm tra thông tin và trạng thái của đơn hàng HD123.">Tra cứu HD123</button>
    <button type="button" data-question="Đơn hàng HD123 của tôi bị rộng size, hãy kiểm tra và tạo phiếu đổi giúp tôi.">Đổi trả HD123</button>
    <button type="button" data-question="Kiểm tra thông tin đơn hàng HD345.">Tra cứu HD345</button>
    <button type="button" data-question="Tôi muốn đổi trả đơn hàng HD567.">Đổi trả HD567</button>
    <button type="button" data-question="Tôi muốn đổi trả đơn hàng HD789.">Đổi trả HD789</button>
  </div>
  <form id="chat-form"><input id="question" maxlength="2000" autocomplete="off" placeholder="Ví dụ: Đơn HD123 của tôi đang ở đâu?" required><button>Gửi</button></form>
</main>
<script>
const messages = document.querySelector('#messages');
const input = document.querySelector('#question');
const form = document.querySelector('#chat-form');
function addMessage(role, content, trace) {
  const item = document.createElement('div'); item.className = `message ${role}`;
  const label = document.createElement('span'); label.className = 'label'; label.textContent = role === 'user' ? 'BẠN' : 'TRỢ LÝ';
  const text = document.createElement('div'); text.textContent = content; item.append(label, text);
  if (trace) { const details = document.createElement('details'); const summary = document.createElement('summary'); summary.textContent = 'Xem ReAct trace'; const pre = document.createElement('pre'); pre.textContent = trace; details.append(summary, pre); item.append(details); }
  messages.append(item); item.scrollIntoView({behavior:'smooth', block:'end'}); return item;
}
async function ask(question) {
  addMessage('user', question); input.value = ''; const waiting = addMessage('agent', 'Đang tra cứu dữ liệu demo…');
  try {
    const res = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question})});
    const data = await res.json(); waiting.remove();
    if (!res.ok) throw new Error(data.error || 'Không thể xử lý yêu cầu.');
    addMessage('agent', data.answer, data.trace);
  } catch (err) { waiting.remove(); const item = addMessage('agent', err.message); item.classList.add('error'); }
}
form.addEventListener('submit', event => { event.preventDefault(); const question = input.value.trim(); if (question) ask(question); });
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => ask(button.dataset.question)));
</script></body></html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if urlparse(self.path).path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = PAGE.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Không tìm thấy API."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            question = payload.get("question", "")
            if not isinstance(question, str):
                raise ValueError("question must be a string")
            question = question.strip()
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Dữ liệu gửi lên không hợp lệ."})
            return

        if not isinstance(question, str) or not question or len(question) > 2000:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Câu hỏi phải dài từ 1 đến 2000 ký tự."})
            return

        trace = StringIO()
        with redirect_stdout(trace):
            answer = run_react_agent(question, MockProvider())
        self._send_json(HTTPStatus.OK, {"answer": answer, "trace": trace.getvalue()})

    def log_message(self, _format: str, *_args: object) -> None:
        """Không in access log để terminal demo gọn hơn."""


def create_server(start_port: int) -> tuple[HTTPServer, int]:
    """Tìm một cổng localhost trống, bắt đầu từ PORT hoặc 8000."""
    for port in range(start_port, start_port + 20):
        try:
            return HTTPServer(("127.0.0.1", port), DemoHandler), port
        except OSError as error:
            if error.errno != errno.EADDRINUSE:
                raise
    raise OSError(f"Không tìm được cổng trống từ {start_port} đến {start_port + 19}.")


def main() -> None:
    requested_port = int(os.getenv("PORT", "8000"))
    server, port = create_server(requested_port)
    if port != requested_port:
        print(f"Cổng {requested_port} đang được dùng; chuyển sang cổng {port}.")
    print(f"Demo web đang chạy tại http://127.0.0.1:{port}")
    print("Nhấn Ctrl+C để dừng server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng demo web.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
