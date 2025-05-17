import os
from flask import Flask, render_template, request, jsonify, send_file, url_for
import random
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from transformers import T5Tokenizer, T5ForConditionalGeneration
from news_scraper.news_loader import load_news # Đã sửa tên thư mục
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import matplotlib
matplotlib.use('Agg') # Quan trọng cho server không có GUI
import matplotlib.pyplot as plt
import io # Cho hình ảnh trong bộ nhớ

# Thử tải lexicon VADER nếu chưa có.
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    print("Lexicon VADER không tìm thấy. Đang tải xuống...")
    nltk.download('vader_lexicon')
except Exception as e: # Bắt các lỗi khác liên quan đến NLTK
    print(f"Lỗi khi kiểm tra/tải lexicon VADER: {e}")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' # Định nghĩa thư mục upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Tạo thư mục nếu chưa có

# === Tải mô hình ===
# Đảm bảo các mô hình này tồn tại ở đường dẫn được chỉ định
try:
    sentiment_model = joblib.load("./models/emotion_classifier.pkl")
    # fruit_model = joblib.load("./models/fruit_model.pkl") # Tải mô hình dinh dưỡng
except FileNotFoundError as e:
    print(f"Lỗi khi tải mô hình: {e}. Đảm bảo các file mô hình đã tồn tại.")
    sentiment_model = None
    # fruit_model = None
except Exception as e: # Bắt các lỗi chung khác khi tải mô hình
    print(f"Lỗi không xác định khi tải mô hình: {e}")
    sentiment_model = None
    # fruit_model = None


# Tải mô hình T5
t5_model_path = "./t5_intent_response_model/checkpoint-9000"
try:
    # Nếu tokenizer của được lưu cùng checkpoint, hãy dùng:
    # t5_tokenizer = T5Tokenizer.from_pretrained(t5_model_path)
    t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
    t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_path)
except OSError as e:
    print(f"Lỗi khi tải mô hình T5: {e}. Kiểm tra đường dẫn và các file.")
    t5_model = None
    t5_tokenizer = None
except Exception as e: # Bắt các lỗi chung khác khi tải mô hình T5
    print(f"Lỗi không xác định khi tải mô hình T5: {e}")
    t5_model = None
    t5_tokenizer = None

# === Dữ liệu dinh dưỡng (ví dụ, nếu fruit_model cần nó ở dạng DataFrame) ===
# Ghi chú: Cách fruit_model sử dụng dữ liệu này phụ thuộc vào cách nó được huấn luyện.
# Đây chỉ là ví dụ cách tải dữ liệu.
# fruit_nutrition_df = None
# try:
#     # Giả sử có file CSV chứa dữ liệu dinh dưỡng mà fruit_model sử dụng
#     fruit_nutrition_df = pd.read_csv("./datasets/expanded_fruit_dataset.csv")
#     # Có thể cần tiền xử lý fruit_nutrition_df ở đây
# except FileNotFoundError:
#     print("Không tìm thấy file expanded_fruit_dataset.csv. Chức năng dinh dưỡng có thể bị hạn chế.")
# except Exception as e:
#     print(f"Lỗi khi tải expanded_fruit_dataset.csv: {e}")


# === Lưu lịch sử trò chuyện ===
chat_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html", chat_history=chat_history)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("user_input")
    if not user_input:
        return render_template("chatbot.html", chat_history=chat_history, error="Vui lòng nhập tin nhắn.")

    bot_response = get_response(user_input)

    chat_history.append({
        "user": user_input,
        "bot": bot_response
    })
    # Giới hạn lịch sử chat (tùy chọn)
    # if len(chat_history) > 50: chat_history.pop(0)

    return render_template("chatbot.html", chat_history=chat_history)

@app.route("/chat_api", methods=["POST"])
def chat_api():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Vui lòng đặt câu hỏi."})
    bot_response = get_response(user_input)
    return jsonify({"response": bot_response})

# === Các hàm chức năng ===
def predict_sentiment(text):
    if sentiment_model:
        try:
            return sentiment_model.predict([text])[0]
        except Exception as e:
            print(f"Lỗi khi dự đoán cảm xúc: {e}")
            return "không xác định"
    return "Mô hình cảm xúc chưa được tải"

def generate_t5_response(text):
    if t5_model and t5_tokenizer:
        try:
            inputs = t5_tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
            outputs = t5_model.generate(
                **inputs,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.9,
                max_length=100
            )
            return t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Lỗi trong quá trình sinh phản hồi T5: {e}")
            return "Xin lỗi, tôi không thể tạo phản hồi lúc này."
    return "Mô hình T5 chưa được tải."

