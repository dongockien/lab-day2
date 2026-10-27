#!/usr/bin/env bash
# Bắt gói tin TRONG network namespace của container HAProxy (hoặc nginx), lưu pcap để mở bằng Wireshark.
#   ./scripts/capture.sh haproxy "tcp port 8081 or tcp port 8000" captures/l4.pcap
#   ./scripts/capture.sh nginx   "tcp port 443"                  captures/tls.pcap
set -euo pipefail
target="${1:-haproxy}"; filter="${2:-tcp}"; out="${3:-captures/out.pcap}"
mkdir -p captures
echo "Đang bắt trên $target với filter: $filter  (Ctrl+C để dừng) -> $out"
docker run --rm -it --net "container:$(docker compose ps -q "$target")" \
  -v "$PWD/captures:/captures" nicolaka/netshoot \
  tcpdump -i any -nn -s 0 -w "/captures/$(basename "$out")" $filter
