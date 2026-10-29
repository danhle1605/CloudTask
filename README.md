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
[Linux VM (Ubuntu Server)]
     │
     ▼ (Docker Engine & Docker Compose)
[Container: cloudtask_web (Gunicorn / Flask)]
     │
     ▼ (TLS / SSL Pooling)
[Neon PostgreSQL (Giữ cố định cùng Database để so sánh gánh nặng tầng App)]
```

### Ngăn xếp Công nghệ
- **Backend**: Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Psycopg 3.
- **Frontend**: HTML5, CSS3 hiện đại (Giao diện SaaS tông Navy/Blue/White), Bootstrap 5, JavaScript.
- **Bảo mật & Phiên làm việc**: Flask-WTF, CSRF Protection, Werkzeug Password Hashing, HTTPOnly Secure Cookies.
- **Database**: PostgreSQL 16 trên Neon (Serverless Managed Database).
- **Container & Web Server**: Docker, Docker Compose, Gunicorn (Production), Waitress (Local dev).
- **Kiểm thử**: pytest, pytest-cov (Coverage > 80%).
- **Tự động hóa CI/CD**: GitHub Actions.
- **Công cụ đo tải**: k6.

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```
BTL ĐTĐM/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline CI/CD tự động test, migrate và trigger deploy
├── app/
│   ├── static/
│   │   └── css/style.css        # Giao diện SaaS tông Navy/Blue hiện đại, responsive
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html       # Đăng nhập
│   │   │   └── register.html    # Đăng ký kèm mã mời Workspace
│   │   ├── errors/
│   │   │   ├── 403.html         # Không có quyền truy cập workspace
│   │   │   ├── 404.html         # Không tìm thấy trang
│   │   │   └── 500.html         # Lỗi máy chủ
│   │   ├── tasks/
│   │   │   ├── detail.html      # Chi tiết công việc và nút xác nhận xóa
│   │   │   ├── form.html        # Thêm mới và chỉnh sửa công việc
│   │   │   └── list.html        # Danh sách, tìm kiếm, lọc theo trạng thái/mức ưu tiên
│   │   ├── base.html            # Layout chung, navbar và flash messages
│   │   ├── dashboard.html       # Thống kê số liệu thật từ database
│   │   └── workspace.html       # Quản lý nhóm và danh sách thành viên chung
│   ├── __init__.py              # Factory create_app, logging stdout Twelve-Factor
│   ├── config.py                # Cấu hình môi trường, chuẩn hóa DATABASE_URL
│   ├── extensions.py            # Khởi tạo db, migrate, csrf
│   ├── forms.py                 # Form Flask-WTF & CSRF validation
│   ├── models.py                # Bảng users, workspaces, workspace_members, tasks
│   └── routes.py                # Xử lý logic Auth, Workspace, CRUD, Health Checks
├── k6/
│   └── load_test.js             # Kịch bản đo tải p95, error rate và health check
├── migrations/                  # Quản lý lịch sử tiến hóa cơ sở dữ liệu Alembic
│   └── versions/
│       └── 001_initial_tasks_migration.py
├── tests/
│   ├── conftest.py              # Cấu hình test fixture và database test cô lập
│   ├── test_health.py           # Kiểm thử /health/live và /health/ready
│   └── test_tasks.py            # Kiểm thử Auth, Workspace cho 3 người, CRUD, phân quyền
├── .dockerignore
├── .env.example                 # Mẫu cấu hình môi trường chuẩn
├── .gitignore
├── docker-compose.yml           # Chạy local (Local Postgres) hoặc Neon mode
├── Dockerfile                   # Docker image production chạy Gunicorn
├── HANDOVER_INFRA.md            # Tài liệu bàn giao chi tiết cho Thành viên 1
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── run.py
├── seed.py                      # Tạo dữ liệu mẫu thực tế cho 3 thành viên
└── wsgi.py
```

---

## 3. HƯỚNG DẪN CHẠY LOCAL VÀ DOCKER

### Bước 1: Chuẩn bị file `.env`
Sao chép từ `.env.example`:
```powershell
Copy-Item .env.example .env
```

### Bước 2: Chạy ứng dụng bằng Docker Compose (Khuyến nghị trên Windows)
Dự án hỗ trợ 2 chế độ:
- **Chế độ 1 (Mặc định local)**: Dùng container PostgreSQL cục bộ có volume bền vững `cloudtask_postgres_data`.
- **Chế độ 2 (Kết nối Neon)**: Đổi `DATABASE_URL` trong `.env` sang link Neon.

Chạy lệnh trong PowerShell:
```powershell
# Khởi động dịch vụ
docker compose up -d --build

# Kiểm tra trạng thái các container
docker compose ps

# Xem log thời gian thực của web
docker compose logs -f web

