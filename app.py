from flask import Flask, request, jsonify, render_template
import json, os

from dotenv import load_dotenv
from openai import OpenAI

import re

def clean_output(text):
    # remove bold/italic markdown
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    return text

# Load env variables
load_dotenv()

# OpenAI client (FIX for your error)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Fixed lecture-tutorial mapping (MVP assumption)
PAIRING = {
    "lec1_tut1": {
        "lecture": "course_materials/lec1.txt",
        "tutorial": "course_materials/tut1.txt"
    },
    "lec2_tut2": {
        "lecture": "course_materials/lec2.txt",
        "tutorial": "course_materials/tut2.txt"
    },
    "lec3_tut3": {
        "lecture": "course_materials/lec3.txt",
        "tutorial": "course_materials/tut3.txt"
    }
}

def load_file(path):
    with open(path, "r") as f:
        return f.read()

app = Flask(__name__, template_folder='frontend')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student')
def student_page():
    return render_template('student.html')

@app.route('/professor')
def professor_page():
    return render_template('professor.html')

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    pair = data["pair"]
    question = data["question"]

    # Load lecture/tutorial context
    lec_path = PAIRING[pair]["lecture"]
    tut_path = PAIRING[pair]["tutorial"]

    lec_content = load_file(lec_path)
    tut_content = load_file(tut_path)

    # Prompt
    prompt = f"""
    You are a study assistant.

    Use the lecture and tutorial content to explain clearly.

    IMPORTANT FORMATTING RULES:
    - Do NOT use LaTeX formatting (no \( \), no \[ \], no math mode).
    - Write all math in plain text only (e.g. O(n), O(1), x^2 instead of \(x^2\)).
    - Do NOT use Markdown formatting (no **bold**, no bullet markdown, no headings).
    - Use plain text only (no special formatting).
    - Keep explanations simple and student-friendly.

    Lecture:
    {lec_content}

    Tutorial:
    {tut_content}

    Student question:
    {question}

    Explain step by step in a simple way.
    """

    # LLM call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    answer = clean_output(answer)

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
