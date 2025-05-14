import os
from flask import Flask, render_template, request, jsonify, send_file, url_for # Added url_for
import random
import joblib
import pandas as pd
# from torch import cosine_similarity # <<< VERWIJDER DEZE
from sklearn.metrics.pairwise import cosine_similarity # <<< VOEG DEZE TOE
from transformers import T5Tokenizer, T5ForConditionalGeneration
from news_scraper.news_loader import load_news
# from chatbot.search import search_product # Niet gebruikt?
# from chatbot.recommender import suggest_product # Niet gebruikt?
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import matplotlib
matplotlib.use('Agg') # Belangrijk voor servers zonder GUI
import matplotlib.pyplot as plt
import io # Voor in-memory image

# Probeer VADER lexicon te downloaden als het niet bestaat.
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    print("VADER lexicon niet gevonden. Aan het downloaden...")
    nltk.download('vader_lexicon')
except Exception as e: # Andere mogelijke NLTK-gerelateerde fouten afvangen
    print(f"Fout bij controleren/downloaden VADER lexicon: {e}")


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' # Definieer upload map
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Maak map als deze niet bestaat

# === Load mô hình ===
# Zorg ervoor dat deze modellen bestaan op de opgegeven paden
try:
    sentiment_model = joblib.load("./models/emotion_classifier.pkl")
    # fruit_model = joblib.load("./models/fruit_model.pkl") # Lijkt niet gebruikt te worden
except FileNotFoundError as e:
    print(f"Fout bij laden model: {e}. Zorg ervoor dat de modellen aanwezig zijn.")
    sentiment_model = None # of exit()

# Load mô hình T5
t5_model_path = "./t5_intent_response_model/checkpoint-9000"
try:
    t5_tokenizer = T5Tokenizer.from_pretrained("t5-small") # Of T5Tokenizer.from_pretrained(t5_model_path) als tokenizer bestanden daar zijn
    t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_path)
except OSError as e:
    print(f"Fout bij laden T5 model: {e}. Controleer het pad en de bestanden.")
    t5_model = None
    t5_tokenizer = None


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
    if not user_input:
        return render_template("chatbot.html", chat_history=chat_history, error="Voer een bericht in.")

    bot_response = get_response(user_input)

    chat_history.append({
        "user": user_input,
        "bot": bot_response
    })
    # Zorg ervoor dat chat_history niet te groot wordt (optioneel)
    # if len(chat_history) > 50: chat_history.pop(0)

    return render_template("chatbot.html", chat_history=chat_history)

@app.route("/chat_api", methods=["POST"])
def chat_api():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Stel alstublieft een vraag."})
    bot_response = get_response(user_input)
    return jsonify({"response": bot_response})

# === Functions ===
def predict_sentiment(text):
    if sentiment_model:
        return sentiment_model.predict([text])[0]
    return "Sentiment model niet geladen"

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
            print(f"Fout tijdens T5 generatie: {e}")
            return "Sorry, ik kon geen antwoord genereren."
    return "T5 model niet geladen."

def get_response(user_input):
    sentiment = predict_sentiment(user_input)
    response = generate_t5_response(user_input)
    return f"(Cảm xúc: {sentiment}) {response}"

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    error_message = None
    if request.method == "POST":
        if 'csv_file' not in request.files or not request.files['csv_file'].filename:
            error_message = "Geen bestand geselecteerd."
            return render_template("analysis.html", result=result, error=error_message)

        file = request.files["csv_file"]
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
            file.save(filepath)

            try:
                df = pd.read_csv(filepath, nrows=5000)
                if 'Text' not in df.columns:
                    error_message = "CSV bestand moet een 'Text' kolom bevatten."
                    return render_template("analysis.html", result=result, error=error_message)

                analyzer = SentimentIntensityAnalyzer()
                positive, negative, neutral = 0, 0, 0

                # Gebruik .get() met een default lege string om KeyError te voorkomen als een review None of NaN is
                for review in df['Text']:
                    score = analyzer.polarity_scores(str(review if pd.notna(review) else ""))['compound']
                    if score > 0.05:
                        positive += 1
                    elif score < -0.05:
                        negative += 1
                    else:
                        neutral += 1
                result = {"positive": positive, "negative": negative, "neutral": neutral}

                # Genereer de grafiek direct na de analyse zodat deze beschikbaar is
                # generate_stats_chart(df) # Optioneel als je het op schijf wilt opslaan

            except pd.errors.EmptyDataError:
                error_message = "Het geüploade CSV bestand is leeg."
            except Exception as e:
                error_message = f"Fout bij verwerken CSV: {e}"
                print(f"Fout bij verwerken CSV: {e}")
        else:
            error_message = "Ongeldig bestandsformaat. Upload alstublieft een CSV bestand."

    return render_template("analysis.html", result=result, error=error_message)


