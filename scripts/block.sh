#!/usr/bin/env bash
# Mô phỏng sự cố mạng ngay trong container API (cổng 8000, chỉ chặn giao diện eth0 để health check nội bộ không bị ảnh hưởng)
#   ./scripts/block.sh api3 drop     # firewall BỎ GÓI: client chờ trong im lặng  -> kết nối TREO tới timeout
#   ./scripts/block.sh api3 reject   # firewall TRẢ RST: client biết ngay là bị từ chối -> LỖI NGAY
#   ./scripts/block.sh api3 off      # gỡ chặn
set -euo pipefail
svc="${1:?tên service, ví dụ api3}"; mode="${2:?drop|reject|off}"
ipt() { docker compose exec -T "$svc" iptables "$@"; }
case "$mode" in
  drop)   ipt -I INPUT -i eth0 -p tcp --dport 8000 -j DROP ;;
  reject) ipt -I INPUT -i eth0 -p tcp --dport 8000 -j REJECT --reject-with tcp-reset ;;
  off)    ipt -F INPUT ;;
  *) echo "mode phải là drop|reject|off"; exit 1 ;;
esac
echo "$svc: $mode xong"; ipt -S INPUT
