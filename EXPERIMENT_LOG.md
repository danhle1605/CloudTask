# Nhật Ký Thực Nghiệm & So Sánh Vận Hành PaaS (Render) và IaaS (Linux VM)
> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành
> **Repository:** https://github.com/danhle1605/CloudTask
> **Cơ sở dữ liệu chung:** Neon PostgreSQL 16 (Managed Database, Singapore)

---

## 1. Bảng So Sánh Thực Nghiệm Định Lượng và Vận Hành (PaaS vs IaaS)

> [!NOTE]
> Bảng tổng hợp minh chứng thực nghiệm giữa hai mô hình triển khai. Các mục đã có dữ liệu thực tế được ghi rõ số đo kèm nguồn kiểm chứng từ log k6 hoặc hệ thống. Các mục chưa triển khai đo đạc thực tế được ghi nhận trung thực là **"Chưa đo"** hoặc **"Chưa có bằng chứng"**, tuyệt đối không giả định số liệu.

| STT | Tiêu chí đánh giá / Metric | PaaS (Render Web Service) | IaaS (Azure Linux VM + Docker) | Nguồn dữ liệu / Phương pháp xác minh |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Thời gian cấu hình môi trường ban đầu (phút)** | ~ 5 - 10 phút *(ước tính ban đầu)* | ~ 20 - 30 phút *(ước tính)* | PaaS: Liên kết GitHub & nạp biến trên Web. IaaS: Cấu hình Azure VM, SSH, cài Docker, mở cổng Firewall 5000. |
| 2 | **Thời gian deploy lần đầu (giây)** | Chưa đo chính xác bằng đồng hồ | Chưa đo chính xác bằng đồng hồ | Cần bấm giờ từ lúc bắt đầu build container đến khi health check đạt 200 OK. |
| 3 | **Thời gian deploy phiên bản cập nhật (giây)** | Chưa đo chính xác bằng đồng hồ | Chưa đo chính xác bằng đồng hồ | Thời gian rebuild/redeploy sau khi cập nhật mã nguồn. |
| 4 | **k6 - p95 Latency riêng cho `/health/ready` (ms)** | Chưa đo riêng trong script k6 | Chưa đo riêng trong script k6 | Metric `custom_req_duration` trong `k6/load_test.js` hiện gộp chung cả 3 endpoint (`/health/ready`, `/health/live`, `/login`). |
| 5 | **k6 - p95 Latency tổng hợp HTTP (`custom_req_duration`) (ms)** | **100.17 ms** *(Avg: 88.24 ms, p50: 86.14 ms)* | **478.44 ms** *(Avg: 146.79 ms, p50: 72.88 ms)* | PaaS: 3.189 điểm đo (`results_paas.json`). IaaS: 2.604 điểm đo trên Azure Linux VM IP `57.158.98.189` (`results_iaas.json`, 31/10/2026). |
| 6 | **k6 - Error Rate (`custom_error_rate`) (%)** | **0.00%** *(0 lỗi / 3.189 lượt kiểm tra)* | **0.00%** *(0 lỗi / 2.604 lượt kiểm tra)* | Cả hai môi trường đều đạt 100% check thành công với 20 Virtual Users đồng thời trong kịch bản k6. |
| 7 | **Thời gian phát hiện lỗi (giây)** | Chưa đo | Chưa đo | Cần kịch bản thử nghiệm sự cố có kiểm soát (ví dụ: ngắt kết nối database kiểm thử). |
| 8 | **Thời gian thao tác rollback / deploy khôi phục (giây)** | **18 giây** *(Deploy khôi phục)* | Chưa đo | Đo đạc chính xác từ timestamp log Render: Bắt đầu deploy lúc 17:44:28, hoàn tất kiểm tra health check và live lúc 17:44:46 (18 giây). |
| 9 | **Tổng thời gian phục hồi dịch vụ (MTTR) (giây)** | **~ 20 - 25 giây** *(ước tính)* | Chưa đo | Bao gồm thời gian kỹ sư nhận diện và thao tác bấm Rollback trên Web UI (~5-7s) cộng thời gian deploy khôi phục của nền tảng (18s). |
| 10 | **Công sức cấu hình và số bước vận hành** | Thấp (~ 4 bước cấu hình trên giao diện Web) | Trung bình - Cao (~ 10-12 lệnh cấu hình Linux & Docker) | Đếm số thao tác UI/CLI cần thực hiện để đưa dịch vụ vào hoạt động ổn định. |
| 11 | **Số thành phần nhóm trực tiếp quản trị** | 1 thành phần *(Mã nguồn ứng dụng & Biến môi trường)* | 4 thành phần *(Hệ điều hành, Docker Daemon, Firewall/Network cổng 5000, App Container)* | Ranh giới trách nhiệm giữa nhà cung cấp nền tảng và nhóm phát triển. |
| 12 | **Chi phí ước tính hàng tháng ($)** | $0/tháng *(Free Tier)* hoặc $7/tháng *(Starter)* | ~$4 - $6/tháng *(VPS 1 vCPU, 1GB RAM)* | Bảng giá niêm yết chính thức của Render và Azure/DigitalOcean ngày 29/10/2026. |