@app.route("/stats")
def stats():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
    if not os.path.exists(filepath):
        # Je kunt een placeholder afbeelding terugsturen of een 404
        return "Statistiekenbestand nog niet gegenereerd. Upload eerst een CSV.", 404

    try:
        df = pd.read_csv(filepath, nrows=5000)
        if 'ProductId' not in df.columns:
             # Stuur een lege afbeelding of foutmelding
            return "ProductId kolom niet gevonden in CSV voor statistieken.", 400

        top_products = df['ProductId'].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(10, 6)) # Gebruik fig, ax
        top_products.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_xlabel('Product ID')
        ax.set_ylabel('Số lượng đánh giá')
        ax.set_title('Top 10 sản phẩm được đánh giá nhiều nhất')
        plt.tight_layout()

        img_io = io.BytesIO()
        fig.savefig(img_io, format='png') # Sla figuur op
        img_io.seek(0)
        plt.close(fig) # Sluit de figuur

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        print(f"Fout bij genereren statistieken: {e}")
        # Stuur eventueel een foutafbeelding of tekst
        return f"Fout bij genereren statistieken: {e}", 500


@app.route("/recommend/<product_id>")
def recommend(product_id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
    if not os.path.exists(filepath):
        return render_template("recommend.html", recommended=[], error="Analyseer eerst een CSV bestand.")

    try:
        df = pd.read_csv(filepath, nrows=5000)
        if not all(col in df.columns for col in ['UserId', 'ProductId', 'Score']):
            return render_template("recommend.html", recommended=[], error="CSV mist benodigde kolommen (UserId, ProductId, Score).")

        user_product_matrix = df.pivot_table(index='UserId', columns='ProductId', values='Score').fillna(0)

        if product_id not in user_product_matrix.columns:
            return render_template("recommend.html", recommended=[], error=f"Product ID '{product_id}' niet gevonden in de data.")

        # Zorg ervoor dat de matrix niet leeg is na pivot
        if user_product_matrix.empty or user_product_matrix.shape[1] < 2: # Minimaal 2 items nodig voor similariteit
             return render_template("recommend.html", recommended=[], error="Niet genoeg data om aanbevelingen te doen.")


        item_similarity = cosine_similarity(user_product_matrix.T)
        item_similarity_df = pd.DataFrame(item_similarity, index=user_product_matrix.columns, columns=user_product_matrix.columns)

        recommendations = item_similarity_df[product_id].sort_values(ascending=False)[1:6].index.tolist()
        return render_template("recommend.html", recommended=recommendations)
    except Exception as e:
        print(f"Fout bij aanbevelen: {e}")
        return render_template("recommend.html", recommended=[], error=f"Fout bij genereren aanbevelingen: {e}")


@app.route("/helpfulness")
def helpfulness():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "latest.csv")
    if not os.path.exists(filepath):
        return render_template("helpful.html", reviews=[], error="Analyseer eerst een CSV bestand.")

    try:
        df = pd.read_csv(filepath, nrows=5000)
        if not all(col in df.columns for col in ['HelpfulnessNumerator', 'HelpfulnessDenominator', 'Text']):
            return render_template("helpful.html", reviews=[], error="CSV mist benodigde kolommen (HelpfulnessNumerator, HelpfulnessDenominator, Text).")

        df['HelpfulnessRatio'] = df.apply(
            lambda x: x['HelpfulnessNumerator'] / x['HelpfulnessDenominator'] if x['HelpfulnessDenominator'] != 0 else 0,
            axis=1
        )
        most_helpful_reviews = df.sort_values(by='HelpfulnessRatio', ascending=False).head(10)
        helpful_reviews = most_helpful_reviews[['Text', 'HelpfulnessRatio']].to_dict(orient='records')
        return render_template("helpful.html", reviews=helpful_reviews)
    except Exception as e:
        print(f"Fout bij helpfulness: {e}")
        return render_template("helpful.html", reviews=[], error=f"Fout bij ophalen helpful reviews: {e}")

@app.route("/news")
def news():
    source = request.args.get("source", "nongnghiep")
    page = int(request.args.get("page", 1))
    articles = load_news(source=source, page=page)
    if articles is None: # Als load_news None retourneert (bv. voor scrape_baomoi)
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
    # Zorg ervoor dat de 'uploads' map bestaat bij het opstarten
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)