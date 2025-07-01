import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
from db import get_connection


class DonationPage(tk.Frame):
    def __init__(self, parent, controller, admin_id):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.admin_id = admin_id

        nav = tk.Frame(self, bg='white')
        nav.pack(fill='x')

        logo_img = ImageTk.PhotoImage(Image.open("bbis_logo.png").resize((30, 30)))
        tk.Label(nav, image=logo_img, bg='white').pack(side='left', padx=10)
        tk.Label(nav, text="Blood Link Hub", fg="maroon", font=("Arial", 12, "bold"), bg='white').pack(side='left')

        for txt, page in [("Home", "HomePage"), ("Donations", "DonationPage"),
                          ("Blood Inventory", "InventoryPage"), ("Donation History", "DonationHistoryPage")]:
            style = ("Arial", 10, "underline") if txt == "Donations" else ("Arial", 10)
            fg = 'red' if txt == "Donations" else 'black'
            lbl = tk.Label(nav, text=txt, font=style, fg=fg, bg='white', cursor="hand2")
            lbl.pack(side='left', padx=20)
            lbl.bind("<Button-1>", lambda e, p=page: controller.show_frame(p))

        tk.Label(nav, text="👤", font=("Arial", 12), bg='white').pack(side='right', padx=20)
        tk.Frame(self, bg='lightgray', height=1).pack(fill='x')

        mf = tk.Frame(self, bg='white')
        mf.pack(fill='both', expand=True, pady=10, padx=10)

        lf = tk.Frame(mf, bg='white')
        lf.pack(side='left', padx=10)

        tk.Label(lf, text="+ ADD DONATION", fg='red', font=("Arial", 10, "bold"), bg='white').pack(anchor='w')
        ff = tk.Frame(lf, bg='red', padx=10, pady=10)
        ff.pack(pady=5)

        def make_field(label, parent=ff):
            tk.Label(parent, text=label, bg='red', fg='white').pack(anchor='w')
            e = tk.Entry(parent, width=30)
            e.pack(pady=2)
            return e

        self.first_name = make_field("First Name:")
        self.last_name = make_field("Last Name:")
        self.contact = make_field("Contact Number:")
        self.email = make_field("Email:")
        self.volume = make_field("Volume (ml):")

        tk.Label(ff, text="Birthday:", bg='red', fg='white').pack(anchor='w')
        self.birthday = DateEntry(ff, width=28, date_pattern='yyyy-mm-dd', maxdate=datetime.today())
        self.birthday.pack(pady=2)

        tk.Label(ff, text="Sex:", bg='red', fg='white').pack(anchor='w')
        self.gender = ttk.Combobox(ff, values=["Male", "Female"], width=28)
        self.gender.pack(pady=2)

        tk.Label(ff, text="Date of Donation:", bg='red', fg='white').pack(anchor='w')
        self.date_field = tk.Entry(ff, width=30)
        self.date_field.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_field.configure(state='readonly')
        self.date_field.pack(pady=2)

        tk.Label(ff, text="Blood Type:", bg='red', fg='white').pack(anchor='w')
        self.blood_type = ttk.Combobox(ff, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], width=28)
        self.blood_type.pack(pady=2)

        tk.Button(ff, text="ADD", bg='white', fg='red',
                  font=("Arial", 10, "bold"), width=20, command=self.add_donation).pack(pady=10)

        tf = tk.Frame(mf, bg='white')
        tf.pack(side='right', fill='both', expand=True, padx=10)
        cols = (
            'First Name', 'Last Name', 'Contact', 'Email', 'Birthday', 'Sex',
            'Date of Donation', 'Blood Type'
        )
        self.donation_table = ttk.Treeview(tf, columns=cols, show='headings', height=15)
        for c in cols:
            self.donation_table.heading(c, text=c)
            self.donation_table.column(c, anchor='center', width=120)
        self.donation_table.pack(fill='both', expand=True)
        tk.Button(tf, text="Refresh", command=self.load_donations, bg='red', fg='white').pack(pady=5)

        self.load_donations()
        self._logo = logo_img

    def add_donation(self):
        fn = self.first_name.get().strip()
        ln = self.last_name.get().strip()
        bd = self.birthday.get_date().strftime("%Y-%m-%d")
        gen = self.gender.get()
        cn = self.contact.get().strip()
        em = self.email.get().strip()
        bt = self.blood_type.get()
        vol = self.volume.get().strip()
        dt = self.date_field.get()

        if not all([fn, ln, bd, gen, cn, bt, vol]):
            return messagebox.showerror("Error", "Please fill out every field.")

        if not vol.isdigit() or int(vol) < 450 or int(vol) > 500:
            return messagebox.showerror("Error", "Volume must be between 450 ml and 500 ml.")

        if not cn.isdigit() or len(cn) != 11:
            return messagebox.showerror("Invalid Format", "Contact number must be exactly 11 digits.")
        if not re.match(r"^09\d{9}$", cn):
            return messagebox.showerror("Invalid Format", "Contact must start with '09' and be 11 digits.")

        name_pattern = r"^[A-Za-z\s\-]+$"
        if not re.match(name_pattern, fn) or not re.match(name_pattern, ln):
            return messagebox.showerror("Error", "Names can only contain letters, spaces, or hyphens.")

        gmail_pattern = r"^[a-zA-Z0-9._%+-]+@gmail.com$"
        if em and not re.match(gmail_pattern, em):
            return messagebox.showerror("Invalid Format", "Enter a valid Gmail address.")

        birth_date = datetime.strptime(bd, "%Y-%m-%d")
        age = relativedelta(datetime.today(), birth_date).years
        if age < 18 or age > 65:
            return messagebox.showerror("Invalid Format", "Age must be between 18 and 65.")

        try:
            conn = get_connection()
            c = conn.cursor()

            c.execute("""
                SELECT donor_id, gender FROM Donor
                WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?) AND date_of_birth = ?
            """, (fn, ln, bd))
            dup = c.fetchone()

            if dup:
                donor_id, gender_db = dup
                c.execute("SELECT MAX(donation_date) FROM Donation WHERE donor_id=?", (donor_id,))
                last_donation = c.fetchone()[0]

                if last_donation:
                    last_date = datetime.strptime(last_donation, "%Y-%m-%d")
                    months_wait = 4 if gender_db.strip().lower() == 'male' else 6
                    next_allowed = last_date + relativedelta(months=+months_wait)
                    if datetime.today() < next_allowed:
                        return messagebox.showwarning("Too Early",
                                                      f"{fn} {ln} can donate again on {next_allowed.strftime('%Y-%m-%d')}")
            else:
                c.execute("""
                    INSERT INTO Donor (first_name, last_name, date_of_birth, gender, contact_number, email_address, blood_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (fn, ln, bd, gen, cn, em, bt))
                donor_id = c.lastrowid

            now = datetime.now()
            c.execute("""
                INSERT INTO Donation (donor_id, admin_id, donation_date, donation_time, volume_ml, notes)
                VALUES (?, ?, ?, ?, ?, 'Walk-in donor')
            """, (donor_id, self.admin_id, dt, now.strftime("%H:%M"), vol))

            conn.commit()
            messagebox.showinfo("Success", "Donation recorded successfully.")
            self.load_donations()

            for var in (self.first_name, self.last_name, self.contact, self.email, self.volume):
                var.delete(0, 'end')
            self.birthday.set_date(datetime.today())
            self.gender.set('')
            self.blood_type.set('')

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def load_donations(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT do.first_name, do.last_name, do.contact_number, do.email_address,
                       do.date_of_birth, do.gender, d.donation_date,
                       do.blood_type
                FROM Donation d
                JOIN Donor do ON d.donor_id = do.donor_id
            """)
            rows = c.fetchall()
            conn.close()
            self.donation_table.delete(*self.donation_table.get_children())
            for r in rows:
                self.donation_table.insert('', 'end', values=r)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))