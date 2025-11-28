import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import os
import datetime
from Model import Exhibition, Workshop
import re

# =============================================================================
#                                    VIEW
# =============================================================================

class BaseFrame(tk.Frame):
    """
    A template class for all pages in the application.
    It inherits from tk.Frame and ensures every page has access to the main 'controller'.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # Initialize the underlying Tkinter Frame widget
        self.controller = controller  # Store a reference to the main application app (GreenWaveApp) logic


# --- STEP 1: START ---
class StartPage(BaseFrame):
    """
    The landing screen of the application.
    Displays general conference information and provides navigation to Login or Register.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize the BaseFrame parent structure
        # Header
        tk.Label(self, text="GREENWAVE CONFERENCE 2026", font=("Helvetica", 24, "bold"), fg="#2E8B57").pack(
            pady=(60, 10))  # Create and pack the main title label with green text and vertical padding
        tk.Label(self, text='"Sustainability in Action"', font=("Helvetica", 16, "italic")).pack(pady=5)  # Subtitle

        # Info
        info_text = (
            "📅 April 15-18, 2026\n"
            "📍 Zayed University • AUH Campus\n\n"
            "EXHIBITIONS:\n"
            "• Climate Tech Innovations\n"
            "• Green Policy & Governance\n"
            "• Community Action & Impact"
        )  # Define the multi-line informational string
        tk.Label(self, text=info_text, justify="left", font=("Courier", 12), bg="#f0f0f0", padx=20, pady=10).pack(
            pady=30)  # Create a label for the info text with a light gray background and monospaced font

        btn_frame = tk.Frame(self)  # Create a separate frame to hold the buttons side-by-side
        btn_frame.pack(pady=30)  # Pack the button frame with vertical padding
        # Use lambda to delay the command execution until the button is actually clicked
        tk.Button(btn_frame, text="REGISTER", width=15, height=2, bg="#90EE90",
                  command=lambda: controller.show_frame("RegisterPage")).pack(side="left", padx=20)  # Register Button
        tk.Button(btn_frame, text="LOGIN", width=15, height=2, bg="#87CEEB",
                  command=lambda: controller.show_frame("LoginPage")).pack(side="left", padx=20)  # Login Button


