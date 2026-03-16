from flask import Flask, render_template, request
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

    if response["Abstract"]:
        return response["Abstract"]

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
# Generate Final Answer
# -------------------------------
def generate_answer(question):

    # First try Wikipedia
    wiki = get_wikipedia_answer(question)

    if wiki:
        return wiki

    # Then try DuckDuckGo
    duck = get_duckduckgo_answer(question)

    if duck:
        return duck

    return "Sorry, no verified answer found."


# -------------------------------
# Home Route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    answer = None
    confidence = None

    if request.method == "POST":

        question = request.form["question"]

        answer = generate_answer(question)

        confidence = verify_answer(answer)

    return render_template("index.html", answer=answer, confidence=confidence)


# -------------------------------
# Feedback Route
# -------------------------------
@app.route("/feedback", methods=["POST"])
def feedback():

    user_feedback = request.form["feedback_text"]

    with open("feedback.txt", "a") as f:
        f.write(user_feedback + "\n")

    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


