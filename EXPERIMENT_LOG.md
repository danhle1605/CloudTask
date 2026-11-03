# Nhật Ký Thực Nghiệm & So Sánh Vận Hành PaaS (Render) và IaaS (Linux VM)
> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành
> **Repository:** https://github.com/danhle1605/CloudTask
> **Cơ sở dữ liệu chung:** Neon PostgreSQL 16 (Serverless Managed Database, Region Singapore)

---

## 1. Bảng So Sánh Thực Nghiệm Định Lượng và Vận Hành (PaaS vs IaaS)

> [!NOTE]
> Bảng tổng hợp minh chứng thực nghiệm giữa hai mô hình triển khai. Số liệu đo lường hiệu năng tải k6 được đồng bộ chính xác với đợt đo cuối cùng (`k6/results_paas_final.json` và `k6/results_iaas.json`).

| STT | Tiêu chí đánh giá / Metric | PaaS (Render Web Service) | IaaS (Azure Linux VM + Docker) | Nguồn dữ liệu / Phương pháp xác minh |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Thời gian cấu hình môi trường ban đầu (phút)** | ~ 5 - 10 phút *(ước tính)* | ~ 20 - 30 phút *(ước tính)* | PaaS: Liên kết GitHub & nạp biến trên Render Dashboard. IaaS: Cấu hình Azure VM `Standard_B2ats_v2` / `B1s`, SSH, cài Docker/Git, mở inbound port 5000 trên Network Security Group. |
| 2 | **Thời gian deploy lần đầu (giây)** | Chưa đo chính xác bằng đồng hồ | Chưa đo chính xác bằng đồng hồ | Cần bấm giờ từ lúc bắt đầu build container đến khi health check đạt 200 OK. |
| 3 | **Thời gian deploy phiên bản cập nhật (giây)** | Khoảng 20s (tính từ lúc Gunicorn start đến health check 200 OK) | **15,59 giây** | Đo từ lệnh `docker compose up -d --build` trên Azure đến khi health check đạt 200 OK. |
| 4 | **k6 - Số lượng requests hoàn thành (2 phút)** | **3.132 requests** | **2.718 requests** | Tải tối đa 20 VUs qua kịch bản `k6/load_test.js`. |
| 5 | **k6 - Throughput trung bình (req/s)** | **26,04 req/s** | **22,42 req/s** | Render xử lý được thông lượng cao hơn 16,1% so với máy ảo Azure. |
| 6 | **k6 - Average Latency (ms)** | **96,79 ms** | **124,31 ms** | PaaS có độ trễ trung bình nhanh hơn 22,1%. |
| 7 | **k6 - p95 Latency tổng hợp HTTP (ms)** | **118,56 ms** | **419,80 ms** | Điểm đo từ file dữ liệu `results_paas_final.json` và `results_iaas.json`. Render vượt trội nhờ mạng nội vùng Singapore. |
| 8 | **k6 - Error Rate (%)** | **0,00%** *(0 lỗi / 3.132)* | **0,00%** *(0 lỗi / 2.718)* | Cả hai môi trường đều đạt 100% check thành công với tải 20 Virtual Users đồng thời trong 2 phút. |
| 9 | **Thời gian phát hiện lỗi (giây)** | Chưa đo bằng đồng hồ | Chưa đo bằng đồng hồ | Cần kịch bản thử nghiệm sự cố có kiểm soát (cố tình ngắt kết nối database kiểm thử). |
| 10 | **Thời gian thao tác rollback / deploy khôi phục (giây)** | **18 giây** *(Deploy khôi phục)* | **4,41 giây** | Render: Thao tác 1-click Rollback trên UI (17:44:28 đến 17:44:46 UTC). Azure: `git checkout <hash> && docker compose restart`. |
| 11 | **Công sức cấu hình và số bước vận hành** | Thấp (~ 4 bước cấu hình trên giao diện Web) | Trung bình - Cao (~ 10-12 lệnh cấu hình Linux & Docker) | Đếm số thao tác UI/CLI cần thực hiện để đưa dịch vụ vào hoạt động ổn định. |
| 12 | **Số thành phần nhóm trực tiếp quản trị** | 1 thành phần *(Mã nguồn ứng dụng & Biến môi trường)* | 4 thành phần *(Hệ điều hành, Docker Daemon, Firewall/Network cổng 5000, App Container)* | Ranh giới trách nhiệm giữa nhà cung cấp nền tảng và nhóm phát triển. |
| 13 | **Chi phí ước tính hàng tháng ($)** | $0/tháng *(Free Tier)* hoặc $7/tháng *(Starter)* | ~$7,50 - $10,50/tháng (Azure VM) + Disk + IP | Bảng giá niêm yết chính thức của Render và Azure Portal. Thực tế nhóm dùng credit Azure for Students. |

