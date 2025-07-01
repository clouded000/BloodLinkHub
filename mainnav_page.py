import tkinter as tk

from home_page import HomePage
from donation_page import DonationPage
from bloodinventory_page import InventoryPage
from donationhistory_page import DonationHistoryPage

class MainApp(tk.Tk):
    def __init__(self, admin_id):
        super().__init__()
        self.title("Blood Bank System")
        self.geometry("1000x600")
        self.configure(bg='white')

        self.admin_id = admin_id
        self.frames = {}

        # Make the window responsive
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        container = tk.Frame(self, bg='white')
        container.grid(row=0, column=0, sticky='nsew')
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Initialize pages
        for F in (HomePage, InventoryPage, DonationHistoryPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        # Special case for DonationPage that needs admin_id
        donation_frame = DonationPage(parent=container, controller=self, admin_id=self.admin_id)
        self.frames["DonationPage"] = donation_frame
        donation_frame.grid(row=0, column=0, sticky='nsew')

        # Show homepage first
        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
