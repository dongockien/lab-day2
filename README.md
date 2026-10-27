# Lab Ngày 2: L4 (HAProxy) và L7 (nginx)

Tài liệu hướng dẫn thực hành hệ thống cân bằng tải phân tầng (Tiered Load Balancing) kết hợp Layer 4 và Layer 7, tích hợp kiểm thử tải k6 và giả lập sự cố Firewall.

## Chạy nhanh

```bash
# 1. Sinh chứng chỉ bảo mật SSL tự ký
bash scripts/gen-certs.sh

# 2. Build và khởi chạy hệ thống
docker compose up -d --build

# 3. Kiểm tra L4 Load Balancer (Round Robin qua cổng 8081)
for i in 1 2 3 4 5 6; do curl -s localhost:8081/api/hello; echo; done

# 4. Kiểm tra L7 Content-Based Routing (Cổng 8082)
curl -s localhost:8082/api/hello; echo                                 # /api -> api1 | api2
curl -s localhost:8082/ai/hello;  echo                                 # /ai  -> api3

# 5. Mở trang thống kê HAProxy Dashboard
# Truy cập trực tiếp trên trình duyệt: http://localhost:8404

Bắn tải (k6) và kiểm tra Failover (Tắt node giữa chừng)
(Lưu ý cho người dùng Windows/Git Bash: sử dụng tiền tố MSYS_NO_PATHCONV=1 để tránh lỗi tự động đổi đường dẫn)
# Terminal 1: Chạy k6 bắn tải liên tục 60 giây qua L4
MSYS_NO_PATHCONV=1 docker compose run --rm k6 run -e TARGET=http://haproxy:8081 -e URL_PATH=/api/hello -e DURATION=60s /scripts/load.js

# Terminal 2 (Sau ~15 giây chạy k6): Chủ động tắt đột ngột api2 rồi bật lại để kiểm chứng Zero-Downtime Failover
docker compose stop api2 ; sleep 5 ; docker compose start api2

Mô phỏng sự cố Firewall (Bài học thực chiến NextX)
bash scripts/block.sh api3 drop     # DROP gói tin -> Kết nối treo tới hết ConnectTimeout (3s) rồi tự động failover an toàn
bash scripts/block.sh api3 reject   # Trả gói RST -> Báo lỗi kết nối ngay lập tức
bash scripts/block.sh api3 off      # Khôi phục trạng thái mạng bình thường

Bắt gói tin (Packet Capture)
bash scripts/capture.sh haproxy "tcp port 8081 or tcp port 8000" captures/l4.pcap

Dọn dẹp môi trường Lab
docker compose down -v

Lưu ý kỹ thuật
Môi trường chỉ dùng cho mục đích học tập và nghiên cứu (chứng chỉ tự ký, container có đặc quyền NET_ADMIN để giả lập iptables).

Đã được kiểm thử thực tế trên Windows (Git Bash + Docker Desktop) thành công.

### ✅ CHECKLIST CÁC BƯỚC LAB ĐÃ HOÀN THÀNH

Dựa trên tiến trình thực chiến của bạn, chúng ta đã kiểm chứng hoàn tất:
1. **Khởi tạo và Build hạ tầng:** Chạy mượt mà 6 container (HAProxy, 2 Nginx, 3 API Replicas).
2. **Kiểm chứng L4 (HAProxy - Cổng 8081):** Xác thực thuật toán Round Robin và nhận diện bản chất truyền tải TCP thô (`x_forwarded_for: null`).
3. **Kiểm chứng L7 (Nginx - Cổng 8082):** Xác thực tính năng định tuyến thông minh theo URL Path (`/api` vs `/ai`) và ghi nhận Header gốc đầy đủ.
4. **Kiểm thử tải bằng k6 & Failover:** Chứng minh hệ thống đạt `0.00%` lỗi (Zero Downtime) khi một node backend chết đột ngột giữa dòng traffic.
5. **Mô phỏng sự cố Firewall DROP:** Tái hiện chính xác thảm họa NextX và kiểm chứng dòng cứu sinh `ConnectTimeout = 3s` cắt đứt kết nối đúng hạn mức để chuyển hướng sang node dự phòng.
```
