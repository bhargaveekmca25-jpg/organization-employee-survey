from flask import Flask, render_template, request, redirect
import sqlite3
import os
from collections import Counter, defaultdict

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  company_name TEXT, name TEXT, department TEXT, experience TEXT,
                  job_satisfaction TEXT, work_environment TEXT, communication TEXT,
                  management_support TEXT, training TEXT, career_growth TEXT,
                  resources TEXT, teamwork TEXT, recommend TEXT, suggestions TEXT)''')
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def survey():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (company_name,name,department,experience,job_satisfaction,work_environment,communication,management_support,training,career_growth,resources,teamwork,recommend,suggestions) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
              (request.form.get('company_name'), request.form.get('name'), request.form.get('department'), request.form.get('experience'),
               request.form.get('job_satisfaction'), request.form.get('work_environment'), request.form.get('communication'),
               request.form.get('management_support'), request.form.get('training'), request.form.get('career_growth'),
               request.form.get('resources'), request.form.get('teamwork'), request.form.get('recommend'), request.form.get('suggestions')))
    conn.commit()
    conn.close()
    return "<h2 style='text-align:center;margin-top:50px;font-family:sans-serif'>✅ Submitted! <br><br><a href='/'>Home</a> | <a href='/analysis'>View Analysis</a></h2>"

def get_analysis_data():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('SELECT * FROM feedback')
    rows = c.fetchall()
    conn.close()

    total = len(rows)
    company_data = Counter([r[1] for r in rows if r[1]])

    # question_data mapping to your template keys
    question_map = {
        "Job Satisfaction": 5,
        "Work Environment": 6,
        "Communication": 7,
        "Management Support": 8,
        "Training": 9,
        "Career Growth": 10,
        "Resources": 11,
        "Teamwork": 12,
        "Recommend Organization": 13
    }
    question_data = {}
    for q_name, idx in question_map.items():
        vals = [r[idx] for r in rows if r[idx]]
        question_data[q_name] = dict(Counter(vals))

    suggestions = []
    for r in rows:
        if r[14] and r[14].strip():
            suggestions.append({"name": r[2], "department": r[3], "company": r[1], "suggestion": r[14]})

    return total, company_data, question_data, suggestions

@app.route('/analysis')
def analysis():
    total, company_data, question_data, suggestions = get_analysis_data()
    return render_template('analysis.html', total=total, company_data=company_data, question_data=question_data, suggestions=suggestions)

@app.route('/admin')
def admin():
    total, company_data, question_data, suggestions = get_analysis_data()
    return render_template('analysis.html', total=total, company_data=company_data, question_data=question_data, suggestions=suggestions)

@app.route('/dashboard')
def dashboard():
    return redirect('/analysis')

if __name__ == '__main__':
    app.run(debug=True)