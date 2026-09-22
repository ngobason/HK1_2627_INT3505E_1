# Audit GitHub REST API

## Endpoints

### 1. List assignees

- **Method:** `GET`
- **Endpoint:** `/repos/{owner}/{repo}/assignees`
- **Purpose:** Lấy danh sách các user có thể được assign vào issue của một repository
- **Status codes:** `200 OK`, `404 Not Found`
- **Important headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <TOKEN>`
  - `X-GitHub-Api-Version: 2026-03-10`
- **RESTful:** Có. URI sử dụng danh từ/resource (`repos`, `assignees`), `GET` được dùng đúng để đọc dữ liệu, path parameters xác định repository, query parameters dùng cho pagination và status codes được sử dụng đúng


### 2. List deployment branch policies

- **Method:** `GET`
- **Endpoint:** `/repos/{owner}/{repo}/environments/{environment_name}/deployment-branch-policies`
- **Purpose:** Lấy danh sách deployment branch policies của một environment trong repository
- **Status codes:** `200 OK`
- **Important headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <TOKEN>`
  - `X-GitHub-Api-Version: 2026-03-10`
- **RESTful:** Có. URI thể hiện resource hierarchy rõ ràng từ repository → environment → deployment branch policies, `GET` được dùng đúng để đọc collection và query parameters được dùng cho pagination


### 3. Revoke a list of credentials

- **Method:** `POST`
- **Endpoint:** `/credentials/revoke`
- **Purpose:** Gửi danh sách credentials cần được thu hồi
- **Status codes:** `202 Accepted`, `422 Validation Failed`, `500 Internal Error`
- **Important headers:**
  - `Accept: application/vnd.github+json`
  - `X-GitHub-Api-Version: 2026-03-10`
- **RESTful:** Không hoàn toàn. `POST` và status code `202` được sử dụng hợp lý cho một operation làm thay đổi trạng thái, nhưng URI chứa động từ `revoke`, nên mang tính action/RPC hơn thiết kế resource-oriented REST thuần


### 4. Get the authenticated app

- **Method:** `GET`
- **Endpoint:** `/app`
- **Purpose:** Lấy GitHub App được liên kết với authentication credentials hiện tại
- **Status codes:** `200 OK`
- **Important headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <JWT>`
  - `X-GitHub-Api-Version: 2026-03-10`
- **RESTful:** Có. `/app` biểu diễn một resource, `GET` được dùng đúng để đọc dữ liệu và resource được xác định thông qua authentication context thay vì cần ID trong path


### 5. Get a GitHub Pages site

- **Method:** `GET`
- **Endpoint:** `/repos/{owner}/{repo}/pages`
- **Purpose:** Lấy thông tin về GitHub Pages site của một repository
- **Status codes:** `200 OK`, `404 Not Found`
- **Important headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <TOKEN>`
  - `X-GitHub-Api-Version: 2026-03-10`
- **RESTful:** Có. URI dùng danh từ/resource, `/pages` là sub-resource của repository, `GET` được dùng đúng để đọc dữ liệu và các status code `200`, `404` đúng HTTP semantics