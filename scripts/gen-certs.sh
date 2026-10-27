#!/usr/bin/env bash
# Tạo chứng chỉ tự ký cho nginx (chỉ dùng cho lab)
set -euo pipefail
cd "$(dirname "$0")/../certs"
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout server.key -out server.crt \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null
chmod 644 server.key server.crt   # để container nginx đọc được
echo "OK: certs/server.crt + certs/server.key"