# --- STEP 2: AUTH ---
class RegisterPage(BaseFrame):
    """
    The Registration screen.
    Collects user details (Name, Email, Phone, Password) and performs validation before creating an account.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set the background color of the entire page to light gray

        # --- OUTER TITLE ---
        # Reduced pady to pull it up slightly
        tk.Label(self, text="New User Registration", font=("Arial", 18, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(20, 5))  # Create the page heading label

        # --- THE "WINDOW" (Compact) ---
        # expand=False prevents it from stretching vertically, simulating a modal dialog box
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Create a frame with a raised 3D border
        window_frame.pack(padx=220, pady=10, fill="x", expand=False)  # Pack it centrally with significant side padding

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e",
                             height=30)  # Create a blue strip at the top of the window frame
        title_bar.pack(fill="x", side="top")  # Pack it to fill the width at the top
        title_bar.pack_propagate(False)  # Prevent the frame from shrinking to fit its children
        tk.Label(title_bar, text="  Create Account", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Add white text inside the blue bar

        # --- CONTENT FORM ---
        # Reduced pady inside the white box for a compact look
        content = tk.Frame(window_frame, bg="white", padx=30, pady=15)  # Create the main form area inside the window
        content.pack(fill="both", expand=True)  # Pack it to fill available space

        # Helper function to create input rows with consistent tighter spacing
        def create_input(label, row, is_pass=False):
            # Reduced pady from 5 to 2 for tighter rows
            tk.Label(content, text=label, font=("Arial", 9, "bold"), bg="white").grid(row=row, column=0, sticky="w",
                                                                                      pady=2)  # Create and grid the label
            entry = tk.Entry(content, font=("Arial", 10), width=30, bd=1, relief="solid",
                             show="*" if is_pass else "")  # Create entry
            entry.grid(row=row, column=1, padx=15, pady=2)  # Grid the entry field next to the label
            return entry  # Return the entry widget so we can access its data later

        self.e_name = create_input("Full Name:", 0)  # Create Name input field at row 0
        self.e_email = create_input("Email:", 1)  # Create Email input field at row 1
        self.e_phone = create_input("Phone:", 2)  # Create Phone input field at row 2
        self.e_pass = create_input("Password:", 3, True)  # Create Password input field (masked) at row 3
        self.e_conf = create_input("Confirm Pass:", 4, True)  # Create Confirmation input field (masked) at row 4

        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(window_frame, bg="white", pady=15)  # Create a frame for action buttons
        btn_frame.pack(side="bottom", fill="x")  # Pack it at the bottom of the window frame

        tk.Button(btn_frame, text="Register Now", font=("Arial", 10, "bold"), width=15,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.submit).pack(side="right", padx=30)  # Submit Button

        tk.Button(btn_frame, text="Cancel", font=("Arial", 9), width=10,
                  bg="#f0f0f0", relief="raised", bd=2, command=lambda: controller.show_frame("StartPage")).pack(
            side="right", padx=5)  # Cancel Button to go back

    def update_data(self):
        # Clear all registration fields
        self.e_name.delete(0, tk.END)
        self.e_email.delete(0, tk.END)
        self.e_phone.delete(0, tk.END)
        self.e_pass.delete(0, tk.END)
        self.e_conf.delete(0, tk.END)

    def submit(self):
        """
        Validates the input fields and attempts to register the user via the Controller.
        """
        # Get values
        name = self.e_name.get().strip()  # Retrieve name and remove leading/trailing whitespace
        email = self.e_email.get().strip()  # Retrieve email and remove whitespace
        phone = self.e_phone.get().strip()  # Retrieve phone and remove whitespace
        pwd = self.e_pass.get()  # Retrieve raw password
        conf = self.e_conf.get()  # Retrieve raw confirmation password

        # 1. Check Empty
        if not (name and email and phone and pwd and conf):  # Check if any field is empty
            messagebox.showerror("Error", "All fields are required.")  # Show error popup
            return  # Stop execution

        # 2. Validate Name (Letters/Spaces only)
        if not re.match(r"^[a-zA-Z\s]+$", name):  # Use regex to ensure name contains only letters and spaces
            messagebox.showerror("Error", "Name must contain only letters.")  # Show error popup
            return  # Stop execution

        # 3. Validate Phone (Digits only, length 8-15)
        if not (phone.isdigit() and 8 <= len(phone) <= 15):  # Check if phone is numeric and within length range
            messagebox.showerror("Error", "Phone must be 8-15 digits.")  # Show error popup
            return  # Stop execution

        # 4. Validate Email Format
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):  # Use regex to validate standard email format
            messagebox.showerror("Error", "Invalid Email Format.")  # Show error popup
            return  # Stop execution

        # --- NEW CHECK: PASSWORD LENGTH ---
        if len(pwd) < 4:  # Check if password is too short
            messagebox.showerror("Error", "Password must be at least 4 characters long.")  # Show error popup
            return  # Stop execution

        # 5. Password Match
        if pwd != conf:  # Check if password and confirmation match exactly
            messagebox.showerror("Error", "Passwords do not match!")  # Show error popup
            return  # Stop execution

        # 6. Attempt Registration
        if self.controller.register_user(name, email, pwd,
                                         phone):  # Call controller to register; returns True if successful
            messagebox.showinfo("Success", "Account created successfully!")  # Show success popup
            self.controller.show_frame("LoginPage")  # Navigate to Login Page
        else:
            messagebox.showerror("Error", "Email is already registered.")  # Show error if email exists


class LoginPage(BaseFrame):
    """
    The Login screen.
    Authenticates users (Attendee or Admin) based on email and password.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize BaseFrame
        self.configure(bg="#f0f0f0")  # Set background color

        # --- OUTER TITLE ---
        tk.Label(self, text="GreenWave Conference", font=("Arial", 22, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(40, 10))  # Main page title

        # --- THE "WINDOW" CONTAINER ---
        # CHANGED: padx=250 squeezes the box to be much smaller/narrower than the Register page
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Create the central window frame
        window_frame.pack(padx=250, pady=20, fill="x", expand=False)  # Pack it with heavy side padding

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Create blue title bar
        title_bar.pack(fill="x", side="top")  # Pack at the top
        title_bar.pack_propagate(False)  # Fix height
        tk.Label(title_bar, text="  User Authentication", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Add title text

        # --- CONTENT AREA ---
        content = tk.Frame(window_frame, bg="white", padx=30, pady=30)  # Create content area with padding
        content.pack(fill="both", expand=True)  # Pack content area

        tk.Label(content, text="Sign In", font=("Arial", 16, "bold"), bg="white", fg="#333").pack(
            pady=(0, 20))  # Header

        # Email Input
        tk.Label(content, text="Email Address:", font=("Arial", 10), bg="white").pack(anchor="w")  # Label
        self.e_email = tk.Entry(content, font=("Arial", 11), width=30, bd=1, relief="solid")  # Entry field
        self.e_email.pack(fill="x", pady=(5, 15), ipady=3)  # Pack entry with internal padding

        # Password Input
        tk.Label(content, text="Password:", font=("Arial", 10), bg="white").pack(anchor="w")  # Label
        self.e_pass = tk.Entry(content, font=("Arial", 11), width=30, bd=1, relief="solid", show="*")  # Entry (masked)
        self.e_pass.pack(fill="x", pady=(5, 20), ipady=3)  # Pack entry

        # --- BUTTONS ---
        tk.Button(content, text="LOGIN", font=("Arial", 10, "bold"), bg="#005a9e", fg="white",
                  relief="flat", cursor="hand2", pady=5,
                  command=self.submit).pack(fill="x", pady=(0, 10))  # Primary Login Button

        tk.Button(content, text="Cancel", font=("Arial", 9), bg="white", fg="#555",
                  relief="flat", cursor="hand2",
                  command=lambda: controller.show_frame("StartPage")).pack()  # Cancel Text Button

    def update_data(self):
        """Clears the entry fields every time this page is shown to ensure security."""
        self.e_email.delete(0, tk.END)  # Clear email field
        self.e_pass.delete(0, tk.END)  # Clear password field

    def submit(self):
        """
        Retrieves input, validates non-empty status, and calls controller.login().
        """
        email = self.e_email.get().strip()  # Get email input
        password = self.e_pass.get().strip()  # Get password input

        if not email or not password:  # Check if either field is empty
            messagebox.showwarning("Input Required", "Please enter both email and password.")  # Show warning
            return  # Stop execution

        if not self.controller.login(email, password):  # Call login logic; returns False if failed
            messagebox.showerror("Login Failed", "Invalid email or password.")  # Show error popup
            self.e_pass.delete(0, tk.END)  # Clear only the password field for retry


# --- STEP 3: ATTENDEE DASHBOARD ---
class AttendeeDashboard(BaseFrame):
    """
    The main menu for logged-in attendees.
    Provides central navigation to all user-specific features (Shop, Schedule, Profile).
    Updates the welcome message dynamically based on the current user.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize the BaseFrame structure
        self.configure(bg="#f0f0f0")  # Set the background color to light gray

        # --- APP TITLE ---
        tk.Label(self, text="GREENWAVE CONFERENCE 2026", font=("Helvetica", 24, "bold"), fg="#2E8B57").pack(
            pady=(60, 10))  # Display the main conference title in green

        self.lbl_user = tk.Label(self, text="Welcome, User", font=("Helvetica", 16),
                                 fg="#2E8B57")  # Create a placeholder label for the username
        self.lbl_user.pack(pady=(0, 20))  # Pack the label below the title

        # --- WINDOW CONTAINER ---
        # Slightly more compact padding for the smaller screen
        window_frame = tk.Frame(self, bg="white", bd=3,
                                relief="raised")  # Create a central white box for the menu buttons
        window_frame.pack(padx=20, pady=5)  # Pack it with padding

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Create the blue title bar
        title_bar.pack(fill="x", side="top")  # Pack it at the top
        title_bar.pack_propagate(False)  # Fix the height

        tk.Label(title_bar, text="  Dashboard Menu", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Add the title text to the bar

        # --- BUTTON AREA ---
        content_area = tk.Frame(window_frame, bg="white", padx=25, pady=25)  # Create the content area for buttons
        content_area.pack()  # Pack it inside the window frame

        # Define a dictionary for common button styling to ensure consistency and reduce code duplication
        btn_style = {
            "font": ("Arial", 10),
            "width": 22,  # Slightly smaller width to fit the grid
            "height": 2,
            "relief": "groove",
            "bg": "#f9f9f9",
            "cursor": "hand2"
        }

        # Grid Layout for Dashboard Buttons
        tk.Button(content_area, text="Purchase Pass", command=lambda: controller.show_frame("PurchasePassPage"),
                  **btn_style).grid(row=0, column=0, padx=10, pady=10)  # Button to navigate to ticket purchase
        tk.Button(content_area, text="My Schedule", command=lambda: controller.show_frame("ManageWorkshopsPage"),
                  **btn_style).grid(row=0, column=1, padx=10, pady=10)  # Button to navigate to workshop management
        tk.Button(content_area, text="Upgrade Ticket", command=lambda: controller.show_frame("UpgradeTicketPage"),
                  **btn_style).grid(row=1, column=0, padx=10, pady=10)  # Button to navigate to upgrade page
        tk.Button(content_area, text="Display Pass", command=lambda: controller.show_frame("HistoryPage"),
                  **btn_style).grid(row=1, column=1, padx=10, pady=10)  # Button to view the digital badge

        # Full width profile button spanning two columns
        tk.Button(content_area, text="Update Profile", command=lambda: controller.show_frame("UpdateProfilePage"),
                  **btn_style).grid(row=2, column=0, columnspan=2, pady=(15, 5))  # Button to edit user details

        # --- FOOTER ---
        btn_logout = tk.Button(self, text="Log Out", font=("Arial", 9), width=15,
                               bg="#e0e0e0", relief="raised",
                               command=controller.logout)  # Logout button calling controller.logout
        btn_logout.pack(side="bottom", pady=25)  # Pack at the bottom of the page

    def update_data(self):
        """
        Called every time this frame is raised to the top.
        Updates the welcome label to show the name of the currently logged-in user.
        """
        if self.controller.current_user:  # Ensure a user is actually logged in
            # UPDATED: Now says "Welcome, [Name]!"
            self.lbl_user.config(
                text=f"Welcome, {self.controller.current_user.name}!")  # Update the label text dynamically


# --- STEP 4: PURCHASE PASS ---
class PurchasePassPage(BaseFrame):
    """
    The ticket selection screen.
    Displays available ticket options (Standard vs Premium).
    Uses Radio Buttons for selecting specific exhibitions for the Standard Pass.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize BaseFrame
        self.configure(bg="#f0f0f0")  # Set background color

        # --- OUTER TITLE ---
        tk.Label(self, text="Purchase New Pass", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Main page title

        # --- THE "WINDOW" ---
        self.window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Create central window container
        self.window_frame.pack(padx=80, pady=10, fill="both", expand=True)  # Pack with padding

        # --- TITLE BAR ---
        title_bar = tk.Frame(self.window_frame, bg="#005a9e", height=30)  # Create blue title bar
        title_bar.pack(fill="x", side="top")  # Pack at top
        title_bar.pack_propagate(False)  # Fix height
        tk.Label(title_bar, text="  Select Plan", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Add title text

        # --- CONTENT AREA ---
        self.content = tk.Frame(self.window_frame, bg="white", padx=30, pady=20)  # Create content frame
        self.content.pack(fill="both", expand=True)  # Pack to fill window

        # We will populate this dynamically in update_data depending on user state
        self.dynamic_frame = tk.Frame(self.content, bg="white")  # Container for dynamic widgets
        self.dynamic_frame.pack(fill="both", expand=True)  # Pack it

        # --- FOOTER ---
        tk.Button(self.window_frame, text="Back to Dashboard", font=("Arial", 9), width=18,
                  bg="#e0e0e0", relief="raised", command=lambda: controller.show_frame("AttendeeDashboard")).pack(
            side="bottom", pady=20)  # Back button

    def update_data(self):
        """
        Determines what to show based on the user's current ticket status.
        If they have a ticket, show a warning. If not, show purchase options.
        """
        # Clear previous content
        for widget in self.dynamic_frame.winfo_children():  # Loop through existing widgets
            widget.destroy()  # Remove them to prevent duplicates

        u = self.controller.current_user  # Get current user object

        # LOGIC CHECK: Does user already have a ticket?
        if u and u.ticket:  # If ticket exists
            # --- VIEW: ALREADY HAS PASS ---
            tk.Label(self.dynamic_frame, text="⚠ Active Pass Detected", font=("Arial", 14, "bold"),
                     bg="white", fg="#d35400").pack(pady=(40, 10))  # Show warning title

            msg = f"You currently hold a '{u.ticket.ticket_type}'.\n\nTo add exhibitions or switch to All-Access,\nplease use the 'Upgrade Ticket' page."
            tk.Label(self.dynamic_frame, text=msg, font=("Arial", 11), bg="white", justify="center").pack(
                pady=10)  # Show instructions

            tk.Button(self.dynamic_frame, text="Go to Upgrade Page", font=("Arial", 10, "bold"),
                      bg="#e1e1e1", relief="raised", bd=2,
                      command=lambda: self.controller.show_frame("UpgradeTicketPage")).pack(pady=20)  # Redirect button

        else:
            # --- VIEW: SHOW PURCHASE OPTIONS ---
            self.show_purchase_options()  # Call helper to draw the pricing table

    def show_purchase_options(self):
        """Draws the Standard vs Premium comparison layout using Radio Buttons."""
        # Container for columns
        grid_frame = tk.Frame(self.dynamic_frame, bg="white")  # Frame for the grid layout
        grid_frame.pack(fill="both", expand=True)  # Pack it
        grid_frame.columnconfigure(0, weight=1)  # Make left column expand
        grid_frame.columnconfigure(1, weight=1)  # Make right column expand

        # --- OPTION 1: STANDARD (Exhibition Pass) ---
        grp_std = tk.LabelFrame(grid_frame, text=" Standard Option ", font=("Arial", 9, "bold"), bg="white", bd=1,
                                relief="solid")  # Create grouped frame for Standard option
        grp_std.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)  # Grid it on the left

        tk.Label(grp_std, text="Exhibition Pass", font=("Arial", 12, "bold"), bg="white").pack(pady=(15, 5))  # Title
        tk.Label(grp_std, text=f"AED {self.controller.config.price_exhibition}", font=("Arial", 14, "bold"), bg="white",
                 fg="green").pack()  # Dynamic price label
        tk.Label(grp_std, text="• 1 Exhibition Access\n• Workshop Booking", bg="white", justify="left").pack(
            pady=10)  # Features list

        # --- RADIO BUTTONS FOR EXHIBITION SELECTION ---
        tk.Label(grp_std, text="Select Topic:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w",
                                                                                            padx=20)  # Label
        self.var_exh = tk.StringVar()  # Variable to hold radio selection

        # Frame to hold the radio buttons cleanly
        radio_container = tk.Frame(grp_std, bg="white")  # Inner frame
        radio_container.pack(fill="x", padx=20, pady=5)  # Pack inner frame

        if self.controller.exhibitions:  # Check if exhibitions exist
            for e in self.controller.exhibitions:  # Loop through exhibitions
                # Create a Radiobutton for each exhibition
                rb = tk.Radiobutton(radio_container, text=e.name, variable=self.var_exh, value=e.name,
                                    bg="white", font=("Arial", 10), anchor="w")  # Configure Radiobutton
                rb.pack(fill="x", pady=2)  # Pack Radiobutton vertically

            # Select the first option by default to avoid empty selection
            self.var_exh.set(self.controller.exhibitions[0].name)
        else:
            tk.Label(radio_container, text="No Exhibitions Available", bg="white", fg="red").pack()  # Error msg
            self.var_exh.set("No Data")  # Set fallback

        tk.Button(grp_std, text="Select Standard", bg="#f0f0f0", relief="raised", bd=2,
                  command=self.sel_std).pack(side="bottom", fill="x", padx=20, pady=20)  # Button to select this plan

        # --- OPTION 2: PREMIUM (All-Access Pass) ---
        grp_all = tk.LabelFrame(grid_frame, text=" Premium Option ", font=("Arial", 9, "bold"), bg="white", bd=1,
                                relief="solid")  # Create grouped frame for Premium option
        grp_all.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)  # Grid it on the right

        tk.Label(grp_all, text="All-Access Pass", font=("Arial", 12, "bold"), bg="white").pack(pady=(15, 5))  # Title
        tk.Label(grp_all, text=f"AED {self.controller.config.price_all_access}", font=("Arial", 14, "bold"), bg="white",
                 fg="#d35400").pack()  # Dynamic price label
        tk.Label(grp_all, text="• All 3 Exhibitions\n• Priority Seating\n• Recordings", bg="white",
                 justify="left").pack(pady=10)  # Features list

        tk.Label(grp_all, text="(Best Value)", font=("Arial", 9, "italic"), bg="white", fg="gray").pack()  # Helper text

        tk.Button(grp_all, text="Select Premium", bg="#f0f0f0", relief="raised", bd=2,
                  command=self.sel_all).pack(side="bottom", fill="x", padx=20, pady=20)  # Button to select this plan

    def sel_std(self):
        """Prepares transaction data for Standard Pass and moves to payment."""
        val = self.var_exh.get()  # Get the selected exhibition name from RadioButton
        if not val or val == "No Data": return  # Validate selection
        self.controller.temp_transaction_data = {  # Store purchase intent in controller
            'action': 'new_ticket', 'type': "Exhibition Pass",
            'price': self.controller.config.price_exhibition, 'access': [val]
        }
        self.controller.show_frame("PaymentPage")  # Navigate to payment

    def sel_all(self):
        """Prepares transaction data for Premium Pass and moves to payment."""
        self.controller.temp_transaction_data = {  # Store purchase intent in controller
            'action': 'new_ticket', 'type': "All-Access",
            'price': self.controller.config.price_all_access,
            'access': [e.name for e in self.controller.exhibitions]  # Grant access to ALL exhibitions
        }
        self.controller.show_frame("PaymentPage")  # Navigate to payment
# --- STEP 5: PAYMENT ---
class PaymentPage(BaseFrame):
    """
    Simulates a secure payment gateway.
    Collects credit card details (validated via regex) and finalizes the transaction.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set background color

        # --- OUTER TITLE ---
        tk.Label(self, text="Secure Checkout", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Main page title

        # --- THE "WINDOW" (Main Container) ---
        # padx=100 makes the window narrow and compact
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Create central window
        window_frame.pack(padx=100, pady=10, fill="x", expand=False)  # Pack it

        # --- WINDOW TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Blue title bar
        title_bar.pack(fill="x", side="top")  # Pack at top
        title_bar.pack_propagate(False)  # Fix height
        tk.Label(title_bar, text="  Transaction Details", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Title text

        # --- CONTENT AREA ---
        content = tk.Frame(window_frame, bg="white", padx=30, pady=20)  # Content frame
        content.pack(fill="both", expand=True)  # Pack it

        # ==========================
        # SECTION 1: ORDER SUMMARY
        # ==========================
        grp_summary = tk.LabelFrame(content, text=" Order Summary ", font=("Arial", 9, "bold"),
                                    bg="white", bd=1, relief="solid")  # Create Summary Box
        grp_summary.pack(fill="x", pady=(0, 15), ipady=5)  # Pack it

        self.lbl_item = tk.Label(grp_summary, text="Item: ...", font=("Arial", 10), bg="white",
                                 anchor="w")  # Placeholder Item Label
        self.lbl_item.pack(fill="x", padx=15, pady=2)  # Pack label

        self.lbl_total = tk.Label(grp_summary, text="Total: AED 0.00", font=("Arial", 12, "bold"), bg="white",
                                  anchor="w")  # Placeholder Price Label
        self.lbl_total.pack(fill="x", padx=15, pady=5)  # Pack label

        # ==========================
        # SECTION 2: PAYMENT METHOD
        # ==========================
        grp_method = tk.LabelFrame(content, text=" Payment Method ", font=("Arial", 9, "bold"),
                                   bg="white", bd=1, relief="solid")  # Create Method Box
        grp_method.pack(fill="x", pady=(0, 15), ipady=5)  # Pack it

        self.var_method = tk.StringVar(value="Card")  # Variable for radio buttons
        tk.Radiobutton(grp_method, text="Credit/Debit Card", variable=self.var_method, value="Card", bg="white").pack(
            side="left", padx=20)  # Card Option
        tk.Radiobutton(grp_method, text="Digital Wallet", variable=self.var_method, value="Wallet", bg="white").pack(
            side="left", padx=20)  # Wallet Option

        # ==========================
        # SECTION 3: CARD DETAILS
        # ==========================
        grp_card = tk.LabelFrame(content, text=" Card Information ", font=("Arial", 9, "bold"),
                                 bg="white", bd=1, relief="solid")  # Create Card Form Box
        grp_card.pack(fill="x", ipady=5)  # Pack it

        input_frame = tk.Frame(grp_card, bg="white", padx=15, pady=5)  # Inner frame for inputs
        input_frame.pack(fill="x")  # Pack it

        # Row 1: Number
        tk.Label(input_frame, text="Card Number:", bg="white").grid(row=0, column=0, sticky="w", pady=5)  # Label
        self.e_card = tk.Entry(input_frame, width=30, bd=1, relief="solid")  # Entry for card number
        self.e_card.grid(row=0, column=1, columnspan=3, sticky="w", pady=5)  # Grid entry

        # Row 2: Exp & CVV
        tk.Label(input_frame, text="Expiry (MM/YY):", bg="white").grid(row=1, column=0, sticky="w", pady=5)  # Label
        self.e_exp = tk.Entry(input_frame, width=10, bd=1, relief="solid")  # Entry for Expiry
        self.e_exp.grid(row=1, column=1, sticky="w", pady=5)  # Grid entry

        tk.Label(input_frame, text="CVV:", bg="white").grid(row=1, column=2, sticky="e", padx=10, pady=5)  # Label
        self.e_cvv = tk.Entry(input_frame, width=5, bd=1, relief="solid")  # Entry for CVV
        self.e_cvv.grid(row=1, column=3, sticky="w", pady=5)  # Grid entry

        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(window_frame, bg="white", pady=15)  # Frame for buttons
        btn_frame.pack(side="bottom", fill="x")  # Pack it

        # Standard System Buttons
        tk.Button(btn_frame, text="Confirm Payment", font=("Arial", 10, "bold"), width=18,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.pay).pack(side="right", padx=30)  # Pay Button

        tk.Button(btn_frame, text="Cancel", font=("Arial", 10), width=10,
                  bg="#f0f0f0", relief="raised", bd=2, command=lambda: controller.show_frame("AttendeeDashboard")).pack(
            side="right", padx=5)  # Cancel Button

    def update_data(self):
        """
        Clears previous inputs and updates the transaction details.
        """
        # 1. Clear Card Fields
        self.e_card.delete(0, tk.END)
        self.e_exp.delete(0, tk.END)
        self.e_cvv.delete(0, tk.END)

        # 2. Update Summary Info
        d = self.controller.temp_transaction_data
        if d:
            item_name = d.get('type', 'Upgrade')
            if d.get('action') == 'upgrade':
                item_name = f"Upgrade to {d.get('upgrade_type').title()}"

            self.lbl_item.config(text=f"Item:  {item_name}")
            self.lbl_total.config(text=f"Total: AED {d['price']}")

    def pay(self):
        """
        Validates the credit card inputs (Length, Digits, Date Format).
        If valid, calls the controller to finalize the transaction.
        """
        # Basic validation
        if not self.e_card.get() or not self.e_cvv.get():  # Check for empty fields
            messagebox.showerror("Error", "Please fill in all card details.")  # Error popup
            return  # Stop execution
        if len(str(self.e_card.get()).replace(' ',
                                              '')) != 16 or not self.e_card.get().isdigit():  # Validate Card Length/Digits
            messagebox.showerror('Error', 'Please fill in 16 digits for card number.')  # Error popup
            return  # Stop execution
        if not str(self.e_cvv.get()).isdigit() or len(str(self.e_cvv.get()).replace(' ', '')) != 3:  # Validate CVV
            messagebox.showerror('Error', 'CVV should be 3 digits!')  # Error popup
            return  # Stop execution
        exp = self.e_exp.get().strip()  # Get Expiry Date
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", exp):  # Validate MM/YY format using Regex
            messagebox.showerror("Error", "Invalid Expiry Date.\nFormat must be MM/YY (e.g., 04/26)")  # Error popup
            return  # Stop execution

        if self.controller.process_payment():  # Execute payment logic in controller; returns True on success
            messagebox.showinfo("Approved", "Transaction Successful.\nYour pass has been updated.")  # Success popup
            self.controller.show_frame("AttendeeDashboard")  # Return to Dashboard

# --- STEP 6: WORKSHOPS ---
class ManageWorkshopsPage(BaseFrame):
    """
    The Workshop Reservation screen.
    Allows attendees to view available sessions in a table format, check real-time availability,
    and reserve or cancel their seats based on their ticket permissions.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize the BaseFrame parent structure
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set background color to light gray

        # --- OUTER TITLE ---
        # Reduced top padding to pull everything up
        tk.Label(self, text="Workshop Schedule", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(20, 5))  # Create and pack the main page title

        # --- THE "WINDOW" ---
        # expand=False prevents the white box from stretching to the very bottom
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Create main container frame
        window_frame.pack(padx=60, pady=10, fill="x", expand=False)  # Pack centrally with side padding

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Create blue header strip
        title_bar.pack(fill="x", side="top")  # Pack at the top
        title_bar.pack_propagate(False)  # Fix height to prevent shrinking
        tk.Label(title_bar, text="  My Reservations & Availability", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Add header text

        # --- CONTENT AREA ---
        # Reduced padding inside the white box
        content = tk.Frame(window_frame, bg="white", padx=20, pady=15)  # Create content container
        content.pack(fill="both", expand=True)  # Pack content

        tk.Label(content, text="Select a session to Reserve or Cancel:", font=("Arial", 10), bg="white").pack(
            anchor="w", pady=(0, 5))  # Instruction Label

        # Table Setup (Treeview)
        tree_container = tk.Frame(content, bg="white", bd=1, relief="solid")  # Bordered frame for the table
        tree_container.pack(fill="both", expand=True)  # Pack container

        scrollbar = ttk.Scrollbar(tree_container)  # Create vertical scrollbar
        scrollbar.pack(side="right", fill="y")  # Pack scrollbar to the right

        columns = ("Title", "Time", "Status")  # Define table column headers
        # Reduced height to 8 rows to save vertical space
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                                 yscrollcommand=scrollbar.set, selectmode="browse", height=8)  # Create Treeview widget

        # Configure Styles for the table
        style = ttk.Style()  # Get style object
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))  # Bold headers
        style.configure("Treeview", font=("Arial", 9), rowheight=25)  # Set row height

        # Column Config
        self.tree.heading("Title", text="Workshop Title", anchor="w")  # Set Title header text
        self.tree.heading("Time", text="Time", anchor="center")  # Set Time header text
        self.tree.heading("Status", text="Availability", anchor="center")  # Set Status header text

        self.tree.column("Title", width=350, anchor="w")  # Set Title column width
        self.tree.column("Time", width=100, anchor="center")  # Set Time column width
        self.tree.column("Status", width=120, anchor="center")  # Set Status column width

        self.tree.pack(side="left", fill="both", expand=True)  # Pack table into frame
        scrollbar.config(command=self.tree.yview)  # Link scrollbar to table

        # --- FOOTER BUTTONS ---
        # Reduced padding in the button frame
        btn_frame = tk.Frame(window_frame, bg="white", pady=10)  # Footer button frame
        btn_frame.pack(side="bottom", fill="x")  # Pack footer

        # Action Buttons
        tk.Button(btn_frame, text="Reserve Seat", font=("Arial", 9, "bold"), width=15,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.reserve).pack(side="left", padx=20)  # Reserve Button

        tk.Button(btn_frame, text="Cancel Seat", font=("Arial", 9, "bold"), width=15,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.cancel_reservation).pack(side="left", padx=5)  # Cancel Button

        # Back
        tk.Button(btn_frame, text="Back to Dashboard", font=("Arial", 9), width=18,
                  bg="#f0f0f0", relief="raised", bd=2, command=lambda: controller.show_frame("AttendeeDashboard")).pack(
            side="right", padx=20)  # Back Button

    def update_data(self):
        """
        Refreshes the workshop list by checking ticket permissions and real-time availability.
        """
        for i in self.tree.get_children(): self.tree.delete(i)  # Clear existing table rows

        u = self.controller.current_user  # Get current user
        if not u or not u.ticket: return  # If no user/ticket, do nothing

        for w in self.controller.workshops:  # Iterate through all workshops
            booked = any(r.w_id == w.w_id for r in u.reservations)  # Check if user booked this specific workshop

            # Status Text Logic
            if booked:  # If user has booked this
                status = "✅ RESERVED"  # Set status text for reserved items
            elif w.is_full():  # If capacity is reached
                status = "FULL"  # Set status text to Full
            else:  # If open slots exist
                status = f"{w.booked}/{w.capacity} Open"  # Show availability count

            # Show if allowed (or if booked, so they can see it to cancel)
            if w.exhibition_name in u.ticket.exhibitions_allowed or booked:  # Check permission based on ticket
                self.tree.insert("", "end", values=(w.title, w.time, status), tags=(str(w.w_id),))  # Insert row

    def reserve(self):
        """Handles the logic when 'Reserve Seat' is clicked."""
        sel = self.tree.selection()  # Get the selected row ID
        if not sel: return  # Do nothing if nothing selected
        w_id = int(self.tree.item(sel[0])['tags'][0])  # Retrieve workshop ID from tags
        res = self.controller.reserve_workshop(w_id)  # Call controller to attempt reservation
        if res == "Success":  # If reservation worked
            messagebox.showinfo("Success", "Workshop reserved.")  # Show success message
            self.update_data()  # Refresh table to show new status
        else:
            messagebox.showerror("Error", res)  # Show specific error message (e.g., "Full")

    def cancel_reservation(self):
        """Handles the logic when 'Cancel Seat' is clicked."""
        sel = self.tree.selection()  # Get selected row
        if not sel: return  # Do nothing if empty selection
        w_id = int(self.tree.item(sel[0])['tags'][0])  # Retrieve workshop ID

        # Confirm
        if messagebox.askyesno("Cancel", "Cancel this reservation?"):  # Ask for user confirmation
            if self.controller.cancel_workshop(w_id):  # Call cancellation method (Assumed existing in Logic)
                messagebox.showinfo("Success", "Reservation cancelled.")  # Success message
                self.update_data()  # Refresh table
            else:
                messagebox.showerror("Error", "You have not reserved this workshop.")  # Error message


