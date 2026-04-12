# Study Assistant-as-a-Service (SAaaS) MVP

A cloud-based learning intelligence system that provides LLM-powered study assistance to students and cohort-level analytics to professors.

## Tech Stack

- Backend: Flask (Python)
- LLM: OpenAI API
- Storage: JSON files (per-student struggle tracking)
- Frontend: HTML/JS (prototype)

## Setup Instructions

### 1\. Clone the repository

```bash
git clone <your-repo-url>
cd SC4052-Project-main
```

### 2\. Install dependencies

```bash
pip install -r requirements.txt
```

### 3\. Set up OpenAI API key

Create a `.env` file in the root directory:

```text
OPENAI_API_KEY=your-api-key-here
```

### 4\. Run the application

```bash
python app.py
```
### 5\. Access the application

Open your browser and navigate to: `http://localhost:5000`

Usage
-----

### Student Flow

1.  Select a lecture or tutorial (e.g., lec1 or tut1)

2.  Type your question or learning struggle

3.  Receive an LLM-generated explanation grounded in course materials

4.  Click "View My Struggles" to see your past questions

### Professor Flow

1.  Select a lecture/tutorial pair for analysis

2.  Click "Analyze Cohort"

3.  View aggregated insights including:

    -   Common misconceptions

    -   Recurring difficulty areas

    -   Tutorial questions most associated with student struggles

Project Structure
-----------------

```text
SC4052-Project/
├─ .env                          # OpenAI API key (not committed)
├─ .gitignore                    # Ignores .env
├─ README.md                     # This file
├─ requirements.txt              # Flask, openai, python-dotenv
│
├─ app.py                        # All backend routes + logic
│
├─ frontend/
│   ├─ index.html                # Home page (student + professor buttons)
│   ├─ student.html              # Student query interface
│   ├─ professor.html            # Professor analytics interface
│   ├─ main.js                   # Frontend API calls
│   └─ styles.css                # Basic styling
│
├─ students/
│   ├─ student_12345.json        # Student 12345 struggle records
│   └─ student_67890.json        # Student 67890 struggle records
│
└─ course_materials/
    ├─ lec1.txt                  # Lecture 1 content
    ├─ tut1.txt                  # Tutorial 1 questions
    ├─ lec2.txt                  # Lecture 2 content
    ├─ tut2.txt                  # Tutorial 2 questions
    ├─ lec3.txt                  # Lecture 3 content
    └─ tut3.txt                  # Tutorial 3 questions
```

Notes
-----

-   No authentication required for MVP demo

-   Each student has a dedicated JSON file created automatically

-   Course materials must follow the naming convention: `lecX.txt` + `tutX.txt` (X = 1, 2, 3)
