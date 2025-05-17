# Fruit Customer Support NLP

## Giới thiệu
Đây là project ứng dụng Xử lý ngôn ngữ tự nhiên (NLP) cho hỗ trợ khách hàng ngành trái cây, bao gồm chatbot, phân tích cảm xúc, gợi ý sản phẩm, và tổng hợp tin tức.

## Hướng dẫn cài đặt

1. **Clone source code từ Github**  
   ```bash
   git clone https://github.com/BaoBao666888/fruit_customer_support_nlp.git
   cd fruit_customer_support_nlp
   ```

2. **Cài đặt thư viện**
   ```bash
   pip install -r requirements.txt
   ```

3. **Tải các model cần thiết**
   - **Cách 1: Tải tự động bằng script (khuyên dùng)**
     ```bash
     python download_models.py
     ```
     > Script sẽ tự động tải và đặt các thư mục `models` và `t5_intent_response_model` vào đúng vị trí.

   - **Cách 2: Tải thủ công từ Google Drive**
     - [models (emotion, fruit, ...)](https://drive.google.com/drive/folders/1V4peAevvw_JYdvVRcCoPgyZ243axDb6g)
     - [t5_intent_response_model](https://drive.google.com/drive/folders/1o09syinXz4mIPG8xhENyrfKqoFEtaH2E)
     - Sau khi tải về, giải nén (nếu có) và đặt:
       - Thư mục `models` vào trong thư mục gốc của project (cùng cấp với `app.py`)
       - Thư mục `t5_intent_response_model` vào trong thư mục gốc của project

4. **Chạy ứng dụng**
   ```bash
   python app.py
   ```

## Demo

- [Link video demo](https://drive.google.com/drive/folders/1CPE0AOsL_o4KOJos-wL_IsTQb7sdSSzE?usp=sharing)

## Github

- [Link Github](https://github.com/BaoBao666888/fruit_customer_support_nlp)  
  (Lưu ý: Github không chứa các model do giới hạn dung lượng.)

---

## Liên hệ

- Nếu có thắc mắc về cài đặt hoặc sử dụng, vui lòng liên hệ.