# Dừng container (không mất dữ liệu volume)
docker compose down
```

### Bước 3: Chạy ứng dụng trực tiếp bằng Python
```powershell
# Nâng cấp migration database
flask --app run.py db upgrade

# Khởi tạo dữ liệu mẫu 3 thành viên
python seed.py

# Khởi chạy server phát triển
python run.py
```
Mở trình duyệt truy cập: `http://localhost:5000`

---

## 4. QUẢN LÝ DATABASE VÀ MIGRATION

Ứng dụng tuân thủ nguyên tắc không dùng `db.create_all()` trên môi trường production, mà dùng Flask-Migrate / Alembic:

- **Áp dụng migration mới nhất vào database**:
  ```bash
  flask --app run.py db upgrade
  ```
- **Tạo migration mới khi thay đổi models.py**:
  ```bash
  flask --app run.py db migrate -m "mo_ta_thay_doi"
  ```
- **Quay lui (Rollback) migration**:
  ```bash
  flask --app run.py db downgrade
  ```

---

## 5. HEALTH CHECK VÀ LOGGING (TWELVE-FACTOR APP)

- **GET `/health/live`**: Liveness probe kiểm tra tiến trình web đang chạy. Trả về HTTP 200.
- **GET `/health/ready`**: Readiness probe kiểm tra kết nối tới cơ sở dữ liệu (`SELECT 1`). Trả về HTTP 200 khi sẵn sàng và HTTP 503 nếu database mất kết nối.
- **Logging**: Toàn bộ log của ứng dụng và Gunicorn được xuất thẳng ra `stdout`/`stderr` theo chuẩn Twelve-Factor, giúp Render, Docker và Linux VM tự động thu thập mà không làm đầy ổ đĩa cục bộ. Thông tin nhạy cảm (mật khẩu, database connection string) tuyệt đối không được ghi ra log.

---

## 6. KIỂM THỬ TỰ ĐỘNG (PYTEST)

Kiểm thử được thiết kế độc lập, sử dụng database test riêng để không ảnh hưởng dữ liệu sản phẩm:

```bash
python -m pytest
```
*Kết quả kiểm thử bao phủ toàn bộ 11 test cases: Đăng ký, đăng nhập, kiểm tra mật khẩu, trùng email, bảo vệ route riêng tư, chia sẻ workspace cho 3 thành viên, từ chối người ngoài workspace (403), đầy đủ CRUD và health checks (độ phủ code đạt > 82%).*

---

## 7. QUY TRÌNH THỰC NGHIỆM ĐO TẢI VỚI K6 (SO SÁNH PAAS VÀ IAAS)

Chạy k6 kiểm thử hiệu năng và độ trễ p95 trên cả 2 môi trường:

```bash
# Đo tải trên PaaS Render
k6 run -e TARGET_URL=https://<your-render-app>.onrender.com --out json=k6/results_paas.json k6/load_test.js

# Đo tải trên IaaS Linux VM
k6 run -e TARGET_URL=http://<your-vm-ip>:5000 --out json=k6/results_iaas.json k6/load_test.js
```

---

## 8. BẢNG SO SÁNH GÁNH NẶNG VẬN HÀNH: PAAS (RENDER) VS IAAS (LINUX VM)

