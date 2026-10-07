from flask import Flask, render_template, request
from database import (
    create_database,
    insert_response,
    get_all_responses,
    delete_all_responses
)

app = Flask(__name__)


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

    company_name = request.form.get("company_name", "").strip()
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "")
    experience = request.form.get("experience", "")
    job_satisfaction = request.form.get("job_satisfaction", "")
    work_environment = request.form.get("work_environment", "")
    communication = request.form.get("communication", "")
    management_support = request.form.get("management_support", "")
    training = request.form.get("training", "")
    career_growth = request.form.get("career_growth", "")
    resources = request.form.get("resources", "")
    teamwork = request.form.get("teamwork", "")
    recommend = request.form.get("recommend", "")
    suggestions = request.form.get("suggestions", "").strip()


    # ---------------- REQUIRED FIELDS ----------------

    required_fields = [
        company_name,
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

        return "Please fill all required fields."


    # ---------------- SAVE RESPONSE ----------------

    insert_response(
        company_name,
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
    )


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


    # ---------------- COMPANY DATA ----------------

    company_data = {}

    for row in responses:

        company = row["company_name"]

        if company not in company_data:

            company_data[company] = 0

        company_data[company] += 1


    # ---------------- QUESTION DATA ----------------

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


    # ---------------- SUGGESTIONS ----------------

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

    create_database()

    app.run(debug=True)