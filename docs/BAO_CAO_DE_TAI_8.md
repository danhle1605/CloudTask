# BÁO CÁO ĐỒ ÁN ĐIỆN TOÁN ĐÁM MÂY (ĐỀ TÀI 8)

**TÊN ĐỀ TÀI:**
**PHÁT TRIỂN ỨNG DỤNG PaaS CÓ CƠ SỞ DỮ LIỆU ĐƯỢC QUẢN LÝ VÀ ĐÁNH GIÁ GÁNH NẶNG VẬN HÀNH**

- **Dự án ứng dụng thực nghiệm:** CloudTask – Hệ thống Quản trị Công việc Nhóm (Task & Workspace Collaboration System)
- **Mã nguồn dự án:** https://github.com/danhle1605/CloudTask
- **Nhánh chính thức:** `connect-neon-postgres`
- **Địa chỉ ứng dụng PaaS (Render):** https://cloudtask-z2wm.onrender.com
- **Địa chỉ hạ tầng IaaS (Azure VM):** http://57.158.98.189:5000

---

## MỤC LỤC
1. Giới thiệu đề tài
2. Câu hỏi nghiên cứu và mục tiêu nghiên cứu
3. Cơ sở lý thuyết PaaS, IaaS và Managed Database
4. Nguyên tắc thiết kế ứng dụng theo Twelve-Factor App
5. Kiến trúc tổng thể hệ thống CloudTask
6. Xây dựng ứng dụng CRUD và kết nối CSDL Neon PostgreSQL
7. Quy trình tự động hóa CI/CD với GitHub Actions và Render
8. Triển khai đối chứng hạ tầng IaaS trên Azure Linux VM
9. Thực nghiệm kiểm thử hiệu năng chịu tải k6 (PaaS vs IaaS)
10. Thực nghiệm khả năng mở rộng (Scaling 1 instance vs 2 instances + HAProxy)
11. Thực nghiệm lỗi và quy trình khôi phục bản phát hành (Rollback)
12. Đánh giá và so sánh gánh nặng vận hành giữa PaaS và IaaS
13. Phân tích chi phí tài nguyên và chi phí nhân lực
14. Đánh giá mức độ phụ thuộc nhà cung cấp (Vendor Lock-in) và giải pháp
15. Thảo luận kết quả thực nghiệm
16. Kết luận trả lời câu hỏi nghiên cứu
17. Tài liệu tham khảo

---

## 1. GIỚI THIỆU ĐỀ TÀI
Trong phát triển phần mềm hiện đại, việc lựa chọn mô hình hạ tầng đám mây tác động trực tiếp tới tốc độ bàn giao sản phẩm, độ ổn định của hệ thống và chi phí vận hành lâu dài. Hai mô hình phổ biến nhất hiện nay là:
- **IaaS (Infrastructure as a Service):** Cung cấp hạ tầng ảo hóa thô (máy ảo, mạng, ổ đĩa). Kỹ sư có toàn quyền kiểm soát hệ điều hành nhưng phải gánh vác toàn bộ công việc thiết lập, vá lỗi bảo mật, cấu hình firewall và giám sát daemon.
- **PaaS (Platform as a Service) kết hợp Managed Database:** Nhà cung cấp trừu tượng hóa hạ tầng, tự động hóa vòng đời phát hành ứng dụng (build, deploy, SSL, health check) và quản lý cơ sở dữ liệu (tự động sao lưu, mở rộng kết nối, bảo trì phần cứng).

Đề tài 8 tập trung phát triển ứng dụng thực tế **CloudTask**, triển khai đồng thời trên nền tảng **PaaS (Render + Neon PostgreSQL)** và môi trường đối chứng **IaaS (Azure Linux VM Ubuntu 24.04 + Docker)**, từ đó đo lường các chỉ số kỹ thuật thực tế để phân tích sự đánh đổi giữa quyền kiểm soát hạ tầng và gánh nặng vận hành.

---

## 2. CÂU HỎI NGHIÊN CỨU VÀ MỤC TIÊU NGHIÊN CỨU

