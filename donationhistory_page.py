import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db import get_connection
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DonationHistoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller


        nav = tk.Frame(self, bg='white')
        nav.pack(fill='x')
        logo_img = ImageTk.PhotoImage(Image.open("bbis_logo.png").resize((30, 30)))
        tk.Label(nav, image=logo_img, bg='white').pack(side='left', padx=10)
        tk.Label(nav, text="Blood Link Hub", fg="maroon", font=("Arial", 12, "bold"), bg='white').pack(side='left')

        for txt, page in [("Home", "HomePage"), ("Donations", "DonationPage"),
                          ("Blood Inventory", "InventoryPage"), ("Donation History", "DonationHistoryPage")]:
            style = ("Arial", 10, "underline") if txt == "Donation History" else ("Arial", 10)
            fg = 'red' if txt == "Donation History" else 'black'
            lbl = tk.Label(nav, text=txt, font=style, fg=fg, bg='white', cursor="hand2")
            lbl.pack(side='left', padx=20)
            lbl.bind("<Button-1>", lambda e, p=page: controller.show_frame(p))


        tf = tk.Frame(self, bg='white')
        tf.pack(fill='both', expand=True, padx=20, pady=20)

        cols = (
            'First Name', 'Last Name', 'Contact', 'Email', 'Birthdate', 'Sex',
            'Date of Donation', 'Blood Type', 'Countdown to Next Donation')
        self.donation_table = ttk.Treeview(tf, columns=cols, show='headings', height=15)
        for c in cols:
            self.donation_table.heading(c, text=c)
            self.donation_table.column(c, anchor='center', width=140)

        self.donation_table.pack(fill='both', expand=True)

        tk.Button(tf, text="Refresh", command=self.load_donations, bg='red', fg='white').pack(pady=10)

        self._logo = logo_img
        self.load_donations()
    #soft delete
    def load_donations(self):
        try:
            conn = get_connection()
            c = conn.cursor()

            c.execute("""
                SELECT do.donor_id, do.first_name, do.last_name, do.contact_number, do.email_address,
                       do.date_of_birth, do.sex, d.donation_date, do.blood_type
                FROM Donation d
                JOIN Donor do ON d.donor_id = do.donor_id
                WHERE d.donation_date = (
                    SELECT MAX(d2.donation_date)
                    FROM Donation d2
                    WHERE d2.donor_id = do.donor_id
                )
            """)
            rows = c.fetchall()
            conn.close()

            # Gets latest donation for each donor
            # Joins Donor and Donation tables
            # Subquery finds the most recent donation per donor using MAX()

            self.donation_table.delete(*self.donation_table.get_children())

            for row in rows:
                donor_id, fn, ln, contact, email, dob, sex, donation_date, blood_type = row
                sex = sex.strip().lower()
                months_required = 3 if sex == 'male' else 3

                last_date = datetime.strptime(donation_date, "%Y-%m-%d")
                next_allowed = last_date + relativedelta(months=+months_required)
                remaining_days = (next_allowed - datetime.today()).days

                if (datetime.today() - last_date).days > 366:
                    continue
                # if (datetime.now() - last_date).total_seconds() > 60:
                    # continue

                countdown = "Eligible now" if remaining_days <= 0 else f"{remaining_days} day(s)"

                self.donation_table.insert('', 'end', values=(
                    fn, ln, contact, email, dob, sex.capitalize(),
                    donation_date, blood_type, countdown
                ))

        except Exception as e:
            messagebox.showerror("Database Error", str(e))