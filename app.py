from flask import Flask, render_template, request, redirect
import requests
import os
from verifier import verify_answer

app = Flask(__name__)


# -------------------------------
# Wikipedia API
# -------------------------------
def get_wikipedia_answer(question):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + question
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "extract" in data:
            return data["extract"]

    return None


# -------------------------------
# DuckDuckGo API
# -------------------------------
def get_duckduckgo_answer(question):
    url = "https://api.duckduckgo.com/?q=" + question + "&format=json"
    response = requests.get(url).json()

    if "AbstractText" in response and response["AbstractText"]:
        return response["AbstractText"]

    return None


# -------------------------------
# StackOverflow API
# -------------------------------
def get_stackoverflow_answer(question):
    url = "https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q=" + question + "&site=stackoverflow"
    response = requests.get(url)
    data = response.json()

    if "items" in data and len(data["items"]) > 0:
        return data["items"][0]["title"]

    return None


# -------------------------------
# Improve Question
# -------------------------------
def improve_question(question):
    q = question.lower()

    # current topics
    if "current" in q or "today" in q or "latest" in q:
        return q + " news"

    # definition questions
    if "what is" in q:
        return q.replace("what is", "").strip()

    # remove unnecessary words
    remove_words = ["explain", "tell me", "about", "please"]
    for word in remove_words:
        q = q.replace(word, "")

    return q.strip()


# -------------------------------
# Generate Final Answer
# -------------------------------
def generate_answer(question):

    # Fix Wikipedia formatting
    formatted_question = question.replace(" ", "_")

    # 1️⃣ Wikipedia
    wiki = get_wikipedia_answer(formatted_question)
    if wiki:
        return wiki

    # 2️⃣ DuckDuckGo
    duck = get_duckduckgo_answer(question)
    if duck:
        return duck

    # 3️⃣ StackOverflow (only coding)
    if "error" in question or "code" in question or "python" in question:
        stack = get_stackoverflow_answer(question)
        if stack:
            return stack

    return "No exact answer found. Try simple keywords like: AI, India news, Python error."


# -------------------------------
# Home Route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    answer = None
    confidence = None

    if request.method == "POST":

        question = request.form["question"]

        # 🔥 IMPORTANT FIX
        better_question = improve_question(question)

        answer = generate_answer(better_question)

        confidence = verify_answer(answer)

    return render_template("index.html", answer=answer, confidence=confidence)


# -------------------------------
# Feedback Route
# -------------------------------
@app.route("/feedback", methods=["POST"])
def feedback():

    user_feedback = request.form.get("feedback_text")

    with open("feedback.txt", "a") as f:
        f.write(user_feedback + "\n")

    return redirect("/")


# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