### 2.1. Câu hỏi nghiên cứu
1. **Về hiệu năng:** Mô hình PaaS kết hợp Managed Database có đảm bảo độ trễ và thông lượng tương đương hoặc tốt hơn mô hình máy ảo IaaS tự quản trị trong điều kiện cùng kết nối một cơ sở dữ liệu đám mây không?
2. **Về độ tin cậy và khôi phục sự cố:** Thời gian phát hiện lỗi và rollback của PaaS có thực sự giúp đội ngũ kỹ thuật giảm tải công việc so với thao tác thủ công trên IaaS không?
3. **Về khả năng mở rộng (Scalability):** Việc nhân rộng container ứng dụng kết hợp cân bằng tải mềm (HAProxy) trên IaaS mang lại sự cải thiện hiệu năng định lượng cụ thể ra sao?
4. **Về gánh nặng vận hành:** Doanh nghiệp nhỏ hoặc nhóm phát triển phải đánh đổi những gì giữa chi phí tài nguyên dịch vụ và chi phí nhân lực khi chọn PaaS thay vì IaaS?

### 2.2. Mục tiêu nghiên cứu
- Xây dựng hoàn chỉnh ứng dụng quản trị công việc nhóm CloudTask chuẩn Twelve-Factor bằng Python Flask và PostgreSQL.
- Triển khai sản phẩm thực tế trên PaaS Render và IaaS Azure Linux VM.
- Tự động hóa kiểm thử và triển khai liên tục qua GitHub Actions.
- Thu thập dữ liệu đo tải thực tế bằng công cụ k6 qua các file JSON minh chứng.
- Đánh giá khách quan, định lượng về thời gian vận hành, rollback, chi phí và mức độ phụ thuộc nhà cung cấp.

---

## 3. CƠ SỞ LÝ THUYẾT PaaS, IaaS VÀ MANAGED DATABASE
- **IaaS (Azure Linux VM):** Người dùng chịu trách nhiệm từ tầng Hệ điều hành (OS), runtime (Python, Docker), middleware (HAProxy, Gunicorn), bảo mật mạng (Network Security Group) đến mã nguồn ứng dụng. Nhà cung cấp chỉ đảm bảo tính sẵn sàng của phần cứng máy chủ vật lý và mạng ảo.
- **PaaS (Render Web Service):** Nhà cung cấp đảm nhận toàn bộ việc quản lý OS, container runtime, reverse proxy, cấp phát chứng chỉ HTTPS tự động và cân bằng tải. Lập trình viên chỉ cần cung cấp mã nguồn qua Git và khai báo biến môi trường.
- **Managed Database (Neon PostgreSQL):** Là hệ thống cơ sở dữ liệu PostgreSQL Serverless tách biệt tài nguyên tính toán (Compute) và lưu trữ (Storage). Neon tự động quản lý backup, tích hợp Connection Pooling (pgBouncer) và mã hóa kết nối SSL/TLS.

---

## 4. NGUYÊN TẮC THIẾT KẾ THEO TWELVE-FACTOR APP
Ứng dụng CloudTask tuân thủ nghiêm ngặt các nguyên tắc của Twelve-Factor App nhằm đảm bảo tính di động (portability) tối đa giữa PaaS, IaaS và môi trường phát triển local:
1. **Codebase:** Một kho mã nguồn duy nhất trên GitHub được theo dõi bằng Git, triển khai ra nhiều môi trường.
2. **Dependencies:** Khai báo tường minh trong `requirements.txt` và `requirements-dev.txt`, cô lập bằng Docker container.
3. **Config:** Tách biệt cấu hình khỏi mã nguồn. Mọi tham số nhạy cảm (`SECRET_KEY`, `DATABASE_URL`, `APP_VERSION`) đều nạp qua biến môi trường.
4. **Backing Services:** Cơ sở dữ liệu PostgreSQL được coi là tài nguyên gắn kết (attached resource), kết nối qua URI đồng nhất.
5. **Build, Release, Run:** Tách biệt các giai đoạn build Docker image, nạp biến cấu hình và khởi chạy ứng dụng.
6. **Processes:** Ứng dụng chạy theo mô hình Stateless (không lưu trạng thái phiên trên ổ đĩa cục bộ mà sử dụng signed session cookie).
7. **Port Binding:** Tự lắng nghe cổng thông qua máy chủ WSGI Gunicorn (cổng 5000), không phụ thuộc vào web server ngoài để inject cổng.
8. **Concurrency:** Mở rộng xử lý song song thông qua worker/threads của Gunicorn và nhân rộng số container.
9. **Disposability:** Khởi động nhanh và tắt êm ái khi nhận tín hiệu `SIGTERM`.
10. **Dev/Prod Parity:** Giữ môi trường kiểm thử và sản xuất tương đồng tối đa thông qua PostgreSQL 16.
11. **Logs:** Xuất toàn bộ nhật ký ứng dụng dưới dạng dòng sự kiện ra stdout/stderr để nền tảng tự thu thập.
12. **Admin Processes:** Các tác vụ quản trị CSDL được thực hiện độc lập thông qua công cụ dòng lệnh `flask db upgrade` (Alembic).