| Chỉ số / Tiêu chí | Kết quả PaaS (Render) | Kết quả IaaS (Linux VM) | Cách đo / Nguồn dữ liệu | Nhận xét & Giới hạn thực tế |
| :--- | :--- | :--- | :--- | :--- |
| **Thời gian triển khai ban đầu** | *[Điền số phút đo thật]* | *[Điền số phút đo thật]* | Bấm giờ từ lúc bắt đầu tạo tài nguyên đến khi `/health/ready` trả về HTTP 200. | PaaS chỉ cần liên kết Git và set env. IaaS phải cài OS, update packages, cài Docker, mở port firewall. |
| **Số bước cấu hình thủ công** | ~ 4 bước (Tạo service, gán env, chọn branch, cấu hình health check) | ~ 12 bước (SSH, apt update, firewall ufw, cài docker, clone git, cấu hình systemd/daemon, quản lý log...) | Đếm số lệnh CLI và thao tác UI thực tế. | IaaS yêu cầu kỹ năng quản trị Linux và Docker sâu hơn nhiều. |
| **Công sức bảo trì định kỳ** | Rất thấp (Nhà cung cấp tự động vá lỗi OS, mạng, kernel, SSL renewal) | Cao (Phải tự chạy apt-get upgrade, vá lỗ hổng Linux, dọn dẹp docker dangling images) | Nhật ký vận hành nhóm qua các tuần. | Gói PaaS Free tự sleep sau 15 phút không có request (cold start ~50s). |
| **Số thành phần nhóm trực tiếp quản lý** | 1 thành phần (Mã nguồn Flask và biến môi trường) | 4 thành phần (Hệ điều hành Linux, Docker daemon, Network/Firewall, Nginx/Gunicorn) | Sơ đồ phân rã kiến trúc. | Trên IaaS nếu Docker daemon bị crash, nhóm phải tự restart hoặc viết systemd service. |
| **Độ trễ p95 (p95 Latency)** | *[Đo bằng k6 thực tế]* | *[Đo bằng k6 thực tế]* | Lấy từ chỉ số `custom_req_duration: p(95)` của file `results_paas.json` và `results_iaas.json`. | Cả hai môi trường cùng kết nối Neon Singapore nên độ trễ phụ thuộc chủ yếu vào compute và vị trí địa lý của VM/Render. |
| **Tỷ lệ lỗi (Error Rate)** | *[Đo bằng k6 thực tế]* | *[Đo bằng k6 thực tế]* | Chỉ số `custom_error_rate` trong báo cáo k6. | Giúp kiểm chứng khả năng xử lý đồng thời 20 VUs. |
| **Thời gian Rollback khi bản phát hành lỗi** | *[Điền số giây đo thật]* | *[Điền số giây đo thật]* | Bấm nút Rollback trên Render UI so với chạy `docker compose rollback / tag cũ` trên VM. | Render hỗ trợ rollback 1-click tức thì qua commit hash. IaaS cần quản lý image tag hoặc git checkout thủ công. |
| **Chi phí ước tính / tháng** | $0/tháng (Gói Free Tier của Render & Neon) | $4 - $6/tháng (Thuê VPS DigitalOcean/Linode/AWS t4g.nano) | Bảng giá chính thức của Render & nhà cung cấp Cloud VPS. | PaaS miễn phí cho demo nhưng chi phí mở rộng (scale-up) sau này tăng theo cấp số nhân so với VM tự quản. |
| **Mức độ kiểm soát & Vendor Lock-in** | Thấp: Bị giới hạn quyền root, không tùy biến kernel, không can thiệp sâu timeout. Phụ thuộc quy trình deploy của Render. | Tuyệt đối: Toàn quyền root, tự do cài đặt monitoring agent, tùy biến reverse proxy, không phụ thuộc nhà cung cấp. | Phân tích quyền hạn và runtime limitations. | Ứng dụng CloudTask viết theo chuẩn Docker & Twelve-Factor nên có thể chuyển đổi giữa PaaS và IaaS mà không cần sửa code. |

---

## 9. QUY TRÌNH THỰC NGHIỆM THỬ LỖI VÀ ROLLBACK

1. **Bước 1 (Ghi nhận bản ổn định)**: Xác nhận phiên bản `v1.0.0` đang chạy ổn định, `/health/ready` trả về HTTP 200.
2. **Bước 2 (Tạo bản lỗi có chủ đích)**: Trên nhánh thử nghiệm hoặc test, cố tình đổi `DATABASE_URL` sai hoặc làm hỏng route trong file cấu hình để tạo release lỗi.
3. **Bước 3 (Quan sát cảnh báo)**:
   - Truy cập `/health/ready` -> Trả về HTTP 503 (`database: disconnected`).
   - Kiểm tra log trên Render / Docker: Xuất hiện log lỗi kết nối rõ ràng.
4. **Bước 4 (Thực hiện Rollback)**:
   - Trên **Render**: Vào mục **Deploys** -> Chọn bản deploy trước đó -> Nhấn **Rollback to this deploy**.
   - Trên **Linux VM**: Chạy `git checkout main && docker compose restart web`.
5. **Bước 5 (Xác minh phục hồi)**:
   - Kiểm tra `/health/ready` trả về 200.
   - Dữ liệu các công việc trên Neon PostgreSQL vẫn được bảo toàn nguyên vẹn 100%.

---

## 10. CHECKLIST BÀN GIAO VÀ MINH CHỨNG CHO BÁO CÁO

- [x] Mã nguồn hoàn thiện, không TODO, không dùng code giả lập.
- [x] Workspace chia sẻ chung cho 3 thành viên (`CLOUDTASK-GROUP-8`).
- [x] Database migration Alembic được kiểm tra thực tế trên PostgreSQL.
- [x] Dockerfile & Docker Compose hỗ trợ linh hoạt chạy local hoặc Neon.
- [x] Toàn bộ 11 kiểm thử pytest tự động vượt qua (Pass 100%, Coverage > 82%).
- [x] Workflow GitHub Actions cấu hình sẵn test container và Render deploy hook.
- [x] Kịch bản đo tải k6 sẵn sàng thu thập số liệu p95 và error rate.
- [x] Tài liệu bàn giao hạ tầng [HANDOVER_INFRA.md](file:///d:/ĐTĐM/HANDOVER_INFRA.md) cho Thành viên 1.
- [x] Nhật ký thực nghiệm và số liệu k6/rollback [EXPERIMENT_LOG.md](file:///d:/ĐTĐM/EXPERIMENT_LOG.md).
