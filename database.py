import sqlite3
import os

# Database file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE DATABASE ----------------
def create_database():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
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
    conn.close()


# ---------------- INSERT RESPONSE ----------------
def insert_response(
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
):

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO responses (
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
    ))

    conn.commit()
    conn.close()


# ---------------- GET ALL RESPONSES ----------------
def get_all_responses():

    conn = get_db_connection()

    responses = conn.execute("""
        SELECT * FROM responses
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return responses


# ---------------- DELETE ALL RESPONSES ----------------
def delete_all_responses():

    conn = get_db_connection()

    conn.execute("DELETE FROM responses")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='responses'")

    conn.commit()
    conn.close()