import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from db import get_connection

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller

        # --- Navbar ---
        nav_bar = tk.Frame(self, bg='white')
        nav_bar.pack(fill='x')

        # Proper image handling to avoid garbage collection
        self.logo_photo = ImageTk.PhotoImage(Image.open("bbis_logo.png").resize((30, 30)))
        tk.Label(nav_bar, image=self.logo_photo, bg='white').pack(side='left', padx=(15, 5), pady=10)
        tk.Label(nav_bar, text="Blood Link Hub", fg="maroon", font=("Arial", 12, "bold"), bg='white').pack(side='left')

        # Navigation Links
        for txt, page in [("Home", "HomePage"), ("Donations", "DonationPage"),
                          ("Blood Inventory", "InventoryPage"), ("Donation History", "DonationHistoryPage")]:
            style = ("Arial", 10, "underline") if txt == "Home" else ("Arial", 10)
            fg = 'red' if txt == "Home" else 'black'
            lbl = tk.Label(nav_bar, text=txt, font=style, fg=fg, bg='white', cursor="hand2")
            lbl.pack(side='left', padx=20)
            if txt != "Home":
                lbl.bind("<Button-1>", lambda e, p=page: controller.show_frame(p))

        user_menu_button = tk.Menubutton(nav_bar, text="👤", font=("Arial", 12), bg='white', relief='flat', activebackground='lightgray')
        user_menu_button.pack(side='right', padx=20)
        user_menu = tk.Menu(user_menu_button, tearoff=0)
        user_menu_button["menu"] = user_menu
        user_menu.add_command(label="Logout", command=self.logout)

        tk.Frame(self, bg='lightgray', height=1).pack(fill='x')


        content = tk.Frame(self, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(content, text="Welcome Admin!", font=("Arial", 18, "bold"), bg='white', fg='red').pack(anchor='w')
        tk.Label(content, text="Overview of current blood trends and inventory status.", font=("Arial", 11), bg='white').pack(anchor='w', pady=(0, 20))


        card_frame = tk.Frame(content, bg='white')
        card_frame.pack(fill='x', pady=(0, 10))

        def create_card(title, content_text, icon="🩸"):
            card = tk.Frame(card_frame, bg='#ffe5e5', padx=15, pady=10, relief='ridge', bd=1)
            card.pack(side='left', padx=10, fill='both', expand=True)
            tk.Label(card, text=f"{icon} {title}", font=("Arial", 11, "bold"), bg='#ffe5e5', fg='red').pack(anchor='w')
            tk.Label(card, text=content_text, font=("Arial", 10), bg='#ffe5e5').pack(anchor='w', pady=(5, 0))

        conn = get_connection()
        c = conn.cursor()

        # Get the blood type with the highest available quantity
        c.execute("""SELECT b.blood_type, SUM(bi.quantity_per_component)
                     FROM Blood_Inventory bi
                     JOIN Donation d ON bi.donation_id = d.donation_id
                     JOIN Donor b ON d.donor_id = b.donor_id
                     WHERE bi.status = 'Available'
                     GROUP BY b.blood_type
                     ORDER BY SUM(bi.quantity_per_component) DESC LIMIT 1""")
        most = c.fetchone()
        most_text = f"{most[0]} ({most[1]} ml)" if most else "No data"

        # Get the blood type with the lowest available quantity
        c.execute("""SELECT b.blood_type, SUM(bi.quantity_per_component)
                     FROM Blood_Inventory bi
                     JOIN Donation d ON bi.donation_id = d.donation_id
                     JOIN Donor b ON d.donor_id = b.donor_id
                     WHERE bi.status = 'Available'
                     GROUP BY b.blood_type
                     ORDER BY SUM(bi.quantity_per_component) ASC LIMIT 1""")
        least = c.fetchone()
        least_text = f"{least[0]} ({least[1]} ml)" if least else "No data"

        # Count how many donations were made in the past 7 days
        c.execute("SELECT COUNT(*) FROM Donation WHERE donation_date >= date('now', '-7 day')")
        recent = c.fetchone()[0]
        recent_text = f"{recent} donations this week"

        # Count how many units will expire within the next 3 days
        c.execute("""SELECT COUNT(*) FROM Blood_Inventory
                     WHERE expiration_date BETWEEN date('now') AND date('now', '+3 day')
                     AND status = 'Available'""")
        expiring = c.fetchone()[0]
        expiring_text = f"{expiring} units in next 3 days"
        conn.close()

        create_card("Most Available Blood", most_text)
        create_card("Least Available Blood", least_text)
        create_card("Recent Donations", recent_text)
        create_card("Expiring Soon", expiring_text)


        dual_frame = tk.Frame(content, bg='white')
        dual_frame.pack(fill='both', expand=True)

        graph_frame = tk.Frame(dual_frame, bg='white')
        graph_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        tk.Label(graph_frame, text="Blood Inventory Trends", font=("Arial", 12, "bold"), bg='white', fg='red').pack()
        self.graph_placeholder = tk.Frame(graph_frame, height=350, bg='#f5f5f5', bd=1, relief='sunken')
        self.graph_placeholder.pack(fill='both', expand=True)
        self.show_line_chart()

        table_frame = tk.Frame(dual_frame, bg='white')
        table_frame.pack(side='left', fill='both', expand=True)
        tk.Label(table_frame, text="Blood Type Compatibility", font=("Arial", 12, "bold"), bg='white', fg='red').pack()

        self.table_placeholder = tk.Frame(table_frame, bg='#f5f5f5', bd=1, relief='sunken')
        self.table_placeholder.pack(fill='both', expand=True)

        headers = ["Blood Type", "Gives", "Receives"]
        compatibility = [
            ["A+", "A+, AB+", "A+, A-, O+, O-"],
            ["B+", "B+, AB+", "B+, B-, O+, O-"],
            ["AB+", "AB+", "Everyone"],
            ["O+", "O+, A+, B+, AB+", "O+, O-"],
            ["A-", "A+, A-, AB+, AB-", "A-, O-"],
            ["B-", "B+, B-, AB+, AB-", "B-, O-"],
            ["AB-", "AB+, AB-", "AB-, A-, B-, O-"],
            ["O-", "Everyone", "O-"]
        ]

        for j in range(len(headers)):
            self.table_placeholder.grid_columnconfigure(j, weight=1)
        for i in range(len(compatibility) + 2):
            self.table_placeholder.grid_rowconfigure(i, weight=1)

        for j, h in enumerate(headers):
            tk.Label(self.table_placeholder, text=h, font=("Arial", 10, "bold"), bg='#f2f2f2', relief='solid').grid(row=0, column=j, sticky='nsew')

        for i, row in enumerate(compatibility):
            for j, val in enumerate(row):
                tk.Label(self.table_placeholder, text=val, font=("Arial", 10), bg='white', relief='solid', wraplength=140).grid(row=i+1, column=j, sticky='nsew')
#line chart
    def get_donations_per_month(self):
        conn = get_connection()
        cursor = conn.cursor()         # Group donations by month and count distinct donors per month
        cursor.execute("""
            SELECT strftime('%Y-%m', donation_date) AS month,
                   COUNT(DISTINCT donor_id) AS total_donors
            FROM donation
            GROUP BY month
            ORDER BY month;
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    def show_line_chart(self):
        for widget in self.graph_placeholder.winfo_children():
            widget.destroy()

        data = self.get_donations_per_month()
        if not data:
            tk.Label(self.graph_placeholder, text="No data found", bg='#f5f5f5', fg='gray').place(relx=0.5, rely=0.5, anchor='center')
            return

        months = [row[0] for row in data]
        totals = [row[1] for row in data]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(months, totals, marker='o', color='red')
        ax.set_title("Blood Donations Per Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Donors")
        ax.grid(True)

        chart_canvas = FigureCanvasTkAgg(fig, master=self.graph_placeholder)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill='both', expand=True)

    def logout(self):
        print("Admin logging out...")
        self.controller.destroy()
        from login_page import start_login_ui
        start_login_ui()
