# NỘI DUNG VÀ CẤU TRÚC THUYẾT TRÌNH CANVA (15 SLIDES)

> **Đề tài 8:** Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành
> **Dự án thực nghiệm:** CloudTask – Collaboration Task Management
> **Tone thiết kế khuyến nghị:** Tối giản (Minimalist), hiện đại, màu nền trắng hoặc xanh nhạt pastel (#F8FAFC), màu chủ đạo và điểm nhấn là Xanh dương đậm / Cyan (#0284C7, #0F172A). Không dùng hiệu ứng chuyển động rườm rà, tập trung làm nổi bật bảng số liệu và biểu đồ trực quan.

---

### SLIDE 1: TRANG TIÊU ĐỀ
- **Tiêu đề lớn:** PHÁT TRIỂN ỨNG DỤNG PaaS CÓ CƠ SỞ DỮ LIỆU ĐƯỢC QUẢN LÝ VÀ ĐÁNH GIÁ GÁNH NẶNG VẬN HÀNH
- **Tiêu đề phụ:** Nghiên cứu thực nghiệm đối chứng PaaS (Render + Neon) và IaaS (Azure Linux VM) qua ứng dụng CloudTask
- **Thông tin nhóm:** Nhóm sinh viên thực hiện Đề tài 8 – Học phần Điện toán đám mây
- **Bố cục đề xuất:** Căn giữa, biểu tượng đám mây tối giản, mã QR liên kết tới GitHub repository (`https://github.com/danhle1605/CloudTask`).
- **Lời thuyết trình:**
  *"Kính thưa quý thầy cô và các bạn, hôm nay nhóm em xin trình bày kết quả nghiên cứu và thực nghiệm Đề tài 8: Phát triển ứng dụng PaaS có cơ sở dữ liệu được quản lý và đánh giá gánh nặng vận hành thông qua dự án CloudTask."*

---

### SLIDE 2: ĐẶT VẤN ĐỀ VÀ CÂU HỎI NGHIÊN CỨU
- **Tiêu đề slide:** ĐẶT VẤN ĐỀ VÀ CÂU HỎI NGHIÊN CỨU
- **Nội dung hiển thị:**
  - **Bài toán đặt ra:** Lựa chọn giữa quyền tự do kiểm soát máy chủ (IaaS) hay sự tiện lợi tự động hóa (PaaS + Managed Database)?
  - **3 Câu hỏi cốt lõi:**
    1. *Hiệu năng:* PaaS có đảm bảo tốc độ và độ trễ tương đương IaaS tự dựng khi cùng kết nối một CSDL đám mây?
    2. *Vận hành & Độ tin cậy:* Khả năng phát hiện lỗi, phục hồi (Rollback) của PaaS giúp giảm bao nhiêu gánh nặng công việc?
    3. *Mở rộng & Chi phí:* Hiệu quả thực tế của việc mở rộng quy mô (Scale Out) và bài toán chi phí tài nguyên so với chi phí nhân lực ra sao?
- **Bố cục:** 2 cột (Cột 1: Bối cảnh; Cột 2: 3 câu hỏi với icon dấu hỏi hoặc mục tiêu).
- **Lời thuyết trình:**
  *"Khi triển khai sản phẩm lên đám mây, các nhóm kỹ thuật thường băn khoăn: liệu dùng PaaS có chậm hơn máy ảo tự cấu hình hay không, và sự tiện lợi của PaaS có thực sự đáng để đánh đổi quyền kiểm soát hệ thống? Đồ án của chúng em sinh ra để trả lời câu hỏi này bằng dữ liệu thực nghiệm."*

---

### SLIDE 3: MỤC TIÊU NGHIÊN CỨU VÀ PHẠM VI THỰC NGHIỆM
- **Tiêu đề slide:** MỤC TIÊU VÀ PHẠM VI THỰC NGHIỆM
- **Nội dung hiển thị:**
  - **Xây dựng ứng dụng mẫu:** Phát triển CloudTask – ứng dụng quản trị công việc nhóm bằng Python Flask, kết nối Neon PostgreSQL.
  - **Triển khai song song:**
    - *PaaS:* Render Web Service + Neon Serverless DB (Singapore).
    - *IaaS:* Azure Linux VM (Ubuntu 24.04, Docker, HAProxy).
  - **Đo lường định lượng:** Thực hiện kiểm thử tải bằng k6, đo đạc thời gian triển khai, thời gian rollback và phân tích chi phí.
- **Bố cục:** Dạng thẻ (3 Cards) trực quan từ Trái sang Phải.
- **Lời thuyết trình:**
  *"Để có kết quả khách quan nhất, nhóm em đã xây dựng CloudTask và triển khai đồng thời trên Render PaaS và Azure VM, cùng trỏ về một cơ sở dữ liệu Neon duy nhất để loại bỏ các biến số sai lệch về cấu trúc dữ liệu."*

---

### SLIDE 4: CƠ SỞ LÝ THUYẾT: PaaS vs IaaS
- **Tiêu đề slide:** CƠ SỞ LÝ THUYẾT: MÔ HÌNH TRÁCH NHIỆM CHIA SẺ
- **Nội dung hiển thị:**
  - **IaaS (Azure VM):** Nhóm trực tiếp quản lý OS, Runtime, Security, Docker, Firewall cổng 5000 và ứng dụng.
  - **PaaS (Render):** Nhà cung cấp lo từ Phần cứng, Mạng, OS, Runtime, Chứng chỉ SSL; Nhóm chỉ tập trung vào Mã nguồn và Biến môi trường.
  - **Managed Database (Neon):** Cơ sở dữ liệu Serverless, tự động tách biệt Compute và Storage, tích hợp sẵn Connection Pooling (pgBouncer).
- **Ảnh minh chứng cần chèn:** Sơ đồ Shared Responsibility Model (IaaS vs PaaS).
- **Bố cục:** Bảng phân tầng màu sắc (Xanh dương cho phần Nhà cung cấp quản lý, Xám cho phần Nhóm tự quản lý).
- **Lời thuyết trình:**
  *"Ở mô hình IaaS, nhóm em phải tự cấu hình từ hệ điều hành, Docker đến firewall. Trong khi ở PaaS, ranh giới trách nhiệm của lập trình viên dừng lại ở mã nguồn và biến môi trường, mọi việc còn lại do nền tảng tự động hóa."*

---

### SLIDE 5: NGUYÊN TẮC TWELVE-FACTOR APP
- **Tiêu đề slide:** NGUYÊN TẮC THIẾT KẾ THEO TWELVE-FACTOR APP
- **Nội dung hiển thị:**
  - **1. Codebase & Dependencies:** 1 Git repository, khai báo tường minh trong `requirements.txt`.
  - **2. Config:** Tách biệt cấu hình qua biến môi trường (`.env`, `SECRET_KEY`, `DATABASE_URL`).
  - **3. Stateless Processes:** Ứng dụng không lưu trạng thái trên đĩa, phiên đăng nhập qua signed cookie.
  - **4. Concurrency & Port Binding:** Chạy độc lập trên cổng 5000 qua Gunicorn WSGI.
  - **5. Admin Processes:** Quản lý lược đồ CSDL tự động qua Alembic migration (`flask db upgrade`).
- **Bố cục:** Lưới 4 ô nổi bật với các icon công nghệ.
- **Lời thuyết trình:**
  *"Nhờ tuân thủ chuẩn 12-Factor App, ứng dụng CloudTask có tính di động tuyệt đối: có thể chạy mượt mà trên môi trường local, container Docker trên Azure, hay trực tiếp trên nền tảng PaaS Render mà không cần sửa đổi bất kỳ dòng mã nguồn nào."*

---

### SLIDE 6: KIẾN TRÚC TỔNG THỂ HỆ THỐNG CLOUDTASK
- **Tiêu đề slide:** SƠ ĐỒ KIẾN TRÚC TỔNG THỂ CLOUDTASK
- **Nội dung hiển thị:**
  - **Client:** Trình duyệt web (UI Bootstrap 5 hiện đại).
  - **PaaS Path:** Client -> Cloudflare Proxy (SSL) -> Render Web Service -> Neon PostgreSQL (SSL).
  - **IaaS Path:** Client -> Azure NSG (Port 5000) -> HAProxy Load Balancer -> Docker Web Containers (`web1`, `web2`) -> Neon PostgreSQL.
- **Ảnh minh chứng cần chèn:** Sơ đồ kiến trúc hệ thống tổng thể (Architecture Diagram).
- **Bố cục:** Sơ đồ khối đối xứng hai luồng PaaS và IaaS cùng trỏ về cụm Neon PostgreSQL trung tâm.
- **Lời thuyết trình:**
  *"Đây là sơ đồ kiến trúc tổng thể. Điểm mấu chốt là cả hai luồng PaaS và IaaS đều trỏ về cụm Managed Database Neon tại Singapore, giúp chúng em so sánh chính xác hiệu năng tầng tính toán và mạng giữa hai nền tảng."*

---

### SLIDE 7: CHỨC NĂNG NGHIỆP VỤ VÀ GIAO DIỆN CLOUDTASK
- **Tiêu đề slide:** CHỨC NĂNG ỨNG DỤNG VÀ QUẢN TRỊ DỮ LIỆU
- **Nội dung hiển thị:**
  - **Xác thực an toàn:** Đăng ký, Đăng nhập với mật khẩu băm Werkzeug.
  - **Không gian làm việc nhóm:** Tham gia workspace chung qua mã mời `CLOUDTASK-GROUP-8`.
  - **CRUD công việc:** Thêm mới, chỉnh sửa, đánh dấu hoàn thành, phân cấp mức độ ưu tiên và lọc tìm kiếm.
  - **Health Check Probes:** `/health/live` và `/health/ready` (truy vấn kết nối CSDL `SELECT 1`).
- **Ảnh minh chứng cần chèn:** Ảnh chụp màn hình giao diện Dashboard và trang Danh sách công việc của CloudTask.
- **Lời thuyết trình:**
  *"Ứng dụng cung cấp đầy đủ các chức năng quản lý công việc nhóm với giao diện chuẩn mực, tích hợp sẵn hai endpoint health check phục vụ việc giám sát tính sẵn sàng của database và web server."*

---

### SLIDE 8: TRIỂN KHAI PaaS VÀ TỰ ĐỘNG HÓA CI/CD
- **Tiêu đề slide:** TRIỂN KHAI PaaS VÀ QUY TRÌNH CI/CD TỰ ĐỘNG
- **Nội dung hiển thị:**
  - **Quy trình CI/CD:**
    `Git Push` -> `GitHub Actions` -> `Ruff Linting` -> `Alembic Migration Test` -> `Pytest Automation` -> `Render Auto-Deploy` -> `Health Check 200 OK`.
  - **Đặc điểm nổi bật:**
    - Hoàn toàn tự động hóa, ngăn chặn phát hành mã nguồn lỗi.
    - Cấp phát SSL/HTTPS tự động trong vòng vài giây.
- **Ảnh minh chứng cần chèn:** Ảnh chụp giao diện GitHub Actions với các bước test tích xanh và Dashboard Render.
- **Lời thuyết trình:**
  *"Trên nền tảng PaaS, toàn bộ quy trình phát hành được tự động hóa qua GitHub Actions. Mỗi commit mới đều phải vượt qua kiểm tra cú pháp, migration CSDL trên container test và chạy pytest trước khi được Render tự động deploy."*

---

### SLIDE 9: TRIỂN KHAI ĐỐI CHỨNG HẠ TẦNG IaaS (AZURE VM)
- **Tiêu đề slide:** TRIỂN KHAI MÁY ẢO IaaS TRÊN MICROSOFT AZURE
- **Nội dung hiển thị:**
  - **Cấu hình máy ảo:** Azure Linux VM `Standard_B2ats_v2` / `Standard_B1s`, Ubuntu 24.04 LTS.
  - **Môi trường:** Cài đặt Docker Engine, Docker Compose, Git.
  - **Bảo mật mạng:** Cấu hình Azure Network Security Group mở inbound port 5000.
  - **Điều phối dịch vụ:** Quản lý container bằng `docker-compose.iaas.yml`.
- **Ảnh minh chứng cần chèn:** Ảnh chụp màn hình Azure Portal (trạng thái VM) và terminal chạy lệnh Docker Compose.
- **Lời thuyết trình:**
  *"Đối với IaaS, nhóm trực tiếp tạo máy ảo Ubuntu trên Azure, cấu hình bảo mật mở cổng mạng, cài đặt Docker và chạy container ứng dụng. Mọi thao tác đều thực hiện thủ công qua giao diện dòng lệnh."*

---

### SLIDE 10: SO SÁNH HIỆU NĂNG TẢI K6 (PaaS vs IaaS)
- **Tiêu đề slide:** KẾT QUẢ ĐO TẢI k6: PaaS (RENDER) vs IaaS (AZURE VM)
- **Bảng số liệu bắt buộc (Bảng 1):**

| Chỉ số đo lường | PaaS (Render) | IaaS (Azure VM) | Nhận xét |
| :--- | :---:| :---:| :--- |
| **Average Latency** | **96,79 ms** | **124,31 ms** | Render phản hồi nhanh hơn 22,1% |
| **p95 Latency** | **118,56 ms** | **419,80 ms** | Render vượt trội và ổn định hơn |
| **Error Rate** | **0,00%** | **0,00%** | Tuyệt đối không có lỗi ở tải 20 VUs |
| **Throughput** | **26,04 req/s** | **22,42 req/s** | Render đạt thông lượng cao hơn 16,1% |
| **Tổng Requests (2 phút)** | **3.132** | **2.718** | Render xử lý nhiều hơn 414 requests |

- **Nhận xét dưới bảng:** Cả hai môi trường cùng đạt 0% lỗi. PaaS đạt độ trễ p95 thấp hơn nhờ hệ thống reverse proxy tích hợp sẵn của Render và tính ổn định của đường truyền tới CSDL Neon.
- **Ảnh minh chứng cần chèn:** Ảnh chụp màn hình kết quả chạy k6 trên terminal PowerShell.
- **Lời thuyết trình:**
  *"Đây là bảng so sánh hiệu năng quan trọng nhất. Dưới tải 20 VUs trong 2 phút, cả hai nền tảng đều không gặp bất kỳ lỗi nào. Đáng chú ý, PaaS đạt độ trễ phân vị p95 chỉ 118,56 ms so với 419,80 ms của máy ảo Azure."*

---

### SLIDE 11: THỰC NGHIỆM KHẢ NĂNG MỞ RỘNG (SCALING TRÊN IaaS)
- **Tiêu đề slide:** THỰC NGHIỆM MỞ RỘNG QUY MÔ (SCALING TRÊN IaaS)
- **Kiến trúc:** 1 instance đơn lẻ so với 2 instances ứng dụng cân bằng tải qua HAProxy (Round Robin).
- **Bảng số liệu bắt buộc (Bảng 2):**

| Chỉ số đo lường | 1 instance | 2 instances (+ HAProxy) | Tỷ lệ cải thiện |
| :--- | :---:| :---:| :---: |
| **Average Latency** | 254,42 ms | 91,73 ms | **Giảm 64,0%** |
| **p95 Latency** | 791,16 ms | 220,95 ms | **Giảm 72,1%** |
| **Error Rate** | 0,00% | 0,00% | Giữ vững 0% |
| **Throughput** | 19,06 req/s | 26,28 req/s | **Tăng +37,9%** |
| **Tổng Requests** | 2.298 | 3.165 | **Tăng +37,7%** |

- **Nhận xét dưới bảng:** Mở rộng lên 2 container sau HAProxy giúp p95 giảm tới 72,1%, thông lượng tăng 37,9%, chứng minh hiệu quả rõ rệt của mô hình phân tải.
- **Ảnh minh chứng cần chèn:** Biểu đồ cột so sánh p95 và thông lượng giữa 1 instance và 2 instances.
- **Lời thuyết trình:**
  *"Khi tiến hành mở rộng từ 1 container lên 2 container sau HAProxy trên máy ảo Azure, hiệu năng cải thiện ngoạn mục: độ trễ p95 giảm tới 72,1% và thông lượng tăng gần 38%. Điều này chứng minh giá trị của việc cân bằng tải khi ứng dụng xử lý nhiều truy vấn cơ sở dữ liệu."*

---

### SLIDE 12: THỰC NGHIỆM LỖI VÀ THỜI GIAN KHÔI PHỤC (ROLLBACK)
- **Tiêu đề slide:** THỰC NGHIỆM SỰ CỐ VÀ KHÔI PHỤC BẢN PHÁT HÀNH
- **Nội dung hiển thị:**
  - **Tạo sự cố thử nghiệm:** Làm sai cấu hình `DATABASE_URL` -> Endpoint `/health/ready` trả về HTTP 503.
  - **Thời gian phục hồi:**
    - **PaaS (Render):** **18 giây** (Thao tác 1-click trên Web Dashboard).
    - **IaaS (Azure VM):** **4,41 giây** (Thao tác qua lệnh `git checkout` & Docker Compose).
  - **Thời gian Deployment mới:**
    - IaaS hoàn tất trong **15,59 giây** (build và start container).
    - PaaS mất khoảng **20 giây** tính từ lúc tiến trình Gunicorn khởi động đến khi health check thành công.
- **Ảnh minh chứng cần chèn:** Ảnh chụp log Rollback trên Render và log terminal trên Azure VM.
- **Lời thuyết trình:**
  *"Khi xảy ra sự cố cấu hình CSDL, PaaS Render cho phép khôi phục chỉ sau 1 cú nhấp chuột trong 18 giây mà không cần vào máy chủ. Trên IaaS, rollback bằng dòng lệnh chỉ mất 4,41 giây nhưng đòi hỏi kỹ sư phải có mặt trực tiếp và nhớ chính xác mã commit ổn định."*

---

### SLIDE 13: SO SÁNH GÁNH NẶNG VẬN HÀNH (OPERATIONAL BURDEN)
- **Tiêu đề slide:** ĐÁNH GIÁ VÀ SO SÁNH GÁNH NẶNG VẬN HÀNH
- **Nội dung hiển thị dạng bảng trực quan:**
  - *Thời gian thiết lập ban đầu:* PaaS (5-10 phút) vs IaaS (20-30 phút).
  - *Bảo trì định kỳ:* PaaS (Tự động 100%) vs IaaS (Tự vá lỗi Linux, dọn dẹp Docker log).
  - *Cấu hình SSL/HTTPS:* PaaS (Tích hợp sẵn) vs IaaS (Tự cài đặt Certbot/Nginx).
  - *Sao lưu cơ sở dữ liệu:* PaaS/Neon (Tự động, Point-in-time) vs IaaS (Tự viết cronjob).
  - *Số thành phần nhóm trực tiếp quản lý:* PaaS (1 thành phần: App Code) vs IaaS (4 thành phần: OS, Docker, Firewall, App).
- **Bố cục:** Bảng đối chiếu 2 cột màu tương phản.
- **Lời thuyết trình:**
  *"Về gánh nặng vận hành, PaaS giúp giảm thiểu tối đa các tác vụ chân tay. Ở IaaS, nhóm phải quản lý tới 4 tầng thành phần, trong khi ở PaaS, nhóm chỉ cần tập trung duy nhất vào mã nguồn ứng dụng."*

---

### SLIDE 14: CHI PHÍ VẬN HÀNH VÀ VENDOR LOCK-IN
- **Tiêu đề slide:** PHÂN TÍCH BÀI TOÁN CHI PHÍ VÀ VENDOR LOCK-IN
- **Chi phí dịch vụ:**
  - PaaS (Render + Neon): **$0/tháng** (Sử dụng các gói Free Tier thử nghiệm).
  - IaaS (Azure VM + Disk + IP): Niêm yết **~$12 - $16/tháng** -> Thực tế chi trả **$0** nhờ Credit **Azure for Students ($100)** và tắt máy ảo khi không đo đạc.
- **Bài toán chi phí nhân lực:** Tiền thuê máy chủ IaaS có thể rẻ, nhưng chi phí kỹ sư vận hành hệ thống (DevOps) thường cao gấp nhiều lần chi phí dịch vụ PaaS.
- **Giải pháp chống Vendor Lock-in:**
  - Chuẩn hóa container bằng Docker.
  - Sử dụng ORM SQLAlchemy và Alembic migration độc lập với nền tảng.
  - Tuân thủ Twelve-Factor App giúp dễ dàng chuyển đổi nhà cung cấp trong vài giờ.
- **Lời thuyết trình:**
  *"Về chi phí, cả hai phương án đều được nhóm tối ưu ở mức 0 đồng trong phạm vi đồ án. Quan trọng hơn, nhờ đóng gói bằng Docker và kiến trúc Twelve-Factor, hệ thống của nhóm hoàn toàn không bị trói buộc vào một nhà cung cấp cụ thể nào."*

---

### SLIDE 15: KẾT LUẬN VÀ BÀI HỌC KINH NGHIỆM
- **Tiêu đề slide:** KẾT LUẬN VÀ ĐỀ XUẤT THỰC TIỄN
- **Trả lời 3 câu hỏi nghiên cứu:**
  1. *Hiệu năng:* PaaS hoàn toàn đáp ứng tốt, độ trễ p95 thậm chí vượt trội hơn IaaS trong bài toán kiểm thử.
  2. *Vận hành:* PaaS giúp giảm hơn 80% gánh nặng quản trị hạ tầng, tự động hóa toàn diện quy trình phát hành.
  3. *Mở rộng:* Cân bằng tải qua nhiều container giúp tăng gần 38% thông lượng và giảm 72,1% độ trễ p95.
- **Khuyến nghị:**
  - Ưu tiên chọn **PaaS + Managed Database** cho các sản phẩm khởi nghiệp, ứng dụng vừa và nhỏ để ra mắt thị trường nhanh nhất.
  - Cân nhắc chuyển sang **IaaS** khi hệ thống đạt lưu lượng rất lớn cần tối ưu chi phí phần cứng chuyên biệt.
- **Lời thuyết trình:**
  *"Tóm lại, PaaS kết hợp Managed Database là giải pháp lý tưởng cho phần lớn các nhóm phát triển hiện đại. Em xin chân thành cảm ơn quý thầy cô đã lắng nghe, nhóm em rất mong nhận được những góp ý để hoàn thiện đồ án tốt hơn!"*
