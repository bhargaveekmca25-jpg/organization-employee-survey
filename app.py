from flask import Flask, render_template, request, redirect
import sqlite3
from collections import Counter

app = Flask(__name__)

# Admin Password
ADMIN_PASSWORD = "admin123"

def init_db():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            name TEXT,
            department TEXT,
            experience TEXT,
            job_satisfaction TEXT,
            work_environment TEXT,
            communication TEXT,
            management_support TEXT,
            training TEXT,
            career_growth TEXT,
            resources TEXT,
            teamwork TEXT,
            recommend TEXT,
            suggestions TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_all_data():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute("SELECT * FROM feedback ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    total = len(rows)

    company_data = dict(
        Counter([r[1] for r in rows if r[1]])
    )

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

    suggestions_anon = []
    suggestions_full = []

    for r in rows:
        if r[14] and str(r[14]).strip():
            suggestions_anon.append({
                "suggestion": r[14]
            })
            suggestions_full.append({
                "company": r[1],
                "name": r[2],
                "department": r[3],
                "suggestion": r[14]
            })

    return rows, total, company_data, question_data, suggestions_anon, suggestions_full

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()

    company_name = request.form.get('company_name')

    c.execute('''
        INSERT INTO feedback (
            company_name, name, department, experience,
            job_satisfaction, work_environment, communication,
            management_support, training, career_growth,
            resources, teamwork, recommend, suggestions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        company_name,
        request.form.get('name'),
        request.form.get('department'),
        request.form.get('experience'),
        request.form.get('job_satisfaction'),
        request.form.get('work_environment'),
        request.form.get('communication'),
        request.form.get('management_support'),
        request.form.get('training'),
        request.form.get('career_growth'),
        request.form.get('resources'),
        request.form.get('teamwork'),
        request.form.get('recommend'),
        request.form.get('suggestions')
    ))

    conn.commit()
    conn.close()

    return render_template('success.html', company=company_name)

@app.route('/analysis')
def analysis():
    rows, total, company_data, question_data, suggestions_anon, suggestions_full = get_all_data()
    return render_template(
        'analysis.html',
        total=total,
        company_data=company_data,
        question_data=question_data,
        suggestions=suggestions_anon
    )

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        entered_password = request.form.get('password', '').strip()

        if entered_password == ADMIN_PASSWORD:
            rows, total, company_data, question_data, suggestions_anon, suggestions_full = get_all_data()
            return render_template(
                'admin.html',
                rows=rows,
                total=total,
                suggestions=suggestions_full
            )
        else:
            return render_template(
                'admin_login.html',
                error=f"Wrong Password! You typed: {entered_password}"
            )

    return render_template('admin_login.html')

@app.route('/reset')
def reset():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute("DELETE FROM feedback")
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)