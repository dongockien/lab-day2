FROM python:3.12-alpine
# iptables chỉ để mô phỏng "firewall bỏ gói" trong lab (cần cap NET_ADMIN)
RUN apk add --no-cache iptables
WORKDIR /app
COPY app.py .
EXPOSE 8000
CMD ["python", "-u", "app.py"]
