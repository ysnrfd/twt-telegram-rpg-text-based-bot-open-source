from managers.profile_manager import *


def add_up(user_id, amount):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE players 
            SET upgrade_points = upgrade_points + ? 
            WHERE user_id = ?
        """, (amount, user_id))
        return conn.total_changes > 0