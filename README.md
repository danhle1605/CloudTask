# CloudTask — Đồ Án Điện Toán Đám Mây (Đề Tài Số 8)

**Tên đề tài chính thức**: *Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành* — Đề tài 8, Chương 2.  
**Câu hỏi nghiên cứu**: *PaaS rút ngắn thời gian triển khai đến mức nào, và đổi lại nhóm phát triển mất quyền kiểm soát hoặc gặp những giới hạn gì?*

---

## 1. KIẾN TRÚC VÀ CÔNG NGHỆ

### Sơ đồ Kiến trúc 1: PaaS (Render)
```
[Người dùng]
     │
     ▼ (HTTPS)
[Render PaaS Web Service] ──(Gunicorn / Flask Stateless)
     │
     ▼ (TLS / SSL Pooling)
[Neon PostgreSQL (Managed Database Cloud - Singapore)]
     ▲
     │ (Chạy pytest & Migrations tự động khi push code)
[GitHub Actions CI/CD Pipeline]
```

### Sơ đồ Kiến trúc 2: IaaS (Linux VM)
```
[Người dùng]
     │
     ▼ (HTTP / Port 5000)
[Azure Linux VM (Ubuntu 24.04 LTS)]
     │
     ▼ (Docker Engine & Docker Compose)
[Container: cloudtask_iaas_web (Gunicorn / Flask)]
     │
     ▼ (TLS / SSL Pooling)
[Neon PostgreSQL (Giữ cố định cùng Database để so sánh gánh nặng tầng App)]
```

### Ngăn xếp Công nghệ
- **Backend**: Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Psycopg 3.
- **Frontend**: HTML5, CSS3 hiện đại (Giao diện SaaS tông Navy/Blue/White), Bootstrap 5, JavaScript.
- **Bảo mật & Phiên làm việc**: Flask-WTF, CSRF Protection, Werkzeug Password Hashing, HTTPOnly Secure Cookies.
- **Database**: PostgreSQL 16 trên Neon (Serverless Managed Database, Region Singapore).
- **Container & Web Server**: Docker, Docker Compose, Gunicorn (Production), Waitress (Local dev).
- **Kiểm thử**: pytest, pytest-cov (Coverage > 80%).
- **Tự động hóa CI/CD**: GitHub Actions.
- **Công cụ đo tải**: k6.

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
CloudTask/
├── .github/workflows/ci.yml       # Pipeline CI/CD trên GitHub Actions
├── app/                           # Mã nguồn Flask Application
│   ├── static/                    # CSS, JavaScript, Assets
│   ├── templates/                 # Jinja2 Templates (HTML)
│   ├── config.py                  # Cấu hình môi trường (Twelve-Factor)
│   ├── extensions.py              # Khởi tạo db, migrate, csrf
│   ├── forms.py                   # Form validation (Flask-WTF)
│   ├── models.py                  # SQLAlchemy Database Models
│   └── routes.py                  # Controllers & Health Check Endpoints
├── db/schema.sql                  # Schema cơ sở dữ liệu mẫu
├── migrations/                    # Quản lý schema database bằng Alembic
├── tests/                         # Bộ kiểm thử tự động pytest
├── k6/                            # Kịch bản và kết quả kiểm thử tải k6
│   ├── load_test.js               # Kịch bản đo tải PaaS & IaaS
│   ├── crud_load_test.js          # Kịch bản kiểm thử tải luồng CRUD
│   └── RESULTS_SUMMARY.md         # Báo cáo tổng hợp số liệu đo tải thực tế
├── docker-compose.yml             # Chạy môi trường phát triển cục bộ
├── docker-compose.iaas.yml        # Chạy môi trường IaaS (Linux VM)
├── Dockerfile                     # Cấu hình đóng gói container ứng dụng
├── EXPERIMENT_LOG.md              # Bảng so sánh thực nghiệm định lượng PaaS vs IaaS
├── HANDOVER_INFRA.md              # Báo cáo bàn giao kiến trúc và vận hành hạ tầng
├── render.yaml                    # Bản thiết kế triển khai tự động trên Render PaaS
├── requirements.txt               # Thư viện phụ thuộc cho Production
├── requirements-dev.txt           # Thư viện phục vụ kiểm thử và phân tích tĩnh
└── wsgi.py                        # Điểm khởi chạy Gunicorn WSGI
```

---

## 3. HƯỚNG DẪN KHỞI CHẠY ỨNG DỤNG CỤC BỘ (LOCAL)

### Bước 1: Sao chép file cấu hình môi trường
```powershell
cp .env.example .env
```
Điền chuỗi kết nối PostgreSQL cục bộ hoặc Neon vào biến `DATABASE_URL`.

### Bước 2: Chạy bằng Docker Compose (Khuyên dùng)
```powershell
docker compose up -d --build
```
Dừng container:
```powershell
docker compose down
```

---

## 4. QUẢN LÝ DATABASE VÀ MIGRATION

Ứng dụng tuân thủ nguyên tắc không dùng `db.create_all()` trên production mà dùng Flask-Migrate / Alembic:
- **Áp dụng migration mới nhất vào database**:
  ```bash
  flask --app run.py db upgrade
  ```
- **Tạo migration mới khi thay đổi models.py**:
  ```bash
  flask --app run.py db migrate -m "mo_ta_thay_doi"
  ```

---

## 5. HEALTH CHECK VÀ LOGGING (TWELVE-FACTOR APP)

- **GET `/health/live`**: Liveness probe kiểm tra tiến trình web đang chạy (HTTP 200).
- **GET `/health/ready`**: Readiness probe kiểm tra kết nối tới CSDL Neon PostgreSQL (`SELECT 1`). Trả về HTTP 200 khi sẵn sàng và HTTP 503 nếu mất kết nối database.
- **Logging**: Toàn bộ log của ứng dụng và Gunicorn được xuất ra `stdout`/`stderr` theo chuẩn Twelve-Factor. Thông tin nhạy cảm (mật khẩu, database connection string) tuyệt đối không được ghi ra log.

---

## 6. KIỂM THỬ TỰ ĐỘNG (PYTEST)

Chạy kiểm thử với coverage kiểm tra chất lượng mã nguồn:
```bash
pytest -q
```

---

## 7. ĐO TẢI VÀ THỰC NGHIỆM HIỆU NĂNG BẰNG K6

Kịch bản đo tải đồng nhất 20 VUs trong 2 phút được lưu tại `k6/load_test.js`:
```bash
# Đo tải trên PaaS Render:
k6 run -e TARGET_URL=https://cloudtask-z2wm.onrender.com --out json=k6/results_paas.json k6/load_test.js

