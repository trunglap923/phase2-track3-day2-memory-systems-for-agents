# Phản hồi: Quyền riêng tư & Hạn chế của Tác nhân Đa bộ nhớ

### 1. Bộ nhớ nào hữu ích nhất cho tác nhân?
**Bộ nhớ Hồ sơ Dài hạn (Long-term Profile Memory)** có lẽ là bộ nhớ hữu ích nhất cho các tương tác hàng ngày. Nó cho phép tác nhân cá nhân hóa các câu trả lời một cách ngầm định mà không yêu cầu người dùng phải lặp lại liên tục các sở thích, tên hoặc các hạn chế (như dị ứng) của họ. Điều này thay đổi căn bản sự tương tác từ một hệ thống truy vấn-phản hồi không trạng thái sang một trợ lý cá nhân hóa.

### 2. Bộ nhớ nào rủi ro nhất nếu truy xuất sai?
**Hồ sơ Dài hạn** và **Bộ nhớ Ngữ nghĩa (Semantic Memory)**.
- **Hồ sơ Dài hạn**: Nếu tác nhân diễn giải sai một sự thật quan trọng (ví dụ: "dị ứng với đậu nành" được ghi lại thành "dị ứng với đậu phộng"), nó có thể đưa ra lời khuyên về chế độ ăn uống hoặc y tế nguy hiểm.
- **Bộ nhớ Ngữ nghĩa**: Nếu nó truy xuất sai khối kiến thức (ví dụ: tài liệu lỗi thời hoặc khóa API không chính xác), tác nhân sẽ tự tin đưa ra thông tin sai lệch dựa trên dữ liệu tồi.

### 3. Rủi ro Quyền riêng tư và Giảm thiểu (PII, Đồng ý, TTL, Xóa)
**Rủi ro:**
- Tác nhân tự động trích xuất và lưu trữ PII (tên, dữ liệu y tế như dị ứng, sở thích) vào bộ lưu trữ cố định (JSON/Redis).
- Người dùng có thể không biết tác nhân đang ghi nhớ *những gì*.

**Giảm thiểu & Thực hành Tốt nhất:**
- **Sự đồng ý:** Hệ thống nên yêu cầu sự đồng ý rõ ràng trước khi lưu các dữ liệu cực kỳ nhạy cảm (ví dụ: "Tôi nhận thấy bạn đã đề cập đến một tình trạng dị ứng, bạn có muốn tôi ghi nhớ điều này vĩnh viễn không?").
- **Xóa:** Phải có một giao diện hoặc điểm cuối (endpoint) backend rõ ràng để người dùng xóa hồ sơ hoặc các tập phim (episodes) cụ thể của họ. Trong kiến trúc hiện tại của chúng tôi, nếu người dùng nói "hãy quên tình trạng dị ứng của tôi", lời nhắc trích xuất LLM phải đủ mạnh để xóa khóa hoặc đặt nó thành null.
- **TTL (Thời gian tồn tại):** Các bộ nhớ tập phim hoặc ngữ cảnh ngắn hạn nên có TTL để ngăn chặn sự phát triển bộ lưu trữ không giới hạn và giảm rủi ro giữ lại dữ liệu hội thoại lỗi thời, có thể nhạy cảm vô thời hạn.

### 4. Hạn chế kỹ thuật của giải pháp hiện tại
- **Độ tin cậy của việc giải quyết xung đột:** Việc giải quyết xung đột hiện tại phụ thuộc hoàn toàn vào khả năng của LLM trích xuất để xuất ra sự thật *đã được sửa đổi* bằng cách sử dụng *cùng một khóa chính xác* để ghi đè lên khóa cũ trong từ điển. Nếu LLM tạo ra một khóa khác (ví dụ: `cow_milk_allergy` thay vì cập nhật `allergy`), sự thật cũ bị xung đột vẫn sẽ tồn tại trong hồ sơ.
- **Độ trễ & Chi phí API:** Mỗi tương tác của người dùng sẽ gọi LLM chính để tạo phản hồi và *hai* cuộc gọi LLM nền bổ sung để trích xuất các cập nhật hồ sơ và tập phim. Điều này làm tăng gấp ba lần độ trễ và chi phí API cho mỗi lượt.
- **Phình to cửa sổ ngữ cảnh:** Khi bộ nhớ tập phim và các kết quả ngữ nghĩa tăng lên, việc đưa trực tiếp chúng vào lời nhắc hệ thống có nguy cơ vượt quá giới hạn token, đòi hỏi các chiến lược cắt tỉa hoặc tóm tắt quyết liệt hơn.
