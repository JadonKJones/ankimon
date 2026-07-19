import sqlite3

conn = sqlite3.connect("test_caught.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS user_data (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
conn.commit()

import json
val = json.dumps([13, 14])
cursor.execute("INSERT OR REPLACE INTO user_data (key, value) VALUES (?, ?)", ("pokedex_caught", val))
conn.commit()

cursor.execute("SELECT value FROM user_data WHERE key = ?", ("pokedex_caught",))
row = cursor.fetchone()
print(json.loads(row[0]))
