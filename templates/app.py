import os
from flask import Flask, render_template, request, jsonify, send_file
import random
import joblib
from transformers import T5Tokenizer, T5ForConditionalGeneration
from news_scraper.news_loader import load_news, get_article_by_id
from chatbot.search import search_product
from chatbot.recommender import suggest_product
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import matplotlib.pyplot as plt

nltk.download('vader_lexicon')

app = Flask(__name__)

# === Load mô hình ===
sentiment_model = joblib.load("emotion_classifier.pkl")
fruit_model = joblib.load("fruit_model.pkl")

t5_model_path = "t5_intent_response_model/checkpoint-9000"
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_path)

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

# === Functions ===
def predict_sentiment(text):
    return sentiment_model.predict([text])[0]

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

def get_response(user_input):
    sentiment = predict_sentiment(user_input)
    response = generate_t5_response(user_input)
    return f"(Cảm xúc: {sentiment}) {response}"

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    if request.method == "POST":
        file = request.files["csv_file"]
        filepath = os.path.join("uploads", "latest.csv")
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)

        df = pd.read_csv(filepath, nrows=5000)
        analyzer = SentimentIntensityAnalyzer()
        positive, negative, neutral = 0, 0, 0

        for review in df['Text']:
            score = analyzer.polarity_scores(str(review))['compound']
            if score > 0.05:
                positive += 1
            elif score < -0.05:
                negative += 1
            else:
                neutral += 1

        result = {"positive": positive, "negative": negative, "neutral": neutral}

    return render_template("analysis.html", result=result)

@app.route("/stats")
def stats():
    filepath = os.path.join("uploads", "latest.csv")
    df = pd.read_csv(filepath, nrows=5000)
    top_products = df['ProductId'].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    top_products.plot(kind='bar', color='skyblue')
    plt.xlabel('Product ID')
    plt.ylabel('Số lượng đánh giá')
    plt.title('Top 10 sản phẩm được đánh giá nhiều nhất')
    chart_path = "uploads/stats_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)

    return send_file(chart_path, mimetype='image/png')

@app.route("/recommend/<product_id>")
def recommend(product_id):
    filepath = os.path.join("uploads", "latest.csv")
    df = pd.read_csv(filepath, nrows=5000)
    user_product_matrix = df.pivot_table(index='UserId', columns='ProductId', values='Score').fillna(0)
    item_similarity = cosine_similarity(user_product_matrix.T)
    item_similarity_df = pd.DataFrame(item_similarity, index=user_product_matrix.columns, columns=user_product_matrix.columns)

    if product_id not in item_similarity_df:
        return render_template("recommend.html", recommended=[])

    recommendations = item_similarity_df[product_id].sort_values(ascending=False)[1:6].index.tolist()
    return render_template("recommend.html", recommended=recommendations)

@app.route("/helpfulness")
def helpfulness():
    filepath = os.path.join("uploads", "latest.csv")
    df = pd.read_csv(filepath, nrows=5000)
    df['HelpfulnessRatio'] = df.apply(
        lambda x: x['HelpfulnessNumerator'] / x['HelpfulnessDenominator'] if x['HelpfulnessDenominator'] != 0 else 0,
        axis=1
    )
    most_helpful_reviews = df.sort_values(by='HelpfulnessRatio', ascending=False).head(10)
    helpful_reviews = most_helpful_reviews[['Text', 'HelpfulnessRatio']].to_dict(orient='records')
    return render_template("helpful.html", reviews=helpful_reviews)

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