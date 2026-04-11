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
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_student_file(student_id):
    return os.path.join(STUDENT_FOLDER, f"student_{student_id}.json")


def default_struggles():
    return {k: [] for k in PAIRING.keys()}

def load_student_data(student_id):
    path = get_student_file(student_id)

    if not os.path.exists(path):
        return {
            "student_id": student_id,
            "struggles": default_struggles()
        }

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_student_data(student_id, data):
    os.makedirs(STUDENT_FOLDER, exist_ok=True)
    path = get_student_file(student_id)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def resolve_pair(selection):
    mapping = {
        "lec1": "lec1_tut1",
        "tut1": "lec1_tut1",
        "lec2": "lec2_tut2",
        "tut2": "lec2_tut2",
        "lec3": "lec3_tut3",
        "tut3": "lec3_tut3"
    }

    return mapping.get(selection)


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
    student_type = data["type"]          # "lec" or "tut"
    selection = data["selection"]        # "lec1", "tut1", etc.
    question = data["question"]

    # -------------------------
    # RESOLVE PAIR (FIXED)
    # -------------------------
    pair = resolve_pair(selection)

    if pair is None:
        return jsonify({"error": "Invalid selection"}), 400

    # -------------------------
    # LOAD COURSE MATERIALS
    # -------------------------
    lec_content = load_file(PAIRING[pair]["lecture"])
    tut_content = load_file(PAIRING[pair]["tutorial"])

    # -------------------------
    # BUILD PROMPT
    # -------------------------
    prompt = f"""
You are a study assistant.

Use the lecture and tutorial content to explain clearly.

IMPORTANT FORMATTING RULES:
- Do NOT use LaTeX formatting.
- Write all math in plain text only (e.g. O(n), O(1), x^2).
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
    print("\n========== PROMPT SENT TO GPT ==========\n")
    print(prompt)
    print("\n=======================================\n")
    
    # -------------------------
    # CALL LLM
    # -------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    answer = clean_output(answer)

    # -------------------------
    # STRUGGLE STORAGE
    # -------------------------
    student_data = load_student_data(student_id)

    struggle = {
        "type": student_type,
        "content": question.strip()
    }

    if pair not in student_data["struggles"]:
        student_data["struggles"][pair] = []

    existing = [s["content"] for s in student_data["struggles"][pair]]

    if struggle["content"] not in existing:
        student_data["struggles"][pair].append(struggle)

    save_student_data(student_id, student_data)

    # -------------------------
    # RETURN RESPONSE
    # -------------------------
    return jsonify({"answer": answer})

# =========================
# VIEW STRUGGLES ENDPOINT
# =========================
@app.route("/view_struggles", methods=["GET"])
def view_struggles():
    student_id = request.args.get("student_id")

    if not student_id:
        return jsonify({"error": "Missing student_id"}), 400

    student_data = load_student_data(student_id)

    return jsonify({
        "student_id": student_id,
        "struggles": student_data["struggles"]
    })

if __name__ == '__main__':
    app.run(debug=True)
