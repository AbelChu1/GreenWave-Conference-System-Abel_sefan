import tkinter as tk
from tkinter import messagebox, ttk
import pickle
import os
import datetime

# =============================================================================
#                                   MODEL
# =============================================================================

class Config:
    """
    Stores global configuration settings for the application.
    This class acts as a central repository for constants such as ticket prices.
    Using a class for this allows prices to be modified dynamically during runtime without hardcoding.
    """

    def __init__(self):
        self.price_exhibition = 200  # Set the default price for a standard exhibition-only ticket
        self.price_all_access = 500  # Set the default price for a premium all-access ticket
        self.upgrade_add_exh_cost = 150  # Set the cost to add a single extra exhibition to a standard ticket

    # Getters and Setters
    def get_price_exhibition(self): return self.price_exhibition  # Retrieve the current price for exhibition tickets

    def set_price_exhibition(self,
                             price): self.price_exhibition = price  # Update the exhibition ticket price with a new value

    def get_price_all_access(self): return self.price_all_access  # Retrieve the current price for all-access tickets

    def set_price_all_access(self,
                             price): self.price_all_access = price  # Update the all-access ticket price with a new value


class Exhibition:
    """
    Represents a major event category or topic within the conference.
    This object holds the name and description of the event, serving as a parent category for workshops.
    """

    def __init__(self, name, description):
        self.name = name  # Assign the display name of the exhibition category
        self.description = description  # Assign the descriptive text explaining the exhibition topic

    # Getters and Setters
    def get_name(self): return self.name  # Retrieve the name of the exhibition

    def set_name(self, name): self.name = name  # Modify the name of the exhibition

    def get_description(self): return self.description  # Retrieve the description text

    def set_description(self, desc): self.description = desc  # Modify the description text


class Workshop:
    """
    Represents a specific scheduled session that attendees can book.
    This class manages the session details and tracks the current booking count against the maximum capacity.
    """

    def __init__(self, w_id, title, time, capacity, exhibition_name):
        self.w_id = w_id  # Assign a unique integer ID to identify this specific workshop session
        self.title = title  # Assign the title of the workshop session
        self.time = time  # Assign the scheduled time string (e.g., "10:30 AM")
        self.capacity = capacity  # Define the maximum number of attendees allowed in this session
        self.booked = 0  # Initialize the count of booked seats to zero as the session starts empty
        self.exhibition_name = exhibition_name  # Link this workshop to a parent exhibition by name

    def is_full(self):
        return self.booked >= self.capacity  # Return True if the booked seats equal or exceed the limit, preventing overbooking

    # Getters and Setters
    def get_id(self): return self.w_id  # Retrieve the workshop's unique identifier

    def get_title(self): return self.title  # Retrieve the workshop title

    def set_title(self, title): self.title = title  # Update the workshop title

    def get_capacity(self): return self.capacity  # Retrieve the maximum capacity

    def set_capacity(self, cap): self.capacity = cap  # Update the maximum capacity limit

    def get_booked(self): return self.booked  # Retrieve the current number of reservations

    def set_booked(self, count): self.booked = count  # Manually set the booking count (used for data correction)


class Ticket:
    """
    Represents a purchased entry pass held by an attendee.
    This class generates a unique ID upon creation and tracks which exhibitions the user is permitted to enter.
    """

    def __init__(self, ticket_type, price, exhibitions_allowed):
        self.ticket_type = ticket_type  # Store the type of ticket (e.g., "Exhibition Pass" or "All-Access")
        self.price = price  # Store the specific amount paid for this ticket
        self.exhibitions_allowed = exhibitions_allowed  # Store the list of exhibition names this ticket grants access to

        # ID Generation
        code = "ALL" if ticket_type == "All-Access" else "EXH"  # distinct prefix code based on the ticket type
        timestamp = int(
            datetime.datetime.now().timestamp() % 10000)  # Generate a short unique number from the current timestamp
        self.ticket_id = f"GW-{code}-{timestamp:04d}"  # Construct the final unique Ticket ID string
        self.purchase_date = datetime.date.today()  # Record the current date as the official purchase date

    # Getters and Setters
    def get_ticket_type(self): return self.ticket_type  # Retrieve the ticket type string

    def set_ticket_type(self, type): self.ticket_type = type  # Update the ticket type (e.g., during an upgrade)

    def get_price(self): return self.price  # Retrieve the price paid

    def set_price(self, price): self.price = price  # Update the price value

    def get_exhibitions(self): return self.exhibitions_allowed  # Retrieve the list of accessible exhibitions

    def set_exhibitions(self,
                        exhibitions): self.exhibitions_allowed = exhibitions  # Update the list of accessible exhibitions


