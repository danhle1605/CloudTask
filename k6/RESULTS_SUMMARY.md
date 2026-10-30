# Tổng Hợp Kết Quả Thực Nghiệm Đo Tải K6 (PaaS vs IaaS)
> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành  
> **Repository:** https://github.com/danhle1605/CloudTask  
> **Cơ sở dữ liệu chung:** Neon PostgreSQL 16 (Serverless Managed Database, Region Singapore - ap-southeast-1)

---

## 1. Bảng Tổng Hợp Thông Số và Kết Quả Thực Nghiệm Đối Chứng

| Tiêu chí / Thông số đo lường | PaaS: Render Web Service | IaaS: Azure Linux VM (cloudtask-vm) | Nhận xét đối chứng |
| :--- | :--- | :--- | :--- |
| **Ngày thực hiện thử nghiệm** | 30/10/2026 | 31/10/2026 | Cùng bộ mã nguồn trên nhánh `connect-neon-postgres`. |
| **Nền tảng hạ tầng & Cấu hình** | Render Web Service (Free Tier, 512MB RAM, shared CPU) | Azure Linux VM (`Standard_B1s`, 1 vCPU, 1GB RAM, Ubuntu 24.04.5 LTS) | PaaS được quản lý tự động; IaaS tự cấu hình Docker Engine và mở port 5000. |
| **Target URL** | `https://cloudtask-z2wm.onrender.com` | `http://57.158.98.189:5000` *(IP tại thời điểm đo)* | PaaS tích hợp sẵn Cloudflare HTTPS; IaaS chạy HTTP trực tiếp qua cổng 5000. |
| **Phiên bản kịch bản k6** | `k6/load_test.js` (v1.0.0) | `k6/load_test.js` (v1.0.0) | Kịch bản đồng nhất: kiểm tra `/health/ready`, `/health/live`, `/login`. |
| **Tải tối đa (Virtual Users - VUs)** | **20 VUs** | **20 VUs** | 3 giai đoạn: 30s ramp-up -> 1m duy trì tải tối đa 20 VUs -> 30s ramp-down. |
| **Thời lượng thực thi** | 2 phút (~120s) | 2 phút (~121.2s) | Cùng chu kỳ tải để bảo đảm tính tương quan thống kê. |
| **Tổng số HTTP Requests / Checks** | **3.189 requests** (1.063 iterations) | **2.604 requests** (868 iterations) | Render xử lý được số request nhiều hơn trong cùng khoảng thời gian. |
| **Throughput trung bình** | **~ 26.5 requests/giây** | **21.49 requests/giây** | Thông lượng xử lý của PaaS cao hơn khoảng 23% so với máy ảo Azure B1s. |
| **Tỷ lệ lỗi (Error Rate)** | **0.00%** *(0 lỗi / 3.189)* | **0.00%** *(0 lỗi / 2.604)* | Cả hai môi trường đạt độ ổn định 100% không có request nào bị timeout/5xx. |
| **Độ trễ trung bình (Average Latency)**| **88.24 ms** | **146.79 ms** | PaaS có độ trễ trung bình thấp hơn đáng kể. |
| **Độ trễ trung vị (p50 Latency)** | **86.14 ms** | **72.88 ms** | IaaS xử lý các request đơn lẻ nhanh hơn một chút ở mức tải trung bình. |
| **Độ trễ phân vị 95 (p95 Latency)** | **100.17 ms** | **478.44 ms** | **Đạt ngưỡng đồ án (< 1500 ms)**. PaaS vượt trội nhờ đặt cùng Region Singapore với Neon DB. |
| **File dữ liệu thô (Raw JSON)** | `k6/results_paas.json` *(12.4 MB)* | `k6/results_iaas.json` *(9.2 MB)* | Lưu trữ cục bộ tại máy trạm làm chứng cứ đối chiếu khi cần kiểm tra. |

---

## 2. Ngưỡng Kiểm Thử (Thresholds) & Kết Quả Xác Minh

Cả hai bài đo đều được kiểm chứng tự động theo các ngưỡng nghiêm ngặt quy định trong `k6/load_test.js`:

```javascript
thresholds: {
  http_req_duration: ['p(95)<1500'], // 95% request phải hoàn thành dưới 1500ms
  'custom_error_rate': ['rate<0.05'], // Tỷ lệ lỗi toàn bộ kịch bản phải dưới 5%
  'custom_req_duration': ['p(95)<1500'],
}
```

- **Kết quả PaaS (Render):**
  - `custom_error_rate`: `rate=0.00%` (Vượt qua, yêu cầu < 5%).
  - `custom_req_duration p(95)`: `100.17 ms` (Vượt qua, yêu cầu < 1500 ms).
- **Kết quả IaaS (Azure VM):**
  - `custom_error_rate`: `rate=0.00%` (Vượt qua, yêu cầu < 5%).
  - `custom_req_duration p(95)`: `478.44 ms` (Vượt qua, yêu cầu < 1500 ms).

---

## 3. Kết Luận Thực Nghiệm & Phân Tích Giới Hạn

1. **Hiệu năng & Định tuyến (Routing & Compute):**
   - PaaS (Render) kết hợp Managed Database Neon (Singapore) mang lại độ trễ p95 rất thấp (~100 ms) nhờ hạ tầng mạng tối ưu nội vùng và hệ thống reverse proxy Cloudflare tích hợp sẵn.
   - IaaS (Azure Linux VM) đạt độ trễ p95 ~478 ms, cao hơn PaaS chủ yếu do độ trễ truyền dẫn mạng Internet giữa máy ảo Azure và cụm Neon PostgreSQL đặt tại Singapore.

2. **Giới hạn thực nghiệm:**
   - Kịch bản k6 hiện tại tập trung vào kiểm thử khả năng chịu tải của các endpoint hệ thống: readiness probe `/health/ready` (truy vấn kết nối DB `SELECT 1`), liveness probe `/health/live` và trang đăng nhập `/login`. Kịch bản chưa mô phỏng luồng người dùng tạo mới/sửa/xóa công việc (CRUD write operations) với tần suất cao, do việc kiểm thử ghi dữ liệu nặng đòi hỏi môi trường database cô lập riêng để tránh làm nhiễu dữ liệu nghiệp vụ của đồ án.

