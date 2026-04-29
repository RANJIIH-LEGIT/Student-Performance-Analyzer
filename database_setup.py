import sqlite3
import os

def update_database():
    # Delete the old database to avoid structure conflicts
    if os.path.exists('college.db'):
        os.remove('college.db')
        print("🗑️ Old database removed for fresh setup.")

    conn = sqlite3.connect('college.db')
    cursor = conn.cursor()

    # 1. Users Table (Login Credentials)
    cursor.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )''')

    # 2. Advanced Students Table (Grouping-Ready)
    # Note: roll_no is NO LONGER UNIQUE here to allow multiple subjects per student
    cursor.execute('''CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL, 
            semester INTEGER,
            subject_name TEXT,
            
            -- Mid-Term Data
            mid_term_marks REAL,
            mid_needs_remedial INTEGER DEFAULT 0,
            mid_rem_topics TEXT DEFAULT 'None',
            mid_rem_attendance REAL DEFAULT 0,
            mid_rem_marks REAL DEFAULT 0,
            
            -- Model Exam Data
            model_marks REAL,
            model_needs_remedial INTEGER DEFAULT 0,
            model_rem_topics TEXT DEFAULT 'None',
            model_rem_attendance REAL DEFAULT 0,
            model_rem_marks REAL DEFAULT 0,
            
            -- Final Tracking
            end_sem_marks REAL DEFAULT 0,
            arrear_status INTEGER DEFAULT 0 
        )''')

    # 3. Create Default Admin Account
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

    conn.commit()
    conn.close()
    print("✅ Database successfully updated for Grouped Subject Tracking!")

if __name__ == "__main__":
    update_database()