---

## 5. KIẾN TRÚC TỔNG THỂ HỆ THỐNG CLOUDTASK
Hệ thống bao gồm các thành phần chính:
- **Tầng Client:** Trình duyệt web gửi yêu cầu HTTP/HTTPS.
- **Tầng Load Balancer / Reverse Proxy:**
  - Trên PaaS: Mạng phân phối và proxy tự động của Render (hỗ trợ SSL termination miễn phí).
  - Trên IaaS: Máy chủ cân bằng tải HAProxy điều phối lưu lượng Round Robin đến các node container.
- **Tầng Ứng dụng (Application Server):** Container chạy Python 3.12, Flask, Gunicorn WSGI Server.
- **Tầng Dữ liệu (Managed Database):** Cụm máy chủ Neon PostgreSQL 16 đặt tại Region Singapore (`ap-southeast-1`), kết nối mã hóa qua giao thức SSL.

---

## 6. XÂY DỰNG ỨNG DỤNG CRUD VÀ KẾT NỐI CSDL NEON POSTGRESQL
- **Chức năng nghiệp vụ:**
  - Xác thực người dùng (Đăng ký, Đăng nhập với mật khẩu mã hóa an toàn bằng Werkzeug).
  - Không gian làm việc chung (Workspace Collaboration) kết nối nhóm qua mã mời `GROUP_INVITE_CODE`.
  - Quản trị công việc đầy đủ (CRUD): Tạo mới task, phân loại ưu tiên (low, medium, high), theo dõi trạng thái (pending, in_progress, completed), lọc và tìm kiếm nhanh.
  - Phân quyền dữ liệu ở tầng server-side: Người dùng chỉ được thao tác trên công việc thuộc workspace của mình.
- **Health Check Probes:**
  - `/health/live`: Liveness probe phản hồi trạng thái tiến trình web server.
  - `/health/ready`: Readiness probe thực hiện truy vấn `SELECT 1` tới CSDL Neon để kiểm tra khả năng phục vụ dữ liệu.

---

## 7. QUY TRÌNH TỰ ĐỘNG HÓA CI/CD VỚI GITHUB ACTIONS VÀ RENDER
Pipeline CI/CD được thiết lập trong tệp `.github/workflows/ci.yml` trên nhánh `connect-neon-postgres`:
1. **Trigger:** Kích hoạt tự động khi có sự kiện `push` hoặc `pull_request`.
2. **Linting Check:** Chạy `ruff check .` để rà soát lỗi cú pháp và chuẩn code.
3. **Database Migration Test:** Khởi chạy dịch vụ container `postgres:16-alpine`, áp dụng migration Alembic (`flask db upgrade`) để xác nhận lược đồ bảng tương thích hoàn toàn.
4. **Automated Testing:** Thực thi toàn bộ kiểm thử tự động với Pytest (kiểm tra xác thực, logic phân quyền, endpoint health check).
5. **Continuous Deployment (CD):** Sau khi toàn bộ các bước kiểm thử vượt qua, job `deploy-render` kích hoạt triển khai phiên bản mới lên Render thông qua cơ chế tích hợp GitHub hoặc Deploy Hook.

---

