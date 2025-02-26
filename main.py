import ttkbootstrap as ttk
from tkinter import messagebox
import db
import datetime

current_user = None

HEllo my name is saurav mainali
def show_login():
    login_window = ttk.Toplevel(root)
    login_window.title("Login")
    login_window.geometry("350x250")
    ttk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = ttk.Entry(login_window)
    username_entry.pack(pady=5)
    ttk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def login():
        global current_user
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if db.verify_user(username, password):
            current_user = username
            messagebox.showinfo("Login Success", "Welcome to Parking System!")
            login_window.destroy()
            show_main_system()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")

    ttk.Button(login_window, text="Login", bootstyle="primary", command=login).pack(pady=5)
    ttk.Button(login_window, text="Signup", bootstyle="secondary", command=show_signup).pack(pady=5)

def show_signup():
    signup_window = ttk.Toplevel(root)
    signup_window.title("Signup")
    signup_window.geometry("350x300")
    ttk.Label(signup_window, text="New Username:").pack(pady=5)
    new_username_entry = ttk.Entry(signup_window)
    new_username_entry.pack(pady=5)
    ttk.Label(signup_window, text="New Password:").pack(pady=5)
    new_password_entry = ttk.Entry(signup_window, show="*")
    new_password_entry.pack(pady=5)
    ttk.Label(signup_window, text="Confirm Password:").pack(pady=5)
    confirm_password_entry = ttk.Entry(signup_window, show="*")
    confirm_password_entry.pack(pady=5)

    def signup():
        username = new_username_entry.get().strip()
        password = new_password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        if db.add_user(username, password):
            messagebox.showinfo("Signup Successful", "Account Created! Please Login.")
            signup_window.destroy()
        else:
            messagebox.showerror("Signup Failed", "Username already exists!")

    ttk.Button(signup_window, text="Register", bootstyle="success", command=signup).pack(pady=10)

