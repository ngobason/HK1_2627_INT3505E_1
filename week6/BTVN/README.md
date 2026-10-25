# Bài tập Buổi 06 – Authentication & Authorization

**Domain:** Social Network API

## 1. Danh sách API

| Method | Endpoint | Xác thực / phân quyền | Thành công | Lỗi |
|---|---|---|---|---|
| POST | `/auth/login` | Email và mật khẩu | 200 | 400, 401, 429 |
| POST | `/auth/refresh` | Refresh token hợp lệ | 200 | 401, 403, 429 |
| GET | `/posts/{id}` | Access token, `posts:read`, quyền xem bài viết | 200 | 400, 401, 403, 404, 429 |

**SecurityAudit.md:** Phân tích 8 rủi ro bảo mật và cách khắc phục.

## 2. Scope, lỗi và HTTP status code

| Endpoint | Scope / xác thực | Lỗi có thể xảy ra | Status code |
|---|---|---|---|
| `POST /auth/login` | Không cần scope; xác thực email/mật khẩu | Dữ liệu sai (400), sai thông tin đăng nhập (401), quá nhiều yêu cầu (429) | 200, 400, 401, 429 |
| `POST /auth/refresh` | Không cần scope; yêu cầu refresh token hợp lệ | Token không hợp lệ/hết hạn/đã thu hồi (401), tài khoản bị vô hiệu hóa (403), quá nhiều yêu cầu (429) | 200, 401, 403, 429 |
| `GET /posts/{id}` | Access token và scope `posts:read`; kiểm tra quyền xem bài viết riêng tư | ID sai (400), token không hợp lệ (401), thiếu scope (403), bài viết không tồn tại hoặc không có quyền xem (404), quá nhiều yêu cầu (429) | 200, 400, 401, 403, 404, 429 |

## 3. Kiểm tra OpenAPI

```bash
python validate_spec.py
```

![Kiểm tra đặc tả OpenAPI](images/01-validate.png)

## 3. Swagger

![Hiển thị 3 endpoint trên Swagger](images/02-swagger.png)

## 4. Kiểm thử API

### 4.1. Đăng nhập thành công – 200

![Login thành công](images/03-login-success.png)

### 4.2. Đăng nhập sai mật khẩu – 401

![Login thất bại](images/04-login-failed.png)

### 4.3. Truy cập không có token – 401

![Không có access token](images/05-unauthorized.png)

### 4.4. Xem bài viết hợp lệ – 200

![GET bài viết thành công](images/06-get-post.png)

### 4.5. Thiếu scope posts:read – 403

![Không đủ quyền truy cập](images/07-forbidden.png)

### 4.6. ID bài viết không hợp lệ – 400

![ID không hợp lệ](images/08-invalid-id.png)

### 4.7. Refresh token thành công – 200

![Cấp lại token](images/09-refresh.png)