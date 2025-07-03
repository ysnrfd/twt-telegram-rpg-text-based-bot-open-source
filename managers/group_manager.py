from database.db import get_conn

def set_player_group(user_id, group_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO player_groups (user_id, group_id) 
            VALUES (?, ?)
        """, (user_id, group_id))
        return conn.total_changes > 0

def get_player_group(user_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT group_id FROM player_groups 
            WHERE user_id = ?
        """, (user_id,))
        row = c.fetchone()
        return row[0] if row else None