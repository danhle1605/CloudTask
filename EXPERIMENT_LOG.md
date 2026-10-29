# Nhật Ký Thực Nghiệm & So Sánh Vận Hành PaaS (Render) và IaaS (Linux VM)
> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành
> **Repository:** https://github.com/danhle1605/CloudTask
> **Cơ sở dữ liệu chung:** Neon PostgreSQL 16 (Managed Database, Singapore)

---

## 1. Bảng So Sánh Thực Nghiệm Định Lượng và Vận Hành (PaaS vs IaaS)

> [!NOTE]
> Bảng tổng hợp minh chứng thực nghiệm giữa hai mô hình triển khai. Các mục đã có dữ liệu thực tế được ghi rõ số đo kèm nguồn kiểm chứng từ log k6 hoặc hệ thống. Các mục chưa triển khai đo đạc thực tế được ghi nhận trung thực là **"Chưa đo"** hoặc **"Chưa có bằng chứng"**, tuyệt đối không giả định số liệu.

| STT | Tiêu chí đánh giá / Metric | PaaS (Render Web Service) | IaaS (Linux VM + Docker) | Nguồn dữ liệu / Phương pháp xác minh |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Thời gian cấu hình môi trường ban đầu (phút)** | ~ 5 - 10 phút *(ước tính ban đầu)* | Chưa đo | Thao tác liên kết GitHub, tạo Web Service và nạp biến môi trường trên Render Dashboard. |
| 2 | **Thời gian deploy lần đầu (giây)** | Chưa đo chính xác bằng đồng hồ | Chưa đo | Cần bấm giờ từ lúc bắt đầu build container đến khi health check đạt 200 OK. |
| 3 | **Thời gian deploy phiên bản cập nhật (giây)** | Chưa đo chính xác bằng đồng hồ | Chưa đo | Thời gian Render tự động build & redeploy sau mỗi lần push commit. |
| 4 | **k6 - p95 Latency riêng cho `/health/ready` (ms)** | Chưa đo riêng trong script k6 | Chưa đo | Metric `custom_req_duration` trong `k6/load_test.js` hiện gộp chung cả 3 endpoint (`/health/ready`, `/health/live`, `/login`), chưa có metric Trend đo riêng biệt cho endpoint này. |
| 5 | **k6 - p95 Latency tổng hợp HTTP (`custom_req_duration`) (ms)** | **100.17 ms** *(Avg: 88.24 ms, p50: 86.14 ms)* | Chưa đo | Trích xuất từ 3.189 điểm đo trong file kết quả thực nghiệm `k6/results_paas.json` chạy ngày 30/10/2026. |
| 6 | **k6 - Error Rate (`custom_error_rate`) (%)** | **0.00%** *(0 lỗi / 3.189 lượt kiểm tra)* | Chưa đo | Metric `custom_error_rate` trong `k6/results_paas.json`. Điều kiện lỗi: HTTP status != 200 tại bất kỳ request nào. |
| 7 | **Thời gian phát hiện lỗi (giây)** | Chưa đo | Chưa đo | Cần kịch bản thử nghiệm sự cố có kiểm soát (ví dụ: ngắt kết nối database kiểm thử). |
| 8 | **Thời gian thao tác rollback / deploy khôi phục (giây)** | Chưa đo | Chưa đo | Thời gian từ lúc kỹ sư kích hoạt Rollback trên dashboard/CLI đến khi bản build cũ hoàn tất triển khai. *(Lưu ý: Thời gian deploy của Render không đồng nhất với tổng thời gian phục hồi).* |
| 9 | **Tổng thời gian phục hồi dịch vụ (MTTR) (giây)** | Chưa đo | Chưa đo | Đo từ thời điểm phát hiện lỗi, ra quyết định rollback cho đến khi endpoint `/health/ready` trả về HTTP 200 ổn định. |
| 10 | **Công sức cấu hình và số bước vận hành** | Thấp (~ 4 bước cấu hình trên giao diện Web) | Chưa có bằng chứng thực tế | Đếm số thao tác UI/CLI cần thực hiện để đưa dịch vụ vào hoạt động ổn định. |
| 11 | **Số thành phần nhóm trực tiếp quản trị** | 1 thành phần *(Mã nguồn ứng dụng & Biến môi trường)* | Dự kiến 4 thành phần *(Hệ điều hành, Docker Daemon, Firewall/Network, App Container)* | Ranh giới trách nhiệm giữa nhà cung cấp nền tảng và nhóm phát triển. |
| 12 | **Chi phí ước tính hàng tháng ($)** | $0/tháng *(Free Tier)* hoặc $7/tháng *(Starter)* | ~$4 - $6/tháng *(VPS 1 vCPU, 1GB RAM)* | Bảng giá niêm yết chính thức của Render và DigitalOcean/AWS ngày 29/10/2026. |

---

## 2. Kết Luận Thực Nghiệm Đo Tải PaaS (Render)

1. **Hiệu năng xử lý tải của PaaS (Render):**
   Kết quả đo tải thực nghiệm bằng k6 với kịch bản 20 người dùng ảo đồng thời (VUs) trong 1 phút ghi nhận tổng cộng 3.189 lượt request (bao gồm probe kiểm tra database `/health/ready`, liveness `/health/live` và giao diện `/login`). Độ trễ tổng hợp p95 đạt **100.17 ms**, độ trễ trung bình đạt **88.24 ms** và tỷ lệ lỗi là **0.00%**. Kết quả này chứng minh rằng khi instance đã ở trạng thái hoạt động (warm), PaaS Render kết hợp với Managed Database Neon tại cùng khu vực Singapore (`ap-southeast-1`) đáp ứng rất tốt yêu cầu hiệu năng và vượt xa ngưỡng cam kết chất lượng của đồ án (ngưỡng p95 đề ra là `< 1500 ms`).

2. **Đánh giá về câu hỏi nghiên cứu (PaaS rút ngắn thời gian triển khai đến mức nào?):**
   Ở giai đoạn hiện tại, nhóm **chưa có đủ bằng chứng định lượng đầy đủ** để khẳng định PaaS rút ngắn thời gian triển khai và giảm gánh nặng vận hành vượt trội so với IaaS, vì toàn bộ số liệu đối chứng trên môi trường Linux VM (IaaS) cũng như các phép đo thời gian rollback/phục hồi dịch vụ thực tế chưa được thực hiện độc lập.

3. **Các phép đo và thực nghiệm bắt buộc cần tiếp tục triển khai:**
   - Triển khai ứng dụng trên máy ảo Linux VM bằng `docker-compose.iaas.yml` và chạy cùng kịch bản k6 để thu thập số liệu đối chứng (p95 latency, error rate).
   - Đo đạc chính xác bằng đồng hồ bấm giờ: Thời gian cấu hình môi trường thực tế, thời gian deploy lần đầu và thời gian cập nhật giữa PaaS và IaaS.
   - Thực hiện kịch bản giả lập sự cố có kiểm soát trên môi trường thử nghiệm để đo lường chính xác: Thời gian phát hiện lỗi, thời gian thao tác rollback và tổng thời gian phục hồi dịch vụ (MTTR) trên cả hai nền tảng.

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
