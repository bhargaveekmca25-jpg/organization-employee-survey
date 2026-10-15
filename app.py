
from flask import Flask, render_template, request

from database import (
    create_database,
    insert_response,
    get_all_responses,
    delete_all_responses
)

app = Flask(__name__)

# ---------------- DATABASE INITIALIZATION ----------------
create_database()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SURVEY ----------------
@app.route("/survey")
def survey():
    return render_template("survey.html")


# ---------------- SUBMIT SURVEY ----------------
@app.route("/submit", methods=["POST"])
def submit():
    company_name = " ".join(
        request.form.get("company_name", "").strip().split()
    )
    employee_id = " ".join(
        request.form.get("employee_id", "").strip().split()
    ).upper()

    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    experience = request.form.get("experience", "").strip()
    job_satisfaction = request.form.get("job_satisfaction", "").strip()
    work_environment = request.form.get("work_environment", "").strip()
    communication = request.form.get("communication", "").strip()
    management_support = request.form.get("management_support", "").strip()
    training = request.form.get("training", "").strip()
    career_growth = request.form.get("career_growth", "").strip()
    resources = request.form.get("resources", "").strip()
    teamwork = request.form.get("teamwork", "").strip()
    recommend = request.form.get("recommend", "").strip()
    suggestions = request.form.get("suggestions", "").strip()

    required_fields = [
        company_name,
        employee_id,
        name,
        department,
        experience,
        job_satisfaction,
        work_environment,
        communication,
        management_support,
        training,
        career_growth,
        resources,
        teamwork,
        recommend
    ]

    if not all(required_fields):
        return "Please fill in all required fields, including Employee ID.", 400

    # Order must match database.py insert_response()
    data = [
        company_name,
        employee_id,
        name,
        department,
        experience,
        job_satisfaction,
        work_environment,
        communication,
        management_support,
        training,
        career_growth,
        resources,
        teamwork,
        recommend,
        suggestions
    ]

    try:
        inserted = insert_response(data)

    except ValueError as error:
        return str(error), 400

    if not inserted:
        return render_template(
            "survey.html",
            error=(
                "Duplicate submission blocked! This Employee ID has "
                "already submitted a survey for this company."
            )
        ), 409

    return render_template(
        "success.html",
        company_name=company_name
    )


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    responses = get_all_responses()
    total = len(responses)

    return render_template(
        "admin.html",
        responses=responses,
        total=total
    )


# ---------------- RESET ALL RESPONSES ----------------
@app.route("/reset", methods=["POST"])
def reset():
    delete_all_responses()

    return """
    <script>
        alert("All responses have been deleted successfully.");
        window.location.href = "/admin";
    </script>
    """


# ---------------- ANALYSIS DASHBOARD ----------------
@app.route("/analysis")
def analysis():
    responses = get_all_responses()
    total = len(responses)

    # Company-wise response counts
    company_data = {}

    for row in responses:
        company = row["company_name"] or "Unknown Company"
        company_data[company] = company_data.get(company, 0) + 1

    # Survey question response counts
    questions = {
        "Job Satisfaction": "job_satisfaction",
        "Work Environment": "work_environment",
        "Communication": "communication",
        "Management Support": "management_support",
        "Training & Learning": "training",
        "Career Growth": "career_growth",
        "Resources & Tools": "resources",
        "Teamwork & Collaboration": "teamwork",
        "Recommendation": "recommend"
    }

    question_data = {}

    for question, column in questions.items():
        counts = {}

        for row in responses:
            answer = row[column]

            if answer:
                counts[answer] = counts.get(answer, 0) + 1

        question_data[question] = counts

    # Employee suggestions
    suggestions = []

    for row in responses:
        if row["suggestions"]:
            suggestions.append({
                "name": row["name"],
                "company": row["company_name"],
                "department": row["department"],
                "suggestion": row["suggestions"]
            })

    return render_template(
        "analysis.html",
        total=total,
        company_data=company_data,
        question_data=question_data,
        suggestions=suggestions
    )


# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    app.run(debug=False)
