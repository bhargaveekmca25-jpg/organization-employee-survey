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

# Secret key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "employee-survey-secret-key"
)

# Organization and admin settings
ORGANIZATION_NAME = os.environ.get(
    "ORGANIZATION_NAME",
    "Organization"
)

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME", ""
).strip()

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD", ""
)


# Create database when the application starts
create_database()


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Survey form page
@app.route("/survey")
def survey():
    return render_template("survey.html")


# Submit survey response
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

        # Save response in the database
        insert_response(data)

        flash("Survey submitted successfully!")
        return redirect(url_for("survey"))

    except Exception:
        app.logger.exception("Error submitting survey")
        flash("Unable to submit the survey. Please try again.")
        return redirect(url_for("survey"))


# Admin login page
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        # Check whether environment variables are configured
        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            app.logger.error(
                "Admin credentials are missing from environment variables."
            )

            flash(
                "Admin login is not configured. "
                "Please contact the administrator."
            )

            return render_template("admin_login.html")

        # Compare submitted credentials
        username_match = username == ADMIN_USERNAME
        password_match = password == ADMIN_PASSWORD

        # Log comparison results without exposing credentials
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


# Admin dashboard
@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        flash("Please log in to access the admin dashboard.")
        return redirect(url_for("admin_login"))

    try:
        responses = get_all_responses()

        return render_template(
            "admin_dashboard.html",
            responses=responses
        )

    except Exception:
        app.logger.exception("Error loading admin dashboard")
        flash("Unable to load survey responses.")
        return redirect(url_for("admin_login"))


# Delete all survey responses
@app.route("/delete-responses", methods=["POST"])
def delete_responses():

    if not session.get("admin_logged_in"):
        flash("Please log in first.")
        return redirect(url_for("admin_login"))

    try:
        delete_all_responses()

        flash("All survey responses have been deleted.")

    except Exception:
        app.logger.exception("Error deleting survey responses")
        flash("Unable to delete survey responses.")

    return redirect(url_for("admin_dashboard"))


# Admin logout
@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    flash("You have been logged out.")

    return redirect(url_for("admin_login"))


# Run application locally
if __name__ == "__main__":
    app.run(debug=True)