### 6. Pagination rõ ràng

- **Đạt**
- Với các endpoint trả về danh sách, DMOJ có cấu trúc pagination rõ ràng trong `data`, gồm:
  + `current_object_count`: số object ở trang hiện tại
  + `objects_per_page`: số object tối đa trên một trang
  + `page_index`: chỉ số trang hiện tại, bắt đầu từ 1
  + `total_objects`: tổng số object
  + `total_pages`: tổng số trang
  + `objects`: danh sách dữ liệu của trang hiện tại
- Ví dụ có thể truy cập trang bằng query parameter:
  + `/api/v2/problems?page=2`
DMOJ đáp ứng yêu cầu collection có pagination và có giới hạn số lượng object trên mỗi trang

### 7. Filter/Sort đa dạng

- **Filter đạt / Sort không đạt**
- DMOJ hỗ trợ filtering khá tốt. Docs mô tả hai kiểu chính:
  + **Basic filtering**: lọc theo một giá trị
  + **List filtering**: lọc theo một danh sách giá trị
- Ví dụ:
  + `/api/v2/problems?partial=True`
  + `/api/v2/problems?organization=1&organization=2&type=Implementation`
- Endpoint `/api/v2/problems` hỗ trợ các filter như:
  + `partial`
  + `code`
  + `group`
  + `type`
  + `organization`
  + `search`
- Endpoint `/api/v2/submissions` hỗ trợ các filter như:
  + `user`
  + `problem`
  + `id`
  + `language`
  + `result`
- Docs không cung cấp query parameter cho phép client tự chọn cách sort
- Nhiều collection được sắp xếp cố định ở phía server, ví dụ theo `id`, thay vì cho client chọn nhiều field để sort
- Docs cũng không mô tả sparse fieldsets như:
  + `?fields=code,name,points`
  để chỉ lấy một số field cần thiết

**Đề xuất cải thiện:**
  + Thêm query parameter `sort` để hỗ trợ sắp xếp theo nhiều field
  + Quy ước dùng dấu `-` để biểu diễn thứ tự giảm dần
  + Ví dụ:
    `/api/v2/problems?sort=-points,name`
    nghĩa là sort theo `points` giảm dần, sau đó theo `name` tăng dần
  + Chỉ cho phép sort trên một danh sách field hợp lệ để tránh query không mong muốn
  + Có thể bổ sung query parameter `fields` để hỗ trợ sparse fieldsets
  + Ví dụ:
    `/api/v2/problems?fields=code,name,points`
    chỉ trả về các field `code`, `name`, `points`.