# --- STEP 7A: UPGRADE TICKET ---
class UpgradeTicketPage(BaseFrame):
    """
    Allows users to upgrade their existing pass to All-Access.
    It calculates the price difference and initiates the payment flow.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set background

        # --- OUTER TITLE ---
        tk.Label(self, text="Membership Management", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(40, 10))  # Page Title

        # --- THE "WINDOW" (Main Container) ---
        # CHANGED: Increased padx to 100 to make the box narrower (smaller)
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Central window frame
        window_frame.pack(padx=100, pady=10, fill="x", expand=False)  # Pack centrally

        # --- WINDOW TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Blue Header
        title_bar.pack(fill="x", side="top")  # Pack at top
        title_bar.pack_propagate(False)  # Fix height
        tk.Label(title_bar, text="  Upgrade Options", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Header text

        # --- CONTENT AREA ---
        # Reduced padding slightly for a tighter feel
        content = tk.Frame(window_frame, bg="white", padx=20, pady=20)  # Content area
        content.pack(fill="both", expand=True)  # Pack content

        # 1. Current Status Section
        tk.Label(content, text="Current Pass Status:", font=("Arial", 10, "bold"),
                 bg="white", fg="#555").pack(anchor="w")  # Status Label

        self.lbl_current = tk.Label(content, text="Loading...", font=("Arial", 12, "bold"),
                                    bg="white", fg="#333", justify="left")  # Dynamic Status Text
        self.lbl_current.pack(anchor="w", pady=(5, 15), padx=10)  # Pack Status Text

        # Divider Line
        tk.Frame(content, height=2, bd=1, relief="sunken").pack(fill="x", pady=5)  # Visual Separator

        # 2. Upgrade Offer Section
        self.offer_frame = tk.Frame(content, bg="white")  # Frame for upgrade offer details
        self.offer_frame.pack(fill="both", expand=True)  # Pack offer frame

        self.lbl_offer = tk.Label(self.offer_frame, text="", font=("Arial", 11),
                                  bg="white", justify="left")  # Label for upgrade description
        self.lbl_offer.pack(anchor="w", pady=10)  # Pack label

        self.btn_upgrade = tk.Button(self.offer_frame, text="Upgrade to All-Access", font=("Arial", 10, "bold"),
                                      width=25,
                                     command=self.do_upgrade)  # Action button for upgrade

        # --- FOOTER (Back Button) ---
        tk.Button(self, text="Back to Dashboard", font=("Arial", 10), width=18,
                  bg="#e0e0e0", relief="raised", command=lambda: controller.show_frame("AttendeeDashboard")).pack(
            side="bottom", pady=30)  # Back button

        self.upgrade_cost = 0  # Initialize cost variable

    def update_data(self):
        """
        Calculates upgrade eligibility and cost difference.
        """
        # Reset View
        self.btn_upgrade.pack_forget()  # Hide button by default

        u = self.controller.current_user  # Get current user
        if not u or not u.ticket:  # Check if ticket exists
            self.lbl_current.config(text="No active pass found.", fg="red")  # Show error
            self.lbl_offer.config(text="Please purchase a pass first.")  # Show instruction
            return  # Stop

        t = u.ticket  # Get ticket object

        # Display Current
        status_text = f"• Type: {t.ticket_type}\n• Access: {len(t.exhibitions_allowed)} Exhibition(s)"  # Format status
        self.lbl_current.config(text=status_text, fg="#333")  # Update label

        # Logic
        if t.ticket_type == "All-Access":  # Check if already maxed out
            self.lbl_offer.config(text="You already have the VIP All-Access Pass.\nNo further upgrades available.")  # Info message
        else:
            # Calculate Price Diff
            self.upgrade_cost = self.controller.config.price_all_access - t.price  # Calculate cost difference

            offer_text = (f"Upgrade Available: All-Access Pass\n"
                          f"Cost: AED {self.upgrade_cost}\n\n"
                          f"Benefits:\n"
                          f"- Access to ALL 3 Exhibitions\n"
                          f"- Priority Seating\n"
                          f"- Session Recordings")  # Format offer text
            self.lbl_offer.config(text=offer_text)  # Update label
            self.btn_upgrade.pack(pady=10)  # Reveal upgrade button

    def do_upgrade(self):
        """Prepares payment data for the upgrade transaction."""
        self.controller.temp_transaction_data = {  # Set transaction context
            'action': 'upgrade',  # Action type
            'upgrade_type': 'all_access',  # Target Type
            'price': self.upgrade_cost,  # Cost
            'new_exh': None  # No single exhibition added
        }
        self.controller.show_frame("PaymentPage")  # Proceed to payment


# --- STEP 7B: HISTORY ---
class HistoryPage(BaseFrame):
    """
    Displays the user's digital pass details.
    Acts as a confirmation document showing Ticket ID, Type, Date, and allowed Exhibitions.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set Background

        # --- OUTER TITLE ---
        tk.Label(self, text="My Digital Pass", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Title

        # --- THE "WINDOW" (Main Container) ---
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=100, pady=10, fill="both", expand=True)  # Pack Window

        # --- WINDOW TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Title Bar
        title_bar.pack(fill="x", side="top")  # Pack Title Bar
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Official Pass Document", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Title Text

        # --- CONTENT AREA ---
        content = tk.Frame(window_frame, bg="white", padx=20, pady=20)  # Content Frame
        content.pack(fill="both", expand=True)  # Pack Content

        # ==========================
        # SECTION 1: PASS DETAILS
        # ==========================
        grp_details = tk.LabelFrame(content, text=" Pass Information ", font=("Arial", 9, "bold"),
                                    bg="white", bd=1, relief="solid")  # Details Group
        grp_details.pack(fill="x", pady=(0, 15), ipady=5)  # Pack Group

        # Grid for details
        f_det = tk.Frame(grp_details, bg="white", padx=10)  # Inner Grid Frame
        f_det.pack(fill="x")  # Pack Frame

        # Row 1
        tk.Label(f_det, text="HOLDER:", font=("Arial", 9, "bold"), bg="white", fg="#555").grid(row=0, column=0,
                                                                                               sticky="w")  # Label
        self.lbl_holder = tk.Label(f_det, text="...", font=("Arial", 11), bg="white")  # Value Label
        self.lbl_holder.grid(row=0, column=1, sticky="w", padx=10)  # Value Grid

        tk.Label(f_det, text="PASS ID:", font=("Arial", 9, "bold"), bg="white", fg="#555").grid(row=0, column=2,
                                                                                                sticky="w",
                                                                                                padx=(20, 0))  # Label
        self.lbl_id = tk.Label(f_det, text="...", font=("Arial", 11), bg="white")  # Value Label
        self.lbl_id.grid(row=0, column=3, sticky="w", padx=10)  # Value Grid

        # Row 2
        tk.Label(f_det, text="TYPE:", font=("Arial", 9, "bold"), bg="white", fg="#555").grid(row=1, column=0,
                                                                                             sticky="w", pady=5)  # Label
        self.lbl_type = tk.Label(f_det, text="...", font=("Arial", 11, "bold"), bg="white", fg="#005a9e")  # Value
        self.lbl_type.grid(row=1, column=1, sticky="w", padx=10, pady=5)  # Value Grid

        tk.Label(f_det, text="DATE:", font=("Arial", 9, "bold"), bg="white", fg="#555").grid(row=1, column=2,
                                                                                             sticky="w", padx=(20, 0),
                                                                                             pady=5)  # Label
        self.lbl_date = tk.Label(f_det, text="...", font=("Arial", 11), bg="white")  # Value Label
        self.lbl_date.grid(row=1, column=3, sticky="w", padx=10, pady=5)  # Value Grid

        # ==========================
        # SECTION 2: ACCESS SCOPE
        # ==========================
        grp_access = tk.LabelFrame(content, text=" Access Scope ", font=("Arial", 9, "bold"),
                                   bg="white", bd=1, relief="solid")  # Access Group
        grp_access.pack(fill="both", expand=True, ipady=5)  # Pack Group

        # Two columns for lists
        f_lists = tk.Frame(grp_access, bg="white", padx=10)  # Inner Frame
        f_lists.pack(fill="both", expand=True)  # Pack Frame
        f_lists.columnconfigure(0, weight=1)  # Expand Col 0
        f_lists.columnconfigure(1, weight=1)  # Expand Col 1

        # Col 1: Exhibitions
        tk.Label(f_lists, text="Included Exhibitions:", font=("Arial", 9, "bold"), bg="white", fg="#333").grid(row=0,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               pady=(5,
                                                                                                                     0))  # Header
        self.lbl_exh = tk.Label(f_lists, text="...", font=("Arial", 10), bg="white", justify="left", fg="#555")  # List Label
        self.lbl_exh.grid(row=1, column=0, sticky="nw", pady=2)  # Grid Label

        # Col 2: Workshops
        tk.Label(f_lists, text="Reserved Workshops:", font=("Arial", 9, "bold"), bg="white", fg="#333").grid(row=0,
                                                                                                             column=1,
                                                                                                             sticky="w",
                                                                                                             pady=(5,
                                                                                                                   0))  # Header
        self.lbl_ws = tk.Label(f_lists, text="...", font=("Arial", 10), bg="white", justify="left", fg="#555")  # List Label
        self.lbl_ws.grid(row=1, column=1, sticky="nw", pady=2)  # Grid Label

        # ==========================
        # SECTION 3: VALIDITY (Footer)
        # ==========================
        f_valid = tk.Frame(content, bg="#f9f9f9", bd=1, relief="sunken", padx=10, pady=5)  # Validity Bar
        f_valid.pack(fill="x", pady=(15, 0))  # Pack Bar

        valid_text = "VALIDITY: April 15–18, 2026  •  9:00 AM – 6:00 PM daily"  # Text
        tk.Label(f_valid, text=valid_text, font=("Arial", 9), bg="#f9f9f9", fg="#555").pack()  # Label

        # --- FOOTER BUTTON ---
        tk.Button(self, text="Back to Dashboard", font=("Arial", 10), width=18,
                  bg="#e0e0e0", relief="raised", command=lambda: controller.show_frame("AttendeeDashboard")).pack(
            side="bottom", pady=20)  # Back Button

    def update_data(self):
        """
        Populates the pass details based on the current user's ticket.
        """
        u = self.controller.current_user  # Get current user
        if not u or not u.ticket:  # Check if ticket exists
            self.lbl_holder.config(text=u.name if u else "Guest")  # Set Name
            self.lbl_id.config(text="---")  # Reset ID
            self.lbl_type.config(text="NO ACTIVE PASS", fg="red")  # Reset Type
            self.lbl_date.config(text="---")  # Reset Date
            self.lbl_exh.config(text="(None)")  # Reset Exhibitions
            self.lbl_ws.config(text="(None)")  # Reset Workshops
            return  # Stop

        t = u.ticket  # Get Ticket

        # Details
        self.lbl_holder.config(text=u.name)  # Set Name
        self.lbl_id.config(text=t.ticket_id)  # Set Ticket ID
        self.lbl_type.config(text=t.ticket_type, fg="#2E8B57" if "Exhibition" in t.ticket_type else "#d35400")  # Set Type
        self.lbl_date.config(text=str(t.purchase_date))  # Set Purchase Date

        # Exhibitions List
        exh_list = "\n".join([f"• {e}" for e in t.exhibitions_allowed])  # Create bulleted list
        self.lbl_exh.config(text=exh_list)  # Set Text

        # Workshops List
        if u.reservations:  # Check reservations
            ws_list = "\n".join([f"• {r.title}" for r in u.reservations])  # Create bulleted list
        else:
            ws_list = "(No reservations)"  # Fallback text
        self.lbl_ws.config(text=ws_list)  # Set Text


