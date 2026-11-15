# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 45 | 1/137 (0,73%) | 4,90 |
| B | 50 | 5 | 60s | 50 | 7/1.376 (0,51%) | 22,03 |
| C | 200 | 50 | 30s | 140 | 2/2.768 (0,07%) | 92,64 |

## 1. Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.

**Kịch bản C** có p95 tổng hợp cao nhất (**140 ms**), so với **50 ms** ở B và **45 ms** ở A. Khi tăng từ 10 lên 200 users, p95 tăng từ 45 lên 140 ms. Đặc biệt, `POST /books` có p95 lần lượt **99 ms (A)**, **100 ms (B)** và **320 ms (C)**. Điều này cho thấy thao tác ghi có độ trễ tăng rõ rệt ở tải cao. Tranh chấp ghi SQLite hoặc giới hạn xử lý của Flask development server có thể góp phần gây ra hiện tượng này, nhưng chưa đủ dữ liệu máy chủ để kết luận nguyên nhân cụ thể.

## 2. Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.

**Không có endpoint nào tăng failure rate liên tục** theo số users trong ba lần đo. Chỉ task `GET /books?year` có lỗi được ghi nhận:

| Kịch bản | Requests `GET /books?year` | Failures | Failure rate endpoint |
|---|---:|---:|---:|
| A | 16 | 1 | 6,25% |
| B | 202 | 7 | 3,47% |
| C | 427 | 2 | 0,47% |

Theo `performance/locustfile.py`, task `search_by_year()` dùng `random.random() < 0.01` và `response.failure("Simulated HTTP 500 (client-side)")` để **đánh dấu lỗi giả lập với xác suất 1%**. Đây **không phải mã HTTP 500 thật** do Flask trả về. Tỷ lệ đo được dao động do lấy mẫu ngẫu nhiên, không chứng minh máy chủ lỗi nhiều hơn khi tăng tải. Ba endpoint còn lại không có failure được Locust ghi nhận.

## 3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.

Nếu xét **p95 tổng hợp**, **cả A (45 ms), B (50 ms) và C (140 ms) đều đạt** mức SLO giả định **p95 < 300 ms**. Tuy nhiên, nếu áp dụng SLO riêng cho từng endpoint, `POST /books` ở C **không đạt** vì p95 = **320 ms**.

**Đề xuất baseline cho CI gate:** Kịch bản **B (50 users, spawn rate 5 users/s, 60 giây)** vì tạo tải thực tế hơn A nhưng vẫn có p95 tổng hợp 50 ms. Có thể kiểm tra p95 tổng hợp < 300 ms, theo dõi riêng p95 của endpoint quan trọng và tách **HTTP 5xx thực** khỏi lỗi giả lập để tránh CI thất bại sai. Kịch bản C phù hợp làm bài kiểm tra spike bổ sung.

**Giới hạn:** Các phép đo chỉ diễn ra trong 30–60 giây trên máy cá nhân với **SQLite + Flask development server**. Chúng chưa phản ánh hạ tầng, traffic mix, concurrency hay độ ổn định lâu dài của production. Vì vậy không thể khẳng định hiệu năng production dựa trên kết quả này.

## 4. Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?

**Giả thuyết:** Nếu tối đa 5 kết nối cơ sở dữ liệu được sử dụng đồng thời, những request cần kết nối tiếp theo sẽ phải chờ. Khi tải tăng, p95/p99 có thể tăng, RPS có thể chững lại và có thể phát sinh timeout. **200 Locust users không đồng nghĩa 200 kết nối DB đồng thời**, vì các user có thời gian nghỉ và không phải request nào cũng đang truy vấn DB.

**Cách kiểm chứng:** Trên môi trường thử nghiệm, cấu hình pool tối đa 5 kết nối, chạy lại các mức 10, 50 và 200 users; đối chiếu p95/p99, RPS, số timeout và log của server. Đồng thời theo dõi số kết nối đang sử dụng, thời gian chờ pool và lỗi pool timeout để xác định nghẽn tại pool.