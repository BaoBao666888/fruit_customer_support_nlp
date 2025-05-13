import os
from flask import Flask, render_template, request, jsonify
import random
import joblib
from transformers import T5Tokenizer, T5ForConditionalGeneration
from news_scraper.news_loader import load_news
from chatbot.search import search_product
from chatbot.recommender import suggest_product

app = Flask(__name__)

# === Load mô hình ===
sentiment_model = joblib.load("./models/emotion_classifier.pkl")
fruit_model = joblib.load("./models/fruit_model.pkl")  # đảm bảo mô hình đúng version sklearn

# Load mô hình T5 (dùng tokenizer từ mô hình gốc nếu checkpoint không có spiece.model)
t5_model_path = "./t5_intent_response_model/checkpoint-9000"
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_path)

# === Lưu lịch sử trò chuyện
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
    bot_response = get_response(user_input)

    chat_history.append({
        "user": user_input,
        "bot": bot_response
    })

    return render_template("chatbot.html", chat_history=chat_history)

@app.route("/chat_api", methods=["POST"])
def chat_api():
    user_input = request.json.get("message", "")
    bot_response = get_response(user_input)
    return jsonify({"response": bot_response})

# === Phân tích cảm xúc sử dụng mô hình ML
def predict_sentiment(text):
    return sentiment_model.predict([text])[0]

# === Sinh phản hồi bằng mô hình T5 với ngẫu nhiên hóa
def generate_t5_response(text):
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

# === Tổng hợp phản hồi chatbot
def get_response(user_input):
    sentiment = predict_sentiment(user_input)
    response = generate_t5_response(user_input)
    return f"(Cảm xúc: {sentiment}) {response}"

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    if request.method == "POST":
        file = request.files["csv_file"]
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Phân tích dữ liệu CSV nếu cần (tạm thời giả lập)
        result = {
            "positive": 5,
            "negative": 2,
            "neutral": 3
        }
    return render_template("analysis.html", result=result)

@app.route("/news")
def news():
    source = request.args.get("source", "nongnghiep")
    page = int(request.args.get("page", 1))
    articles = load_news(source=source, page=page)

    return render_template("news.html", articles=articles, source=source, current_page=page)















@app.route("/news/api")
def news_api():
    source = request.args.get("source", "nongnghiep")
    page = int(request.args.get("page", 1))
    articles = load_news(source=source, page=page)
    return jsonify(articles)


if __name__ == "__main__":
    app.run(debug=True)