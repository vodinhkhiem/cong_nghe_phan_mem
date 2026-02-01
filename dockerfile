# Sử dụng Python 3.11 bản nhẹ (Slim) để tiết kiệm dung lượng
FROM python:3.11-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Cài đặt các công cụ hệ thống cần thiết cho SQL Server (pymssql)
# (Bước này cực quan trọng, thiếu là lỗi kết nối ngay)
RUN apt-get update && apt-get install -y \
    gcc \
    freetds-dev \
    freetds-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy file thư viện vào trước để tận dụng Cache (Build nhanh hơn)
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt
# Copy toàn bộ code vào container
COPY . .

# Mở cổng 9999 (để khớp với code của bạn)
EXPOSE 9999

# Lệnh chạy ứng dụng (Giả sử code nằm trong thư mục src)
CMD ["python", "src/app.py"]