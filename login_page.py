import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import bcrypt
from admin import get_admin_by_username

def open_main_app(admin_id):
    from mainnav_page import MainApp
    app = MainApp(admin_id)
    app.mainloop()

def start_login_ui():
    def login():
        username = email_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            return messagebox.showerror("Login Failed", "Please enter both username and password.")

        try:
            admin = get_admin_by_username(username)   # Retrieve admin record by username

            if admin:
                admin_id, hashed_password = admin

                if isinstance(hashed_password, str):
                    hashed_password = hashed_password.encode('utf-8')  # Ensure the password is in byte format for bcrypt verification

                # Compare entered password with the stored hashed password
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    if animation_id is not None:
                        root.after_cancel(animation_id)  # Cancel animation
                    root.destroy()
                    open_main_app(admin_id)
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password.")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    global root
    root = tk.Tk()
    root.title("Blood Bank Inventory")
    root.geometry("800x600")
    root.configure(bg='black')
    root.resizable(True, True)

    # Load GIF animation
    gif_path = "duguan.gif"  # Replace with your gif file
    gif = Image.open(gif_path)
    gif_frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]

    # Background label
    background_label = tk.Label(root)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    current_width, current_height = 800, 600
    animation_id = None

    def animate(index=0):
        nonlocal current_width, current_height, animation_id
        frame = gif_frames[index].copy().resize((current_width, current_height))
        photo = ImageTk.PhotoImage(frame)
        background_label.config(image=photo)
        background_label.image = photo
        animation_id = root.after(100, animate, (index + 1) % len(gif_frames))

    def on_resize(event):
        nonlocal current_width, current_height
        current_width = event.width
        current_height = event.height

    root.bind("<Configure>", on_resize)
    animate()

    # Centered white container
    container = tk.Frame(root, bg='white')
    container.place(relx=0.5, rely=0.5, anchor='center')

    # Top logo + title
    top_frame = tk.Frame(container, bg='white')
    top_frame.pack(anchor='nw', padx=20, pady=(20, 10))

    try:
        logo_image = Image.open("bbis_logo.png").resize((40, 40))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_frame, image=logo_photo, bg='white')
        logo_label.image = logo_photo
        logo_label.pack(side='left')
    except Exception as e:
        print("Logo load error:", e)

    text_frame = tk.Frame(top_frame, bg='white')
    text_frame.pack(side='left', padx=10)

    tk.Label(text_frame, text="Blood Link Hub", fg="maroon", font=("Arial", 10, "bold"), bg='white').pack(anchor='w')
    tk.Label(text_frame, text="Log In", font=("Arial", 14, "bold"), bg='white').pack(anchor='w')

    # Login form
    form_frame = tk.Frame(container, bg='white')
    form_frame.pack(padx=20, pady=(10, 20))

    tk.Label(form_frame, text="Admin?", font=("Arial", 15, "bold"), bg='white').pack()
    tk.Label(form_frame, text="Let's log you in!", font=("Arial", 9), bg='white').pack()

    # Username field
    email_frame = tk.Frame(form_frame, bg='white')
    email_frame.pack(pady=(20, 5))

    global email_entry
    tk.Label(email_frame, text="Username", font=("Arial", 9, "bold"), bg='white').pack(anchor='w')
    email_entry = tk.Entry(email_frame, font=("Arial", 10), width=40)
    email_entry.pack(ipady=5)

    # Password field
    password_frame = tk.Frame(form_frame, bg='white')
    password_frame.pack(pady=(10, 5))

    global password_entry
    tk.Label(password_frame, text="Password", font=("Arial", 10, "bold"), bg='white').pack(anchor='w')
    password_entry = tk.Entry(password_frame, font=("Arial", 10), width=40, show="*")
    password_entry.pack(ipady=5)

    # Login button
    tk.Button(form_frame, text="Log In", bg="#a00", fg="white",
              font=("Arial", 10, "bold"), width=35, height=2, command=login).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_login_ui()
