import bcrypt
from db import get_connection

def create_admin_account(username, raw_password, first_name, last_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Admin WHERE username = ?", (username,))
    if cursor.fetchone():
        print(f"Username '{username}' already exists.")
        conn.close()
        return False

    hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO Admin (username, password, first_name, last_name)
        VALUES (?, ?, ?, ?)
    """, (username, hashed_password, first_name, last_name))

    conn.commit()
    conn.close()
    print(f"Admin '{username}' created successfully.")
    return True

def get_admin_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, password FROM Admin WHERE username = ?", (username,))
    admin = cursor.fetchone()
    conn.close()
    return admin

if __name__ == "__main__":
    username = input("Enter new admin username: ")
    password = input("Enter new admin password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ").strip() or None

    create_admin_account(username, password, first_name, last_name)
