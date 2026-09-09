# ============================================================
# 매출 REST API 서버 (파이썬 표준 라이브러리만 사용 — pip 설치 불필요)
# GET /sales?date=2026-04-29  →  {"records": [...]}
# ============================================================
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

SALES = {
    "2026-04-28": [
        {"channel": "web",    "clicks": 1200, "revenue": 350000},
        {"channel": "mobile", "clicks": 2100, "revenue": 520000},
    ],
    "2026-04-29": [
        {"channel": "web",    "clicks": 1350, "revenue": 410000},
        {"channel": "mobile", "clicks": 2400, "revenue": 610000},
        {"channel": "ads",    "clicks": 900,  "revenue": 180000},
    ],
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/sales":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found. use /sales?date=YYYY-MM-DD"}')
            return
        date = parse_qs(url.query).get("date", [""])[0]
        records = SALES.get(date, [])
        body = json.dumps({"date": date, "records": records}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # 콘솔 로그 간소화
        print("[sales-api]", fmt % args)


if __name__ == "__main__":
    print("sales-api 기동: http://0.0.0.0:5000/sales?date=2026-04-29")
    HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
