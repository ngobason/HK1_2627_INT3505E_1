# Bài 2 – Flask pagination (Bookstore API)

## API mới

| Method | Endpoint / Query | Tác dụng |
|---|---|---|
| GET | `/api/v1/books` | Offset mặc định, `sort=-id`, `limit=20` |
| GET | `/api/v1/books?strategy=offset&limit=2&offset=0` | Phân trang theo OFFSET |
| GET | `/api/v1/books?strategy=cursor&limit=2` | Trang đầu theo cursor |
| GET | `/api/v1/books?strategy=cursor&limit=2&cursor=...` | Trang tiếp theo |
| GET | `/api/v1/books?genre=fiction` | Lọc theo thể loại |
| GET | `/api/v1/books?sort=price,-title` | Giá tăng, tên giảm |
| GET | `/api/v1/books?genre=fiction&sort=-price,title&strategy=cursor&limit=2` | Kết hợp filter + sort + pagination |