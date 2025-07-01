import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from db import get_connection


def open_main_app(admin_id):
    from mainnav_page import MainApp
    app = MainApp(admin_id)
    app.mainloop()

def login():
    username = email_entry.get().strip()
    password = password_entry.get().strip()
    if not username or not password:
        return messagebox.showerror("Login Failed", "Please enter both username and password.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT admin_id FROM Admin WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            admin_id = admin[0]
            root.destroy()
            open_main_app(admin_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def forgot_password():
    messagebox.showinfo("Forgot Password", "Password recovery is not yet implemented.")

# --- Main App Window ---
root = tk.Tk()
root.title("Blood Bank Inventory")
root.geometry("600x400")
root.configure(bg='white')
root.resizable(False, False)

# --- Top Left Header ---
top_frame = tk.Frame(root, bg='white')
top_frame.pack(anchor='nw', padx=20, pady=10)

logo_image = Image.open("bbis_logo.png").resize((40, 40))
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(top_frame, image=logo_photo, bg='white')
logo_label.image = logo_photo  # prevent garbage collection
logo_label.pack(side='left')

text_frame = tk.Frame(top_frame, bg='white')
text_frame.pack(side='left', padx=10)

admin_label = tk.Label(text_frame, text="Sintang Duguan", fg="maroon", font=("Arial", 10, "bold"), bg='white')
admin_label.pack(anchor='w')

title_label = tk.Label(text_frame, text="Log In", font=("Arial", 14), bg='white')
title_label.pack(anchor='w')

# --- Center Login Form ---
center_frame = tk.Frame(root, bg='white')
center_frame.pack(expand=True)

admin_word = tk.Label(center_frame, text="Admin?", font=("Times New Roman", 14, "bold"), bg='white')
admin_word.pack()

log_text = tk.Label(center_frame, text="Let's log you in!", font=("Arial", 9), bg='white')
log_text.pack()

# --- Username Field ---
email_frame = tk.Frame(center_frame, bg='white')
email_frame.pack(pady=(20, 5), padx=50)

email_label = tk.Label(email_frame, text="Username", font=("Times New Roman", 9, "bold"), bg='white')
email_label.pack(anchor='w')

email_entry = tk.Entry(email_frame, font=("Arial", 10), width=50)
email_entry.pack(ipady=5)

# --- Password Field ---
password_frame = tk.Frame(center_frame, bg='white')
password_frame.pack(pady=(10, 5), padx=50)

password_label = tk.Label(password_frame, text="Password", font=("Times New Roman", 10, "bold"), bg='white')
password_label.pack(anchor='w')

password_entry = tk.Entry(password_frame, font=("Arial", 10), width=50, show="*")
password_entry.pack(ipady=5)

forgot_btn = tk.Button(password_frame, text="Forgot password?", fg="maroon",
                       font=("Times New Roman", 9, "underline"), bg='white',
                       bd=0, cursor="hand2", command=forgot_password)
forgot_btn.pack(anchor='e', pady=(3, 0))

# --- Login Button ---
login_btn = tk.Button(center_frame, text="Log In", bg="#a00", fg="white",
                      font=("Arial", 10, "bold"), width=40, height=2, command=login)
login_btn.pack(pady=20)

root.mainloop()