def show_main_system():
    global root
    for widget in root.winfo_children():
        widget.destroy()
    root.deiconify()
    root.title("Parking Management System")
    root.geometry("800x600")
    root.resizable(True, True)

    frame_top = ttk.Frame(root, padding=10)
    frame_top.pack(fill="x")
    ttk.Label(frame_top, text="Vehicle Type:").pack(side="left", padx=5)
    vehicle_type_var = ttk.Combobox(frame_top, values=["Car", "Motorcycle"], state="readonly")
    vehicle_type_var.pack(side="left", padx=5)
    vehicle_type_var.current(0)
    ttk.Label(frame_top, text="Plate Number:").pack(side="left", padx=5)
    entry_plate = ttk.Entry(frame_top)
    entry_plate.pack(side="left", padx=5)

    frame_search = ttk.Frame(root, padding=10)
    frame_search.pack(fill="x")

    ttk.Label(frame_search, text="Search Plate Number:").pack(side="left", padx=5)
    entry_search = ttk.Entry(frame_search)
    entry_search.pack(side="left", padx=5)

    ttk.Button(frame_search, text="Search", bootstyle="primary", 
               command=lambda: search_vehicle(entry_search, tree)).pack(side="left", padx=5)

    frame_table = ttk.Frame(root, padding=10)
    frame_table.pack(fill="both", expand=True)
    columns = ("ID", "Type", "Plate", "Entry Time", "Exit Time", "Fare")
    tree = ttk.Treeview(frame_table, columns=columns, show="headings")
    ttk.Style().configure("Treeview", rowheight=45, font=("Arial", 11))
    for col in columns:
        tree.heading(col, text=col)
        if col in ["ID"]:
            tree.column(col, width=80, minwidth=80, anchor="center", stretch=False)
        elif col in ["Type"]:
            tree.column(col,width=120, minwidth=120, anchor="center")
        elif col == "Plate":
            tree.column(col, width=120, minwidth=120, anchor="center", stretch=False)
        elif col in ["Entry Time", "Exit Time"]:
            tree.column(col, width=120, minwidth=120, anchor="center")
        elif col in ["Fare"]:
            tree.column(col, width=100, minwidth=100, anchor="center", stretch=False)
    h_scrollbar = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
    v_scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
    tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    tree.pack(fill="both", expand=True)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")

    ttk.Button(frame_top, text="Add Vehicle",bootstyle="primary" ,
               command=lambda: add_vehicle(vehicle_type_var, entry_plate, tree)).pack(side="left", padx=5)

    button_frame = ttk.Frame(root, padding=10)
    button_frame.pack(fill="x")
    ttk.Button(button_frame, text="Exit Vehicle", bootstyle="primary", 
               command=lambda: exit_vehicle(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Delete", bootstyle="primary", 
               command=lambda: delete_vehicle(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Logout", bootstyle="primary", 
               command=lambda: logout(root)).pack(side="right", padx=5)

    try:
        update_list(tree)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load vehicles: {e}")

def add_vehicle(vehicle_type_var, entry_plate, tree):
    vehicle_type = vehicle_type_var.get()
    plate_number = entry_plate.get().strip()
    if not plate_number:
        messagebox.showerror("Error", "Plate Number cannot be empty!")
        return
    try:
        entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.add_vehicle(vehicle_type, plate_number, entry_time)
        messagebox.showinfo("Success", "Vehicle Added Successfully!")
        entry_plate.delete(0, 'end')
        update_list(tree)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add vehicle: {e}")

def search_vehicle(entry_search, tree):
    plate_number = entry_search.get().strip()
    if not plate_number:
        messagebox.showwarning("Input Error", "Please enter a plate number!")
        return

    found = False
    for row in tree.get_children():
        values = tree.item(row, "values")
        if values and values[2].strip() == plate_number:
            tree.selection_set(row)
            tree.focus(row)
            found = True
            entry_time = values[3]
            exit_time = values[4]
            fare = values[5]

            # Check if the vehicle has not exited.
            # Sometimes, None may be converted to the string "None" in the Treeview.
            if exit_time in (None, "", "None"):
                response = messagebox.askyesno(
                    "Search Result", 
                    f"Vehicle Found:\n\nPlate: {values[2]}\nType: {values[1]}\nEntry Time: {entry_time}\n\nThis vehicle has not exited.\nWould you like to exit this vehicle?"
                )
                if response:  # User clicked "Yes"
                    exit_vehicle(tree)
            else:
                response = messagebox.askyesno(
                    "Search Result", 
                    f"Vehicle Found:\n\nPlate: {values[2]}\nType: {values[1]}\nEntry Time: {entry_time}\nExit Time: {exit_time}\nFare: Rs. {fare}\n\nThis vehicle has already exited.\nWould you like to delete this vehicle?"
                )
                if response:  # User clicked "Yes"
                    delete_vehicle(tree)
            break

    if not found:
        messagebox.showerror("Search Error", "No vehicle found with that plate number!")


def exit_vehicle(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a vehicle to exit!")
        return

    # Retrieve the selected row's values.
    values = tree.item(selected_item[0])["values"]
    plate_number = values[2]
    vehicle_type = values[1]  # "Car" or "Motorcycle"
    exit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get the entry time from the database.
    entry_time = db.get_entry_time(plate_number)
    if not entry_time:
        messagebox.showerror("Error", "Invalid vehicle record! Entry time not found.")
        return

    try:
        # Parse the entry and exit times.
        entry_dt = datetime.datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
        exit_dt = datetime.datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S")
        duration = (exit_dt - entry_dt).total_seconds() / 60  # duration in minutes

        # Calculate fare based on vehicle type and duration.
        if vehicle_type == "Car":
            if duration < 15:
                fare = 25
            elif duration < 30:
                fare = 50
            elif duration < 60:
                fare = 100
            else:
                fare = round(duration * 2, 2)
        elif vehicle_type == "Motorcycle":
            if duration < 15:
                fare = 15
            elif duration < 30:
                fare = 30
            elif duration < 60:
                fare = 60
            else:
                fare = round(duration * 1, 2)
        else:
            # Fallback in case of unknown vehicle type.
            fare = round(duration * 2, 2)
        
        # Update the database and notify the user.
        db.exit_vehicle(plate_number, exit_time, fare)
        messagebox.showinfo("Success", f"Vehicle Exited Successfully!\nTotal Fare: Rs. {fare}")
        update_list(tree)  # Refresh the Treeview list.
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to exit vehicle: {e}")



def delete_vehicle(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a vehicle to delete!")
        return
    plate_number = tree.item(selected_item[0])['values'][2]
    print(f"Attempting to delete plate: {plate_number}")  # Debug
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete vehicle {plate_number}?"):
        try:
            db.delete_vehicle(plate_number)
            update_list(tree)
            # Check if there are no vehicles left; if so, reset the id sequence.
            vehicles = db.get_all_vehicles()
            if not vehicles:  # If the table is empty
                db.reset_ids()
            messagebox.showinfo("Success", "Vehicle deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete vehicle: {e}")


def update_list(tree):
    for row in tree.get_children():
        tree.delete(row)
    vehicles = db.get_all_vehicles()
    print(f"Updated vehicles: {vehicles}")  # Debug
    for vehicle in vehicles:
        # vehicle = (id, type, plate, entry_time, exit_time, fare)
        exit_time = vehicle[4] if vehicle[4] is not None else ""
        fare = vehicle[5] if vehicle[5] is not None else ""
        tree.insert("", "end", values=(vehicle[0], vehicle[1], vehicle[2], vehicle[3], exit_time, fare))

def logout(root):
    global current_user
    current_user = None
    for widget in root.winfo_children():
        widget.destroy()
    root.title("Parking System - Login")
    root.geometry("300x150")
    ttk.Button(root, text="Login", bootstyle="primary", command=show_login).pack(pady=20)

root = ttk.Window(themename="cosmo")
root.title("Parking System - Login")
root.geometry("300x150")
ttk.Button(root, text="Login", bootstyle="primary", command=show_login).pack(pady=20)
root.mainloop()