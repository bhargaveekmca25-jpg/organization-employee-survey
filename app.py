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

app = Flask(__name__)

# Secret key for session security
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-key-change-before-deployment"
)

# Admin credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Organization name
ORGANIZATION_NAME = "TCS"


# Create database during application startup
create_database()


# ADMIN AUTHENTICATION
def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# HOME PAGE
@app.route("/")
def home():

    return render_template("index.html")


# EMPLOYEE SURVEY
@app.route("/survey")
def survey():

    return render_template(
        "survey.html",
        organization_name=ORGANIZATION_NAME
    )


# SUBMIT SURVEY
@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    experience = request.form.get("experience", "").strip()

    job_satisfaction = request.form.get(
        "job_satisfaction", ""
    )

    work_environment = request.form.get(
        "work_environment", ""
    )

    communication = request.form.get(
        "communication", ""
    )

    management_support = request.form.get(
        "management_support", ""
    )

    training = request.form.get("training", "")
    career_growth = request.form.get("career_growth", "")
    resources = request.form.get("resources", "")
    teamwork = request.form.get("teamwork", "")
    recommend = request.form.get("recommend", "")

    suggestions = request.form.get(
        "suggestions", ""
    ).strip()

    # Validate required fields
    required_fields = [
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

        return (
            "Please complete all required fields.",
            400
        )

    # Save response
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

    return render_template(
        "success.html",
        organization_name=ORGANIZATION_NAME
    )


# ADMIN LOGIN
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):

        return redirect(url_for("admin"))

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not ADMIN_USERNAME or not ADMIN_PASSWORD:

            return (
                "Admin credentials are not configured.",
                500
            )

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session.clear()
            session["admin_logged_in"] = True

            return redirect(url_for("admin"))

        flash("Invalid username or password.")

    return render_template("login.html")


# ADMIN DASHBOARD
@app.route("/admin")
@admin_required
def admin():

    responses = get_all_responses()

    return render_template(
        "admin.html",
        responses=responses,
        total=len(responses)
    )


# ANALYSIS DASHBOARD
@app.route("/analysis")
@admin_required
def analysis():

    responses = get_all_responses()

    total = len(responses)

    # Positive satisfaction responses
    positive = sum(
        1 for r in responses
        if r["job_satisfaction"] in [
            "Very Satisfied",
            "Satisfied"
        ]
    )

    negative = sum(
        1 for r in responses
        if r["job_satisfaction"] in [
            "Dissatisfied",
            "Very Dissatisfied"
        ]
    )

    neutral = sum(
        1 for r in responses
        if r["job_satisfaction"] == "Neutral"
    )

    satisfaction_percentage = (
        round((positive / total) * 100, 1)
        if total else 0
    )

    positive_percentage = (
        round((positive / total) * 100, 1)
        if total else 0
    )

    negative_percentage = (
        round((negative / total) * 100, 1)
        if total else 0
    )

    neutral_percentage = (
        round((neutral / total) * 100, 1)
        if total else 0
    )

    # Department-wise response count
    departments = {}

    for response in responses:

        department = response["department"]

        departments[department] = (
            departments.get(department, 0) + 1
        )

    return render_template(
        "analysis.html",
        total=total,
        positive=positive,
        negative=negative,
        neutral=neutral,
        satisfaction_percentage=satisfaction_percentage,
        positive_percentage=positive_percentage,
        negative_percentage=negative_percentage,
        neutral_percentage=neutral_percentage,
        departments=departments,
        responses=responses
    )


# DELETE ALL RESPONSES
# Admin only; POST request required
@app.route("/reset", methods=["POST"])
@admin_required
def reset():

    delete_all_responses()

    flash("All survey responses have been deleted.")

    return redirect(url_for("admin"))


# ADMIN LOGOUT
@app.route("/admin-logout", methods=["POST"])
@admin_required
def admin_logout():

    session.clear()

    return redirect(url_for("home"))


# RUN APPLICATION
if __name__ == "__main__":

    app.run(debug=True)