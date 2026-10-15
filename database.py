import os
import sqlite3
try:
    import psycopg2
    import psycopg2.extras
except:
    psycopg2 = None

DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = False
if DATABASE_URL and DATABASE_URL.startswith(("postgres://","postgresql://")):
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://","postgresql://",1)
    IS_POSTGRES = True

def get_connection():
    if IS_POSTGRES and psycopg2:
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn

def create_database():
    conn = get_connection()
    cur = conn.cursor()
    if IS_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id SERIAL PRIMARY KEY,
                company_name TEXT, name TEXT, department TEXT, experience TEXT,
                job_satisfaction TEXT, work_environment TEXT, communication TEXT,
                management_support TEXT, training TEXT, career_growth TEXT,
                resources TEXT, teamwork TEXT, recommend TEXT, suggestions TEXT
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT, name TEXT, department TEXT, experience TEXT,
                job_satisfaction TEXT, work_environment TEXT, communication TEXT,
                management_support TEXT, training TEXT, career_growth TEXT,
                resources TEXT, teamwork TEXT, recommend TEXT, suggestions TEXT
            )
        """)
    conn.commit()
    conn.close()

def insert_response(company_name, name, department, experience, job_satisfaction, work_environment, communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions):
    conn = get_connection()
    cur = conn.cursor()
    placeholders_pg = ",".join(["%s"]*14)
    placeholders_sqlite = ",".join(["?"]*14)
    if IS_POSTGRES:
        cur.execute(f"INSERT INTO responses (company_name, name, department, experience, job_satisfaction, work_environment, communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions) VALUES ({placeholders_pg})", (company_name, name, department, experience, job_satisfaction, work_environment, communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions))
    else:
        cur.execute(f"INSERT INTO responses (company_name, name, department, experience, job_satisfaction, work_environment, communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions) VALUES ({placeholders_sqlite})", (company_name, name, department, experience, job_satisfaction, work_environment, communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions))
    conn.commit()
    conn.close()

def get_all_responses():
    conn = get_connection()
    if IS_POSTGRES and psycopg2:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM responses ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return rows
    else:
        cur = conn.cursor()
        cur.execute("SELECT * FROM responses ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def delete_all_responses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM responses")
    conn.commit()
    conn.close()
