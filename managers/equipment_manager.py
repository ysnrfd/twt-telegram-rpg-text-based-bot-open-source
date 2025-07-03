from database.db import get_conn

def add_equipment(user_id, item_name):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO equipment (user_id, name) 
            VALUES (?, ?)
        """, (user_id, item_name))
        return conn.total_changes > 0

def get_equipment(user_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT name FROM equipment 
            WHERE user_id = ?
        """, (user_id,))
        return [row[0] for row in c.fetchall()]

def remove_equipment(user_id, item_name):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            DELETE FROM equipment 
            WHERE user_id = ? AND name = ?
        """, (user_id, item_name))
        return conn.total_changes > 0