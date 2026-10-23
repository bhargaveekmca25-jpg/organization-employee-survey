import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ascent-solutions-final-secret-2024')
ADMIN_HASH = os.getenv('ADMIN_PASSWORD_HASH')

# Database helper
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('survey.db')
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            employee_name TEXT,
            department TEXT,
            experience TEXT,
            q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT,
            q6 TEXT, q7 TEXT, q8 TEXT, q9 TEXT,
            suggestion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        db.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    db = get_db()
    db.execute("""INSERT INTO responses 
    (company, employee_name, department, experience, q1, q2, q3, q4, q5, q6, q7, q8, q9, suggestion)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
    (
        request.form.get('company'),
        request.form.get('employee_name'),
        request.form.get('department'),
        request.form.get('experience'),
        request.form.get('q1'),
        request.form.get('q2'),
        request.form.get('q3'),
        request.form.get('q4'),
        request.form.get('q5'),
        request.form.get('q6'),
        request.form.get('q7'),
        request.form.get('q8'),
        request.form.get('q9'),
        request.form.get('suggestion')
    ))
    db.commit()
    return render_template('success.html')

@app.route('/admin/login', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password','')
        ok = False
        if ADMIN_HASH:
            try:
                ok = check_password_hash(ADMIN_HASH, pwd)
            except:
                ok = False
        if not ok and pwd == 'admin123':
            ok = True
        if ok:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid password. Try admin123'
    return render_template('admin_login.html', error=error)

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    rows = db.execute('SELECT * FROM responses ORDER BY id DESC').fetchall()
    return render_template('admin.html', responses=rows, total=len(rows))

@app.route('/analysis')
def analysis_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    db = get_db()
    rows = db.execute('SELECT * FROM responses ORDER BY id DESC').fetchall()
    total = len(rows)
    
    # Organization wise
    orgs = {}
    
    # Question wise stats
    q_labels = {
        'q1':'Job Satisfaction',
        'q2':'Work Environment',
        'q3':'Communication',
        'q4':'Management Support',
        'q5':'Training',
        'q6':'Career Growth',
        'q7':'Resources',
        'q8':'Teamwork',
        'q9':'Recommendation'
    }
    
    q_stats = {}
    for q in q_labels:
        q_stats[q] = {}
    
    # Employee wise + dept wise
    dept_stats = {}
    
    for r in rows:
        comp = r['company'] or 'Ascent Solutions'
        orgs[comp] = orgs.get(comp, 0) + 1
        
        dept = r['department'] or 'Other'
        dept_stats[dept] = dept_stats.get(dept, 0) + 1
        
        for q in q_labels:
            val = r[q]
            if val:
                q_stats[q][val] = q_stats[q].get(val, 0) + 1
    
    return render_template(
        'analysis.html',
        responses=rows,
        total=total,
        org_count=len(orgs),
        orgs=orgs,
        q_stats=q_stats,
        q_labels=q_labels,
        dept_stats=dept_stats
    )

@app.route('/reset-all')
def reset_all():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    db.execute('DELETE FROM responses')
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize DB
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)