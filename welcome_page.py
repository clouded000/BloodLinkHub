import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db import get_connection
from datetime import datetime

class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')

        # Navbar
        nav_bar = tk.Frame(self, bg='white')
        nav_bar.pack(fill='x')

        logo_img = Image.open("bbis_logo.png").resize((30, 30))
        logo_photo = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(nav_bar, image=logo_photo, bg='white')
        logo_label.image = logo_photo
        logo_label.pack(side='left', padx=(10, 5), pady=10)

        tk.Label(nav_bar, text="Blood Link Hub", fg="maroon", font=("Arial", 12, "bold"), bg='white').pack(side='left')

        for txt, page in [("Home", "HomePage"), ("Donations", "DonationPage"),
                          ("Blood Inventory", "InventoryPage"), ("Donation History", "DonationHistoryPage")]:
            style = ("Arial", 10, "underline") if txt == "Blood Inventory" else ("Arial", 10)
            fg = 'red' if txt == "Blood Inventory" else 'black'
            lbl = tk.Label(nav_bar, text=txt, font=style, fg=fg, bg='white', cursor="hand2")
            lbl.pack(side='left', padx=20)
            lbl.bind("<Button-1>", lambda e, p=page: controller.show_frame(p))

        tk.Label(nav_bar, text="👤", font=("Arial", 12), bg='white').pack(side='right', padx=20)
        tk.Frame(self, bg='lightgray', height=1).pack(fill='x')

        tk.Label(self, text="A - AVAILABLE    U - USED    E - EXPIRED", font=("Arial", 8), bg='white', anchor='e').pack(fill='x', padx=20, pady=(0, 5))

        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10)

        # Filter section
        filter_frame = tk.Frame(main_frame, bg='white')
        filter_frame.pack(side='left', padx=10, pady=10, anchor='n')

        tk.Label(filter_frame, text="⛭ FILTER", fg='red', font=("Arial", 9, "bold"), bg='white').pack(anchor='w', pady=(5, 2))

        filter_box = tk.Frame(filter_frame, bg='red', padx=10, pady=10)
        filter_box.pack()

        def create_dropdown(label_text, values):
            tk.Label(filter_box, text=label_text, bg='red', fg='white', font=("Arial", 9, "bold")).pack(anchor='w', pady=(5, 0))
            combo = ttk.Combobox(filter_box, values=values, state="readonly", font=("Arial", 9), width=18)
            combo.pack(anchor='w', pady=(0, 5))
            combo.set("Select")

        create_dropdown("Blood Type", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        create_dropdown("Blood Component Type", ["Whole Blood", "Plasma", "Platelets", "RBC", "WBC", "Cryo"])
        create_dropdown("Status", ["Available", "Used", "Expired"])

        tk.Button(filter_box, text="FILTER", font=("Arial", 9, "bold"), bg='white', fg='red', relief='ridge', width=18).pack(pady=(10, 0))

        # Table section
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(side='right', fill='both', expand=True)

        columns = ('INVENTORY ID', 'BLOOD TYPE', 'BLOOD COMPONENT', 'QUANTITY', 'ENTRY DATE', 'EXPIRY DATE', 'STATUS A/U/E')
        self.table = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white", bordercolor='black', borderwidth=1)
        style.map('Treeview', background=[('selected', 'lightgray')])
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"), background='red', foreground='white', relief="ridge")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor='w', width=125, stretch=False)

        self.table.pack(fill='both', expand=True)

        # Load data from database
        self.load_inventory_data()

    def load_inventory_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT 
                    i.inventory_id,
                    d.blood_type,
                    c.component_type,
                    i.quantity_units,
                    i.entry_time_stamp,
                    i.expiration_date,
                    i.status
                FROM Blood_Inventory i
                JOIN Donation d ON i.donation_id = d.donation_id
                JOIN Blood_Component c ON i.component_id = c.component_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                self.table.insert('', 'end', values=row)

            conn.close()
        except Exception as e:
            print("Error loading inventory data:", e)
