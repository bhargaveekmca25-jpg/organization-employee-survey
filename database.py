import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    # Render pe Postgres hai to psycopg2 use hoga
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # Local pe SQLite
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn

def create_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if DATABASE_URL: # Postgres syntax
        cur.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id SERIAL PRIMARY KEY,
                company_name TEXT,
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
        ''')
    else: # SQLite syntax
        cur.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
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
        ''')
    conn.commit()
    cur.close()
    conn.close()

def insert_response(data):
    conn = get_db_connection()
    cur = conn.cursor()
    if DATABASE_URL:
        cur.execute('''
            INSERT INTO responses 
            (company_name, name, department, experience, job_satisfaction, work_environment, 
             communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', data)
    else:
        cur.execute('''
            INSERT INTO responses 
            (company_name, name, department, experience, job_satisfaction, work_environment, 
             communication, management_support, training, career_growth, resources, teamwork, recommend, suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
    conn.commit()
    cur.close()
    conn.close()

def get_all_responses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM responses')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def delete_all_responses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM responses')
    conn.commit()
    cur.close()
    conn.close()