---

## 2. Kết Luận Thực Nghiệm Đối Chứng PaaS (Render) và IaaS (Azure Linux VM)

1. **Hiệu năng xử lý tải và Độ ổn định:**
   - **Tỷ lệ thành công:** Cả PaaS (Render) và IaaS (Azure Linux VM tại IP `57.158.98.189`) đều hoàn thành 100% các lượt kiểm thử với tỷ lệ lỗi **0.00%** (2.604/2.604 checks pass trên IaaS và 3.189/3.189 checks pass trên PaaS).
   - **Độ trễ phản hồi (p95 latency):**
     + PaaS (Render Singapore) đạt p95 là **100.17 ms** (trung bình 88.24 ms).
     + IaaS (Azure Linux VM) đạt p95 là **478.44 ms** (trung bình 146.79 ms, trung vị 72.88 ms).
     + Cả hai nền tảng đều đáp ứng xuất sắc ngưỡng cam kết chất lượng của đồ án (ngưỡng p95 đề ra là `< 1500 ms`).

2. **Đánh giá về câu hỏi nghiên cứu (PaaS rút ngắn thời gian triển khai đến mức nào? Đổi lại mất quyền kiểm soát gì?):**
   - **Thời gian và Công sức Triển khai:**
     + **PaaS (Render):** Rút ngắn đáng kể thời gian đưa ứng dụng vào hoạt động (~5-10 phút). Không cần cài đặt máy chủ, không cần cấu hình reverse proxy, tự động tích hợp SSL/HTTPS và pipeline CI/CD từ GitHub.
     + **IaaS (Linux VM):** Tốn nhiều thời gian và công sức hơn (~20-30 phút ban đầu), đòi hỏi kỹ sư phải có kiến thức quản trị Linux, bảo mật SSH, mở port firewall (Inbound port 5000), quản lý tiến trình Docker daemon và giám sát tài nguyên máy chủ.
   - **Khả năng Phục hồi (Rollback):**
     + **PaaS:** Hỗ trợ rollback 1-click tức thì qua giao diện dashboard, tự động lấy lại image cũ và phục hồi dịch vụ chỉ trong **18 giây** (MTTR ~20-25s).
     + **IaaS:** Cần thao tác thủ công qua SSH (`git checkout` commit hash cũ, rebuild container hoặc chuyển image tag).
   - **Sự đánh đổi về Quyền kiểm soát & Giới hạn:**
     + PaaS tiện lợi nhưng nhóm bị giới hạn quyền truy cập sâu (không có quyền root OS, không tùy chỉnh kernel, gói Free bị sleep sau 15 phút idle).
     + IaaS mang lại quyền kiểm soát tuyệt đối trên máy chủ, không bị phụ thuộc vào chính sách nền tảng (Vendor Lock-in), nhưng đổi lại gánh nặng bảo trì và vận hành hoàn toàn thuộc về nhóm phát triển.

