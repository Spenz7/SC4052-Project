from flask import Flask, request, jsonify, render_template
import json, os

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

if __name__ == '__main__':
    app.run(debug=True)
