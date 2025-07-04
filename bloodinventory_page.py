import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db import get_connection
from datetime import datetime

class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='white')
        self.controller = controller
        self.component_expiration_days = {
            1: 365,
            2: 5,
            3: 42
        }

        self.setup_ui()
        self.load_inventory_data()

    def setup_ui(self):
        nav_bar = tk.Frame(self, bg='white')
        nav_bar.pack(fill='x')

        try:
            logo_img = Image.open("bbis_logo.png").resize((30, 30))
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(nav_bar, image=logo_photo, bg='white')
            logo_label.image = logo_photo
            logo_label.pack(side='left', padx=(10, 5), pady=10)
        except:
            pass

        tk.Label(nav_bar, text="Blood Link Hub", fg="maroon", font=("Arial", 12, "bold"), bg='white').pack(side='left')

        for txt, page in [("Home", "HomePage"), ("Donations", "DonationPage"),
                          ("Blood Inventory", "InventoryPage"), ("Donation History", "DonationHistoryPage")]:
            style = ("Arial", 10, "underline") if txt == "Blood Inventory" else ("Arial", 10)
            fg = 'red' if txt == "Blood Inventory" else 'black'
            lbl = tk.Label(nav_bar, text=txt, font=style, fg=fg, bg='white', cursor="hand2")
            lbl.pack(side='left', padx=20)
            lbl.bind("<Button-1>", lambda e, p=page: self.controller.show_frame(p))

        legend_frame = tk.Frame(self, bg='white')
        legend_frame.pack(fill='x', padx=20, pady=(5, 0))
        tk.Label(legend_frame, text="AVAILABLE    U - USED    E - EXPIRED", font=("Arial", 8), bg='white').pack(side='left')

        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10)

        self.setup_filter_section(main_frame)
        self.setup_table_section(main_frame)

    def setup_filter_section(self, parent):
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(side='left', padx=10, pady=10, anchor='n')

        tk.Label(filter_frame, text="FILTER", fg='red', font=("Arial", 9, "bold"), bg='white').pack(anchor='w', pady=(5, 2))

        filter_box = tk.Frame(filter_frame, bg='red', padx=10, pady=10)
        filter_box.pack()

        tk.Label(filter_box, text="Blood Type", bg='red', fg='white', font=("Arial", 9, "bold")).pack(anchor='w')
        self.blood_type_combo = ttk.Combobox(filter_box, values=["All", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
                                             state="readonly", font=("Arial", 9), width=18)
        self.blood_type_combo.pack(anchor='w')
        self.blood_type_combo.set("All")

        tk.Label(filter_box, text="Blood Component Type", bg='red', fg='white', font=("Arial", 9, "bold")).pack(anchor='w')
        self.component_combo = ttk.Combobox(filter_box, values=["All", "Plasma", "Platelets", "Red Blood Cells"],
                                            state="readonly", font=("Arial", 9), width=18)
        self.component_combo.pack(anchor='w')
        self.component_combo.set("All")

        tk.Label(filter_box, text="Status", bg='red', fg='white', font=("Arial", 9, "bold")).pack(anchor='w')
        self.status_combo = ttk.Combobox(filter_box, values=["All", "Available", "Used", "Expired"],
                                         state="readonly", font=("Arial", 9), width=18)
        self.status_combo.pack(anchor='w')
        self.status_combo.set("All")

        tk.Button(filter_box, text="APPLY FILTER", font=("Arial", 9, "bold"), bg='white', fg='red',
                  relief='ridge', width=18, command=self.apply_filters).pack(pady=(10, 0))

        button_frame = tk.Frame(filter_frame, bg='white')
        button_frame.pack(pady=(15, 0))

        tk.Button(button_frame, text="Mark as Used", font=("Arial", 9), bg='orange', fg='white',
                  command=self.mark_as_used, width=18).pack(pady=(0, 5))
        tk.Button(button_frame, text="Mark as Available", font=("Arial", 9), bg='green', fg='white',
                  command=self.mark_as_available, width=18).pack(pady=(0, 5))
        tk.Button(button_frame, text="Refresh", font=("Arial", 9, "bold"), bg='red', fg='white',
                  command=self.load_inventory_data, width=18).pack()

    def setup_table_section(self, parent):
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(side='right', fill='both', expand=True)

        columns = ('INVENTORY ID', '☐', 'BLOOD TYPE', 'BLOOD COMPONENT', 'QUANTITY', 'ENTRY DATE', 'EXPIRY DATE', 'STATUS')
        self.table = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.table.heading(col, text=col)
            if col == 'INVENTORY ID':
                self.table.column(col, width=0, stretch=False)
            elif col == '☐':
                self.table.column(col, width=30, anchor='center')
            else:
                self.table.column(col, anchor='center', width=110)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"), background='red', foreground='white')
        style.map("Treeview", background=[("selected", "#ffcccc")], foreground=[("selected", "black")])

        self.table.tag_configure("default_black", foreground="black")

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.no_data_label = tk.Label(table_frame, text="— No data found. —", font=("Arial", 11, "italic"), fg="gray", bg="white")
        self.no_data_label.place(relx=0.5, rely=0.5, anchor="center")
        self.no_data_label.lower(self.table)

        self.table.bind('<Double-1>', self.toggle_selection)

    def load_inventory_data(self):
        try:
            for item in self.table.get_children():
                self.table.delete(item)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.inventory_id, d2.blood_type, c.component_type, i.quantity_per_component,
                       i.entry_date_stamp, i.expiration_date, i.status
                FROM Blood_Inventory i
                JOIN Donation d ON i.donation_id = d.donation_id
                JOIN Blood_Component c ON i.component_id = c.component_id
                JOIN Donor d2 ON d.donor_id = d2.donor_id
                WHERE c.component_type IN ('Plasma', 'Platelets', 'Red Blood Cells')
                ORDER BY i.inventory_id DESC
            """)

            rows = cursor.fetchall()
            for row in rows:
                inventory_id, blood_type, component_type, quantity, entry_time, expiration, current_status = row
                actual_status = self.calculate_status(expiration, current_status)
                entry_date = str(entry_time).split()[0]

                if actual_status == 'Expired' and actual_status != current_status:
                    self.update_status_in_db(inventory_id, 'Expired')

                values = (inventory_id, '⬛', blood_type, component_type,
                          quantity, entry_date, expiration, actual_status)
                self.table.insert('', 'end', values=values, tags=("default_black",))
                self.table.set(self.table.get_children()[-1], '☐', '⬛')

            if not self.table.get_children():
                self.no_data_label.lift(self.table)
            else:
                self.no_data_label.lower(self.table)

            self.update_checkbox_colors()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def apply_filters(self):
        try:
            for item in self.table.get_children():
                self.table.delete(item)

            blood_type = self.blood_type_combo.get()
            component = self.component_combo.get()
            status = self.status_combo.get()

            query = """
                SELECT i.inventory_id, d2.blood_type, c.component_type, i.quantity_per_component,
                       i.entry_date_stamp, i.expiration_date, i.status
                FROM Blood_Inventory i
                JOIN Donation d ON i.donation_id = d.donation_id
                JOIN Blood_Component c ON i.component_id = c.component_id
                JOIN Donor d2 ON d.donor_id = d2.donor_id
                WHERE c.component_type IN ('Plasma', 'Platelets', 'Red Blood Cells')
            """
            params = []

            if blood_type != "All":
                query += " AND d2.blood_type = ?"
                params.append(blood_type)
            if component != "All":
                query += " AND c.component_type = ?"
                params.append(component)
            if status != "All":
                query += " AND i.status = ?"
                params.append(status)

            query += " ORDER BY i.inventory_id DESC"

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                inventory_id, blood_type, component_type, quantity, entry_time, expiration, current_status = row
                actual_status = self.calculate_status(expiration, current_status)
                entry_date = str(entry_time).split()[0]

                values = (inventory_id, '⬛', blood_type, component_type,
                          quantity, entry_date, expiration, actual_status)
                self.table.insert('', 'end', values=values, tags=("default_black",))
                self.table.set(self.table.get_children()[-1], '☐', '⬛')

            if not self.table.get_children():
                self.no_data_label.lift(self.table)
            else:
                self.no_data_label.lower(self.table)

            self.update_checkbox_colors()
            conn.close()

        except Exception as e:
            messagebox.showerror("Filter Error", str(e))

    def update_checkbox_colors(self):
        for item in self.table.get_children():
            self.table.tag_configure(item + "_checkbox", foreground="red")
            self.table.item(item, tags=("default_black", item + "_checkbox"))

    def calculate_status(self, expiration_date, current_status):
        try:
            exp = datetime.strptime(expiration_date, "%Y-%m-%d")
            return 'Expired' if exp < datetime.now() else current_status
        except:
            return current_status

    def toggle_selection(self, event):
        item = self.table.selection()[0]
        current_value = self.table.set(item, '☐')
        new_value = '✅' if current_value == '⬛' else '⬛'
        self.table.set(item, '☐', new_value)
        self.update_checkbox_colors()

    def get_selected_items(self):
        return [item for item in self.table.get_children() if self.table.set(item, '☐') == '✅']

    def mark_as_used(self):
        selected_items = self.get_selected_items()
        if not selected_items:
            return messagebox.showwarning("No Selection", "Select items first.")
        if messagebox.askyesno("Confirm", f"Mark {len(selected_items)} as used?"):
            conn = get_connection()
            cur = conn.cursor()
            for item in selected_items:
                id = self.table.set(item, 'INVENTORY ID')
                self.update_status_in_db(id, 'Used')
            conn.commit()
            conn.close()
            self.load_inventory_data()

    def mark_as_available(self):
        selected_items = self.get_selected_items()
        if not selected_items:
            return messagebox.showwarning("No Selection", "Select items first.")

        skipped = 0
        for item in selected_items:
            id = self.table.set(item, 'INVENTORY ID')
            exp = self.table.set(item, 'EXPIRY DATE')
            status = self.table.set(item, 'STATUS')

            if status == "Used":
                skipped += 1
                continue  # Do not allow reverting from Used to Available

            if not self.is_expired(exp):
                self.update_status_in_db(id, 'Available')

        self.load_inventory_data()

        if skipped > 0:
            messagebox.showinfo("Notice", f"{skipped} item(s) were already marked as 'Used' and cannot be changed.")

    def is_expired(self, expiry_date):
        try:
            return datetime.strptime(expiry_date, "%Y-%m-%d") < datetime.now()
        except:
            return False

    def update_status_in_db(self, inventory_id, new_status):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE Blood_Inventory SET status = ? WHERE inventory_id = ?", (new_status, inventory_id))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
