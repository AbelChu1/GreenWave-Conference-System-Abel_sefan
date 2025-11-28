# GreenWave-Conference-System-Abel_Sefan_Muath
Programming Final Assignment by Abel Chuchu M80009115, Sefan Herpassa M80009123, and Muath Alshehhi 202214858

A comprehensive ticketing and session management system for the GreenWave Sustainability Conference.

## Project Overview
This application allows attendees to purchase tickets, manage workshop schedules, and view their digital passes. It includes a full Administrator Dashboard for managing sales, pricing, and event capacity.

## Key Features
* **MVC Architecture:** Code is organized into Model, View, and Controller for clean separation of concerns.
* **Role-Based Access:** Distinct interfaces for Attendees and Administrators.
* **Data Persistence:** Uses `pickle` to save users, tickets, and workshops locally.
* **Security:** Input validation (Regex) and secure login handling.

## How to Run
1.  Download all files in this repository.
2.  Run the application entry point:
    ```bash
    python main.py
    ```

## Credentials
* **Admin:** Username: `admin` | Password: `admin123`
* **User:** Register a new account or use existing data.
  - e.g: **email:** aaaa@aaaa.com **Password:** aaaa@aaaa.com 

## Files
* `model.py`: Data classes (Person, Ticket, Workshop)
* `view.py`: GUI Classes (Tkinter Frames)
* `controller.py`: Business logic and navigation
* `main.py`: Launcher script
