from auth import get_connection

# ================= ASSIGNMENTS =================

def insert_assignment(user_id, name, subject, deadline, priority):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO assignments (user_id, name, subject, deadline, priority)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, name, subject, deadline, priority))

    conn.commit()
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
    conn.close()
    return data


def delete_assignment(assignment_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM assignments
        WHERE id=%s AND user_id=%s
    """, (assignment_id, user_id))

    conn.commit()
    conn.close()