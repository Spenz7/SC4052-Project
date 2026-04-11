from flask import Flask, request, jsonify, render_template
import json, os
import re

from dotenv import load_dotenv
from openai import OpenAI

# =========================
# CLEAN OUTPUT FUNCTION
# =========================
def clean_output(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    return text

# =========================
# LOAD ENV + CLIENT
# =========================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# FILE PATHS
# =========================
STUDENT_FOLDER = "students"

# =========================
# PAIRING
# =========================
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

# =========================
# HELPERS
# =========================
def load_file(path):
    with open(path, "r") as f:
        return f.read()


def get_student_file(student_id):
    return os.path.join(STUDENT_FOLDER, f"student_{student_id}.json")


def load_student_data(student_id):
    path = get_student_file(student_id)

    if not os.path.exists(path):
        return {
            "student_id": student_id,
            "struggles": {}
        }

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_student_data(student_id, data):
    path = get_student_file(student_id)
    os.makedirs(STUDENT_FOLDER, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =========================
# FLASK APP
# =========================
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


# =========================
# MAIN ENDPOINT
# =========================
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    student_id = data["student_id"]
    pair = data["pair"]
    question = data["question"]

    # =========================
    # LOAD COURSE MATERIALS
    # =========================
    lec_content = load_file(PAIRING[pair]["lecture"])
    tut_content = load_file(PAIRING[pair]["tutorial"])

    # =========================
    # BUILD PROMPT
    # =========================
    prompt = f"""
You are a study assistant.

Use the lecture and tutorial content to explain clearly.

IMPORTANT FORMATTING RULES:
- Do NOT use LaTeX formatting (no \\( \\), no \\[ \\], no math mode).
- Write all math in plain text only (e.g. O(n), O(1), x^2 instead of x^2).
- Do NOT use Markdown formatting.
- Use plain text only.

Lecture:
{lec_content}

Tutorial:
{tut_content}

Student question:
{question}

Explain step by step in a simple way.
"""

    # =========================
    # CALL LLM
    # =========================
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    answer = clean_output(answer)

    # =========================
    # STRUGGLE STORAGE LOGIC (NEW)
    # =========================
    student_data = load_student_data(student_id)

    # simple MVP extraction (you can upgrade later with LLM)
    struggle = question.lower().strip()

    if pair not in student_data["struggles"]:
        student_data["struggles"][pair] = []

    # dedup
    if struggle not in student_data["struggles"][pair]:
        student_data["struggles"][pair].append(struggle)

    save_student_data(student_id, student_data)

    # =========================
    # RETURN RESPONSE
    # =========================
    return jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True)
