# ==============================================================================
# BÁO CÁO BÀN GIAO DATABASE VÀ HẠ TẦNG (THÀNH VIÊN 2 -> THÀNH VIÊN 1)
# Đề tài số 8: Phát triển ứng dụng PaaS có CSDL được quản lý và đánh giá gánh nặng vận hành
# ==============================================================================

Xin chào Thành viên 1 (Phụ trách Hạ tầng & Triển khai),

Thành viên 2 (Phụ trách Ứng dụng, Database Schema/Migration, Kiểm thử và CI/CD) bàn giao cấu hình cơ sở dữ liệu và hạ tầng để bạn triển khai ứng dụng CloudTask lên Render (PaaS) và Linux VM (IaaS).

---

## 1. THÔNG TIN DATABASE NEON POSTGRESQL

- **Tên Project đề xuất trên Neon**: `cloudtask-db`
- **PostgreSQL Version**: PostgreSQL 16 (phiên bản ổn định)
- **Region khuyến nghị**: `Asia Pacific (Singapore) - ap-southeast-1` (tối ưu độ trễ khi kết nối với Render)
- **Branch**: `main`
- **Database mặc định**: `cloudtask-db` (hoặc `neondb`)

### Cách lấy Connection String an toàn từ Neon:
1. Đăng nhập vào [https://neon.tech](https://neon.tech)
2. Vào Dashboard của project `cloudtask-db` -> tab **Dashboard**
3. Tìm phần **Connection Details** -> Chọn database và role mong muốn
4. Copy chuỗi kết nối dạng:
   `postgresql://neondb_owner:YOUR_PASSWORD@ep-sample-pooler.ap-southeast-1.aws.neon.tech/cloudtask-db?sslmode=require`
5. **LƯU Ý QUAN TRỌNG KHI CẤU HÌNH CHO FLASK**:
   Do ứng dụng sử dụng Psycopg 3, chuỗi `DATABASE_URL` phải có tiền tố `postgresql+psycopg://` (code của Thành viên 2 đã tự động chuẩn hóa tiền tố này qua hàm `normalize_db_url`, nhưng khuyến khích cấu hình chuẩn):
   `postgresql+psycopg://neondb_owner:YOUR_PASSWORD@ep-sample-pooler.ap-southeast-1.aws.neon.tech/cloudtask-db?sslmode=require`

> **NGUYÊN TẮC BẢO MẬT**: Tuyệt đối KHÔNG commit chuỗi kết nối chứa mật khẩu lên GitHub repository hoặc file README công khai!

---

## 2. DANH SÁCH BIẾN MÔI TRƯỜNG CẦN THIẾT

Cần cấu hình các biến này trên **Render Environment Variables** và file `.env` trên **Linux VM**:

| Tên biến | Giá trị mẫu / Ý nghĩa | Môi trường bắt buộc |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Cả hai |
| `SECRET_KEY` | Tạo chuỗi ngẫu nhiên 32+ ký tự (ví dụ: `python -c "import secrets; print(secrets.token_hex(32))"`) | Cả hai |
| `DATABASE_URL` | Connection string của Neon PostgreSQL (xem Mục 1) | Cả hai |
| `GROUP_INVITE_CODE` | `CLOUDTASK-GROUP-8` (Mã mời để 3 thành viên vào chung 1 workspace) | Cả hai |
| `APP_VERSION` | `v1.0.0` | Cả hai |
| `SESSION_COOKIE_SECURE` | `true` (Render bật sẵn HTTPS; trên Linux VM nếu dùng domain có SSL thì bật true) | Cả hai |

---

## 3. CÁCH CHẠY DATABASE MIGRATION AN TOÀN

Khi đã có database Neon và biến môi trường `DATABASE_URL`, chạy lệnh migration ban đầu để tạo 4 bảng (`users`, `workspaces`, `workspace_members`, `tasks`):

```bash
# Trong môi trường đã cài đặt requirements.txt
export DATABASE_URL="postgresql+psycopg://neondb_owner:YOUR_PASSWORD@ep-sample.../cloudtask-db?sslmode=require"
flask --app run.py db upgrade
```

**Khởi tạo dữ liệu mẫu (Seed Data) cho 3 thành viên demo**:
```bash
python seed.py
```
*Lệnh này sẽ tự động tạo workspace "CloudTask Team 8", 3 tài khoản demo cho 3 thành viên và 5 công việc mẫu.*

---

## 4. HƯỚNG DẪN CẤU HÌNH VÀ TRIỂN KHAI

### A. Triển khai Render (PaaS)
1. Kết nối kho GitHub của dự án vào Render.
2. Tạo mới một **Web Service**:
   - **Environment**: `Docker` (hoặc `Python 3`)
   - **Branch**: `main`
   - **Instance Type**: `Free` (hoặc Starter)
3. Điền các biến môi trường tại mục **Environment** theo bảng ở Mục 2.
4. Cấu hình **Health Check Path**: `/health/ready`
5. Lấy **Deploy Hook URL** từ Render Settings và thêm vào GitHub Repository Secret với tên `RENDER_DEPLOY_HOOK_URL` để GitHub Actions tự động kích hoạt triển khai khi test pass.

### B. Triển khai Linux VM (IaaS)
1. Cài đặt Docker và Docker Compose trên Linux VM:
   ```bash
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2
   sudo systemctl enable --now docker
   ```
2. Clone repository về VM:
   ```bash
   git clone https://github.com/danhle1605/CloudTask.git /opt/cloudtask
   cd /opt/cloudtask
   git checkout connect-neon-postgres
   ```
3. Tạo file `.env` trên VM từ `.env.example`, điền `DATABASE_URL` của Neon và `SECRET_KEY`.
4. Khởi chạy ứng dụng bằng Docker Compose dành riêng cho IaaS (không khởi chạy postgres local):
   ```bash
   docker compose -f docker-compose.iaas.yml up -d --build
   ```
5. Kiểm tra log và trạng thái container:
   ```bash
   docker compose -f docker-compose.iaas.yml ps
   docker compose -f docker-compose.iaas.yml logs -f web
   ```

---

## 5. XÁC MINH HAI MÔI TRƯỜNG KẾT NỐI ĐÚNG DATABASE

1. **Kiểm tra Health Endpoint**:
   - Truy cập `https://<render-app-url>/health/ready` -> Trả về `{"status":"ready","database":"connected"}`.
   - Truy cập `http://<vm-ip>:5000/health/ready` -> Trả về kết quả tương tự.
2. **Kiểm tra tính bền vững và đồng bộ dữ liệu của Workspace chung**:
   - Đăng nhập trên Render bằng tài khoản Thành viên 1 (`member1@cloudtask.local` / `CloudTask2026!`).
   - Tạo một công việc mới: *"Test đồng bộ từ PaaS Render"*.
   - Mở trình duyệt truy cập ứng dụng trên Linux VM, đăng nhập bằng tài khoản Thành viên 2 (`member2@cloudtask.local` / `CloudTask2026!`).
   - Tải lại trang: Công việc *"Test đồng bộ từ PaaS Render"* phải xuất hiện ngay lập tức trên Linux VM.
   - Xóa công việc đó trên Linux VM -> Tải lại trang trên Render: công việc đã biến mất.
   => **Kết luận**: Cả hai môi trường chia sẻ 100% dữ liệu thống nhất trên Neon PostgreSQL managed database.