## 8. TRIỂN KHAI ĐỐI CHỨNG HẠ TẦNG IaaS TRÊN AZURE LINUX VM
- **Thông số máy ảo:** Azure Virtual Machine dòng `Standard_B2ats_v2` / `Standard_B1s`, hệ điều hành Ubuntu 24.04.5 LTS, cấu hình mạng mở inbound port 5000 cho lưu lượng web.
- **Công nghệ container:** Docker Engine và Docker Compose.
- **Tệp điều phối hạ tầng:**
  - `docker-compose.iaas.yml`: Triển khai 1 container ứng dụng CloudTask độc lập.
  - `docker-compose.scale.yml`: Triển khai 2 container ứng dụng song song (`web1`, `web2`) kết hợp container `lb` chạy HAProxy 3.0 Alpine.

---

## 9. THỰC NGHIỆM KIỂM THỬ HIỆU NĂNG CHỊU TẢI K6 (PaaS vs IaaS)

### 9.1. Thiết lập kịch bản kiểm thử
- Kịch bản: `k6/load_test.js` kiểm tra các endpoint `/health/live`, `/health/ready` (truy vấn DB) và `/login`.
- Tải thử nghiệm: Mô phỏng người dùng ảo biến thiên theo 3 giai đoạn: 30s ramp-up lên 20 VUs -> 1 phút duy trì tối đa 20 VUs -> 30s ramp-down về 0. Tổng thời gian chạy ~2 phút.
- File dữ liệu thực nghiệm: `k6/results_paas_final.json` và `k6/results_iaas.json`.

### 9.2. Bảng 1: So sánh hiệu năng PaaS (Render) và IaaS (Azure VM)

| Chỉ số đo lường | PaaS: Render Web Service | IaaS: Azure Linux VM | Đánh giá so sánh |
| :--- | :---:| :---:| :--- |
| **Virtual Users (Tối đa)** | 20 VUs | 20 VUs | Tải thử nghiệm đồng nhất |
| **Tổng số Requests hoàn thành** | **3.132** | **2.718** | Render hoàn thành nhiều hơn 15,2% |
| **Độ trễ trung bình (Average Latency)** | **96,79 ms** | **124,31 ms** | Render nhanh hơn 22,1% |
| **Độ trễ phân vị 95 (p95 Latency)** | **118,56 ms** | **419,80 ms** | Render ổn định hơn đáng kể |
| **Tỷ lệ lỗi (Error Rate)** | **0,00%** | **0,00%** | Cả hai đạt độ tin cậy tuyệt đối |
| **Thông lượng (Throughput)** | **26,04 req/s** | **22,42 req/s** | Render cao hơn 16,1% |

*Định nghĩa chỉ số p95:* Độ trễ phân vị thứ 95 (p95) thể hiện mốc thời gian mà 95% tổng số yêu cầu được hệ thống phản hồi nhanh hơn hoặc bằng giá trị này. Đây là chỉ số quan trọng phản ánh trải nghiệm người dùng thực tế dưới tải.

*Phân tích nguyên nhân:* Cả hai môi trường cùng kết nối chung tới CSDL Neon PostgreSQL đặt tại Region Singapore. Render đạt p95 vượt trội (118,56 ms so với 419,80 ms của Azure) chủ yếu nhờ hạ tầng mạng nội vùng Singapore tối ưu và hệ thống reverse proxy Cloudflare tích hợp sẵn.

---

## 10. THỰC NGHIỆM KHẢ NĂNG MỞ RỘNG (SCALING 1 INSTANCE vs 2 INSTANCES + HAPROXY)

### 10.1. Thiết lập kiến trúc mở rộng
Nhóm tiến hành thực nghiệm mở rộng quy mô ngang (Scale Out) trên chính máy ảo Azure IaaS bằng cách chạy 2 container ứng dụng độc lập (`web1`, `web2`) được cân bằng tải bằng container HAProxy với thuật toán Round Robin (`docker-compose.scale.yml`).

### 10.2. Bảng 2: So sánh hiệu năng Scaling trên IaaS

| Chỉ số đo lường | 1 instance (Đơn lẻ) | 2 instances (+ HAProxy) | Tỷ lệ thay đổi |
| :--- | :---:| :---:| :---: |
| **Tổng số Requests hoàn thành** | 2.298 | 3.165 | **Tăng +37,7%** |
| **Độ trễ trung bình (Average Latency)** | 254,42 ms | 91,73 ms | **Giảm 64,0%** |
| **Độ trễ phân vị 95 (p95 Latency)** | 791,16 ms | 220,95 ms | **Giảm 72,1%** |
| **Tỷ lệ lỗi (Error Rate)** | 0,00% | 0,00% | Giữ vững 0% |
| **Thông lượng (Throughput)** | 19,06 req/s | 26,28 req/s | **Tăng +37,9%** |

