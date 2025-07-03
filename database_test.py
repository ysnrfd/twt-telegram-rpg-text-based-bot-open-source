import sqlite3
conn = sqlite3.connect("rpg.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(players)")
print(cursor.fetchall())
