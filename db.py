def get_connection():
    import sqlite3
    conn = sqlite3.connect('bloodbank.db')
    conn.execute("PRAGMA foreign_keys = ON")  # enable FK constraints
    return conn