### 10.3. Nhận xét định lượng
- Khi mở rộng từ 1 container lên 2 container sau HAProxy, độ trễ p95 giảm ngoạn mục từ 791,16 ms xuống 220,95 ms (giảm 72,1%).
- Thông lượng hệ thống tăng từ 19,06 req/s lên 26,28 req/s (tăng 37,9%), xử lý được 3.165 requests so với 2.298 requests.
- *Lưu ý kỹ thuật:* Hai instance ở đây là 2 container chạy chung tài nguyên CPU/RAM trên một máy ảo Azure. Việc chia sẻ tải qua 2 tiến trình giúp tận dụng tốt hơn khả năng xử lý bất đồng bộ I/O khi kết nối CSDL từ xa. Tuy nhiên, hiệu năng scaling trên môi trường thực tế còn phụ thuộc vào giới hạn phần cứng của máy chủ chủ quản.

---

## 11. THỰC NGHIỆM LỖI VÀ QUY TRÌNH KHÔI PHỤC BẢN PHÁT HÀNH (ROLLBACK)

### 11.1. Kịch bản thực nghiệm
Nhóm cố tình tạo ra bản phát hành lỗi trên môi trường thử nghiệm bằng cách làm hỏng cấu hình kết nối CSDL (`DATABASE_URL` sai). Khi truy cập `/health/ready`, hệ thống trả về mã lỗi HTTP 503 Service Unavailable (`database: disconnected`).

### 11.2. Quy trình và thời gian khôi phục
- **Trên PaaS (Render):** Thao tác 1-click Rollback trên giao diện Web Dashboard để quay về bản deploy ổn định trước đó.
  - Timestamp bắt đầu deploy khôi phục: `17:44:28 UTC`.
  - Timestamp hoàn tất và health check 200 OK: `17:44:46 UTC`.
  - **Thời gian Rollback PaaS:** **18 giây**.
- **Trên IaaS (Azure VM):** Thao tác qua SSH terminal: chuyển về commit ổn định và khởi động lại container:
  ```bash
  git checkout <STABLE_COMMIT_HASH> && docker compose -f docker-compose.iaas.yml up -d --build
  ```
  - **Thời gian Rollback IaaS:** **4,41 giây**.
  - **Thời gian Deployment bản dựng mới trên IaaS:** **15,59 giây** (đo từ lệnh khởi chạy Docker Compose đến khi health check đạt 200 OK).
  - *Lưu ý về deployment Render:* Trên Render, nhật ký ghi nhận Gunicorn khởi động lúc 13:48:44 UTC và health check đạt 200 OK lúc 13:49:04 UTC (khoảng 20 giây cho giai đoạn khởi động). Khoảng thời gian này không bao gồm thời gian clone code và build container từ đầu.

---

## 12. ĐÁNH GIÁ VÀ SO SÁNH GÁNH NẶNG VẬN HÀNH GIỮA PaaS VÀ IaaS

| Tiêu chí vận hành | Mô hình PaaS (Render + Neon) | Mô hình IaaS (Azure Linux VM) |
| :--- | :--- | :--- |
| **Thiết lập ban đầu** | Nhanh (~5-10 phút), cấu hình hoàn toàn qua Web Dashboard. | Tốn nhiều thời gian (~20-30 phút), cần tạo VM, SSH, cài Docker, mở firewall. |
| **Quản lý hạ tầng & OS** | Nhà cung cấp chịu trách nhiệm 100% (vá lỗi kernel, quản lý phần cứng). | Nhóm phải tự bảo trì OS, cập nhật bản vá bảo mật định kỳ (`apt upgrade`). |
| **Cấp phát SSL/HTTPS** | Tự động 100% thông qua Cloudflare và Let's Encrypt. | Tự cấu hình qua Certbot/Nginx hoặc chấp nhận HTTP thô nếu chạy thử nghiệm. |
| **Giám sát & Logs** | Tập trung trực tiếp trên Dashboard, có sẵn biểu đồ RAM/CPU. | Tự quản lý log file của Docker hoặc cài thêm giải pháp bên thứ ba (Prometheus/Grafana). |
| **Quản trị cơ sở dữ liệu** | Neon tự quản lý connection pooling, sao lưu tự động và phục hồi point-in-time. | Nếu tự host PostgreSQL, nhóm phải tự cấu hình sao lưu định kỳ qua cron job. |
| **Quyền kiểm soát** | Bị giới hạn quyền truy cập root, không can thiệp sâu vào kernel hay network rules. | Toàn quyền kiểm soát root, tự do tùy biến mọi tham số hệ thống. |

