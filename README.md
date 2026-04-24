# Lab #17: Multi-Memory Agent with LangGraph

Dự án này triển khai một Tác nhân AI được trang bị đầy đủ các loại bộ nhớ bằng cách sử dụng LangGraph. Nó được thiết kế để đáp ứng các yêu cầu của Rubric Lab 17.

## Cấu trúc

Hệ thống bao gồm 4 loại bộ nhớ:

1. **Bộ nhớ Ngắn hạn (Short-term Memory)**: Bộ đệm hội thoại thông qua trạng thái LangGraph và cơ chế cửa sổ trượt.
2. **Hồ sơ Dài hạn (Long-term Profile)**: Bộ lưu trữ KV dạng JSON cho các thông tin người dùng cố định.
3. **Bộ nhớ Tập phim (Episodic Memory)**: Danh sách JSON để ghi nhật ký và tóm tắt các sự kiện/nhiệm vụ.
4. **Bộ nhớ Ngữ nghĩa (Semantic Memory)**: ChromaDB để truy xuất kiến thức dựa trên vector.

## Hướng dẫn cài đặt

1. **Cài đặt các thư viện phụ thuộc:**

```bash
pip install -r requirements.txt
```

2. **Thiết lập API Keys:**
   Tạo một file `.env` trong thư mục gốc:

```env
OPENAI_API_KEY=your_api_key_here
```

## Chạy Benchmark

Benchmark so sánh tác nhân `no-memory` (không bộ nhớ) cơ bản với tác nhân LangGraph `with-memory` (có bộ nhớ) qua 10 tình huống hội thoại đa lượt, bao gồm truy xuất hồ sơ, cập nhật xung đột, nhớ lại tập phim và truy xuất ngữ nghĩa.

Chạy benchmark:

```bash
python benchmarks/runner.py
```

Kết quả so sánh benchmark sẽ được xuất trực tiếp ra file `BENCHMARK.md`.

## Cấu trúc dự án

- `agent/`: Định nghĩa LangGraph (`graph.py`), các node và lời nhắc (prompts).
- `memory/`: Giao diện và triển khai cho 4 loại bộ nhớ.
- `benchmarks/`: 10 kịch bản kiểm thử đa lượt và script chạy benchmark.
- `data/`: Thư mục lưu trữ dữ liệu tự động cho ChromaDB và các file JSON.
- `REFLECTION.md`: Thảo luận về quyền riêng tư, PII, TTL và các hạn chế kỹ thuật.
