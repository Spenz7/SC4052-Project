from flask import Flask, request, jsonify, render_template
import json, os

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


# Add routes for LLM, student data, aggregation here

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    pair = data["pair"]
    question = data["question"]

    # 1. Load lecture/tutorial context
    lec_path = PAIRING[pair]["lecture"]
    tut_path = PAIRING[pair]["tutorial"]

    with open(lec_path, "r") as f:
        lec_content = f.read()

    with open(tut_path, "r") as f:
        tut_content = f.read()

    # 2. Build prompt (VERY IMPORTANT for grading)
    prompt = f"""
You are a study assistant.

Use the lecture and tutorial content to explain clearly.

Lecture:
{lec_content}

Tutorial:
{tut_content}

Student question:
{question}

Explain step by step in a simple way.
"""

    # 3. Call LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    return {"answer": answer}

if __name__ == '__main__':
    app.run(debug=True)