# --- STEP 7C: UPDATE PROFILE ---
class UpdateProfilePage(BaseFrame):
    """
    Form for updating account details.
    Allows changing Name, Phone, and Password with validation logic.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set Background

        # --- OUTER TITLE ---
        tk.Label(self, text="Account Settings", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Page Title

        # --- THE "WINDOW" ---
        # padx=100 keeps it compact and centered
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=100, pady=10, fill="x", expand=False)  # Pack Window

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Title Bar
        title_bar.pack(fill="x", side="top")  # Pack Title Bar
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Edit Profile Information", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Title Text

        # --- FORM CONTENT ---
        content = tk.Frame(window_frame, bg="white", padx=30, pady=20)  # Content Frame
        content.pack(fill="both", expand=True)  # Pack Content

        # Helper to create rows
        def create_row(label_text, row_idx, is_pass=False):
            tk.Label(content, text=label_text, font=("Arial", 10), bg="white", anchor="w").grid(row=row_idx, column=0,
                                                                                                sticky="w", pady=10)  # Label
            entry = tk.Entry(content, font=("Arial", 10), width=30, bd=1, relief="solid", show="*" if is_pass else "")  # Entry
            entry.grid(row=row_idx, column=1, padx=20, pady=10)  # Grid Entry
            return entry  # Return Entry object

        self.e_name = create_row("Full Name:", 0)  # Create Name Input
        self.e_phone = create_row("Phone Number:", 1)  # Create Phone Input

        # Divider
        tk.Frame(content, height=1, bg="#ccc").grid(row=2, column=0, columnspan=2, sticky="ew", pady=15)  # Visual Line

        self.e_pass = create_row("New Password:", 3, True)  # Create Password Input
        self.e_conf = create_row("Confirm Password:", 4, True)  # Create Confirm Input

        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(window_frame, bg="white", pady=15)  # Footer Frame
        btn_frame.pack(side="bottom", fill="x")  # Pack Footer

        tk.Button(btn_frame, text="Save Changes", font=("Arial", 10, "bold"), width=15,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.update).pack(side="right", padx=30)  # Save Button

        tk.Button(btn_frame, text="Cancel", font=("Arial", 10), width=10,
                  bg="#f0f0f0", relief="raised", bd=2, command=lambda: controller.show_frame("AttendeeDashboard")).pack(
            side="right", padx=5)  # Cancel Button

    def update_data(self):
        """
        Prefills the input fields with the current user's existing data.
        """
        u = self.controller.current_user  # Get User
        if u:
            self.e_name.delete(0, tk.END);
            self.e_name.insert(0, u.name)  # Insert Name
            self.e_phone.delete(0, tk.END);
            self.e_phone.insert(0, u.phone)  # Insert Phone
            self.e_pass.delete(0, tk.END)  # Clear Password
            self.e_conf.delete(0, tk.END)  # Clear Confirm

    def update(self):
        """
        Validates new profile inputs and saves changes to the database.
        """
        # 1. Get Values
        new_name = self.e_name.get().strip()  # Get Input
        new_phone = self.e_phone.get().strip()  # Get Input
        new_pass = self.e_pass.get()  # Get Input
        conf_pass = self.e_conf.get()  # Get Input

        # 2. Validation: Empty Check
        if not new_name or not new_phone:  # Check Mandatory Fields
            messagebox.showerror("Error", "Name and Phone cannot be empty.")  # Error
            return  # Stop

        # 3. Validation: Phone Digits
        if not (new_phone.isdigit() and len(new_phone) >= 8):  # Check Phone Format
            messagebox.showerror("Error", "Phone must be valid digits.")  # Error
            return  # Stop

        # 4. Validation: Passwords
        if new_pass and (new_pass != conf_pass):  # Check Password Match
            messagebox.showerror("Error", "New passwords do not match.")  # Error
            return  # Stop

        # 5. Save Changes
        u = self.controller.current_user  # Get Current User Object
        u.name = new_name  # Update Name
        u.phone = new_phone  # Update Phone
        if new_pass:  # Only update password if user entered a new one
            u.password = new_pass  # Update Password

        self.controller.dm.save("attendees", self.controller.attendees)  # Save to File
        messagebox.showinfo("Success", "Profile Updated Successfully.")  # Success

# =============================================================================
#                               ADMIN PAGES
# =============================================================================

class AdminDashboard(BaseFrame):
    """
    The central hub for Administrators.
    Displays Key Performance Indicators (KPIs) like total sales and revenue.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Initialize BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set background color

        # --- OUTER TITLE ---
        tk.Label(self, text="Administrator Panel", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Main Title

        # --- THE "WINDOW" (Main Container) ---
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Create main container
        window_frame.pack(padx=80, pady=10, fill="both", expand=True)  # Pack centrally

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Create blue header
        title_bar.pack(fill="x", side="top")  # Pack at top
        title_bar.pack_propagate(False)  # Fix height
        tk.Label(title_bar, text="  Management Menu", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Title Text

        # --- CONTENT AREA ---
        content = tk.Frame(window_frame, bg="white", padx=30, pady=20)  # Content area
        content.pack(fill="both", expand=True)  # Pack content

        # ==========================
        # BOX 1: QUICK STATS (No Colors)
        # ==========================
        grp_stats = tk.LabelFrame(content, text=" System Status ", font=("Arial", 9, "bold"),
                                  bg="white", bd=1, relief="solid")  # Statistics Group Frame
        grp_stats.pack(fill="x", pady=(0, 20), ipady=10)  # Pack Group

        # Grid for stats
        stat_frame = tk.Frame(grp_stats, bg="white")  # Inner Frame for grid
        stat_frame.pack(fill="x", padx=10)  # Pack Inner Frame
        stat_frame.columnconfigure(0, weight=1)  # Expand Col 0
        stat_frame.columnconfigure(1, weight=1)  # Expand Col 1
        stat_frame.columnconfigure(2, weight=1)  # Expand Col 2

        # Stat 1
        tk.Label(stat_frame, text="Tickets Sold:", font=("Arial", 9), bg="white").grid(row=0, column=0)  # Label
        self.lbl_sold = tk.Label(stat_frame, text="0", font=("Arial", 11, "bold"), bg="white", fg="#333")  # Value
        self.lbl_sold.grid(row=1, column=0)  # Grid Value

        # Stat 2
        tk.Label(stat_frame, text="Total Revenue:", font=("Arial", 9), bg="white").grid(row=0, column=1)  # Label
        self.lbl_rev = tk.Label(stat_frame, text="AED 0", font=("Arial", 11, "bold"), bg="white", fg="#333")  # Value
        self.lbl_rev.grid(row=1, column=1)  # Grid Value

        # Stat 3
        tk.Label(stat_frame, text="Workshop Load:", font=("Arial", 9), bg="white").grid(row=0, column=2)  # Label
        self.lbl_cap = tk.Label(stat_frame, text="0%", font=("Arial", 11, "bold"), bg="white", fg="#333")  # Value
        self.lbl_cap.grid(row=1, column=2)  # Grid Value

        # ==========================
        # BOX 2: ACTIONS
        # ==========================
        grp_tools = tk.LabelFrame(content, text=" Tasks ", font=("Arial", 9, "bold"),
                                  bg="white", bd=1, relief="solid")  # Management Tools Group
        grp_tools.pack(fill="both", expand=True, ipady=10)  # Pack Group

        # Button Style (Standard Gray)
        btn_style = {
            "font": ("Arial", 10),
            "width": 25,
            "height": 2,
            "relief": "groove",
            "bg": "#f9f9f9"
        }  # Style Dictionary

        # Row 1
        tk.Button(grp_tools, text="Sales Reports", command=lambda: controller.show_frame("AdminSalesPage"),
                  **btn_style).grid(row=0, column=0, padx=20, pady=15)  # Button
        tk.Button(grp_tools, text="Manage Pricing", command=lambda: controller.show_frame("AdminPricingPage"),
                  **btn_style).grid(row=0, column=1, padx=20, pady=15)  # Button

        # Row 2
        tk.Button(grp_tools, text="Manage Exhibitions", command=lambda: controller.show_frame("AdminExhibitionsPage"),
                  **btn_style).grid(row=1, column=0, padx=20, pady=15)  # Button
        tk.Button(grp_tools, text="Manage Workshops", command=lambda: controller.show_frame("AdminWorkshopsPage"),
                  **btn_style).grid(row=1, column=1, padx=20, pady=15)  # Button

        # Row 3 (Full Width)
        tk.Button(grp_tools, text="Upgrade User Ticket", command=lambda: controller.show_frame("AdminUserUpgradePage"),
                  **btn_style).grid(row=2, column=0, columnspan=2, pady=10)  # Button

        # --- FOOTER ---
        # Placed inside the window frame for a cleaner look
        tk.Button(window_frame, text="Log Out", font=("Arial", 9), width=15, bg="#e0e0e0", relief="raised",
                  command=controller.logout).pack(side="bottom", pady=20)  # Button

    def update_data(self):
        """
        Refreshes the dashboard statistics (Sales, Revenue) in real-time.
        """
        # Calculate Stats
        attendees = self.controller.attendees  # Get list of all users
        sold = sum(1 for a in attendees if a.ticket)  # Count users who have a ticket
        revenue = sum(a.ticket.price for a in attendees if a.ticket)  # Sum the price of all sold tickets

        total_cap = sum(w.capacity for w in self.controller.workshops)  # Calculate total workshop seats available
        total_booked = sum(w.booked for w in self.controller.workshops)  # Calculate total seats currently taken
        avg_load = int((total_booked / total_cap) * 100) if total_cap > 0 else 0  # Calculate percentage load

        self.lbl_sold.config(text=str(sold))  # Update Sales Label
        self.lbl_rev.config(text=f"AED {revenue}")  # Update Revenue Label
        self.lbl_cap.config(text=f"{avg_load}%")  # Update Load Label

class AdminSalesPage(BaseFrame):
    """
    Generates text-based sales reports filtered by date.
    Displays a detailed log of transactions for accounting purposes.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        self.configure(bg="#f0f0f0")  # Set background

        # --- TITLE ---
        tk.Label(self, text="Sales Report Generator", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Page Title

        # --- WINDOW FRAME ---
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=50, pady=10, fill="both", expand=True)  # Pack Window

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Header
        title_bar.pack(fill="x", side="top")  # Pack Header
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Daily Report", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Header Text

        # --- CONTENT ---
        content = tk.Frame(window_frame, bg="white", padx=20, pady=20)  # Content Frame
        content.pack(fill="both", expand=True)  # Pack Content

        # Controls (Top)
        control_frame = tk.Frame(content, bg="white")  # Control bar for inputs
        control_frame.pack(fill="x", pady=(0, 15))  # Pack Controls

        tk.Label(control_frame, text="Date (YYYY-MM-DD):", font=("Arial", 10), bg="white").pack(side="left")  # Input Label

        self.e_date = tk.Entry(control_frame, font=("Arial", 10), width=15, bd=1, relief="solid")  # Date Entry
        self.e_date.insert(0, str(datetime.date.today()))  # Default to Today's date
        self.e_date.pack(side="left", padx=10)  # Pack Entry

        tk.Button(control_frame, text="Generate", font=("Arial", 9, "bold"), width=12,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.gen).pack(side="left")  # Generate Button

        # Report View (Text Box)
        # Using Courier font to make the text align like a table
        self.txt_report = tk.Text(content, font=("Courier", 10), bg="#f9f9f9", fg="#333",
                                  bd=1, relief="solid", height=15)  # Multi-line Text Widget
        self.txt_report.pack(fill="both", expand=True)  # Pack Text Widget

        # --- FOOTER (Back Button) ---
        tk.Button(self, text="Back to Dashboard", font=("Arial", 10), width=18,
                  bg="#e0e0e0", relief="raised", command=lambda: controller.show_frame("AdminDashboard")).pack(
            side="bottom", pady=30)  # Back Button

    def gen(self):
        """
        Filters attendees by the selected purchase date and generates a formatted text report.
        """
        date_str = self.e_date.get().strip()  # Get Date Input

        # 1. Validate Date Format (YYYY-MM-DD)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):  # Regex check for date format
            messagebox.showerror("Format Error", "Invalid Date Format.\nPlease use YYYY-MM-DD (e.g., 2026-04-15).")  # Error Popup
            return  # Stop

        # 2. Filter Logic
        sold = [a for a in self.controller.attendees if a.ticket and str(a.ticket.purchase_date) == date_str]  # Filter List

        self.txt_report.delete("1.0", tk.END)  # Clear previous report

        if not sold:  # If list is empty
            self.txt_report.insert(tk.END, f"\n   NO RECORDS FOUND FOR DATE: {date_str}\n")  # Show 'No Data' message
            return  # Stop

        # Stats Calculation
        rev = sum(a.ticket.price for a in sold)  # Sum revenue
        count_exh = sum(1 for a in sold if a.ticket.ticket_type == "Exhibition Pass")  # Count standard tickets
        count_all = sum(1 for a in sold if a.ticket.ticket_type == "All-Access")  # Count premium tickets

        # Layout Construction
        sep = "=" * 60  # Separator line
        thin = "-" * 60  # Thin separator line


        report = (
            f"{sep}\n"
            f" GREENWAVE CONFERENCE - DAILY SALES REPORT\n"
            f" Date: {date_str}\n"
            f"{sep}\n\n"
            f" SUMMARY:\n"
            f" {thin}\n"
            f" Total Transactions   : {len(sold)}\n"
            f" Total Revenue        : AED {rev}\n"
            f" Exhibition Passes    : {count_exh}\n"
            f" All-Access Passes    : {count_all}\n"
            f" {thin}\n\n"
            f" LOG:\n"
            f" {thin}\n"
            f" {'TICKET ID':<20} | {'TYPE':<15} | {'PRICE'}\n"
            f" {thin}\n"
        )  # Build the header string

        for a in sold:  # Loop through sold tickets
            t_type = "Exhibition" if a.ticket.ticket_type == "Exhibition Pass" else "All-Access"  # Shorten type name
            report += f" {a.ticket.ticket_id:<20} | {t_type:<15} | AED {a.ticket.price}\n"  # Append row

        report += f" {thin}\n"  # Append footer line

        self.txt_report.insert(tk.END, report)  # Insert generated text into the widget

    def update_data(self):
        """Resets date to today and clears previous reports."""
        self.e_date.delete(0, tk.END)
        self.e_date.insert(0, str(datetime.date.today()))
        self.txt_report.delete("1.0", tk.END)


class AdminPricingPage(BaseFrame):
    """
    Form to update global ticket prices.
    Changes made here update the 'Config' object and persist to 'config.pkl'.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        # 1. Desktop Background
        self.configure(bg="#f0f0f0")  # Set background

        # --- OUTER TITLE ---
        tk.Label(self, text="Pricing Configuration", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Page Title

        # --- WINDOW FRAME ---
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=80, pady=10, fill="both", expand=True)  # Pack Window

        # --- TITLE BAR ---
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Header Bar
        title_bar.pack(fill="x", side="top")  # Pack Header
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Set Ticket Costs", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Header Text

        # --- CONTENT ---
        content = tk.Frame(window_frame, bg="white", padx=30, pady=20)  # Content Frame
        content.pack(fill="both", expand=True)  # Pack Content

        # Grid Layout for 2 Columns
        content.columnconfigure(0, weight=1)  # Expand left col
        content.columnconfigure(1, weight=1)  # Expand right col

        # --- BOX 1: STANDARD PASS ---
        grp_std = tk.LabelFrame(content, text=" Exhibition Pass ", font=("Arial", 9, "bold"),
                                bg="white", bd=1, relief="solid")  # Group for Standard
        grp_std.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)  # Grid it

        tk.Label(grp_std, text="Current Price:", font=("Arial", 9), bg="white", fg="#555").pack(pady=(15, 5))  # Label
        self.lbl_cur_exh = tk.Label(grp_std, text="AED 0.00", font=("Arial", 14, "bold"), bg="white", fg="#333")  # Value Label
        self.lbl_cur_exh.pack(pady=5)  # Pack Value

        tk.Label(grp_std, text="New Price:", font=("Arial", 9, "bold"), bg="white").pack(pady=(15, 5))  # Input Label
        self.e_exh = tk.Entry(grp_std, font=("Arial", 11), width=10, bd=1, relief="solid", justify="center")  # Entry Field
        self.e_exh.pack(pady=5)  # Pack Entry

        # --- BOX 2: PREMIUM PASS ---
        grp_prem = tk.LabelFrame(content, text=" All-Access Pass ", font=("Arial", 9, "bold"),
                                 bg="white", bd=1, relief="solid")  # Group for Premium
        grp_prem.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)  # Grid it

        tk.Label(grp_prem, text="Current Price:", font=("Arial", 9), bg="white", fg="#555").pack(pady=(15, 5))  # Label
        self.lbl_cur_all = tk.Label(grp_prem, text="AED 0.00", font=("Arial", 14, "bold"), bg="white", fg="#333")  # Value Label
        self.lbl_cur_all.pack(pady=5)  # Pack Value

        tk.Label(grp_prem, text="New Price:", font=("Arial", 9, "bold"), bg="white").pack(pady=(15, 5))  # Input Label
        self.e_all = tk.Entry(grp_prem, font=("Arial", 11), width=10, bd=1, relief="solid", justify="center")  # Entry Field
        self.e_all.pack(pady=5)  # Pack Entry

        # --- FOOTER BUTTONS ---
        btn_frame = tk.Frame(window_frame, bg="white", pady=15)  # Footer Frame
        btn_frame.pack(side="bottom", fill="x")  # Pack Footer

        tk.Button(btn_frame, text="Update Prices", font=("Arial", 10, "bold"), width=15,
                  bg="#e1e1e1", relief="raised", bd=2, command=self.upd).pack(side="right", padx=30)  # Update Button

        tk.Button(btn_frame, text="Cancel", font=("Arial", 10), width=10,
                  bg="#f0f0f0", relief="raised", bd=2, command=lambda: controller.show_frame("AdminDashboard")).pack(
            side="right", padx=5)  # Cancel Button

    def update_data(self):
        """
        Fetches current prices from config and updates the display labels.
        """
        c = self.controller.config  # Get config object
        self.lbl_cur_exh.config(text=f"AED {c.price_exhibition}")  # Update standard label
        self.lbl_cur_all.config(text=f"AED {c.price_all_access}")  # Update premium label
        self.e_exh.delete(0, tk.END)  # Clear input
        self.e_all.delete(0, tk.END)  # Clear input

    def upd(self):
        """
        Validates inputs and updates the configuration object.
        """
        c = self.controller.config  # Get config object
        changed = False  # Track if any change happened

        try:
            # Check Exhibition Price Input
            if self.e_exh.get():  # If input not empty
                new_price = float(self.e_exh.get())  # Convert to float
                if new_price < 0:  # Check non-negative
                    messagebox.showerror("Error", "Price cannot be negative.")  # Error
                    return  # Stop
                c.price_exhibition = new_price  # Update config
                changed = True  # Set flag

            # Check All-Access Price Input
            if self.e_all.get():  # If input not empty
                new_price = float(self.e_all.get())  # Convert to float
                if new_price < 0:  # Check non-negative
                    messagebox.showerror("Error", "Price cannot be negative.")  # Error
                    return  # Stop
                c.price_all_access = new_price  # Update config
                changed = True  # Set flag

            # Save if changes were made
            if changed:  # If anything changed
                self.controller.dm.save("config", c)  # Save to file
                messagebox.showinfo("Success", "Prices Updated Successfully")  # Success
                self.update_data()  # Refresh UI
            else:
                messagebox.showwarning("Warning", "No changes entered.")  # Warning

        except ValueError:
            messagebox.showerror("Error", "Prices must be valid numbers.")  # Error


