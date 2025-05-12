from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

chat_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form["user_input"]
        # Tạm thời: phản hồi đơn giản
        bot_response = f"Bot trả lời: Bạn hỏi '{user_input}'"
        chat_history.append({"user": user_input, "bot": bot_response})
        return redirect("/chat")  # Redirect lại trang chatbot sau khi gửi form

    return render_template("chatbot.html", chat_history=chat_history)

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

@app.route("/news", methods=["GET"])
def news():
    fruit = request.args.get("fruit_type")
    # Tạm thời: tin tức mẫu
    mock_news = [
        {"title": f"Tình hình mùa vụ {fruit}", "summary": f"{fruit.capitalize()} đang vào mùa thu hoạch.", "date": "2025-05-12"},
        {"title": f"Giá {fruit} tăng", "summary": f"Giá {fruit} tăng nhẹ trong tuần qua.", "date": "2025-05-10"},
    ] if fruit else []
    return render_template("news.html", articles=mock_news)

if __name__ == "__main__":
    app.run(debug=True)
