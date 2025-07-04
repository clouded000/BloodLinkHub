import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import subprocess
import os
import sys

def open_login():
    root.destroy()
    script_path = os.path.join(os.path.dirname(__file__), "login_page.py")
    python_exec = sys.executable if hasattr(sys, 'executable') else "python"
    subprocess.Popen([python_exec, script_path], cwd=os.path.dirname(script_path))


# --- Main Window ---
root = tk.Tk()
root.title("Welcome to Blood Link Hub!")
root.geometry("800x500")
root.configure(bg='black')
root.resizable(True, True)

# --- Resample Compatibility ---
try:
    resample_filter = Image.Resampling.LANCZOS
except AttributeError:
    resample_filter = Image.ANTIALIAS

# --- Background GIF ---
gif_path = "duguduguan.gif"
bg_label = tk.Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

try:
    gif = Image.open(gif_path)
    original_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(gif)]
except Exception as e:
    print("GIF load error:", e)
    original_frames = []

gif_frames = []

def resize_gif_frames(width, height):
    global gif_frames
    if original_frames:
        gif_frames = [
            ImageTk.PhotoImage(frame.resize((width, height), resample_filter))
            for frame in original_frames
        ]

def animate(index=0):
    if gif_frames:
        bg_label.config(image=gif_frames[index])
        root.after(100, animate, (index + 1) % len(gif_frames))

root.update_idletasks()
resize_gif_frames(root.winfo_width(), root.winfo_height())
animate()

def on_resize(event):
    resize_gif_frames(event.width, event.height)

root.bind("<Configure>", on_resize)

# --- Logo and Title Section ---
content_frame = tk.Frame(root, bg='white', padx=2, pady=2)
content_frame.place(relx=0.5, rely=0.4, anchor="center")

inner_frame = tk.Frame(content_frame, bg='black')
inner_frame.pack()

# --- Logo ---
try:
    logo_img = Image.open("bbis_logo.png").resize((200, 200), resample_filter)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(inner_frame, image=logo_photo, bg='black', bd=0)
    logo_label.image = logo_photo
    logo_label.pack(pady=(20, 10))
except Exception as e:
    print("Logo error:", e)

# --- Title Image ---
try:
    title_img = Image.open("BLOOD LINK HUB.png").resize((400, 200), resample_filter)
    title_photo = ImageTk.PhotoImage(title_img)
    title_label = tk.Label(inner_frame, image=title_photo, bg='black', bd=0)
    title_label.image = title_photo
    title_label.pack(pady=(0, 10))
except Exception as e:
    print("Title image error:", e)

# --- Proceed Button Section with Border ---
button_border = tk.Frame(root, bg="white", padx=2, pady=2)
button_border.place(relx=0.5, rely=0.82, anchor="center")

button_frame = tk.Frame(button_border, bg='black')
button_frame.pack()

proceed_btn = tk.Button(
    button_frame,
    text="Welcome to Blood Link Hub! Proceed to Log In.",
    font=("Arial", 12, "bold"),
    bg="black",
    fg="white",
    activebackground="black",
    activeforeground="white",
    padx=20, pady=10,
    bd=0,
    highlightthickness=0,
    command=open_login
)
proceed_btn.pack()

root.mainloop()
