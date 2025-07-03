from database.db import get_conn
from levels.level_stats import level_stats

def create_player(user_id, name, age=None):
    # Set initial stats based on level
    initial_level = "-F"
    stats = level_stats.get(initial_level, {"HP": 100, "MP": 50, "SP": 5})
    
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO players (user_id, name, age, hp, mp, sp, physical_level) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO NOTHING
        """, (user_id, name, age, stats["HP"], stats["MP"], stats["SP"], initial_level))
        return conn.total_changes > 0

def get_player(user_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM players WHERE user_id = ?
        """, (user_id,))
        row = c.fetchone()
        
        if not row:
            return None
            
        return {
            "user_id": row[0],
            "name": row[1],
            "age": row[2],
            "coins": row[3],
            "upgrade_points": row[4],
            "physical_level": row[5],
            "mental_level": row[6],
            "hp": row[7],
            "mp": row[8],
            "sp": row[9]
        }

def set_player_level(user_id, level):
    if level not in level_stats:
        raise ValueError("Invalid level")
    
    stats = level_stats[level]
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE players 
            SET physical_level = ?, hp = ?, mp = ?, sp = ?
            WHERE user_id = ?
        """, (level, stats["HP"], stats["MP"], stats["SP"], user_id))
        return conn.total_changes > 0

def add_coins(user_id, amount, coin_type="gold"):
    if coin_type not in ["gold", "silver", "bronze"]:
        return False
    column = f"{coin_type}_coins"
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            UPDATE players SET {column} = {column} + ? 
            WHERE user_id = ?
        """, (amount, user_id))
        return conn.total_changes > 0


def remove_coins(user_id, amount, coin_type="gold"):
    if coin_type not in ["gold", "silver", "bronze"]:
        return False
    column = f"{coin_type}_coins"
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            UPDATE players 
            SET {column} = MAX(0, {column} - ?) 
            WHERE user_id = ?
        """, (amount, user_id))
        return conn.total_changes > 0




def set_age(user_id, age):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE players SET age = ? 
            WHERE user_id = ?
        """, (age, user_id))
        return conn.total_changes > 0

def format_profile(player, skills_combat, skills_common, skills_special):
    """
    Formats the player profile with the requested sections:
    - مهارت‌های رزمی (Combat skills)
    - مهارت های رعیتی (Common skills - everyday medieval skills)
    - مهارت‌های ویژه (Special skills)
    """
    return f"""═════════ ◉ پروفایل بازیکن ◉ ════════

✦ نام بازیکن: {player['name']}
✦ سن: {player.get('age', 'نامشخص')}
✦ پوینت ارتقا: {player.get('upgrade_points', 20)}
✦ سطح توانایی: {player.get('physical_level', '-F')}

───── ◈ وضعیت جسمانی ◈ ─────  
  ▶ HP:  {player.get('hp', 100)}
  ▶ SP:  {player.get('sp', 5)}
  
───── ◈ مهارت‌های رزمی ◈ ─────  
{format_skills(skills_combat)}

───── ◈ مهارت های رعیتی ◈ ─────  
{format_skills(skills_common)}

───── ◈ مهارت‌های ویژه ◈ ─────  
{format_skills(skills_special)}

# Developer: YSNRFD
# Telegram: @ysnrfd

"""

def format_skills(skills):
    """Formats skills list with bullet points"""
    if not skills:
        return "➤"
    return "\n".join(f"➤ {s}" for s in skills)