# Đo tải trên IaaS Azure Linux VM:
k6 run -e TARGET_URL=http://<VM_IP>:5000 --out json=k6/results_iaas.json k6/load_test.js
```
Chi tiết bảng so sánh các chỉ số thực nghiệm xem tại [`k6/RESULTS_SUMMARY.md`](file:///d:/ĐTĐM/k6/RESULTS_SUMMARY.md) và [`EXPERIMENT_LOG.md`](file:///d:/ĐTĐM/EXPERIMENT_LOG.md).

---

## 8. BẢNG SO SÁNH GÁNH NẶNG VẬN HÀNH: PAAS (RENDER) VS IAAS (AZURE VM)

| Chỉ số / Tiêu chí | Kết quả PaaS (Render) | Kết quả IaaS (Azure Linux VM) | Cách đo / Nguồn dữ liệu | Nhận xét & Giới hạn thực tế |
| :--- | :--- | :--- | :--- | :--- |
| **Thời gian triển khai ban đầu** | ~ 5 - 10 phút *(ước tính)* | ~ 20 - 30 phút *(ước tính)* | Bấm giờ từ lúc bắt đầu tạo tài nguyên đến khi `/health/ready` trả về HTTP 200. | PaaS chỉ cần liên kết Git và set env. IaaS phải tạo VM, SSH, cài Docker, mở port firewall 5000. |
| **Số bước cấu hình thủ công** | ~ 4 bước (Tạo service, gán env, chọn branch, cấu hình health check) | ~ 12 bước (SSH, apt update, cấu hình Azure NSG, cài Docker, clone git, cấu hình env, quản lý container...) | Đếm số lệnh CLI và thao tác UI thực tế. | IaaS yêu cầu kỹ năng quản trị Linux và Docker sâu hơn nhiều. |
| **Công sức bảo trì định kỳ** | Rất thấp (Nhà cung cấp tự động vá lỗi OS, mạng, kernel, SSL renewal) | Cao (Phải tự chạy apt upgrade, vá lỗ hổng Linux, quản lý log và dọn dẹp Docker container) | Phân tích ranh giới trách nhiệm vận hành. | Gói PaaS Free tự sleep sau 15 phút không có request (cold start ~27s). |
| **Số thành phần nhóm trực tiếp quản lý** | 1 thành phần (Mã nguồn Flask và biến môi trường) | 4 thành phần (Hệ điều hành Linux, Docker daemon, Firewall/Network cổng 5000, App Container) | Sơ đồ phân rã kiến trúc. | Trên IaaS nếu Docker daemon bị crash, nhóm phải tự restart hoặc viết systemd service. |
| **Độ trễ p95 (p95 Latency)** | **100.17 ms** | **478.44 ms** | Lấy từ chỉ số `custom_req_duration: p(95)` của file `k6/results_paas.json` và `k6/results_iaas.json`. | Cả hai môi trường cùng kết nối Neon Singapore. PaaS đạt p95 nhanh hơn nhờ mạng nội vùng Singapore. |
| **Tỷ lệ lỗi (Error Rate)** | **0.00%** *(0 / 3.189 requests)* | **0.00%** *(0 / 2.604 requests)* | Chỉ số `custom_error_rate` trong báo cáo k6. | Cả hai môi trường chịu tải 20 VUs xuất sắc với 0 lỗi. |
| **Thời gian Rollback khi bản phát hành lỗi** | **18 giây** *(Deploy khôi phục)* | *Chưa đo thực tế* | Bấm nút Rollback trên Render UI so với chạy `git checkout <tag> && docker compose rebuild` trên VM. | Render hỗ trợ rollback 1-click tức thì qua commit hash. IaaS cần thao tác terminal thủ công. |
| **Chi phí ước tính / tháng** | $0/tháng (Free Tier) hoặc $7/tháng (Starter) | ~$5.50/tháng (Azure B1s: 1 vCPU, 1GB RAM) | Bảng giá chính thức của Render & Azure Portal ngày 29/10/2026. | PaaS miễn phí cho thử nghiệm đồ án; IaaS tính phí theo giờ máy ảo chạy thực tế. |
| **Mức độ kiểm soát & Vendor Lock-in** | Thấp: Bị giới hạn quyền root, không tùy biến kernel, không can thiệp sâu timeout. Phụ thuộc quy trình deploy của Render. | Tuyệt đối: Toàn quyền root, tự do cài đặt monitoring agent, tùy biến reverse proxy, không phụ thuộc nhà cung cấp. | Phân tích quyền hạn và runtime limitations. | Ứng dụng CloudTask viết theo chuẩn Docker & Twelve-Factor nên có thể chuyển đổi linh hoạt giữa PaaS và IaaS. |

---

## 9. QUY TRÌNH THỰC NGHIỆM THỬ LỖI VÀ ROLLBACK

1. **Bước 1 (Ghi nhận bản ổn định)**: Xác nhận phiên bản `v1.0.0` đang chạy ổn định, `/health/ready` trả về HTTP 200.
2. **Bước 2 (Tạo bản lỗi có chủ đích)**: Trên môi trường thử nghiệm, cố tình làm hỏng cấu hình kết nối database để tạo release lỗi.
3. **Bước 3 (Quan sát cảnh báo)**:
   - Truy cập `/health/ready` -> Trả về HTTP 503 (`database: disconnected`).
   - Kiểm tra log trên Render / Docker: Xuất hiện log lỗi kết nối rõ ràng.
4. **Bước 4 (Thực hiện Rollback)**:
   - Trên **Render**: Vào mục **Deploys** -> Chọn bản deploy trước đó -> Nhấn **Rollback to this deploy**.
   - Trên **Linux VM**: Chạy `git checkout <STABLE_COMMIT_HASH> && docker compose -f docker-compose.iaas.yml up -d --build`.
5. **Bước 5 (Xác minh phục hồi)**:
   - Kiểm tra `/health/ready` trả về 200.
   - Dữ liệu các công việc trên Neon PostgreSQL vẫn được bảo toàn nguyên vẹn 100%.

---

## 10. CHECKLIST BÀN GIAO VÀ MINH CHỨNG CHO BÁO CÁO

- [x] Mã nguồn hoàn thiện, không TODO, không dùng code giả lập.
- [x] Workspace chia sẻ chung cho 3 thành viên (`CLOUDTASK-GROUP-8`).
- [x] Database migration Alembic được kiểm tra thực tế trên PostgreSQL.
- [x] Dockerfile & Docker Compose hỗ trợ linh hoạt chạy local hoặc Neon.
- [x] Toàn bộ kiểm thử pytest tự động vượt qua (Pass 100%, Coverage > 80%).
- [x] Workflow GitHub Actions cấu hình sẵn test container và Render deploy hook.
- [x] Kịch bản đo tải k6 sẵn sàng thu thập số liệu p95 và error rate.
- [x] Tài liệu bàn giao hạ tầng [HANDOVER_INFRA.md](file:///d:/ĐTĐM/HANDOVER_INFRA.md) cho Thành viên 1.
- [x] Nhật ký thực nghiệm và số liệu k6/rollback [EXPERIMENT_LOG.md](file:///d:/ĐTĐM/EXPERIMENT_LOG.md).
- [x] Báo cáo chi tiết số liệu đo tải đối chứng [RESULTS_SUMMARY.md](file:///d:/ĐTĐM/k6/RESULTS_SUMMARY.md).