# === Ghi chú về tích hợp fruit_model ===
# Để sử dụng fruit_model, cần định nghĩa cách nó xử lý câu hỏi.
# Ví dụ, nếu fruit_model có hàm `get_nutrition_info(fruit_name_hoac_cau_hoi)`
# def get_nutrition_from_model(user_input):
#     if fruit_model and fruit_nutrition_df is not None:
#         try:
#             # Logic để xác định xem user_input có phải là câu hỏi về dinh dưỡng không
#             # và trích xuất tên trái cây nếu cần.
#             # Ví dụ đơn giản:
#             possible_fruit_name = user_input.lower() # Cần xử lý tinh vi hơn
#             if any(fruit_name in possible_fruit_name for fruit_name in fruit_nutrition_df['name'].str.lower()):
#                 # Đây là nơi sẽ gọi logic của fruit_model
#                 # Ví dụ: nutrition_info = fruit_model.query(user_input, fruit_nutrition_df)
#                 # return nutrition_info
#                 # Tạm thời trả về thông tin từ DataFrame cho mục đích demo
#                 for index, row in fruit_nutrition_df.iterrows():
#                     if row['name'].lower().split(" ")[0] in possible_fruit_name: # tìm từ đầu tiên của tên
#                         return f"Thông tin dinh dưỡng cho {row['name']}: {row['energy (kcal/kJ)']} kcal, {row['sugars (g)']}g đường."
#                 return "Tôi tìm thấy thông tin liên quan đến dinh dưỡng nhưng chưa rõ cụ thể."
#         except Exception as e:
#             print(f"Lỗi khi truy vấn fruit_model: {e}")
#             return "Tôi gặp sự cố khi tra cứu thông tin dinh dưỡng."
#     return None # Không có thông tin dinh dưỡng hoặc mô hình chưa sẵn sàng

def get_response(user_input):
    sentiment = predict_sentiment(user_input)
    
    # === PHẦN TÍCH HỢP FRUIT_MODEL (ĐANG ĐƯỢC CHÚ THÍCH) ===
    # nutrition_response = get_nutrition_from_model(user_input)
    # if nutrition_response:
    #     # Nếu có phản hồi dinh dưỡng, có thể ưu tiên nó
    #     # hoặc kết hợp nó với phản hồi T5.
    #     # Ví dụ: return f"(Cảm xúc: {sentiment}) {nutrition_response}"
    #     # Hoặc:
    #     # t5_response_text = generate_t5_response(user_input)
    #     # return f"(Cảm xúc: {sentiment}) {nutrition_response} Ngoài ra, {t5_response_text}"
    #     pass # Hiện tại bỏ qua để dùng T5 mặc định

    # Mặc định sử dụng T5 nếu không có phản hồi chuyên biệt từ fruit_model
    t5_response = generate_t5_response(user_input)
    return f"(Cảm xúc: {sentiment}) {t5_response}"

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    error_message = None
    if request.method == "POST":
        if 'csv_file' not in request.files or not request.files['csv_file'].filename:
            error_message = "Không có file nào được chọn."
            return render_template("analysis.html", result=result, error=error_message)

        file = request.files["csv_file"]
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
            file.save(filepath)

            try:
                df = pd.read_csv(filepath, nrows=5000)
                if 'Text' not in df.columns:
                    error_message = "File CSV phải có cột 'Text'."
                    return render_template("analysis.html", result=result, error=error_message)

                analyzer = SentimentIntensityAnalyzer()
                positive, negative, neutral = 0, 0, 0

                for review in df['Text']:
                    # Đảm bảo review là string và xử lý giá trị NaN/None
                    score = analyzer.polarity_scores(str(review if pd.notna(review) else ""))['compound']
                    if score > 0.05:
                        positive += 1
                    elif score < -0.05:
                        negative += 1
                    else:
                        neutral += 1
                result = {"positive": positive, "negative": negative, "neutral": neutral}

            except pd.errors.EmptyDataError:
                error_message = "File CSV được tải lên bị trống."
            except Exception as e:
                error_message = f"Lỗi khi xử lý CSV: {e}"
                print(f"Lỗi khi xử lý CSV: {e}")
        else:
            error_message = "Định dạng file không hợp lệ. Vui lòng tải lên file CSV."

    return render_template("analysis.html", result=result, error=error_message)