---

## 13. PHÂN TÍCH CHI PHÍ TÀI NGUYÊN VÀ CHI PHÍ NHÂN LỰC

### 13.1. Bảng so sánh chi phí dịch vụ

| Nền tảng | Dịch vụ thành phần | Thông số cấu hình | Giá niêm yết (USD/tháng) | Chi phí thực tế nhóm chi trả |
| :--- | :--- | :--- | :---:| :---:|
| **PaaS** | Render Web Service | Free Tier (512MB RAM, shared CPU) | $0 | **$0** (Miễn phí) |
| | Neon PostgreSQL | Serverless Free Tier (0.5 GiB storage, pooled) | $0 | **$0** (Miễn phí) |
| | GitHub Actions | 2.000 phút CI/CD miễn phí/tháng | $0 | **$0** (Miễn phí) |
| **IaaS** | Azure VM Standard_B2ats_v2 / B1s | 1-2 vCPU, 1GB RAM (Southeast Asia, 730h) | ~$7,50 - $10,50/tháng | Trừ vào Credit **Azure for Students ($100)** |
| | Azure OS Managed Disk | 30-64GB SSD tiêu chuẩn | ~$1,50 - $3,00/tháng | Trừ vào Credit Azure for Students |
| | Azure Public IP | Dynamic/Standard IPv4 SKU | ~$2,90/tháng (nếu tính phí) | Trừ vào Credit Azure for Students |
| | Database Neon | Dùng chung cụm Neon Singapore | $0 | $0 |

*Ghi chú minh bạch về chi phí:* Đối với IaaS, tổng chi phí tính theo biểu giá niêm yết khi vận hành liên tục 24/7 dao động khoảng $12 - $16/tháng. Tuy nhiên, nhóm sử dụng gói tài trợ **Azure for Students**, đồng thời thực hiện thao tác **Stop (Deallocate) máy ảo** ngay sau khi hoàn thành các bài đo kiểm thực tế, giúp số dư credit được bảo toàn tối đa.

### 13.2. Đánh giá chi phí nhân lực vận hành
Mặc dù chi phí phần cứng thô của IaaS có thể rẻ hơn ở quy mô lớn, chi phí nhân lực (DevOps Engineer) để duy trì một cụm máy ảo (cập nhật bảo mật, giám sát daemon, cấu hình backup và xử lý sự cố lúc nửa đêm) thường vượt xa chi phí phần mềm. Đối với các nhóm khởi nghiệp hoặc dự án vừa và nhỏ, PaaS giúp tiết kiệm hàng chục giờ công vận hành mỗi tháng.

---

## 14. ĐÁNH GIÁ MỨC ĐỘ PHỤ THUỘC NHÀ CUNG CẤP (VENDOR LOCK-IN) VÀ GIẢI PHÁP

### 14.1. Bảng phân tích rủi ro phụ thuộc

| Thành phần | Rủi ro phụ thuộc | Mức độ | Khó khăn khi di chuyển | Giải pháp giảm thiểu |
| :--- | :--- | :---:| :--- | :--- |
| **Render** | Phụ thuộc cơ chế deploy hook và đặc tả service của Render. | Thấp | Cần cấu hình lại file build ở nền tảng mới (như Fly.io, Railway). | Đóng gói toàn bộ ứng dụng thành Docker container tiêu chuẩn. |
| **Neon PostgreSQL** | Phụ thuộc tính năng serverless và endpoint pooling chuyên dụng. | Rất thấp | Chỉ cần đổi chuỗi kết nối URI chuẩn. | Dùng chuẩn PostgreSQL tiêu chuẩn, sao lưu bằng lệnh `pg_dump`. |
| **Azure VM** | Phụ thuộc cấu hình mạng Azure NSG và Public IP. | Rất thấp | Chuyển đổi qua lại dễ dàng giữa AWS EC2, Google Compute Engine. | Sử dụng script cài đặt tự động và file Docker Compose độc lập. |
| **GitHub Actions** | Phụ thuộc cú pháp YAML workflow của GitHub. | Trung bình | Phải viết lại cấu hình nếu chuyển sang GitLab CI hay Jenkins. | Đóng gói các bước test thành script Shell/Python độc lập để gọi từ bất kỳ đâu. |

