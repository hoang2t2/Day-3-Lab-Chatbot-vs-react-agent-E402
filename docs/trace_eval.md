# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | 	Phải tra đơn → lấy ngày giao → tính số ngày đã trôi qua → đối chiếu hạn đổi trả theo ngành hàng → mới quyết định được. Không bước nào bỏ được. |
| 🛠️ **Tool Interaction** | `5/5` | Trạng thái đơn hàng và chính sách đổi trả nằm trong DB nội bộ, LLM không thể biết. Bắt buộc gọi tool. |
| 🔀 **Dynamic Decision** | `4/5` | 	Kết quả bước trước đổi hẳn nhánh xử lý: đơn "Đang giao" → từ chối tạo yêu cầu; "Đã giao 5 ngày" → cho đổi trả; "Đã giao 40 ngày" → quá hạn. |
| ⏳ **Long Horizon** | `3/5` | Luồng dài nhất 3 tool call, chưa cần memory dài hạn hay planning nhiều tầng. |
| **TỔNG ĐIỂM FIT** | **16/20** | **	Bài toán rất nên dùng ReAct Agent.** |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Tôi muốn xin đổi trả cho đơn hàng mã HD99999 mua từ 3 năm trước."*

### 🤖 Chatbot Baseline:
* **Phản hồi**: 

```text
Dạ chào bạn, cảm ơn bạn đã liên hệ với cửa hàng ạ! Chúc bạn một ngày tốt lành nhé! 😊

Về yêu cầu đổi trả cho đơn hàng **HD99999**, rất tiếc là hiện tại tôi **không thể truy cập vào hệ thống quản lý đơn hàng thời gian thực** hay kiểm tra các thông tin dữ liệu cá nhân của bạn được.

Bên cạnh đó, theo chính sách chung của cửa hàng, thời gian hỗ trợ đổi trả thường chỉ áp dụng trong vòng vài ngày đến vài tháng (tùy sản phẩm) kể từ ngày mua hàng. Đơn hàng mua từ 3 năm trước hiện đã vượt quá thời gian hỗ trợ đổi trả quy định rồi ạ.

Nếu bạn cần thêm thông tin về chính sách chung hoặc cần hỗ trợ tư vấn sản phẩm mới, cứ nhắn cho mình nhé! Còn để kiểm tra chi tiết trường hợp cụ thể của đơn hàng cũ, bạn vui lòng liên hệ trực tiếp với **tổng đài chăm sóc khách hàng** để các bạn điện thoại viên hỗ trợ bạn tốt nhất nha.
```
* **Nhận xét**: An toàn nhưng không giải quyết được nhu cầu thực tế của người dùng.

### 🧠 ReAct Agent:
* **Thought 1**: Khách hàng muốn đổi trả đơn hàng mã HD99999 mua từ 3 năm trước. Tôi cần kiểm tra thông tin đơn hàng này trên hệ thống trước.
* **Action 1**: get_order_info["HD99999"]
* **Observation 1**: Không tìm thấy mã đơn hàng 'HD99999' trong hệ thống.
* **Thought 2**: Dựa trên kết quả từ công cụ `get_order_info`, mã đơn hàng 'HD99999' không tồn tại trong hệ thống. Do đó, tôi không thể tiếp tục thực hiện việc kiểm tra điều kiện đổi trả hay tạo phiếu đổi trả. Tôi sẽ thông báo lịch sự cho khách hàng về việc này.
* **Final Answer**: 
```text
Chào bạn, tôi đã kiểm tra trên hệ thống nhưng rất tiếc không tìm thấy thông tin về mã đơn hàng "HD99999". Bạn vui lòng kiểm tra lại giúp tôi chính xác mã đơn hàng (thường được in trên hóa đơn hoặc email xác nhận mua hàng) để tôi hỗ trợ bạn tốt nhất nhé!
```
* **Nhận xét**: Hoàn thành xuất sắc nhiệm vụ nhờ sự kết hợp giữa suy luận và công cụ.