class Person:
    """
    Defines the base attributes for any user in the system.
    This is a parent class that holds common credentials like name, email, and password.
    """

    def __init__(self, name, email, password):
        self.name = name  # Assign the full name of the user
        self.email = email  # Assign the email address, which acts as the unique username
        self.password = password  # Assign the user's login password

    # Getters and Setters
    def get_name(self): return self.name  # Retrieve the user's name

    def set_name(self, name): self.name = name  # Update the user's name

    def get_email(self): return self.email  # Retrieve the user's email

    def set_email(self, email): self.email = email  # Update the user's email

    def get_password(self): return self.password  # Retrieve the user's password

    def set_password(self, pwd): self.password = pwd  # Update the user's password


class Attendee(Person):
    """
    Represents a standard conference participant.
    Inherits from Person and adds fields for ticket management and workshop reservations.
    """

    def __init__(self, name, email, password, phone):
        super().__init__(name, email, password)  # Initialize the parent Person class with basic credentials
        self.phone = phone  # Store the attendee's contact phone number
        self.ticket = None  # Initialize the ticket slot as None (attendee starts without a pass)
        self.reservations = []  # Initialize an empty list to track future workshop bookings

    # Getters and Setters
    def get_phone(self): return self.phone  # Retrieve the phone number

    def set_phone(self, phone): self.phone = phone  # Update the phone number

    def get_ticket(self): return self.ticket  # Retrieve the Ticket object associated with this user

    def set_ticket(self, ticket): self.ticket = ticket  # Assign a purchased Ticket object to this user

    def get_reservations(self): return self.reservations  # Retrieve the list of workshop reservations

    def add_reservation(self, workshop): self.reservations.append(
        workshop)  # Add a specific workshop to the reservations list


class Admin(Person):
    """
    Represents a System Administrator with privileged access.
    This class is instantiated when specific admin credentials are used during login.
    """

    def __init__(self):
        super().__init__("Administrator", "admin", "admin123")  # Initialize with hardcoded Admin credentials


class DataManager:
    """
    Manages the persistence of application data to the local file system.
    This class uses the pickle library to save and load objects, ensuring data is not lost when the app closes.
    """

    def __init__(self):
        self.files = {
            "attendees": "attendees.pkl",  # Map the logical key 'attendees' to its physical filename
            "workshops": "workshops.pkl",  # Map the logical key 'workshops' to its physical filename
            "exhibitions": "exhibitions.pkl",  # Map the logical key 'exhibitions' to its physical filename
            "config": "config.pkl"  # Map the logical key 'config' to its physical filename
        }

    def save(self, key, data):
        try:
            with open(self.files[key], 'wb') as f:  # Open the file corresponding to the key in write-binary mode
                pickle.dump(data, f)  # Serialize and write the data object to the file
        except Exception as e:
            print(f"Save error ({key}): {e}")  # Catch and log any file writing errors to the console

    def load(self, key, default):
        if not os.path.exists(self.files[key]):  # Check if the data file exists on the disk
            return default  # Return the default empty value if the file is missing (first run)
        try:
            with open(self.files[key], 'rb') as f:  # Open the data file in read-binary mode
                return pickle.load(f)  # Deserialize the file content back into a Python object
        except Exception as e:
            print(f"Load error ({key}): {e}")  # Catch and log any file reading errors
            return default  # Return the default value if the file is corrupt to prevent crashing