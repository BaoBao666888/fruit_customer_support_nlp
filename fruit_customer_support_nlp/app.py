from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Fruit Customer Support NLP!"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    # Dummy response
    return jsonify({"response": f"Bạn vừa nói: {user_input}"})

if __name__ == "__main__":
    app.run(debug=True)
