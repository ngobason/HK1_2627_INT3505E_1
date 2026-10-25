# Security Audit – Social Network API

## Tám rủi ro bảo mật và biện pháp xử lý

| STT | Rủi ro | Hậu quả | Biện pháp đề xuất |
|---|---|---|---|
| 1 | Mật khẩu/token bị lộ khi truyền hoặc lưu trữ | Kẻ tấn công chiếm tài khoản hoặc phiên | Bắt buộc HTTPS; lưu mật khẩu bằng Argon2id/bcrypt; không ghi mật khẩu/token vào log |
| 2 | Login không chống dò mật khẩu hoặc dò tài khoản | Brute force, credential stuffing, biết email nào tồn tại | Rate limit; trả chung lỗi `invalid_credentials`; quá giới hạn trả `429` |
| 3 | JWT không được xác minh đầy đủ | Token giả, hết hạn hoặc cấp cho API khác vẫn được chấp nhận | Kiểm chữ ký, `exp`, `iss`, `aud`; giới hạn thuật toán cho phép; từ chối token sai bằng `401` |
| 4 | Refresh token bị dùng lại sau khi cấp token mới | Kẻ giữ token bị lộ có thể duy trì phiên trái phép | Phân biệt access/refresh token; rotate refresh token, theo dõi `jti`, thu hồi và phát hiện reuse |
| 5 | API đọc bài viết không kiểm tra scope | Người dùng có token nhưng không có quyền vẫn truy cập được bài viết | Kiểm tra `posts:read` trước khi xử lý; thiếu scope trả `403` |
| 6 | Thiếu kiểm tra chủ sở hữu của bài viết riêng tư (BOLA) | Người A đoán `postId` để đọc bài viết private của người B | Kiểm tra `author_id` hoặc quyền admin; không tiết lộ bài viết private cho người không có quyền (`404`) |
| 7 | Khóa ký JWT yếu, hardcode hoặc không được luân chuyển | Kẻ tấn công biết khóa có thể tự tạo JWT giả để truy cập API | Dùng khóa bí mật đủ mạnh, lưu trong biến môi trường/secret manager; hạn chế truy cập và có quy trình rotate khóa |
| 8 | Chứa thông tin nhạy cảm trong JWT payload | Ai có token có thể giải mã phần payload và đọc dữ liệu riêng tư | Chỉ đưa claims cần thiết (`sub`, `scope`, `exp`, `iss`, `aud`, `jti`); không lưu mật khẩu, secret hay PII không cần thiết |

## Phân quyền và HTTP status

| Endpoint | Xác thực / quyền | Thành công | Lỗi chính |
|---|---|---|---|
| `POST /auth/login` | Email và mật khẩu | `200` | `400`, `401`, `429` |
| `POST /auth/refresh` | Refresh token còn hiệu lực, chưa bị thu hồi | `200` | `401`, `403`, `429` |
| `GET /posts/{id}` | Access token có scope `posts:read`; kiểm tra quyền đọc post private | `200` | `400`, `401`, `403`, `404`, `429` |

`401` = chưa xác thực/token không hợp lệ; `403` = đã xác thực nhưng thiếu quyền; `404` = không tìm thấy hoặc không được phép biết bài viết riêng tư tồn tại.

## Các trường hợp cần kiểm tra

1. Login sai mật khẩu hoặc email không tồn tại → `401`, cùng thông báo lỗi.
2. Login quá nhiều lần → `429`.
3. Gửi JWT giả hoặc hết hạn đến `/posts/{id}` → `401`.
4. Dùng access token để gọi `/auth/refresh`, hoặc tái sử dụng refresh token đã rotate → `401`.
5. Token thiếu `posts:read` khi đọc post → `403`.
6. User A đọc post private của user B → `404`.
7. Kiểm tra cấu hình khóa JWT: không hardcode, khóa đủ mạnh và có quy trình rotate.
8. Giải mã một JWT mẫu để xác nhận payload không có mật khẩu, secret hoặc PII không cần thiết.