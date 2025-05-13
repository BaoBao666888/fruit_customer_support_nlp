import os
from flask import Flask, render_template, request, jsonify
import random
from news_scraper.news_loader import load_news, get_article_by_id
from chatbot.search import search_product
from chatbot.recommender import suggest_product
from sentiment_analysis.sentiment import predict_sentiment



app = Flask(__name__)

# === Lưu lịch sử trò chuyện (mất sau mỗi lần chạy lại)
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

# === API gọi từ giao diện JavaScript không cần reload
@app.route("/chat_api", methods=["POST"])
def chat_api():
    user_input = request.json.get("message", "")
    bot_response = get_response(user_input)
    return jsonify({"response": bot_response})

# === Giả lập phản hồi (thay bằng NLP thật)
def get_response(user_input):
    sentiment = predict_sentiment(user_input)
    search_result = search_product(user_input)

    if search_result:
        return f"(Cảm xúc: {sentiment}) {search_result}"
    
    if "gợi ý" in user_input or "nên mua" in user_input:
        return f"(Cảm xúc: {sentiment}) {suggest_product()}"

    if "giá" in user_input:
        return "(Cảm xúc: {}) Giá cụ thể bạn cần tìm loại nào?".format(sentiment)

    if "tiêu cực" in sentiment:
        return "(Cảm xúc: {}) Tôi thấy bạn đang không vui, có gì tôi có thể giúp không?".format(sentiment)
    if "tích cực" in sentiment:
        return "(Cảm xúc: {}) Tôi rất vui khi bạn hài lòng, có gì tôi có thể giúp không?".format(sentiment)
    if "trung lập" in sentiment:
        return "(Cảm xúc: {}) Tôi không rõ cảm xúc của bạn, có gì tôi có thể giúp không?".format(sentiment)
    return "(Cảm xúc: {}) Tôi chưa hiểu rõ câu hỏi, bạn cần giúp gì về trái cây?".format(sentiment)

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    if request.method == "POST":
        file = request.files["csv_file"]
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Logic phân tích dữ liệu ở đây (có thể dùng thư viện pandas)
        result = {
            "positive": 5,
            "negative": 2,
            "neutral": 3
        }
    return render_template("analysis.html", result=result)

@app.route("/news")
def news():
    fruit_type = request.args.get("fruit_type")
    articles = load_news(fruit_type=fruit_type)
    return render_template("news.html", articles=articles)

@app.route("/news/<int:article_id>")
def news_detail(article_id):
    article = get_article_by_id(article_id)
    if not article:
        return "Không tìm thấy bài viết", 404
    return render_template("news_detail.html", article=article)

if __name__ == "__main__":
    app.run(debug=True)
