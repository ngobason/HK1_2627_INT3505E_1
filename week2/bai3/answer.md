# Test 1:

```text
$ curl -i http://127.0.0.1:5000/books
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.7
Date: Mon, 21 Sep 2026 09:26:47 GMT
Content-Type: application/json
Content-Length: 812
Cache-Control: public, max-age=30
Connection: close

{
  "_links": {
    "first": {
      "href": "/books?page=1&size=3"
    },
    "last": {
      "href": "/books?page=4&size=3"
    },
    "next": {
      "href": "/books?page=2&size=3"
    },
    "self": {
      "href": "/books?page=1&size=3"
    }
  },
  "data": [
    {
      "author": "Robert C. Martin",
      "id": 1,
      "isbn": "9780132350884",
      "price": 25.99,
      "title": "Clean Code"
    },
    {
      "author": "Robert C. Martin",
      "id": 2,
      "isbn": "9780134494166",
      "price": 30.5,
      "title": "Clean Architecture"
    },
    {
      "author": "Andrew Hunt",
      "id": 3,
      "isbn": "9780135957059",
      "price": 27.99,
      "title": "The Pragmatic Programmer"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 3,
    "total": 10,
    "total_pages": 4
  }
}
```

# Test 2:

```text
$ curl -i "http://127.0.0.1:5000/books?page=2&size=3"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.7
Date: Mon, 21 Sep 2026 09:27:58 GMT
Content-Type: application/json
Content-Length: 868
Cache-Control: public, max-age=30
Connection: close

{
  "_links": {
    "first": {
      "href": "/books?page=1&size=3"
    },
    "last": {
      "href": "/books?page=4&size=3"
    },
    "next": {
      "href": "/books?page=3&size=3"
    },
    "prev": {
      "href": "/books?page=1&size=3"
    },
    "self": {
      "href": "/books?page=2&size=3"
    }
  },
  "data": [
    {
      "author": "Erich Gamma",
      "id": 4,
      "isbn": "9780201633610",
      "price": 35.0,
      "title": "Design Patterns"
    },
    {
      "author": "Miguel Grinberg",
      "id": 5,
      "isbn": "9781491991732",
      "price": 29.99,
      "title": "Flask Web Development"
    },
    {
      "author": "Eric Matthes",
      "id": 6,
      "isbn": "9781593279288",
      "price": 24.99,
      "title": "Python Crash Course"
    }
  ],
  "pagination": {
    "page": 2,
    "size": 3,
    "total": 10,
    "total_pages": 4
  }
}
```

# Test 3:

```text
$ curl -i "http://127.0.0.1:5000/books?q=clean"
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.7
Date: Mon, 21 Sep 2026 09:28:47 GMT
Content-Type: application/json
Content-Length: 599
Cache-Control: public, max-age=30
Connection: close

{
  "_links": {
    "first": {
      "href": "/books?page=1&size=3"
    },
    "last": {
      "href": "/books?page=1&size=3"
    },
    "self": {
      "href": "/books?page=1&size=3"
    }
  },
  "data": [
    {
      "author": "Robert C. Martin",
      "id": 1,
      "isbn": "9780132350884",
      "price": 25.99,
      "title": "Clean Code"
    },
    {
      "author": "Robert C. Martin",
      "id": 2,
      "isbn": "9780134494166",
      "price": 30.5,
      "title": "Clean Architecture"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 3,
    "total": 2,
    "total_pages": 1
  }
}
```