class AdminExhibitionsPage(BaseFrame):
    """
    Manager for Exhibition Topics.
    Allows adding new topics and removing existing ones (with safety checks).
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        self.configure(bg="#f0f0f0")  # Set background

        tk.Label(self, text="Exhibition Manager", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Title

        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=50, pady=10, fill="both", expand=True)  # Pack Window

        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Header
        title_bar.pack(fill="x", side="top")  # Pack Header
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Manage Event Topics", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Header Text

        content = tk.Frame(window_frame, bg="white", padx=20, pady=20)  # Content Frame
        content.pack(fill="both", expand=True)  # Pack Content

        # --- LEFT: LIST BOX ---
        left_frame = tk.LabelFrame(content, text=" Current Exhibitions ", font=("Arial", 9, "bold"), bg="white")  # Left Group
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))  # Pack Left Group

        self.lst = tk.Listbox(left_frame, font=("Arial", 10), bd=1, relief="solid", height=12)  # Listbox Widget
        self.lst.pack(fill="both", expand=True, padx=10, pady=10)  # Pack Listbox

        tk.Button(left_frame, text="Remove Selected", bg="#f0f0f0", relief="raised", bd=2,
                  command=self.rem).pack(fill="x", padx=10, pady=10)  # Remove Button

        # --- RIGHT: ADD FORM ---
        right_frame = tk.LabelFrame(content, text=" Add New ", font=("Arial", 9, "bold"), bg="white")  # Right Group
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))  # Pack Right Group

        f_inputs = tk.Frame(right_frame, bg="white", padx=10, pady=10)  # Input Frame
        f_inputs.pack(fill="x")  # Pack Input Frame

        tk.Label(f_inputs, text="Name:", bg="white", anchor="w").pack(fill="x")  # Label
        self.e_name = tk.Entry(f_inputs, bd=1, relief="solid")  # Entry
        self.e_name.pack(fill="x", pady=(5, 15))  # Pack Entry

        tk.Label(f_inputs, text="Description:", bg="white", anchor="w").pack(fill="x")  # Label
        self.e_desc = tk.Entry(f_inputs, bd=1, relief="solid")  # Entry
        self.e_desc.pack(fill="x", pady=(5, 15))  # Pack Entry

        tk.Button(f_inputs, text="Add Record", bg="#e1e1e1", relief="raised", bd=2,
                  command=self.add).pack(fill="x", pady=10)  # Add Button

        # --- FOOTER ---
        tk.Button(window_frame, text="Back to Dashboard", font=("Arial", 9), width=18,
                  bg="#e0e0e0", relief="raised", command=lambda: controller.show_frame("AdminDashboard")).pack(side="bottom", pady=20)  # Back Button

    def update_data(self):
        """Refreshes list and clears input fields."""
        # 1. Refresh List
        self.lst.delete(0, tk.END)
        for e in self.controller.exhibitions:
            self.lst.insert(tk.END, f" {e.name}")

        # 2. Clear Inputs
        self.e_name.delete(0, tk.END)
        self.e_desc.delete(0, tk.END)

    def add(self):
        """
        Adds a new exhibition to the system.
        """
        n, d = self.e_name.get().strip(), self.e_desc.get().strip()  # Get Inputs
        if n and d:  # Check valid
            self.controller.exhibitions.append(Exhibition(n, d))  # Create object
            self.controller.dm.save("exhibitions", self.controller.exhibitions)  # Save
            self.update_data()  # Refresh
            self.e_name.delete(0, tk.END)  # Clear field
            self.e_desc.delete(0, tk.END)  # Clear field
        else:
            messagebox.showwarning("Error", "Missing fields")  # Error

    def rem(self):
        """
        Removes the selected exhibition, but blocks deletion if tickets are using it.
        """
        sel = self.lst.curselection()  # Get selected index
        if not sel:  # Check selection
            messagebox.showwarning("Selection Error", "Please select an exhibition to remove.")  # Warning
            return  # Stop

        index = sel[0]  # Get index
        name = self.controller.exhibitions[index].name  # Get name

        # --- SAFETY CHECK ---
        # Check if any user holds a ticket for this exhibition
        for user in self.controller.attendees:  # Loop users
            if user.ticket and name in user.ticket.exhibitions_allowed:  # Check usage
                messagebox.showerror("Action Denied",
                                     f"Cannot delete '{name}'.\n\nIt is currently active on user tickets.\nYou must refund or upgrade those users first.")  # Error
                return  # Stop
        # --------------------

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{name}'?"):  # Confirm
            self.controller.exhibitions.pop(index)  # Remove
            self.controller.dm.save("exhibitions", self.controller.exhibitions)  # Save
            self.update_data()  # Refresh


class AdminWorkshopsPage(BaseFrame):
    """
    Manager for Workshop Sessions.
    Allows creating new sessions linked to exhibitions and removing existing ones.
    Includes a critical UI fix for packing order to ensure buttons remain visible.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        self.configure(bg="#f0f0f0")  # Set background

        # --- OUTER TITLE ---
        tk.Label(self, text="Workshop Manager", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(20, 10))  # Title

        # --- THE "WINDOW" ---
        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=80, pady=10, fill="both", expand=True)  # Pack Window

        # ==========================================
        # CRITICAL FIX: PACKING ORDER
        # We pack Top and Bottom elements FIRST so they never disappear.
        # ==========================================

        # 1. WINDOW TITLE BAR (Top)
        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Header
        title_bar.pack(side="top", fill="x")  # Pack Header at Top
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Schedule Sessions", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Title Text

        # 2. FOOTER / BACK BUTTON (Bottom)
        # Packed immediately so it sticks to the bottom of the white box
        footer = tk.Frame(window_frame, bg="white", pady=15)  # Footer Frame
        footer.pack(side="bottom", fill="x")  # Pack Footer at Bottom

        tk.Button(footer, text="Back to Dashboard", width=18, bg="#e0e0e0", relief="raised",
                  command=lambda: controller.show_frame("AdminDashboard")).pack()  # Back Button

        # 3. CONTENT AREA (Middle)
        # fill="both", expand=True makes this take up whatever space is left
        content = tk.Frame(window_frame, bg="white", padx=30, pady=10)  # Content Frame
        content.pack(side="top", fill="both", expand=True)  # Pack Content in remaining space

        # ==========================
        # SECTION 1: LIST (Scrollable)
        # ==========================
        tk.Label(content, text="Current Schedule:", font=("Arial", 9, "bold"), bg="white").pack(anchor="w")  # Label

        list_frame = tk.Frame(content, bd=1, relief="solid")  # List Frame
        list_frame.pack(fill="both", expand=True, pady=5)  # Pack List Frame

        scrollbar = tk.Scrollbar(list_frame)  # Scrollbar
        scrollbar.pack(side="right", fill="y")  # Pack Scrollbar

        self.lst = tk.Listbox(list_frame, font=("Courier", 10),
                              yscrollcommand=scrollbar.set, activestyle="none")  # Listbox
        self.lst.pack(side="left", fill="both", expand=True)  # Pack Listbox
        scrollbar.config(command=self.lst.yview)  # Link Scrollbar

        tk.Button(content, text="Delete Selected", bg="#e1e1e1", relief="raised", bd=2,
                  command=self.rem).pack(anchor="e", pady=5)  # Delete Button

        # ==========================
        # SECTION 2: ADD NEW (Compact)
        # ==========================
        grp_add = tk.LabelFrame(content, text=" Add New Session ", font=("Arial", 9, "bold"),
                                bg="white", bd=1, relief="solid")  # Add Group
        grp_add.pack(fill="x", pady=10, ipady=5)  # Pack Group

        # Helper for compact rows
        def row(parent, label, r):
            tk.Label(parent, text=label, bg="white", anchor="w").grid(row=r, column=0, sticky="w", padx=10, pady=2)  # Label
            e = tk.Entry(parent, width=25, bd=1, relief="solid")  # Entry
            e.grid(row=r, column=1, padx=10, pady=2)  # Grid Entry
            return e  # Return Entry

        f_in = tk.Frame(grp_add, bg="white")  # Input Frame
        f_in.pack(fill="x", pady=5)  # Pack Input Frame

        self.e_t = row(f_in, "Title:", 0)  # Title Input
        self.e_ti = row(f_in, "Time:", 1)  # Time Input
        self.e_c = row(f_in, "Cap:", 2)  # Capacity Input

        # Exhibition Dropdown
        tk.Label(f_in, text="Link:", bg="white", anchor="w").grid(row=3, column=0, sticky="w", padx=10, pady=2)  # Label
        self.exh_var = tk.StringVar()  # Variable
        self.opt = tk.OptionMenu(f_in, self.exh_var, "")  # Dropdown
        self.opt.config(bg="white", width=20, bd=1, relief="solid")  # Config
        self.opt.grid(row=3, column=1, padx=10, pady=2)  # Grid Dropdown

        # Add Button (Right side of the form)
        tk.Button(f_in, text="Add +", bg="#e1e1e1", relief="raised", bd=2, width=10, height=4,
                  command=self.add).grid(row=0, column=2, rowspan=4, padx=20)  # Add Button

    def update_data(self):
        """Refreshes list, dropdowns, and clears inputs."""
        # 1. Refresh List
        self.lst.delete(0, tk.END)
        for w in self.controller.workshops:
            item = f"{w.title} ({w.time}) - {w.capacity} seats"
            self.lst.insert(tk.END, item)

        # 2. Refresh Dropdown
        menu = self.opt["menu"]
        menu.delete(0, "end")
        exhibitions = self.controller.exhibitions
        if exhibitions:
            for e in exhibitions:
                menu.add_command(label=e.name, command=tk._setit(self.exh_var, e.name))
            if not self.exh_var.get(): self.exh_var.set(exhibitions[0].name)
        else:
            self.exh_var.set("No Exhibitions")

        # 3. Clear Inputs
        self.e_t.delete(0, tk.END)
        self.e_ti.delete(0, tk.END)
        self.e_c.delete(0, tk.END)

    def add(self):
        """
        Creates a new workshop and saves it.
        """
        try:
            t, ti, cap = self.e_t.get(), self.e_ti.get(), self.e_c.get()  # Get Inputs
            if t and ti and cap:  # Check valid
                wid = len(self.controller.workshops) + 101  # Generate ID
                w = Workshop(wid, t, ti, int(cap), self.exh_var.get())  # Create Object
                self.controller.workshops.append(w)  # Add to list
                self.controller.dm.save("workshops", self.controller.workshops)  # Save
                self.update_data()  # Refresh
                self.e_t.delete(0, tk.END);  # Clear Field
                self.e_ti.delete(0, tk.END);  # Clear Field
                self.e_c.delete(0, tk.END)  # Clear Field
            else:
                messagebox.showwarning("Error", "Missing Fields")  # Error
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a number")  # Error

    def rem(self):
        """
        Removes a workshop, blocking deletion if bookings exist.
        """
        sel = self.lst.curselection()  # Get selection
        if not sel:  # Check selection
            messagebox.showwarning("Selection Error", "Please select a workshop to remove.")  # Warning
            return  # Stop

        wid_index = sel[0]  # Get index
        # Safety Check: Does anyone have this booked?
        if wid_index < len(self.controller.workshops):  # Check bounds
            target_w = self.controller.workshops[wid_index]  # Get object

            # Check usage
            active_users = 0  # Counter
            for u in self.controller.attendees:  # Loop users
                for r in u.reservations:  # Loop reservations
                    if r.w_id == target_w.w_id:  # Check ID
                        active_users += 1  # Increment

            if active_users > 0:  # If used
                messagebox.showerror("Action Denied", f"Cannot delete.\n{active_users} user(s) have booked this.")  # Error
                return  # Stop

            if messagebox.askyesno("Confirm", "Delete this workshop?"):  # Confirm
                self.controller.workshops.pop(wid_index)  # Remove
                self.controller.dm.save("workshops", self.controller.workshops)  # Save
                self.update_data()  # Refresh


