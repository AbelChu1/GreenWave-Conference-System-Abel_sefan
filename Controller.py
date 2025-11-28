import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import os
import datetime
from view import StartPage, RegisterPage, LoginPage, AttendeeDashboard,PurchasePassPage, PaymentPage, ManageWorkshopsPage, HistoryPage,UpdateProfilePage, UpgradeTicketPage,AdminDashboard, AdminSalesPage, AdminPricingPage,AdminExhibitionsPage, AdminWorkshopsPage, AdminUserUpgradePage
from Model import Workshop, DataManager, Exhibition, Admin, Attendee,Ticket, Config

# =============================================================================
#                                 CONTROLLER
# =============================================================================

class GreenWaveApp(tk.Tk):
    """
    The main application class that manages the window, data, and navigation.
    This class acts as the 'Controller' in the MVC architecture, coordinating
    interaction between the Data Model and the View (GUI pages).
    """

    def __init__(self):
        super().__init__()  # Initialize the parent Tkinter window class
        self.title("GreenWave Conference 2026")  # Set the main window title text
        self.geometry("800x600")  # Set the default dimensions of the application window

        self.dm = DataManager()  # Create an instance of DataManager to handle file I/O operations

        # Load Data
        self.config = self.dm.load("config", Config())  # Load global settings or create a new Config object if missing
        self.exhibitions = self.dm.load("exhibitions", [])  # Load the list of exhibitions or start with an empty list
        self.workshops = self.dm.load("workshops", [])  # Load the list of workshops or start with an empty list
        self.attendees = self.dm.load("attendees",
                                      [])  # Load the list of registered attendees or start with an empty list

        # --- DATA REPAIR (Fixes your crash) ---
        # Checks if loaded exhibitions are missing 'description' (from old save)
        if self.exhibitions and (
        not hasattr(self.exhibitions[0], 'description')):  # Detect if data structure is outdated
            print("Detected old data format. Resetting Exhibitions to defaults...")  # Log a warning to the console
            self.create_defaults()  # Reset the exhibition data to default values to prevent errors
        elif not self.exhibitions:  # Check if the exhibition list is completely empty (first run)
            self.create_defaults()  # Populate the system with initial default data

        self.current_user = None  # Initialize the current user session as None (logged out state)
        self.temp_transaction_data = {}  # Initialize a dictionary to temporarily store payment details during checkout

        # GUI Container
        self.container = tk.Frame(self)  # Create a main frame to act as a container for all page views
        self.container.pack(side="top", fill="both", expand=True)  # Pack the container to fill the entire window area
        self.container.grid_rowconfigure(0, weight=1)  # Configure the grid system to expand vertically
        self.container.grid_columnconfigure(0, weight=1)  # Configure the grid system to expand horizontally

        self.frames = {}  # Initialize a dictionary to store references to all page instances
        self.register_frames()  # Call the helper method to instantiate and stack all GUI pages
        self.show_frame("StartPage")  # Display the initial Start Page to the user

    def register_frames(self):
        """
        Instantiates all UI page classes and stores them in the frames dictionary.
        This sets up the navigation stack so pages can be brought to the front instantly.
        """
        # List of all page classes
        pages = (StartPage, RegisterPage, LoginPage, AttendeeDashboard,
                 PurchasePassPage, PaymentPage, ManageWorkshopsPage, HistoryPage,
                 UpdateProfilePage, UpgradeTicketPage,
                 AdminDashboard, AdminSalesPage, AdminPricingPage,
                 AdminExhibitionsPage, AdminWorkshopsPage, AdminUserUpgradePage)  # Tuple containing all View classes

        for F in pages:  # Iterate through every page class in the tuple
            page_name = F.__name__  # Extract the class name string (e.g., "StartPage")
            frame = F(parent=self.container, controller=self)  # Create an instance of the page, passing the controller
            self.frames[page_name] = frame  # Store the created instance in the dictionary using its name as the key
            frame.grid(row=0, column=0,
                       sticky="nsew")  # Place the frame in the grid; all frames stack on top of each other

    def create_defaults(self):
        """
        Populates the application with initial seed data.
        This is run only if the data files are missing or corrupted.
        """
        # Default Exhibitions
        self.exhibitions = [  # Define a list of hardcoded Exhibition objects for the initial setup
            Exhibition("Climate Tech Innovations",
                       "Workshops: Intro to Data (10:30), Renewable Energy (12:30), Smart Agri (14:30)"),
            Exhibition("Green Policy & Governance",
                       "Workshops: Policy Sim (09:30), Reporting 101 (12:00), Corp Strategy (14:00)"),
            Exhibition("Community Action & Impact",
                       "Workshops: Low-Carbon (12:30), Waste Reduction (14:00), Circular Econ (15:30)")
        ]
        # Default Workshops
        self.workshops = [  # Define a list of hardcoded Workshop objects linked to the exhibitions
            Workshop(101, "Intro to Climate Data Tools", "10:30 AM", 50, "Climate Tech Innovations"),
            Workshop(102, "Renewable Energy Systems", "12:30 PM", 50, "Climate Tech Innovations"),
            Workshop(201, "Policy Simulation Lab", "09:30 AM", 50, "Green Policy & Governance"),
            Workshop(301, "Building Low-Carbon Communities", "12:30 PM", 50, "Community Action & Impact"),
            Workshop(302, "Circular Economy", "03:30 PM", 50, "Community Action & Impact")
        ]
        self.dm.save("exhibitions", self.exhibitions)  # Save the newly created exhibition list to disk
        self.dm.save("workshops", self.workshops)  # Save the newly created workshop list to disk

    def show_frame(self, page_name):
        """
        Navigates to a specific page by bringing its frame to the top of the stack.
        Also calls the page's update_data() method if it exists to refresh content.
        """
        frame = self.frames[page_name]  # Retrieve the requested page instance from the frames dictionary
        frame.tkraise()  # Raise the selected frame to the top of the visual stack (making it visible)
        if hasattr(frame, "update_data"):  # Check if the page class has an 'update_data' method defined
            frame.update_data()  # Call the method to refresh dynamic data (like username or ticket status)

    # --- LOGIC ---
    def register_user(self, name, email, password, phone):
        """
        Registers a new attendee in the system.
        Returns True if successful, or False if the email is already taken.
        """
        # LOGIC FIX: Normalize email to lowercase
        email_clean = email.strip().lower()  # Remove whitespace and convert email to lowercase for consistent comparisons

        if any(u.email == email_clean for u in
               self.attendees):  # Iterate through attendees to check for duplicate email
            return False  # Return False to indicate registration failure due to duplicate email

        self.attendees.append(
            Attendee(name, email_clean, password, phone))  # Create a new Attendee object and add to list
        self.dm.save("attendees", self.attendees)  # Save the updated list of attendees to the file system
        return True  # Return True to indicate successful registration

    def login(self, email, password):
        """
        Authenticates a user against the stored records.
        Supports both Admin (hardcoded) and standard Attendee logins.
        """
        # LOGIC FIX: Normalize email to lowercase
        email_clean = email.strip().lower()  # Clean the input email for consistent matching

        # Admin check (hardcoded)
        if email_clean == "admin" and password == "admin123":  # specific check for the hardcoded admin credentials
            self.current_user = Admin()  # Instantiate an Admin object and set it as the current user
            self.show_frame("AdminDashboard")  # Navigate the user to the Admin Dashboard
            return True  # Return True to indicate successful login

        for u in self.attendees:  # Iterate through the list of registered attendees
            if u.email == email_clean and u.password == password:  # Check if the email and password match a record
                self.current_user = u  # Set the matched attendee object as the current session user
                self.show_frame("AttendeeDashboard")  # Navigate the user to the Attendee Dashboard
                return True  # Return True to indicate successful login
        return False  # Return False if no matching credentials were found

    def logout(self):
        """
        Ends the current user session and returns to the start screen.
        """
        self.current_user = None  # Clear the current user variable to end the session
        messagebox.showinfo("Logout", "Logged out successfully.")  # Display a popup message confirming logout
        self.show_frame("StartPage")  # Navigate back to the main Start Page

    def process_payment(self):
        """
        Finalizes a transaction based on data in 'temp_transaction_data'.
        Handles both creating new tickets and upgrading existing ones.
        """
        # Apply the transaction stored in temp_transaction_data
        data = self.temp_transaction_data  # Retrieve the temporary payment details set by the purchase page
        user = self.current_user  # Get the currently logged-in user object

        if data['action'] == 'new_ticket':  # Check if the transaction is for buying a fresh ticket
            user.ticket = Ticket(data['type'], data['price'],
                                 data['access'])  # Create a new Ticket object and assign it

        elif data['action'] == 'upgrade':  # Check if the transaction is for upgrading an existing ticket
            # Update existing ticket
            if data['upgrade_type'] == 'all_access':  # If upgrading to the premium All-Access tier
                user.ticket.ticket_type = "All-Access"  # Update the ticket type string description
                # Add all exhibitions that aren't already there
                all_names = [e.name for e in self.exhibitions]  # Generate a list of all exhibition names in the system
                user.ticket.exhibitions_allowed = all_names  # Grant access to all exhibitions
            elif data['upgrade_type'] == 'add_exh':  # If upgrading by adding a single exhibition
                user.ticket.exhibitions_allowed.append(data['new_exh'])  # Append the new exhibition name to the list

            # Update price paid tracker if needed (simplification: just updating object)
            user.ticket.price += data['price']  # Add the upgrade cost to the total price tracked on the ticket

        self.dm.save("attendees", self.attendees)  # Save the updated user (and their ticket) to the file system
        return True  # Return True to indicate the payment logic completed successfully

    def reserve_workshop(self, w_id):
        """
        Attempts to reserve a workshop seat for the current user.
        Performs validation checks for existence, capacity, duplication, and ticket scope.
        """
        ws = next((w for w in self.workshops if w.w_id == w_id), None)  # Search for the workshop object by its ID
        u = self.current_user  # Get the currently logged-in user

        if not ws or not u.ticket: return "Error"  # Fail if workshop doesn't exist or user has no ticket
        if ws.is_full(): return "Workshop Full"  # Fail if the workshop has reached maximum capacity
        if any(r.w_id == w_id for r in u.reservations): return "Already Booked"  # Fail if user already reserved this
        if ws.exhibition_name not in u.ticket.exhibitions_allowed: return "Invalid Pass Scope"  # Fail if ticket doesn't cover this topic

        ws.booked += 1  # Increment the booking counter on the workshop object
        u.reservations.append(ws)  # Add the workshop object to the user's list of reservations
        self.dm.save("workshops", self.workshops)  # Save the updated workshop data (booking count)
        self.dm.save("attendees", self.attendees)  # Save the updated attendee data (reservation list)
        return "Success"  # Return success string

    def cancel_workshop(self, w_id):
        """
        Cancels a user's reservation for a specific workshop.
        Restores the workshop capacity by decrementing the 'booked' count.
        """
        u = self.current_user  # Get current logged-in user
        ws = next((w for w in self.workshops if w.w_id == w_id), None)  # Find the workshop object by ID

        # Safety Check: Ensure workshop and user exist
        if not ws or not u:
            return False

        # Find the specific reservation in the user's list
        found_index = -1
        for i, res in enumerate(u.reservations):
            if res.w_id == w_id:
                found_index = i
                break

        # If reservation found, remove it
        if found_index != -1:
            u.reservations.pop(found_index)  # Remove from User's reservation list
            ws.booked -= 1  # Decrease the 'booked' count on the Workshop object

            # Save the changes to files immediately
            self.dm.save("workshops", self.workshops)
            self.dm.save("attendees", self.attendees)
            return True  # Return success

        return False  # Return failure (reservation not found)
