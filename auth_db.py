import psycopg2
import hashlib

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="smart_timetable",
        user="postgres",
        password="YOUR_PASSWORD",
        port="5432"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, hash_password(password))
    )

    user = cur.fetchone()
    conn.close()

    return user