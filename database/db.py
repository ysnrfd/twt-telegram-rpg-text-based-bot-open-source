import sqlite3
import os
from config import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        
        # Players table
        c.execute("""
            CREATE TABLE IF NOT EXISTS players (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gold_coins INTEGER DEFAULT 0,
        silver_coins INTEGER DEFAULT 0,
        bronze_coins INTEGER DEFAULT 0,
        upgrade_points INTEGER DEFAULT 20,
        physical_level TEXT DEFAULT '-F',
        mental_level TEXT DEFAULT 'ندارد',
        hp INTEGER,
        mp INTEGER,
        sp INTEGER
        )
        """)
        
        # Player groups table
        c.execute("""
            CREATE TABLE IF NOT EXISTS player_groups (
                user_id TEXT PRIMARY KEY,
                group_id TEXT
            )
        """)
        
        # Equipment table
        c.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                name TEXT,
                FOREIGN KEY(user_id) REFERENCES players(user_id)
            )
        """)
        
        # Skills table
        c.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                user_id TEXT,
                category TEXT,
                name TEXT,
                level TEXT,
                current_up INTEGER DEFAULT 0,
                required_up INTEGER,
                PRIMARY KEY (user_id, category, name),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        """)
        

        # Shop items table (public)
        c.execute("""
            CREATE TABLE IF NOT EXISTS shop_items (
                name TEXT PRIMARY KEY,
                quantity INTEGER,
                price INTEGER,
                coin_type TEXT,
                health INTEGER
            )
        """)

        # Purchased items (who bought what)
        c.execute("""
            CREATE TABLE IF NOT EXISTS player_items (
                user_id TEXT,
                item_name TEXT,
                health INTEGER,
                PRIMARY KEY (user_id, item_name),
                FOREIGN KEY(user_id) REFERENCES players(user_id),
                FOREIGN KEY(item_name) REFERENCES shop_items(name)
            )
        """)



        conn.commit()