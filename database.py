
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use PostgreSQL on Render and SQLite locally.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

IS_POSTGRES = DATABASE_URL.startswith(
    ("postgres://", "postgresql://")
)

DATABASE = os.path.join(BASE_DIR, "database.db")

COLUMNS = [
    "company_name",
    "name",
    "department",
    "experience",
    "job_satisfaction",
    "work_environment",
    "communication",
    "management_support",
    "training",
    "career_growth",
    "resources",
    "teamwork",
    "recommend",
    "suggestions",
]


def get_db_connection():
    if IS_POSTGRES:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL driver missing. Add psycopg2-binary "
                "to requirements.txt."
            ) from exc

        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
        return conn

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()

    try:
        if IS_POSTGRES:
            id_column = "BIGSERIAL PRIMARY KEY"
        else:
            id_column = "INTEGER PRIMARY KEY AUTOINCREMENT"

        conn.cursor().execute(f"""
            CREATE TABLE IF NOT EXISTS responses (
                id {id_column},
                company_name TEXT NOT NULL DEFAULT 'Organization',
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                experience TEXT NOT NULL,
                job_satisfaction TEXT NOT NULL,
                work_environment TEXT NOT NULL,
                communication TEXT NOT NULL,
                management_support TEXT NOT NULL,
                training TEXT NOT NULL,
                career_growth TEXT NOT NULL,
                resources TEXT NOT NULL,
                teamwork TEXT NOT NULL,
                recommend TEXT NOT NULL,
                suggestions TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


def insert_response(data, *args, **kwargs):
    """
    Accept a dictionary from app.py.
    Also support the older positional-argument calling style.
    """
    if isinstance(data, dict):
        response = data.copy()
    else:
        values = (data,) + args
        if len(values) != len(COLUMNS):
            raise ValueError(
                f"Expected {len(COLUMNS)} response values; "
                f"received {len(values)}."
            )
        response = dict(zip(COLUMNS, values))

    response.setdefault("company_name", "Organization")
    response.setdefault("suggestions", "")

    for column in COLUMNS:
        response.setdefault(column, "")

    # Normalize values and guard against missing required answers.
    for column in COLUMNS:
        value = response.get(column)
        response[column] = (
            str(value).strip() if value is not None else ""
        )

    required = COLUMNS[:-1]
    missing = [
        column for column in required
        if not response[column]
    ]
    if missing:
        raise ValueError(
            "Missing required survey fields: " + ", ".join(missing)
        )

    conn = get_db_connection()

    try:
        placeholders = (
            ", ".join(["%s"] * len(COLUMNS))
            if IS_POSTGRES
            else ", ".join(["?"] * len(COLUMNS))
        )

        columns_sql = ", ".join(COLUMNS)

        values = tuple(response[column] for column in COLUMNS)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO responses ({columns_sql})
            VALUES ({placeholders})
            """,
            values,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_responses():
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM responses ORDER BY id DESC"
        )
        return cursor.fetchall()
    finally:
        conn.close()


def delete_all_responses():
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM responses")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
