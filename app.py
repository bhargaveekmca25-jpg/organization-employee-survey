import os
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database import (
    create_database,
    insert_response,
    get_all_responses,
    delete_all_responses
)


# --------------------------------------------------
# Flask Application Configuration
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "employee-survey-local-secret-key"
)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
print("Admin username configured:", bool(ADMIN_USERNAME))
print("Admin password configured:", bool(ADMIN_PASSWORD))

ORGANIZATION_NAME = "Ascent Solutions"


# Create database and required table
create_database()


# --------------------------------------------------
# Admin Authentication Decorator
# --------------------------------------------------

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Employee Survey Page
# --------------------------------------------------

@app.route("/survey")
def survey():
    return render_template(
        "survey.html",
        organization_name=ORGANIZATION_NAME
    )


# --------------------------------------------------
# Submit Employee Survey
# --------------------------------------------------

@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    experience = request.form.get("experience", "").strip()

    job_satisfaction = request.form.get(
        "job_satisfaction", ""
    ).strip()

    work_environment = request.form.get(
        "work_environment", ""
    ).strip()

    communication = request.form.get(
        "communication", ""
    ).strip()

    management_support = request.form.get(
        "management_support", ""
    ).strip()

    training = request.form.get(
        "training", ""
    ).strip()

    career_growth = request.form.get(
        "career_growth", ""
    ).strip()

    resources = request.form.get(
        "resources", ""
    ).strip()

    teamwork = request.form.get(
        "teamwork", ""
    ).strip()

    recommend = request.form.get(
        "recommend", ""
    ).strip()

    suggestions = request.form.get(
        "suggestions", ""
    ).strip()

    # Validate required fields
    required_fields = {
        "Employee Name": name,
        "Department": department,
        "Experience": experience,
        "Job Satisfaction": job_satisfaction,
        "Work Environment": work_environment,
        "Communication": communication,
        "Management Support": management_support,
        "Training": training,
        "Career Growth": career_growth,
        "Resources": resources,
        "Teamwork": teamwork,
        "Recommendation": recommend
    }

    missing_fields = [
        field
        for field, value in required_fields.items()
        if not value
    ]

    if missing_fields:
        flash(
            "Please complete all required survey questions.",
            "error"
        )

        return redirect(url_for("survey"))

    # Save response in database
    try:
        insert_response(
            ORGANIZATION_NAME,
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

    except Exception:
        app.logger.exception("Failed to save survey response")

        return (
            "Unable to save your response. "
            "Please check the application logs.",
            500
        )

    return render_template(
        "success.html",
        organization_name=ORGANIZATION_NAME
    )


# --------------------------------------------------
# Admin Login Page
# --------------------------------------------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            return (
                "Admin credentials are not configured. "
                "Set ADMIN_USERNAME and ADMIN_PASSWORD "
                "in your environment variables.",
                500
            )

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):
            session.clear()
            session["admin_logged_in"] = True

            return redirect(url_for("admin"))

        flash("Invalid username or password.", "error")

    return render_template("admin_login.html")


# --------------------------------------------------
# Admin Dashboard
# --------------------------------------------------

@app.route("/admin")
@admin_required
def admin():

    responses = get_all_responses()

    total = len(responses)

    return render_template(
        "admin.html",
        responses=responses,
        total=total
    )


# --------------------------------------------------
# Analysis Dashboard
# --------------------------------------------------

@app.route("/analysis")
@admin_required
def analysis():

    responses = get_all_responses()

    total = len(responses)

    positive = 0
    negative = 0
    neutral = 0

    departments = {}

    # Analyse employee responses
    for response in responses:

        satisfaction = response["job_satisfaction"]

        if satisfaction in [
            "Very Satisfied",
            "Satisfied"
        ]:
            positive += 1

        elif satisfaction in [
            "Very Dissatisfied",
            "Dissatisfied"
        ]:
            negative += 1

        else:
            neutral += 1

        # Department-wise response count
        department = (
            response["department"] or "Not Specified"
        )

        departments[department] = (
            departments.get(department, 0) + 1
        )

    # Calculate percentages
    if total > 0:

        positive_percentage = round(
            positive / total * 100, 1
        )

        negative_percentage = round(
            negative / total * 100, 1
        )

        neutral_percentage = round(
            neutral / total * 100, 1
        )

    else:

        positive_percentage = 0
        negative_percentage = 0
        neutral_percentage = 0

    satisfaction_percentage = positive_percentage

    return render_template(
        "analysis.html",
        responses=responses,
        total=total,
        positive=positive,
        negative=negative,
        neutral=neutral,
        positive_percentage=positive_percentage,
        negative_percentage=negative_percentage,
        neutral_percentage=neutral_percentage,
        satisfaction_percentage=satisfaction_percentage,
        departments=departments
    )


# --------------------------------------------------
# Delete All Survey Responses
# --------------------------------------------------

@app.route("/reset", methods=["POST"])
@admin_required
def reset():

    try:
        delete_all_responses()

        flash(
            "All survey responses have been deleted.",
            "success"
        )

    except Exception:
        app.logger.exception("Failed to delete responses")

        flash(
            "Unable to delete survey responses.",
            "error"
        )

    return redirect(url_for("admin"))


# --------------------------------------------------
# Admin Logout
# --------------------------------------------------

@app.route("/admin-logout", methods=["POST"])
@admin_required
def admin_logout():

    session.clear()

    return redirect(url_for("home"))


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)