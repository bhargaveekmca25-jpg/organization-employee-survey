
import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL")
UNIQUE_INDEX = "uq_responses_company_employee"


def get_db_connection():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn


def create_database():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if DATABASE_URL:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    company_name TEXT,
                    employee_id TEXT NOT NULL DEFAULT '',
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
            """)

            cur.execute("""
                ALTER TABLE responses
                ADD COLUMN IF NOT EXISTS employee_id
                TEXT NOT NULL DEFAULT ''
            """)

        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    employee_id TEXT NOT NULL DEFAULT '',
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
            """)

            cur.execute("PRAGMA table_info(responses)")
            columns = [row["name"] for row in cur.fetchall()]

            if "employee_id" not in columns:
                cur.execute("""
                    ALTER TABLE responses
                    ADD COLUMN employee_id TEXT NOT NULL DEFAULT ''
                """)

        # Same company + same Employee ID = only one response.
        # Company names are compared without case or outer spaces.
        # Employee IDs are compared without case or outer spaces.
        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS {UNIQUE_INDEX}
            ON responses (
                LOWER(TRIM(company_name)),
                UPPER(TRIM(employee_id))
            )
            WHERE employee_id IS NOT NULL
              AND TRIM(employee_id) <> ''
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def insert_response(data):
    # Expected order:
    # company_name, employee_id, name, department, experience,
    # job_satisfaction, work_environment, communication,
    # management_support, training, career_growth, resources,
    # teamwork, recommend, suggestions

    if len(data) != 15:
        raise ValueError(
            "Survey data must contain Employee ID after company name. "
            "The app.py submit route must also be updated."
        )

    data = list(data)

    company_name = " ".join(str(data[0] or "").split())
    employee_id = " ".join(str(data[1] or "").split()).upper()

    if not company_name or not employee_id:
        raise ValueError("Company Name and Employee ID are required.")

    data[0] = company_name
    data[1] = employee_id

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if DATABASE_URL:
            cur.execute("""
                INSERT INTO responses (
                    company_name, employee_id, name, department,
                    experience, job_satisfaction, work_environment,
                    communication, management_support, training,
                    career_growth, resources, teamwork, recommend,
                    suggestions
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, tuple(data))

        else:
            cur.execute("""
                INSERT INTO responses (
                    company_name, employee_id, name, department,
                    experience, job_satisfaction, work_environment,
                    communication, management_support, training,
                    career_growth, resources, teamwork, recommend,
                    suggestions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(data))

        conn.commit()
        return True

    except Exception as error:
        conn.rollback()

        if DATABASE_URL:
            # Only treat a violation of our duplicate-prevention
            # index as a duplicate submission.
            constraint_name = getattr(
                getattr(error, "diag", None),
                "constraint_name",
                None
            )

            if constraint_name == UNIQUE_INDEX:
                return False

        else:
            message = str(error).lower()

            if (
                "unique constraint failed" in message
                and UNIQUE_INDEX in message
            ):
                return False

        raise

    finally:
        cur.close()
        conn.close()


def get_all_responses():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM responses")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def delete_all_responses():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM responses")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
