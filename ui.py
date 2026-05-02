import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import DateEntry
import db
from datetime import date

# Ensure tables exist
db.create_tables()

# Login Window 
def login():
    username = entry_user.get()
    password = entry_pass.get()
    if username == "teacher" and password == "123456":
        root.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

#  Dashboard 
def open_dashboard():
    dash = tk.Tk()
    dash.title("Attendance Management System")
    dash.state("zoomed")
    dash.configure(bg="#ffb6c1")

    notebook = ttk.Notebook(dash)
    notebook.pack(fill="both", expand=True)

    # 1. Manage Students 
    frame_students = tk.Frame(notebook, bg="#ffc0cb")
    notebook.add(frame_students, text="Manage Students")

    tk.Label(frame_students, text="Roll No:", bg="#ffc0cb").grid(row=0, column=0, padx=10, pady=5)
    roll_entry = tk.Entry(frame_students)
    roll_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(frame_students, text="Name:", bg="#ffc0cb").grid(row=1, column=0, padx=10, pady=5)
    name_entry = tk.Entry(frame_students)
    name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(frame_students, text="Department:", bg="#ffc0cb").grid(row=2, column=0, padx=10, pady=5)
    dept_entry = tk.Entry(frame_students)
    dept_entry.grid(row=2, column=1, padx=10, pady=5)

    cols = ("Roll", "Name", "Department")
    tree_students = ttk.Treeview(frame_students, columns=cols, show="headings", height=10)
    for col in cols:
        tree_students.heading(col, text=col)
        tree_students.column(col, width=150, anchor='center')
    tree_students.grid(row=4, column=0, columnspan=3, pady=10)

    def refresh_students():
        for row in tree_students.get_children():
            tree_students.delete(row)
        for s in db.get_students():
            tree_students.insert("", "end", values=s)

    def add():
        db.add_student(roll_entry.get(), name_entry.get(), dept_entry.get())
        messagebox.showinfo("Success", "Student Added!")
        refresh_students()

    def update():
        db.update_student(roll_entry.get(), name_entry.get(), dept_entry.get())
        messagebox.showinfo("Success", "Student Updated!")
        refresh_students()

    def delete():
        db.delete_student(roll_entry.get())
        messagebox.showinfo("Success", "Student Deleted!")
        refresh_students()

    tk.Button(frame_students, text="Add", command=add, bg="pink").grid(row=3, column=0, pady=5)
    tk.Button(frame_students, text="Update", command=update, bg="pink").grid(row=3, column=1, pady=5)
    tk.Button(frame_students, text="Delete", command=delete, bg="pink").grid(row=3, column=2, pady=5)

    refresh_students()

    # 2. Mark Attendance 
    frame_attendance = tk.Frame(notebook, bg="#ffccd5")
    notebook.add(frame_attendance, text="Mark Attendance")

    tk.Label(frame_attendance, text="Select Date:", bg="#ffccd5").pack(pady=5)
    date_entry = DateEntry(frame_attendance, width=12, background='darkblue',foreground='white', borderwidth=2, year=date.today().year,month=date.today().month, day=date.today().day)
    date_entry.pack(pady=5)

    cols_att = ("Roll", "Name", "Department", "Status")
    tree_attendance = ttk.Treeview(frame_attendance, columns=cols_att, show="headings", height=15)
    for col in cols_att:
        tree_attendance.heading(col, text=col)
        tree_attendance.column(col, width=150, anchor='center')
    tree_attendance.pack(pady=10, fill="x")

    # status (dropdown) Present/Absent
    status_var = tk.StringVar()
    status_dropdown = ttk.Combobox(frame_attendance, textvariable=status_var, values=["Present", "Absent"])
    status_dropdown.pack(pady=5)
    status_dropdown.current(0)

    def load_attendance():
        for row in tree_attendance.get_children():
            tree_attendance.delete(row)
        att_date = date_entry.get_date().isoformat()
        for s in db.get_attendance(att_date):
            tree_attendance.insert("", "end", values=s)

    def mark_selected():
        att_date = date_entry.get_date().isoformat()
        selected = tree_attendance.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a student row!")
            return
        status = status_var.get()
        for item in selected:
            roll = tree_attendance.item(item)['values'][0]
            db.mark_attendance(roll, status, att_date)
        load_attendance()
        messagebox.showinfo("Success", "Attendance marked!")

    tk.Button(frame_attendance, text="Load Attendance", command=load_attendance, bg="pink").pack(pady=5)
    tk.Button(frame_attendance, text="Mark Selected", command=mark_selected, bg="pink").pack(pady=5)

    load_attendance()

    #3. Defaulters 
    frame_defaulters = tk.Frame(notebook, bg="#ffe4e1")
    notebook.add(frame_defaulters, text="Defaulter List")

    cols_def = ("Roll", "Name", "Department", "Attendance %")
    tree_defaulters = ttk.Treeview(frame_defaulters, columns=cols_def, show="headings", height=15)
    for col in cols_def:
        tree_defaulters.heading(col, text=col)
        tree_defaulters.column(col, width=150, anchor='center')
    tree_defaulters.pack(fill="both", expand=True, pady=10)

    def show_defaulters():
        for row in tree_defaulters.get_children():
            tree_defaulters.delete(row)
        for d in db.get_defaulters():
            tree_defaulters.insert("", "end", values=d)

    tk.Button(frame_defaulters, text="Generate Defaulters", command=show_defaulters, bg="pink").pack(pady=5)

    dash.mainloop()

# Login Window UI 
root = tk.Tk()
root.title("Login")
root.geometry("1500x800")
root.configure(bg="#ffb6c1")

tk.Label(root, text="Username:", bg="#ffb6c1").pack(pady=5)
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password:", bg="#ffb6c1").pack(pady=5)
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login", command=login, bg="pink").pack(pady=20)

root.mainloop()
