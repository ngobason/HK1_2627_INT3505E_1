# Lab 1 – Bookstore REST API

## 1. Danh sách REST API

Thay `<resource>` bằng `books`, `authors`, `categories`, `users`, `reviews`.

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/v1/<resource>` | Lấy danh sách |
| GET | `/api/v1/<resource>/<id>` | Lấy chi tiết |
| POST | `/api/v1/<resource>` | Tạo mới |
| PATCH | `/api/v1/<resource>/<id>` | Cập nhật |
| DELETE | `/api/v1/<resource>/<id>` | Xóa |

## 2. Kiểm thử API

### Test 1 – Kiểm tra server và danh sách Book

```
curl -i http://localhost:5000/
curl -i http://localhost:5000/api/v1/books
```

![Test 1 - Server](images/01-server.png)
![Test 1 - Book ban đầu](images/02-books-initial.png)

### Test 2 – Tạo Category, Author và User

**POST Category**

```
curl -i -X POST http://localhost:5000/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"Technology","slug":"technology"}'
```

![POST Category](images/03-create-category.png)

**POST Author**

```
curl -i -X POST http://localhost:5000/api/v1/authors \
  -H "Content-Type: application/json" \
  -d '{"name":"Robert C. Martin","bio":"Author of Clean Code"}'
```

![POST Author](images/04-create-author.png)

**POST User**

```
curl -i -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email":"reader@example.com","display_name":"Reader A"}'
```

![POST User](images/05-create-user.png)

### Test 3 – Tạo và xem Book

**POST Book**

```
curl -i -X POST http://localhost:5000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","isbn":"9780132350884","price_vnd":320000,"stock":10,"category_id":1,"author_ids":[1]}'
```

![POST Book](images/06-create-book.png)

**GET danh sách Book**

```
curl -i http://localhost:5000/api/v1/books
```

![GET Book list](images/07-books-list.png)

**GET chi tiết Book**

```
curl -i http://localhost:5000/api/v1/books/1
```

![GET Book detail](images/08-book-detail.png)

### Test 4 – Cập nhật Book

```
curl -i -X PATCH http://localhost:5000/api/v1/books/1 \
  -H "Content-Type: application/json" \
  -d '{"price_vnd":299000,"stock":8}'
```

![PATCH Book](images/09-patch-book.png)

### Test 5 – Tạo và xem Review

**POST Review**

```
curl -i -X POST http://localhost:5000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{"rating":5,"comment":"Very useful book","book_id":1,"user_id":1}'
```

![POST Review](images/10-create-review.png)

**GET danh sách Review**

```
curl -i http://localhost:5000/api/v1/reviews
```

![GET Review list](images/11-reviews-list.png)

### Test 6 – Xóa Review và Book

**DELETE Review**

```
curl -i -X DELETE http://localhost:5000/api/v1/reviews/1
```

![DELETE Review](images/12-delete-review.png)

**DELETE Book**

```
curl -i -X DELETE http://localhost:5000/api/v1/books/1
```

![DELETE Book](images/13-delete-book.png)

**GET danh sách Book sau khi xóa**

```
curl -i http://localhost:5000/api/v1/books
```

![GET Book after DELETE](images/14-books-after-delete.png)