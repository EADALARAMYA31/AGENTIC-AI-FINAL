import psycopg2
import hashlib
from datetime import date

# ================= DATABASE CONNECTION =================
import os
#import psycopg2

import streamlit as st

def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        sslmode="require"
    )
#def get_connection():
    #try:
     #   return psycopg2.connect(
      #      host="localhost",
       #     database="smart_timetable",
        #    user="postgres",
         #   password="MYSQLramya31",   # Your PostgreSQL password
          #  port="5432"
        #)
    #except Exception as e:
     #   print("Database Connection Error:", e)
      #  raise


# ================= PASSWORD HASHING =================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================= USER FUNCTIONS =================

def register_user(username, password):

    conn = get_connection()
    cur = conn.cursor()

    try:
        hashed = hash_password(password)

        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """, (username, hashed))

        conn.commit()

        return True

    except psycopg2.Error:
        conn.rollback()
        return False

    finally:
        cur.close()
        conn.close()


def login_user(username, password):

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    cur.execute("""
        SELECT id, username
        FROM users
        WHERE username=%s
        AND password=%s
    """, (username, hashed))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user   # ✅ returns tuple or None


# ================= ASSIGNMENT FUNCTIONS =================

def insert_assignment(user_id, name, subject, deadline, priority):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO assignments
        (user_id, name, subject, deadline, priority)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id,
        name,
        subject,
        deadline,
        priority
    ))

    conn.commit()

    cur.close()
    conn.close()


def get_assignments(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, subject, deadline, priority
        FROM assignments
        WHERE user_id=%s
        ORDER BY deadline ASC
    """, (user_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def delete_assignment(assignment_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM assignments
        WHERE id=%s AND user_id=%s
    """, (
        assignment_id,
        user_id
    ))

    conn.commit()

    cur.close()
    conn.close()


# ================= EVENT FUNCTIONS =================

def insert_event(
    user_id,
    title,
    event_date,
    start_time,
    end_time,
    category,
    priority
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events
        (
            user_id,
            title,
            event_date,
            start_time,
            end_time,
            category,
            priority
        )

        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        title,
        event_date,
        start_time,
        end_time,
        category,
        priority
    ))

    conn.commit()

    cur.close()
    conn.close()


def get_events(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            title,
            event_date,
            start_time,
            end_time,
            category,
            priority

        FROM events

        WHERE user_id=%s

        ORDER BY event_date ASC
    """, (user_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data
# ================= CONFLICT DETECTION =================

def check_conflict(user_id, event_date, start_time, end_time):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            title,
            event_date,
            start_time,
            end_time,
            category,
            priority
        FROM events
        WHERE user_id=%s
        AND event_date=%s
        AND (
            start_time < %s
            AND end_time > %s
        )
    """, (
        user_id,
        event_date,
        end_time,
        start_time
    ))

    conflict = cur.fetchone()

    cur.close()
    conn.close()

    return conflict

def delete_event(event_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM events
        WHERE id=%s AND user_id=%s
    """, (
        event_id,
        user_id
    ))

    conn.commit()

    cur.close()
    conn.close()


# ================= GOAL FUNCTIONS =================

def insert_goal(user_id, goal, progress):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO goals (user_id, goal, progress)
        VALUES (%s, %s, %s)
    """, (
        user_id,
        goal,
        progress
    ))

    conn.commit()

    cur.close()
    conn.close()


def get_goals(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, goal, progress
        FROM goals
        WHERE user_id=%s
    """, (user_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def delete_goal(goal_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM goals
        WHERE id=%s AND user_id=%s
    """, (
        goal_id,
        user_id
    ))

    conn.commit()

    cur.close()
    conn.close()
def delete_expired_events(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM events
        WHERE user_id=%s
        AND event_date < CURRENT_DATE
    """, (user_id,))

    conn.commit()

    cur.close()
    conn.close()
def update_goal_progress(
    goal_id,
    progress,
    user_id
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE goals
        SET progress=%s
        WHERE id=%s
        AND user_id=%s
        """,
        (
            progress,
            goal_id,
            user_id
        )
    )

    conn.commit()

    cur.close()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user