class AdminUserUpgradePage(BaseFrame):
    """
    Administrator tool to search for a user by email and manually apply a VIP upgrade.
    Useful for customer support or complimentary upgrades.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)  # Init BaseFrame
        self.configure(bg="#f0f0f0")  # Set background

        tk.Label(self, text="Comp Upgrade Tool", font=("Arial", 20, "bold"),
                 bg="#f0f0f0", fg="#444").pack(pady=(30, 10))  # Title

        window_frame = tk.Frame(self, bg="white", bd=3, relief="raised")  # Window Frame
        window_frame.pack(padx=80, pady=10, fill="both", expand=True)  # Pack Window

        title_bar = tk.Frame(window_frame, bg="#005a9e", height=30)  # Header
        title_bar.pack(fill="x", side="top")  # Pack Header
        title_bar.pack_propagate(False)  # Fix Height
        tk.Label(title_bar, text="  Search & Modify User", font=("Arial", 10, "bold"),
                 bg="#005a9e", fg="white").pack(side="left", pady=5)  # Header Text

        content = tk.Frame(window_frame, bg="white", padx=30, pady=20)  # Content Frame
        content.pack(fill="both", expand=True)  # Pack Content

        # --- SEARCH BOX ---
        grp_search = tk.LabelFrame(content, text=" Search Attendee ", font=("Arial", 9, "bold"),
                                   bg="white")  # Search Group
        grp_search.pack(fill="x", pady=(0, 20), ipady=5)  # Pack Group

        f_s = tk.Frame(grp_search, bg="white", padx=10, pady=10)  # Inner Frame
        f_s.pack(fill="x")  # Pack Inner Frame

        tk.Label(f_s, text="Email Address:", bg="white").pack(side="left")  # Label
        self.e_mail = tk.Entry(f_s, width=30, bd=1, relief="solid")  # Entry
        self.e_mail.pack(side="left", padx=10)  # Pack Entry
        tk.Button(f_s, text="Find", bg="#e1e1e1", width=8, relief="raised", bd=2, command=self.search).pack(
            side="left")  # Find Button

        # --- RESULT BOX ---
        self.grp_result = tk.LabelFrame(content, text=" Search Result ", font=("Arial", 9, "bold"),
                                        bg="white")  # Result Group
        self.grp_result.pack(fill="both", expand=True, ipady=10)  # Pack Group

        # We use a frame inside to hold dynamic content
        self.res_content = tk.Frame(self.grp_result, bg="white")  # Dynamic Content Frame
        self.res_content.pack(fill="both", expand=True, padx=20, pady=10)  # Pack Content Frame

        self.lbl_info = tk.Label(self.res_content, text="Enter an email above to search.", bg="white",
                                 fg="#555")  # Info Label
        self.lbl_info.pack()  # Pack Label

        self.btn_upgrade = tk.Button(self.res_content, text="Apply All-Access Upgrade",
                                     bg="#e1e1e1", relief="raised", bd=2, command=self.upg)  # Upgrade Button

        # --- FOOTER ---
        tk.Button(window_frame, text="Back to Dashboard", font=("Arial", 9), width=18,
                  bg="#e0e0e0", relief="raised", command=lambda: controller.show_frame("AdminDashboard")).pack(
            side="bottom", pady=20)  # Back Button

        self.target_user = None  # Init Target

    def search(self):
        """
        Finds a user by email and displays their current ticket status.
        """
        self.btn_upgrade.pack_forget()  # Hide button
        email = self.e_mail.get()  # Get email
        self.target_user = next((u for u in self.controller.attendees if u.email == email), None)  # Search user

        if not self.target_user:  # Check found
            self.lbl_info.config(text="User not found.")  # Update text
            return  # Stop

        # Show info
        t_status = "No Ticket"  # Default status
        if self.target_user.ticket:  # Check ticket
            t_status = self.target_user.ticket.ticket_type  # Get type

        info = f"Name: {self.target_user.name}\nEmail: {self.target_user.email}\nCurrent Pass: {t_status}"  # Format info
        self.lbl_info.config(text=info)  # Update label

        # Show Upgrade button only if they have a ticket and it's not VIP
        if self.target_user.ticket and self.target_user.ticket.ticket_type != "All-Access":  # Check eligibility
            self.btn_upgrade.pack(pady=15)  # Show button
        elif self.target_user.ticket:  # Check VIP
            self.lbl_info.config(text=info + "\n\n(Already All-Access)")  # Update text

    def upg(self):
        """
        Applies the All-Access upgrade to the found user.
        """
        if self.target_user and self.target_user.ticket:  # Validate
            self.target_user.ticket.ticket_type = "All-Access"  # Change type
            # Grant full access
            self.target_user.ticket.exhibitions_allowed = [e.name for e in self.controller.exhibitions]  # Update scope

            self.controller.dm.save("attendees", self.controller.attendees)  # Save
            messagebox.showinfo("Success", "User upgraded successfully.")  # Success
            self.search()  # Refresh

    def update_data(self):
        """Resets the search form when the page is opened."""
        self.e_mail.delete(0, tk.END)
        self.lbl_info.config(text="Enter an email above to search.")
        self.btn_upgrade.pack_forget()
        self.target_user = None


