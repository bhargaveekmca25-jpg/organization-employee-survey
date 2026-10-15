
import os
import sqlite3

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None


DATABASE_URL = os.environ.get("DATABASE_URL")
UNIQUE_INDEX = "uq_responses_company_employee"

IS_POSTGRES = bool(
    DATABASE_URL
    and DATABASE_URL.startswith(("postgres://", "postgresql://"))
)

if IS_POSTGRES and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_db_connection():
    if IS_POSTGRES:
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for PostgreSQL.")
        return psycopg2.connect(DATABASE_URL)

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if IS_POSTGRES:
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
            "Expected 15 survey fields, with employee_id after company_name."
        )

    data = list(data)
    data[0] = " ".join(str(data[0] or "").split())
    data[1] = " ".join(str(data[1] or "").split()).upper()

    if not data[0] or not data[1]:
        raise ValueError("Company name and Employee ID are required.")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        placeholders = (
            "%s" if IS_POSTGRES else "?"
        )
        placeholders = ", ".join([placeholders] * 15)

        cur.execute(f"""
            INSERT INTO responses (
                company_name, employee_id, name, department,
                experience, job_satisfaction, work_environment,
                communication, management_support, training,
                career_growth, resources, teamwork, recommend,
                suggestions
            )
            VALUES ({placeholders})
        """, tuple(data))

        conn.commit()
        return True

    except Exception as error:
        conn.rollback()

        if IS_POSTGRES:
            constraint = getattr(
                getattr(error, "diag", None),
                "constraint_name",
                None
            )
            if constraint == UNIQUE_INDEX:
                return False
        else:
            message = str(error).lower()
            if (
                "unique constraint failed" in message
                and UNIQUE_INDEX in message
            ):