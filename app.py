from flask import Flask, render_template, request
from database import create_database, insert_response, get_all_responses
import os

app = Flask(__name__)
create_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    insert_response(
        request.form.get('company_name'),
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
    )
    return render_template('thankyou.html')

@app.route('/admin')
def admin():
    responses = get_all_responses()
    return render_template('admin.html', responses=responses)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)