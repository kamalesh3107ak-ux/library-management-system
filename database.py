import sqlite3

connection = sqlite3.connect("library.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    image TEXT,
    status TEXT DEFAULT 'Available',
    due_date TEXT,
    fine INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

connection.commit()

connection.close()

print("Database Created Successfully")