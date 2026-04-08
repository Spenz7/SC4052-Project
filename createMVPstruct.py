import os
import json

# --- Project root ---
root = "SC4052-Project"
os.makedirs(root, exist_ok=True)

# --- .env ---
with open(os.path.join(root, ".env"), "w") as f:
    f.write("OPENAI_API_KEY=your_openai_api_key_here\n")

# --- .gitignore ---
with open(os.path.join(root, ".gitignore"), "w") as f:
    f.write(".env\n__pycache__/\n")

# --- README.md ---
with open(os.path.join(root, "README.md"), "w") as f:
    f.write("# Study Assistant-as-a-Service (SAaaS) MVP\n\n"
            "Minimal setup instructions and usage for demo.\n")

# --- requirements.txt ---
with open(os.path.join(root, "requirements.txt"), "w") as f:
    f.write("flask\nopenai\npython-dotenv\n")

# --- Backend: app.py ---
with open(os.path.join(root, "app.py"), "w") as f:
    f.write(
        "from flask import Flask, request, jsonify, render_template\n"
        "import json, os\n\n"
        "app = Flask(__name__, template_folder='frontend')\n\n"
        "@app.route('/')\n"
        "def student_page():\n"
        "    return render_template('index.html')\n\n"
        "@app.route('/professor')\n"
        "def professor_page():\n"
        "    return render_template('professor.html')\n\n"
        "# Add routes for LLM, student data, aggregation here\n\n"
        "if __name__ == '__main__':\n"
        "    app.run(debug=True)\n"
    )

# --- Frontend ---
frontend_path = os.path.join(root, "frontend")
os.makedirs(frontend_path, exist_ok=True)

# index.html
with open(os.path.join(frontend_path, "index.html"), "w") as f:
    f.write(
        "<!DOCTYPE html>\n<html>\n<head>\n<title>Student Page</title>\n</head>\n"
        "<body>\n<h1>Student Interface</h1>\n<!-- Input, buttons, output here -->\n</body>\n</html>"
    )

# professor.html
with open(os.path.join(frontend_path, "professor.html"), "w") as f:
    f.write(
        "<!DOCTYPE html>\n<html>\n<head>\n<title>Professor Page</title>\n</head>\n"
        "<body>\n<h1>Professor Interface</h1>\n<!-- Query and results here -->\n</body>\n</html>"
    )

# main.js
with open(os.path.join(frontend_path, "main.js"), "w") as f:
    f.write("// JS for frontend interactions and fetch calls to backend\n")

# styles.css
with open(os.path.join(frontend_path, "styles.css"), "w") as f:
    f.write("/* Optional CSS styling */\n")

# --- Students folder ---
students_path = os.path.join(root, "students")
os.makedirs(students_path, exist_ok=True)

# Example student JSONs
for student_id in ["12345", "67890"]:
    student_file = os.path.join(students_path, f"student_{student_id}.json")
    data = {
        "student_id": student_id,
        "struggles": {
            "lec1_tut1": [],
            "lec2_tut2": [],
            "lec3_tut3": []
        }
    }
    with open(student_file, "w") as f:
        json.dump(data, f, indent=4)

# --- Course materials ---
course_path = os.path.join(root, "course_materials")
os.makedirs(course_path, exist_ok=True)

for lec_tut in ["lec1", "tut1", "lec2", "tut2", "lec3", "tut3"]:
    with open(os.path.join(course_path, f"{lec_tut}.txt"), "w") as f:
        f.write(f"# Placeholder content for {lec_tut}\n")

print("MVP folder structure created successfully!")
