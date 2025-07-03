from database.db import get_conn
from levels.level_table import level_table

def set_skill_level(user_id, category, skill_name, level):
    # Find required UP for the level
    required_up = 0
    for from_lvl, to_lvl, up_cost in level_table:
        if from_lvl == level or to_lvl == level:
            required_up = up_cost
            break
    # Valid categories
    valid_categories = ["combat", "common", "special"]
    if category not in valid_categories:
        return False  # Invalid category
    
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO skills (user_id, category, name, level, current_up, required_up) 
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, category, name) 
            DO UPDATE SET level=?, current_up=0, required_up=?
        """, (user_id, category, skill_name, level, 0, required_up, level, required_up))
        return conn.total_changes > 0

def get_skills(user_id, category):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT name, level, current_up, required_up 
            FROM skills 
            WHERE user_id = ? AND category = ?
        """, (user_id, category))
        return [
            f"{name} {level} [UP {current_up}/{required_up}]"
            for name, level, current_up, required_up in c.fetchall()
        ]