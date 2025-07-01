import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from db import get_connection

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')

        # --- Navbar ---
        nav_bar = tk.Frame(self, bg='white')
        nav_bar.pack(fill='x')

        logo_img = Image.open("bbis_logo.png").resize((30, 30))
        logo_photo = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(nav_bar, image=logo_photo, bg='white')
        logo_label.image = logo_photo
        logo_label.pack(side='left', padx=(15, 5), pady=10)

        tk.Label(nav_bar, text="Blood Link Hub", fg="maroon", font=("Arial", 12, "bold"), bg='white').pack(side='left')

        # Navigation
        tk.Label(nav_bar, text="Home", font=("Arial", 10, "underline"), fg='red', bg='white').pack(side='left', padx=25)
        tk.Label(nav_bar, text="Donations", font=("Arial", 10), bg='white', cursor="hand2").pack(side='left', padx=5)
        tk.Label(nav_bar, text="Blood Inventory", font=("Arial", 10), bg='white', cursor="hand2").pack(side='left', padx=25)
        tk.Label(nav_bar, text="Donation History", font=("Arial", 10), bg='white', cursor="hand2").pack(side='left', padx=25)

        nav_bar.winfo_children()[3].bind("<Button-1>", lambda e: controller.show_frame("DonationPage"))
        nav_bar.winfo_children()[4].bind("<Button-1>", lambda e: controller.show_frame("InventoryPage"))
        nav_bar.winfo_children()[5].bind("<Button-1>", lambda e: controller.show_frame("DonationHistoryPage"))

        tk.Label(nav_bar, text="👤", font=("Arial", 12), bg='white').pack(side='right', padx=20)
        tk.Frame(self, bg='lightgray', height=1).pack(fill='x')

        # Dashboard Content
        content = tk.Frame(self, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(content, text="Blood Bank Admin Dashboard", font=("Arial", 18, "bold"), bg='white', fg='red').pack(anchor='w')
        tk.Label(content, text="Overview of current blood trends and inventory status.", font=("Arial", 11), bg='white').pack(anchor='w', pady=(0, 20))

        # Cards
        card_frame = tk.Frame(content, bg='white')
        card_frame.pack(fill='x', pady=(0, 10))

        def create_card(title, content_text, icon="🩸"):
            card = tk.Frame(card_frame, bg='#ffe5e5', padx=15, pady=10, relief='ridge', bd=1)
            card.pack(side='left', padx=10, fill='both', expand=True)
            tk.Label(card, text=f"{icon} {title}", font=("Arial", 11, "bold"), bg='#ffe5e5', fg='red').pack(anchor='w')
            tk.Label(card, text=content_text, font=("Arial", 10), bg='#ffe5e5').pack(anchor='w', pady=(5, 0))

        conn = get_connection()
        c = conn.cursor()

        # Most Available
        c.execute("""
            SELECT b.blood_type, SUM(bi.quantity_units)
            FROM Blood_Inventory bi
            JOIN Donation d ON bi.donation_id = d.donation_id
            JOIN Donor b ON d.donor_id = b.donor_id
            WHERE bi.status = 'Available'
            GROUP BY b.blood_type
            ORDER BY SUM(bi.quantity_units) DESC
            LIMIT 1
        """)
        most = c.fetchone()
        most_text = f"{most[0]} ({most[1]} units)" if most else "No data"

        # Least Available
        c.execute("""
            SELECT b.blood_type, SUM(bi.quantity_units)
            FROM Blood_Inventory bi
            JOIN Donation d ON bi.donation_id = d.donation_id
            JOIN Donor b ON d.donor_id = b.donor_id
            WHERE bi.status = 'Available'
            GROUP BY b.blood_type
            ORDER BY SUM(bi.quantity_units) ASC
            LIMIT 1
        """)
        least = c.fetchone()
        least_text = f"{least[0]} ({least[1]} units)" if least else "No data"

        # Recent Donations
        c.execute("""
            SELECT COUNT(*) FROM Donation
            WHERE donation_date >= date('now', '-7 day')
        """)
        recent = c.fetchone()[0]
        recent_text = f"{recent} donations this week"

        # Expiring Soon
        c.execute("""
            SELECT COUNT(*) FROM Blood_Inventory
            WHERE expiration_date BETWEEN date('now') AND date('now', '+3 day')
            AND status = 'Available'
        """)
        expiring = c.fetchone()[0]
        expiring_text = f"{expiring} units in next 3 days"

        conn.close()

        create_card("Most Available Blood", most_text)
        create_card("Least Available Blood", least_text)
        create_card("Recent Donations", recent_text)
        create_card("Expiring Soon", expiring_text)

        # Graph
        graph_frame = tk.Frame(content, bg='white')
        graph_frame.pack(fill='both', expand=True, pady=10)
        tk.Label(graph_frame, text="📊 Blood Inventory Trends", font=("Arial", 12, "bold"), bg='white', fg='red').pack(anchor='w')

        self.graph_placeholder = tk.Frame(graph_frame, height=350, bg='#f5f5f5', bd=1, relief='sunken')
        self.graph_placeholder.pack(fill='both', expand=True)

        self.show_line_chart()

    def get_donations_per_month(self):
        conn = get_connection()
        cursor = conn.cursor()
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
        # Clear previous chart if exists
        for widget in self.graph_placeholder.winfo_children():
            widget.destroy()

        data = self.get_donations_per_month()
        if not data:
            tk.Label(self.graph_placeholder, text="No data found", bg='#f5f5f5', fg='gray').place(relx=0.5, rely=0.5, anchor='center')
            return

        months = [row[0] for row in data]
        totals = [row[1] for row in data]

        fig, ax = plt.subplots(figsize=(8, 4))  # Adjust this size if needed
        ax.plot(months, totals, marker='o', color='red')
        ax.set_title("Blood Donations Per Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Donors")
        ax.grid(True)

        chart_canvas = FigureCanvasTkAgg(fig, master=self.graph_placeholder)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill='both', expand=True)
