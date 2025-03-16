import sqlite3

# Database Initialization
def initialize_db():
    conn = sqlite3.connect("parking_system.db",timeout=5)
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    # Create Vehicles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_type TEXT NOT NULL,
        plate_number TEXT UNIQUE NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        fare REAL
    )""")
    conn.commit()
    conn.close()

# User Login Verification
def verify_user(username, password):
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Add New User for Signup
def add_user(username, password):
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Username already exists

# Add Vehicle Entry
def add_vehicle(vehicle_type, plate_number, entry_time):
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vehicles (vehicle_type, plate_number, entry_time) VALUES (?, ?, ?)", 
                   (vehicle_type, plate_number, entry_time))
    conn.commit()
    conn.close()

# Get Entry Time for a Vehicle
def get_entry_time(plate_number):
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT entry_time FROM vehicles WHERE plate_number = ? AND exit_time IS NULL", (plate_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Exit Vehicle and Calculate Fare
def exit_vehicle(plate_number, exit_time, fare):
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE vehicles SET exit_time = ?, fare = ? WHERE plate_number = ?", (exit_time, round(fare), plate_number))
    conn.commit()
    conn.close()

# Delete Vehicle
def delete_vehicle(plate_number):
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE plate_number = ?", (plate_number,))
    conn.commit()
    conn.close()

# Get All Vehicles
def get_all_vehicles():
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    conn.close()
    return vehicles

def reset_ids():
    conn = sqlite3.connect("parking_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='vehicles'")
    conn.commit()
    conn.close()

# Initialize Database
initialize_db()