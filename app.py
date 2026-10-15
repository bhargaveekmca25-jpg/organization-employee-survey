from flask import Flask, render_template, request, redirect, url_for
from database import create_database, insert_response, get_all_responses
import os

app = Flask(__name__)

# Table banane ke liye
create_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit():
    company_name = request.form.get('company_name')
    name = request.form.get('name')
    department = request.form.get('department')
    experience = request.form.get('experience')
    job_satisfaction = request.form.get('job_satisfaction')
    work_environment = request.form.get('work_environment')
    communication = request.form.get('communication')
    management_support = request.form.get('management_support')
    training = request.form.get('training')
    career_growth = request.form.get('career_growth')
    resources = request.form.get('resources')
    teamwork = request.form.get('teamwork')
    recommend = request.form.get('recommend')
    suggestions = request.form.get('suggestions')

    # Ab 14 alag value bhej rahe hai, dict nahi - yahi tera error tha
    insert_response(
        company_name, name, department, experience,
        job_satisfaction, work_environment, communication,
        management_support, training, career_growth,
        resources, teamwork, recommend, suggestions
    )
    return render_template('thankyou.html')

@app.route('/admin')
def admin():
    responses = get_all_responses()
    return render_template('admin.html', responses=responses)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)