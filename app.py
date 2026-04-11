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

@app.route("/cohort_analytics", methods=["GET"])
def cohort_analytics():
    pair = request.args.get("pair")  # e.g. lec1_tut1

    if pair not in PAIRING:
        return jsonify({"error": "Invalid pair"}), 400

    # ------------------------
    # LOAD COURSE MATERIALS
    # ------------------------
    lec_content = load_file(PAIRING[pair]["lecture"])
    tut_content = load_file(PAIRING[pair]["tutorial"])

    # ------------------------
    # LOAD ALL STUDENT STRUGGLES
    # ------------------------
    all_struggles = []

    for file in os.listdir(STUDENT_FOLDER):
        if file.endswith(".json"):
            with open(os.path.join(STUDENT_FOLDER, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                struggles = data.get("struggles", {}).get(pair, [])
                for s in struggles:
                    if isinstance(s, dict):
                        content = s.get("content", "")
                        if content.strip():
                            all_struggles.append(content)
    if not all_struggles:
        return jsonify({
            "pair": pair,
            "analysis": "No student data available for this lecture/tutorial pair yet."
        }), 200
    
    # ------------------------
    # BUILD PROMPT
    # ------------------------
    prompt = f"""
        You are an educational analytics system.

        Analyze student struggles and identify learning patterns.

        LECTURE CONTENT:
        {lec_content}

        TUTORIAL CONTENT:
        {tut_content}

        STUDENT STRUGGLES:
        {chr(10).join(all_struggles)}

        TASK:
        Analyze student struggles for a lecture/tutorial pair and produce a concise cohort-level summary.

        You must:

        Each student struggle must be assigned to exactly ONE tutorial question.
        Do not duplicate assignments across questions.
        Map each student struggle cluster to the single best matching tutorial question (Q1, Q2, etc.) using semantic similarity.
        For each tutorial question, compute:
        MATCH_COUNT = number of student struggles assigned to it
        Rank tutorial questions using ONLY MATCH_COUNT:
        Higher MATCH_COUNT = higher rank
        No other factor is allowed to affect ranking
        If two questions have the same MATCH_COUNT, break ties using:
        stronger and more consistent semantic alignment (only as a tie-breaker, never for primary ranking)

        IMPORTANT RULE:

        You must compute MATCH_COUNT based only on the final assigned grouping of struggles. Each struggle counts once only.
        You MUST NOT reorder questions based on explanation quality or clarity.

        IMPORTANT DESIGN NOTE:

        Tutorial question IDs (Q1, Q2, etc.) are not stored or tracked in the system.
        There is no ground-truth mapping between student struggles and tutorial questions.
        Any mapping is inferred dynamically using tutorial content and semantic similarity.
        Student references to question numbers are weak contextual signals only.

        IMPORTANT OUTPUT CONSTRAINTS:

        Do NOT use Markdown.
        Do NOT use symbols like ###, **, *, or -.
        Do NOT include indices, list positions, or ordering of student struggle entries.
        Only use tutorial question IDs (Q1, Q2, etc.) when referring to tutorial questions.
        Do NOT infer weak relationships to include extra tutorial questions.
        Only include tutorial questions that have at least one strong semantic match with student struggles.
        If a tutorial question has no strong evidence of student difficulty, it MUST be excluded.

        OUTPUT FORMAT (STRICT):

        Main Student Struggles:
        Ranked list of key conceptual difficulties (most common to least common, based on number of student mentions per concept cluster)
        Tutorial Questions with Highest Difficulty:
        Ranked list of tutorial questions (most to least struggled, based strictly on counted matches after clustering)
        Each item must include:
        Tutorial question ID (Q1, Q2, etc.)
        Short description of the associated struggle pattern
        Only include questions with strong evidence of student struggle
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a teaching analytics assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content
    result = clean_output(result)

    result = re.sub(r"#{2,6}\s*", "", result)

    return jsonify({
        "pair": pair,
        "analysis": result
    })

if __name__ == '__main__':
    app.run(debug=True)