@app.route("/stats")
def stats():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
    if not os.path.exists(filepath):
        return "File thống kê chưa được tạo. Vui lòng tải lên file CSV trước.", 404

    try:
        df = pd.read_csv(filepath, nrows=5000)
        if 'ProductId' not in df.columns:
            return "Không tìm thấy cột 'ProductId' trong CSV để tạo thống kê.", 400

        top_products = df['ProductId'].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(10, 6))
        top_products.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_xlabel('Mã Sản Phẩm')
        ax.set_ylabel('Số lượng đánh giá')
        ax.set_title('Top 10 sản phẩm được đánh giá nhiều nhất')
        plt.tight_layout()

        img_io = io.BytesIO()
        fig.savefig(img_io, format='png')
        img_io.seek(0)
        plt.close(fig) # Đóng biểu đồ để giải phóng bộ nhớ

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        print(f"Lỗi khi tạo biểu đồ thống kê: {e}")
        return f"Lỗi khi tạo biểu đồ thống kê: {e}", 500


@app.route("/recommend/<product_id>")
def recommend(product_id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
    if not os.path.exists(filepath):
        return render_template("recommend.html", recommended=[], error="Vui lòng phân tích file CSV trước.")

    try:
        df = pd.read_csv(filepath, nrows=5000)
        required_cols = ['UserId', 'ProductId', 'Score']
        if not all(col in df.columns for col in required_cols):
            return render_template("recommend.html", recommended=[], error=f"CSV thiếu các cột cần thiết: {', '.join(required_cols)}.")

        user_product_matrix = df.pivot_table(index='UserId', columns='ProductId', values='Score').fillna(0)

        if product_id not in user_product_matrix.columns:
            return render_template("recommend.html", recommended=[], error=f"Mã sản phẩm '{product_id}' không tìm thấy trong dữ liệu.")

        if user_product_matrix.empty or user_product_matrix.shape[1] < 2:
             return render_template("recommend.html", recommended=[], error="Không đủ dữ liệu để đưa ra gợi ý.")

        item_similarity = cosine_similarity(user_product_matrix.T)
        item_similarity_df = pd.DataFrame(item_similarity, index=user_product_matrix.columns, columns=user_product_matrix.columns)

        # Lấy top 5 sản phẩm tương tự, loại bỏ chính sản phẩm đó (sản phẩm đầu tiên sau khi sort)
        recommendations = item_similarity_df[product_id].sort_values(ascending=False)[1:6].index.tolist()
        return render_template("recommend.html", recommended=recommendations)
    except Exception as e:
        print(f"Lỗi khi gợi ý sản phẩm: {e}")
        return render_template("recommend.html", recommended=[], error=f"Lỗi khi tạo gợi ý: {e}")


@app.route("/helpfulness")
def helpfulness():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
    if not os.path.exists(filepath):
        return render_template("helpful.html", reviews=[], error="Vui lòng phân tích file CSV trước.")

    try:
        df = pd.read_csv(filepath, nrows=5000)
        required_cols = ['HelpfulnessNumerator', 'HelpfulnessDenominator', 'Text']
        if not all(col in df.columns for col in required_cols):
            return render_template("helpful.html", reviews=[], error=f"CSV thiếu các cột cần thiết: {', '.join(required_cols)}.")

        df['HelpfulnessRatio'] = df.apply(
            lambda x: (x['HelpfulnessNumerator'] / x['HelpfulnessDenominator']) if x['HelpfulnessDenominator'] != 0 else 0,
            axis=1
        )
        most_helpful_reviews = df.sort_values(by='HelpfulnessRatio', ascending=False).head(10)
        helpful_reviews_list = most_helpful_reviews[['Text', 'HelpfulnessRatio']].to_dict(orient='records') # Đổi tên biến
        return render_template("helpful.html", reviews=helpful_reviews_list) # Truyền biến đã đổi tên
    except Exception as e:
        print(f"Lỗi ở chức năng helpfulness: {e}")
        return render_template("helpful.html", reviews=[], error=f"Lỗi khi lấy đánh giá hữu ích: {e}")

@app.route("/news")
def news():
    source = request.args.get("source", "nongnghiep") # Mặc định là nongnghiep
    page = int(request.args.get("page", 1))
    articles = load_news(source=source, page=page)
    if articles is None: # Nếu load_news trả về None (ví dụ: scrape_baomoi chưa implement)
        articles = []
    return render_template("news.html", articles=articles, source=source, current_page=page)

@app.route("/news/api")
def news_api():
    source = request.args.get("source", "nongnghiep")
    page = int(request.args.get("page", 1))
    articles = load_news(source=source, page=page)
    if articles is None:
        articles = []
    return jsonify(articles)


if __name__ == "__main__":
    # Đảm bảo thư mục 'uploads' tồn tại khi khởi động
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)