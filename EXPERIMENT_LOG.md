# Nhật Ký Thực Nghiệm & So Sánh Vận Hành PaaS (Render) và IaaS (Linux VM)
> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành
> **Repository:** https://github.com/danhle1605/CloudTask
> **Cơ sở dữ liệu chung:** Neon PostgreSQL 16 (Managed Database)

---

## 1. Mẫu Nhật Ký Thực Nghiệm (Ghi nhận thực tế)

> [!NOTE]
> Các trường số liệu bên dưới được giữ nguyên định dạng mẫu để thành viên phụ trách đo đạc điền kết quả đo thực tế từ k6 và môi trường vận hành. Tuyệt đối không tự bịa số liệu.

| Tiêu chí đo lường / Thực nghiệm | PaaS (Render Web Service) | IaaS (Linux VM + Docker) | Ghi chú / Phương pháp đo |
| :--- | :--- | :--- | :--- |
| **Cấu hình phần cứng instance** | Free / Starter (0.1 CPU, 512MB RAM) | [Điền cấu hình VM thực tế, ví dụ: 1 vCPU, 1GB RAM] | Thông số instance thực tế |
| **Hệ điều hành / Runtime** | Container hóa quản lý bởi Render | [Điền OS, ví dụ: Ubuntu 22.04 LTS] | Runtime môi trường máy chủ |
| **Số bước cấu hình ban đầu** | [Ghi nhận số bước thực tế] | [Ghi nhận số bước thực tế] | Số thao tác/lệnh từ lúc bắt đầu tới khi live |
| **Thời gian cấu hình (phút)** | [Đo thực tế] phút | [Đo thực tế] phút | Công sức thiết lập môi trường |
| **Thời gian deploy lần đầu (giây)** | [Đo thực tế] s | [Đo thực tế] s | Từ git push / build đến khi healthcheck 200 |
| **Thời gian deploy bản update (giây)** | [Đo thực tế] s | [Đo thực tế] s | Thời gian cập nhật phiên bản mới |
| **k6 - p95 Latency (/health/ready)** | [Đo từ kết quả k6] ms | [Đo từ kết quả k6] ms | Lệnh: `k6 run -e TARGET_URL=...` |
| **k6 - p95 Latency (Overall)** | [Đo từ kết quả k6] ms | [Đo từ kết quả k6] ms | Metric: `custom_req_duration` (p95) |
| **k6 - Error Rate (%)** | [Đo từ kết quả k6] % | [Đo từ kết quả k6] % | Metric: `custom_error_rate` |
| **Thời gian phát hiện lỗi (s)** | [Đo thực tế] s | [Đo thực tế] s | Giả lập lỗi qua health check |
| **Thời gian thực hiện rollback (s)** | [Đo thực tế] s | [Đo thực tế] s | Từ lúc bấm rollback/chuyển tag tới khi phục hồi |
| **Thời gian phục hồi dịch vụ (s)** | [Đo thực tế] s | [Đo thực tế] s | Health check quay lại trạng thái 200 OK |
| **Chi phí hàng tháng ước tính ($)** | [Tra cứu giá Render] | [Tra cứu giá nhà cung cấp VM] | Nguồn giá & ngày ghi nhận bên dưới |

---

## 2. Quy Trình và Kịch Bản Thực Nghiệm

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

### B. Quy trình Rollback trên Render (PaaS)
1. Đăng nhập Render Dashboard -> Chọn service `cloudtask`.
2. Vào tab **Events** hoặc **Deploys**.
3. Xác định bản deploy thành công gần nhất trước sự cố (hiển thị trạng thái "Live").
4. Nhấn vào biểu tượng ba chấm `...` bên cạnh bản deploy đó -> Chọn **Rollback to this deploy**.
5. Quan sát log triển khai và kiểm tra endpoint phục hồi:
   ```bash
   curl -i https://<your-render-url>.onrender.com/health/ready
   ```
6. Ghi nhận thời gian từ lúc bấm Rollback đến khi endpoint trả về `HTTP 200 {"status":"ready"}`.

### C. Quy trình Rollback trên Linux VM (IaaS)
1. SSH vào Linux VM:
   ```bash
   ssh user@<VM_IP>
   cd /opt/cloudtask
   ```
2. Xác định commit hash hoặc image tag hoạt động ổn định:
   ```bash
   git log --oneline -n 5
   ```
3. Chuyển mã nguồn về commit ổn định (hoặc image tag trước đó):
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
6. Ghi nhận thời gian từ lệnh checkout đến khi container vượt qua health check thành công.

---

## 3. Bảng Ước Tính Chi Phí (Nguồn và Ngày Ghi Nhận)

- **Ngày khảo sát giá:** 29/10/2026.
- **Nguồn:**
  - Render Pricing: https://render.com/pricing (Free Tier: $0/tháng, 512MB RAM, shared CPU; Starter: $7/tháng).
  - Neon PostgreSQL: https://neon.tech/pricing (Free Tier: 0.5 GiB storage, $0/tháng).
  - AWS EC2 / DigitalOcean Droplet: 1 vCPU, 1GB RAM (~$4 - $6/tháng).
- **So sánh TCO (Tổng chi phí sở hữu):**
  - **PaaS (Render):** Tiết kiệm chi phí nhân công vận hành ban đầu (zero sysadmin), phù hợp nhóm nhỏ, nhược điểm là chi phí scale theo instance tăng nhanh hơn.
  - **IaaS (Linux VM):** Chi phí tài nguyên tính toán rẻ hơn khi chạy 24/7 tải cao, nhưng tốn chi phí thời gian bảo trì hệ điều hành, cập nhật bảo mật, firewall và cấu hình Docker.