---

## 2. Hai Bảng Số Liệu p95 Bắt Buộc

### Bảng 1: So sánh hiệu năng PaaS (Render) và IaaS (Azure VM)

| Chỉ số | Render (PaaS) | Azure VM (IaaS) |
|---|---:|---:|
| **Average Latency** | **96,79 ms** | **124,31 ms** |
| **p95 Latency** | **118,56 ms** | **419,80 ms** |
| **Error rate** | **0%** | **0%** |
| **Throughput** | **26,04 req/s** | **22,42 req/s** |
| **Tổng Requests** | **3.132** | **2.718** |

*Định nghĩa p95:* Phân vị thứ 95 nghĩa là 95% số request có độ trễ nhỏ hơn hoặc bằng giá trị p95 ghi nhận.

---

### Bảng 2: So sánh hiệu năng Scaling trên IaaS (1 instance vs 2 instances + HAProxy)

| Chỉ số | 1 instance (Đơn lẻ) | 2 instances (+ HAProxy) | Tỷ lệ thay đổi |
|---|---:|---:|:---:|
| **Average Latency** | **254,42 ms** | **91,73 ms** | **Giảm 64,0%** |
| **p95 Latency** | **791,16 ms** | **220,95 ms** | **Giảm 72,1%** |
| **Error rate** | **0%** | **0%** | **0%** |
| **Throughput** | **19,06 req/s** | **26,28 req/s** | **Tăng +37,9%** |
| **Tổng Requests** | **2.298** | **3.165** | **Tăng +37,7%** |

*Nhận xét về Scaling:*
- p95 latency giảm mạnh từ 791,16 ms xuống 220,95 ms (giảm 72,1%).
- Average latency giảm từ 254,42 ms xuống 91,73 ms (giảm 64,0%).
- Throughput tăng từ 19,06 req/s lên 26,28 req/s (tăng 37,9%).
- *Lưu ý:* Hai instance được triển khai dưới dạng 2 container trên cùng một máy ảo Azure Linux, điều phối lưu lượng qua HAProxy với thuật toán Round Robin.

---

## 3. Nhật Ký Chi Tiết Thực Nghiệm Rollback và Deployment

| Kịch bản / Thao tác | PaaS (Render) | IaaS (Azure VM) | Ghi chú & Nguồn trích xuất |
| :--- | :---:| :---:| :--- |
| **Thời gian Rollback bản lỗi** | **18 giây** | **4,41 giây** | Render: 1-click rollback trên UI (log: 17:44:28 - 17:44:46 UTC). Azure: lệnh terminal Git checkout và restart. |
| **Thời gian Deployment mới** | ~20 giây *(Gunicorn -> Health 200)* | **15,59 giây** | Azure đo từ lúc chạy `docker compose up -d --build` đến khi health check 200 OK. |
| **Health Check sau khôi phục** | HTTP 200 OK | HTTP 200 OK | Endpoint `/health/ready` xác nhận database đã kết nối trở lại. |

---

## 4. Minh Bạch Về Cấu Hình Môi Trường

1. **Trạng thái máy ảo Azure VM:** Máy ảo `Standard_B2ats_v2` / `Standard_B1s` hiện được Stop (Deallocated) để bảo toàn hạn mức tín dụng sinh viên (Azure for Students $100).
2. **Swap memory:** Trong quá trình thiết lập máy ảo, lệnh `fallocate` gặp thông báo `Text file busy`. Do đó, tài liệu ghi nhận swap là chưa xác minh hoạt động để đảm bảo tính khách quan.
3. **Phạm vi kịch bản đo tải k6:** Kịch bản `k6/load_test.js` tập trung kiểm tra tính ổn định của `/health/ready` (truy vấn DB), `/health/live` và `/login`. Kịch bản không thực hiện ghi dữ liệu nặng (heavy write CRUD) lên CSDL Production của đồ án.