---

## 3. Quy Trình và Kịch Bản Thực Nghiệm Chi Tiết

### A. Kiểm thử tải bằng k6
Cài đặt k6:
- Windows: `choco install k6` hoặc `winget install k6`
- Linux: `sudo gpg -k && sudo apt-get install k6`

Thực thi kịch bản đo đồng nhất trên cả 2 nền tảng:
```bash
# 1. Đo kiểm trên Render PaaS
k6 run -e TARGET_URL=https://<your-render-url>.onrender.com -e VUS=20 -e DURATION=1m --out json=k6/results_paas.json k6/load_test.js

# 2. Đo kiểm trên Linux VM IaaS
k6 run -e TARGET_URL=http://<VM_IP>:5000 -e VUS=20 -e DURATION=1m --out json=k6/results_iaas.json k6/load_test.js
```

### B. Quy trình Đo Đạc Rollback trên Render (PaaS)
1. Đăng nhập Render Dashboard -> Chọn service `cloudtask`.
2. Vào tab **Events** hoặc **Deploys**.
3. Xác định bản deploy thành công gần nhất trước sự cố (hiển thị trạng thái "Live").
4. Bắt đầu bấm giờ -> Nhấn vào biểu tượng ba chấm `...` bên cạnh bản deploy đó -> Chọn **Rollback to this deploy**.
5. Quan sát log triển khai và liên tục gửi probe kiểm tra endpoint phục hồi:
   ```bash
   curl -i https://<your-render-url>.onrender.com/health/ready
   ```
6. Dừng bấm giờ ngay khi endpoint trả về `HTTP 200 {"status":"ready"}` -> Ghi nhận thời gian phục hồi thực tế vào bảng.

### C. Quy trình Đo Đạc Rollback trên Linux VM (IaaS)
1. SSH vào Linux VM:
   ```bash
   ssh user@<VM_IP>
   cd /opt/cloudtask
   ```
2. Xác định commit hash hoặc image tag hoạt động ổn định:
   ```bash
   git log --oneline -n 5
   ```
3. Bắt đầu bấm giờ -> Chuyển mã nguồn về commit ổn định (hoặc image tag trước đó):
   ```bash
   git checkout <STABLE_COMMIT_HASH>
   ```
4. Build lại và tái khởi động container ứng dụng:
   ```bash
   docker compose -f docker-compose.iaas.yml up -d --build
   ```
5. Kiểm tra health check xác nhận phục hồi:
   ```bash
   curl -i http://localhost:5000/health/ready
   ```
6. Dừng bấm giờ khi container vượt qua health check thành công -> Ghi nhận tổng thời gian vào bảng.

---

## 4. Bảng Ước Tính Chi Phí (Nguồn và Ngày Ghi Nhận)

- **Ngày khảo sát giá:** 29/10/2026.
- **Nguồn:**
  - Render Pricing: https://render.com/pricing (Free Tier: $0/tháng, 512MB RAM, shared CPU; Starter: $7/tháng).
  - Neon PostgreSQL: https://neon.tech/pricing (Free Tier: 0.5 GiB storage, $0/tháng).
  - AWS EC2 / DigitalOcean Droplet: 1 vCPU, 1GB RAM (~$4 - $6/tháng).
- **So sánh TCO (Tổng chi phí sở hữu):**
  - **PaaS (Render):** Tiết kiệm chi phí nhân công vận hành ban đầu (zero sysadmin), phù hợp nhóm nhỏ, nhược điểm là chi phí scale theo instance tăng nhanh hơn.
  - **IaaS (Linux VM):** Chi phí tài nguyên tính toán rẻ hơn khi chạy 24/7 tải cao, nhưng tốn chi phí thời gian bảo trì hệ điều hành, cập nhật bảo mật, firewall và cấu hình Docker.
