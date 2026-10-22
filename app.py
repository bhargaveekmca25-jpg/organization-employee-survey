import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from database import (
    create_database,
    insert_response,
    get_all_responses,
    delete_all_responses
)


app = Flask(__name__)

# Application configuration
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "employee-survey-secret-key"
)

ORGANIZATION_NAME = os.environ.get(
    "ORGANIZATION_NAME",
    "Organization"
)

# Admin credentials from Render environment variables
ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME", ""
).strip()

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD", ""
)


# Initialize database
create_database()


# ---------------- HOME PAGE ----------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- SURVEY FORM ----------------

@app.route("/survey")
def survey():
    return render_template("survey.html")


# ---------------- SUBMIT SURVEY ----------------

@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = {
            "company_name": request.form.get(
                "company_name", ORGANIZATION_NAME
            ).strip(),

            "name": request.form.get("name", "").strip(),

            "department": request.form.get(
                "department", ""
            ).strip(),

            "experience": request.form.get(
                "experience", ""
            ),

            "job_satisfaction": request.form.get(
                "job_satisfaction", ""
            ),

            "work_environment": request.form.get(
                "work_environment", ""
            ),

            "communication": request.form.get(
                "communication", ""
            ),

            "management_support": request.form.get(
                "management_support", ""
            ),

            "training": request.form.get(
                "training", ""
            ),

            "career_growth": request.form.get(
                "career_growth", ""
            ),

            "resources": request.form.get(
                "resources", ""
            ),

            "teamwork": request.form.get(
                "teamwork", ""
            ),

            "recommend": request.form.get(
                "recommend", ""
            ),

            "suggestions": request.form.get(
                "suggestions", ""
            )
        }

        insert_response(data)

        flash("Survey submitted successfully!")
        return redirect(url_for("survey"))

    except Exception:
        app.logger.exception("Survey submission failed")
        flash("Unable to submit the survey. Please try again.")
        return redirect(url_for("survey"))


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        # Check environment configuration
        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            app.logger.error(
                "Admin credentials are missing from environment variables."
            )

            flash("Admin login is not configured.")
            return render_template("admin_login.html")

        # Compare credentials without logging passwords
        username_match = username == ADMIN_USERNAME
        password_match = password == ADMIN_PASSWORD

        app.logger.info(
            "Admin login check: username_match=%s, password_match=%s",
            username_match,
            password_match
        )

        if username_match and password_match:
            session["admin_logged_in"] = True

            flash("Login successful!")

            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.")

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        flash("Please log in first.")
        return redirect(url_for("admin_login"))

    try:
        responses = get_all_responses()

        return render_template(
            "admin_dashboard.html",
            responses=responses
        )

    except Exception:
        app.logger.exception("Admin dashboard loading failed")
        flash("Unable to load survey responses.")
        return redirect(url_for("admin_login"))


# ---------------- ANALYSIS PAGE ----------------

@app.route("/analysis")
def analysis():

    if not session.get("admin_logged_in"):
        flash("Please log in to view survey analysis.")
        return redirect(url_for("admin_login"))

    try:
        responses = get_all_responses()

        return render_template(
            "analysis.html",
            responses=responses
        )

    except Exception:
        app.logger.exception("Analysis page loading failed")
        flash("Unable to load survey analysis.")
        return redirect(url_for("admin_dashboard"))


# ---------------- DELETE RESPONSES ----------------

@app.route("/delete-responses", methods=["POST"])
def delete_responses():

    if not session.get("admin_logged_in"):
        flash("Please log in first.")
        return redirect(url_for("admin_login"))

    try:
        delete_all_responses()
        flash("All survey responses have been deleted.")

    except Exception:
        app.logger.exception("Deleting responses failed")
        flash("Unable to delete survey responses.")

    return redirect(url_for("admin_dashboard"))


# ---------------- ADMIN LOGOUT ----------------

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    flash("You have been logged out.")

    return redirect(url_for("admin_login"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)