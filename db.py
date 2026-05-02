import sqlite3
from datetime import date

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect("attendance.db")
    return conn

# Create tables
def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    # Students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL
    )
    """)

    # Attendance table with date column
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        roll INTEGER,
        status TEXT,
        date TEXT,
        FOREIGN KEY (roll) REFERENCES students(roll)
    )
    """)

    conn.commit()
    conn.close()

# Insert student
def add_student(roll, name, dept):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO students VALUES (?, ?, ?)", (roll, name, dept))
    conn.commit()
    conn.close()

# Update student
def update_student(roll, name, dept):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE students SET name=?, department=? WHERE roll=?", (name, dept, roll))
    conn.commit()
    conn.close()

# Delete student
def delete_student(roll):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE roll=?", (roll,))
    # Also delete their attendance records
    cur.execute("DELETE FROM attendance WHERE roll=?", (roll,))
    conn.commit()
    conn.close()

# Get all students
def get_students():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY roll")
    rows = cur.fetchall()
    conn.close()
    return rows

# Mark attendance with date
def mark_attendance(roll, status, attendance_date=None):
    if not attendance_date:
        attendance_date = date.today().isoformat()  # default to today
    conn = connect_db()
    cur = conn.cursor()
    # Check if attendance already marked for the date
    cur.execute("SELECT * FROM attendance WHERE roll=? AND date=?", (roll, attendance_date))
    if cur.fetchone():
        # Update existing record
        cur.execute("UPDATE attendance SET status=? WHERE roll=? AND date=?", (status, roll, attendance_date))
    else:
        # Insert new record
        cur.execute("INSERT INTO attendance VALUES (?, ?, ?)", (roll, status, attendance_date))
    conn.commit()
    conn.close()

# Get attendance for a specific date
def get_attendance(attendance_date=None):
    if not attendance_date:
        attendance_date = date.today().isoformat()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT s.roll, s.name, s.department,COALESCE(a.status, 'Not Marked') 
    FROM students s
    LEFT JOIN attendance a 
    ON s.roll = a.roll AND a.date = ?
    ORDER BY s.roll
    """, (attendance_date,))
    rows = cur.fetchall()
    conn.close()
    return rows

# Get total attendance % for each student
def get_attendance_percentage():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT s.roll, s.name, s.department,
    CASE WHEN COUNT(a.status) = 0 THEN 0
    ELSE (CAST(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(a.status)) * 100
    END AS attendance_percentage
    FROM students s
    LEFT JOIN attendance a ON s.roll = a.roll
    GROUP BY s.roll
    ORDER BY s.roll
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# Get defaulters (<75% attendance)
def get_defaulters():
    all_attendance = get_attendance_percentage()
    defaulters = [s for s in all_attendance if s[3] < 75]
    return defaulters

# Run this once to create tables
if __name__ == "__main__":
    create_tables()
