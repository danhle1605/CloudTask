# Tổng Hợp Kết Quả Thực Nghiệm Đo Tải K6 (PaaS vs IaaS)
> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành
> **Repository:** https://github.com/danhle1605/CloudTask
> **Cơ sở dữ liệu chung:** Neon PostgreSQL 16 (Serverless Managed Database, Region Singapore - ap-southeast-1)

---

## 1. Bảng 1: So Sánh Hiệu Năng PaaS (Render) và IaaS (Azure VM)

| Chỉ số đo lường | PaaS: Render Web Service | IaaS: Azure Linux VM | Nhận xét đối chứng |
| :--- | :---:| :---:| :--- |
| **Nền tảng hạ tầng & Cấu hình** | Render Web Service (Free Tier, 512MB RAM, shared CPU) | Azure Linux VM (`Standard_B2ats_v2` / `B1s`, Ubuntu 24.04 LTS) | PaaS được quản lý tự động; IaaS tự cấu hình Docker Engine và mở port 5000. |
| **Target URL** | `https://cloudtask-z2wm.onrender.com` | `http://57.158.98.189:5000` *(IP tại thời điểm đo)* | PaaS tích hợp sẵn Cloudflare HTTPS; IaaS chạy HTTP trực tiếp qua cổng 5000. |
| **Tải tối đa (Virtual Users - VUs)** | **20 VUs** | **20 VUs** | 3 giai đoạn: 30s ramp-up -> 1m duy trì tải tối đa 20 VUs -> 30s ramp-down. |
| **Thời lượng thực thi** | 2 phút (~120s) | 2 phút (~120s) | Cùng chu kỳ tải để bảo đảm tính tương quan thống kê. |
| **Tổng số HTTP Requests hoàn thành** | **3.132 requests** | **2.718 requests** | Render xử lý được số request nhiều hơn 15,2% trong cùng khoảng thời gian. |
| **Throughput trung bình** | **26,04 requests/giây** | **22,42 requests/giây** | Thông lượng xử lý của PaaS cao hơn khoảng 16,1% so với máy ảo Azure. |
| **Tỷ lệ lỗi (Error Rate)** | **0,00%** *(0 lỗi / 3.132)* | **0,00%** *(0 lỗi / 2.718)* | Cả hai môi trường đạt độ ổn định 100% không có request nào bị timeout hoặc lỗi 5xx. |
| **Độ trễ trung bình (Average Latency)**| **96,79 ms** | **124,31 ms** | PaaS có độ trễ trung bình nhanh hơn 22,1%. |
| **Độ trễ phân vị 95 (p95 Latency)** | **118,56 ms** | **419,80 ms** | **Đạt ngưỡng đồ án (< 1500 ms)**. PaaS vượt trội nhờ đặt cùng Region Singapore với Neon DB. |
| **File dữ liệu thô (Raw JSON)** | `k6/results_paas_final.json` | `k6/results_iaas.json` | Lưu trữ trực tiếp trong repository làm chứng cứ đối chiếu. |

---

## 2. Bảng 2: So Sánh Hiệu Năng Mở Rộng Quy Mô (Scaling 1 instance vs 2 instances + HAProxy)

| Chỉ số đo lường | 1 instance (Đơn lẻ) | 2 instances (+ HAProxy) | Tỷ lệ thay đổi |
| :--- | :---:| :---:| :---: |
| **Tổng số HTTP Requests hoàn thành** | 2.298 | 3.165 | **Tăng +37,7%** |
| **Throughput trung bình** | 19,06 req/s | 26,28 req/s | **Tăng +37,9%** |
| **Độ trễ trung bình (Average Latency)** | 254,42 ms | 91,73 ms | **Giảm 64,0%** |
| **Độ trễ phân vị 95 (p95 Latency)** | 791,16 ms | 220,95 ms | **Giảm 72,1%** |
| **Tỷ lệ lỗi (Error Rate)** | 0,00% | 0,00% | Giữ vững 0,00% |
| **File dữ liệu thô (Raw JSON)** | `k6/results_iaas_1_instance.json` | `k6/results_iaas_2_instances.json` | Minh chứng thực nghiệm trong repository. |

*Phân tích kết quả Scaling:*
- p95 latency giảm mạnh từ 791,16 ms xuống 220,95 ms (giảm 72,1%).
- Thông lượng tăng từ 19,06 req/s lên 26,28 req/s (tăng 37,9%).
- Việc áp dụng 2 container sau HAProxy (Round Robin) giúp san sẻ tải hiệu quả, giảm hiện tượng tắc nghẽn I/O khi kết nối cơ sở dữ liệu Neon.

---

## 3. Ngưỡng Kiểm Thử (Thresholds) & Kết Luận Thực Nghiệm

Cả hai bài đo đều được kiểm chứng tự động theo các ngưỡng quy định trong `k6/load_test.js`:
- `custom_error_rate`: `rate < 0.05` (Tỷ lệ lỗi phải dưới 5%) -> Thực tế đạt **0,00%**.
- `custom_req_duration`: `p(95) < 1500ms` -> Render đạt **118,56 ms**, Azure VM đạt **419,80 ms**, 2 instances đạt **220,95 ms**.

*Giới hạn thực nghiệm:* Kịch bản k6 tập trung vào các endpoint kiểm tra tính sẵn sàng (`/health/live`, `/health/ready` thực thi truy vấn DB `SELECT 1`) và trang đăng nhập (`/login`). Kịch bản không thực hiện ghi dữ liệu nặng liên tục (heavy write CRUD) lên CSDL Production của đồ án để bảo vệ an toàn cho dữ liệu chung.
