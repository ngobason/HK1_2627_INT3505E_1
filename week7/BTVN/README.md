# Buổi 7 – Lab 1: Product API

Flask Application Factory, Blueprint, SQLAlchemy 2.x, Marshmallow, Flask-Migrate và SQLite.

## API

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/v1/products?page=1&size=20` | Danh sách, phân trang |
| GET | `/api/v1/products/{id}` | Chi tiết |
| POST | `/api/v1/products` | Tạo sản phẩm |
| POST | `/api/v1/products/{id}/reserve` | Đặt trước, trừ tồn kho |
| PATCH | `/api/v1/products/{id}` | Cập nhật một phần |
| DELETE | `/api/v1/products/{id}` | Xóa mềm |

**Ràng buộc:** SKU dài 3–32 ký tự và duy nhất; tên 1–255 ký tự; giá và tồn kho không âm. GET không trả sản phẩm đã xóa mềm. Lỗi có dạng `{"error":"...","detail":"..."}`.

## Cài đặt (Git Bash)

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

## Khởi tạo database (lần đầu)

```bash
flask --app app db init
flask --app app db migrate -m "initial product"
flask --app app db upgrade
```

## Chạy

```bash
python app.py
```

Server: `http://127.0.0.1:5000`. Với PowerShell, kích hoạt môi trường bằng `.\.venv\Scripts\Activate.ps1`.

## Kiểm tra nhanh (Git Bash)

```bash
curl -i http://127.0.0.1:5000/api/v1/products
curl -i -X POST http://127.0.0.1:5000/api/v1/products \
  -H 'Content-Type: application/json' \
  -d '{"sku":"BK-001","name":"Book A","price_cents":5000,"qty_in_stock":5}'
curl -i http://127.0.0.1:5000/api/v1/products/1
curl -i -X POST http://127.0.0.1:5000/api/v1/products/1/reserve \
  -H 'Content-Type: application/json' -d '{"qty":2}'
curl -i -X PATCH http://127.0.0.1:5000/api/v1/products/1 \
  -H 'Content-Type: application/json' -d '{"name":"Book A updated"}'
curl -i -X DELETE http://127.0.0.1:5000/api/v1/products/1
```

Sau khi sinh migration, commit cả thư mục `migrations/`. Không commit `.venv/` hoặc `instance/`.