Nhóm không khẳng định hệ thống hoàn toàn triệt tiêu được Vendor Lock-in, nhưng bằng cách áp dụng **Docker container hóa**, kiến trúc **Twelve-Factor App**, thư viện ORM **SQLAlchemy** và công cụ migration **Alembic**, ứng dụng CloudTask có khả năng chuyển đổi linh hoạt sang bất kỳ nền tảng đám mây nào chỉ trong vài giờ làm việc.

---

## 15. THẢO LUẬN KẾT QUẢ THỰC NGHIỆM
- **Về tính ổn định:** Cả PaaS và IaaS đều đạt tỷ lệ lỗi **0,00%** trong suốt các kịch bản kiểm thử với 20 người dùng ảo đồng thời. Điều này chứng minh ứng dụng Flask được thiết kế vững chắc về mặt quản lý phiên và kết nối CSDL.
- **Về độ trễ:** PaaS đạt kết quả p95 ấn tượng (118,56 ms) do tận dụng được hạ tầng mạng đám mây hiện đại. IaaS có độ trễ cao hơn do khoảng cách truyền dẫn Internet, nhưng đã được cải thiện rõ rệt từ 791,16 ms xuống 220,95 ms khi áp dụng mô hình 2 instances + HAProxy.
- **Về tính ứng dụng:** PaaS Free Tier có đặc điểm tự động chuyển sang chế độ "ngủ" (Sleep) sau 15 phút không có yêu cầu, dẫn tới thời gian khởi động lạnh (Cold Start) khoảng 20-30 giây cho lượt truy cập đầu tiên. Đây là sự đánh đổi cần cân nhắc giữa chi phí $0 và trải nghiệm người dùng liên tục.

---

## 16. KẾT LUẬN TRẢ LỜI CÂU HỎI NGHIÊN CỨU
1. **PaaS có đảm bảo hiệu năng không?** Có. PaaS kết hợp Managed Database đạt độ trễ p95 thấp hơn IaaS trong cùng điều kiện thử nghiệm, đáp ứng xuất sắc yêu cầu của ứng dụng web tương tác.
2. **PaaS có giảm tải gánh nặng vận hành không?** Hoàn toàn có. PaaS giảm thiểu hơn 80% công việc thiết lập hạ tầng, tự động hóa cấp SSL, cung cấp quy trình rollback an toàn và loại bỏ hoàn toàn việc bảo trì máy chủ vật lý.
3. **Scaling trên IaaS có hiệu quả không?** Rất hiệu quả. Việc phân tải qua 2 container với HAProxy giúp giảm 72,1% độ trễ p95 và tăng 37,9% thông lượng xử lý.
4. **Khuyến nghị thực tiễn:** Đối với các dự án giai đoạn đầu, nhóm phát triển nên ưu tiên mô hình PaaS kết hợp Managed Database để tối đa hóa tốc độ phát triển. Chỉ nên chuyển sang IaaS khi hệ thống đạt quy mô rất lớn và yêu cầu can thiệp sâu vào cấu hình phần cứng hạ tầng.

---

## 17. TÀI LIỆU THAM KHẢO
1. The Twelve-Factor App Methodology – Adam Wiggins (https://12factor.net/).
2. Render Platform Documentation (https://render.com/docs).
3. Neon Serverless PostgreSQL Documentation (https://neon.tech/docs).
4. Microsoft Azure Virtual Machines Documentation (https://learn.microsoft.com/azure/virtual-machines/).
5. Grafana k6 Load Testing Documentation (https://grafana.com/docs/k6/).
6. HAProxy Starter Guide & Configuration Manual (https://www.haproxy.org/).
