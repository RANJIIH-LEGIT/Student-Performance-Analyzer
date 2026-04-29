from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import numpy as np
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'gnc_portal_final_2026'

# --- SMART DATABASE CONNECTION ---
def get_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'college.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# --- 1. SECURE LOGIN ROUTE ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        selected_role = request.form['selected_role']
        
        conn = get_db()
        acc = conn.execute('SELECT * FROM users WHERE username=? AND password=? AND role=?', 
                          (user, pwd, selected_role)).fetchone()
        conn.close()
        
        if acc:
            session['user'], session['role'] = acc['username'], acc['role']
            if acc['role'] == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('student_panel'))
        else:
            return render_template('login.html', error="Invalid credentials or incorrect portal selected.")
    return render_template('login.html')

# --- 2. ADMIN PANEL ---
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db()
    query = '''
        SELECT name, roll_no, 
        GROUP_CONCAT('Sem ' || semester || ': ' || subject_name || ' (M:' || mid_term_marks || ', E:' || model_marks || ')', ' | ') as all_marks,
        MAX(mid_needs_remedial) as fail_mid,
        MAX(model_needs_remedial) as fail_mod
        FROM students 
        GROUP BY roll_no
    '''
    students = conn.execute(query).fetchall()
    conn.close()
    return render_template('admin.html', students=students)

# --- 3. ADD STUDENT ---
@app.route('/add', methods=['POST'])
def add_student():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    name, roll, pwd = request.form['name'], request.form['roll_no'], request.form['password']
    sem, sub = int(request.form['semester']), request.form['subject']
    mid, model = float(request.form['mid_term']), float(request.form['model_exam'])
    
    mid_rem = 1 if mid < 50 else 0
    model_rem = 1 if model < 50 else 0
    
    conn = get_db()
    conn.execute('INSERT INTO students (name, roll_no, semester, subject_name, mid_term_marks, mid_needs_remedial, model_marks, model_needs_remedial) VALUES (?,?,?,?,?,?,?,?)', 
                 (name, roll, sem, sub, mid, mid_rem, model, model_rem))
    conn.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', (roll, pwd, 'student'))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

# --- 4. REMEDIAL TRACKING ---
@app.route('/remedial')
def remedial_panel():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db()
    slow_learners = conn.execute('SELECT * FROM students WHERE mid_needs_remedial=1 OR model_needs_remedial=1').fetchall()
    conn.close()
    return render_template('remedial.html', students=slow_learners)

# --- 5. UPDATE REMEDIAL ---
@app.route('/update_remedial', methods=['POST'])
def update_remedial():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    sid, etype = request.form['student_id'], request.form['exam_type']
    att, topics, marks = float(request.form['rem_attendance']), request.form['topics'], float(request.form['rem_marks'])
    conn = get_db()
    status = 0 if marks >= 50 else 1
    if etype == 'mid':
        conn.execute('UPDATE students SET mid_rem_attendance=?, mid_rem_topics=?, mid_rem_marks=?, mid_needs_remedial=? WHERE id=?', (att, topics, marks, status, sid))
    else:
        conn.execute('UPDATE students SET model_rem_attendance=?, model_rem_topics=?, model_rem_marks=?, model_needs_remedial=? WHERE id=?', (att, topics, marks, status, sid))
    conn.commit()
    conn.close()
    return redirect(url_for('remedial_panel'))

# --- 6. FILTERED REPORT ---
@app.route('/generate_report')
def generate_report():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    selected_sem = request.args.get('semester')
    conn = get_db()
    query = 'SELECT * FROM students WHERE (mid_rem_attendance > 0 OR model_rem_attendance > 0)'
    params = []
    if selected_sem and selected_sem != "All":
        query += ' AND semester = ?'
        params.append(selected_sem)
    report_data = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('remedial_report.html', students=report_data, today=date.today().strftime('%d-%m-%Y'), current_sem=selected_sem)

# --- 7. STUDENT PANEL ---
@app.route('/student')
def student_panel():
    if session.get('role') != 'student': return redirect(url_for('login'))
    conn = get_db()
    subs = conn.execute('SELECT * FROM students WHERE roll_no=?', (session['user'],)).fetchall()
    conn.close()
    if subs:
        avg = np.mean([s['mid_term_marks'] for s in subs] + [s['model_marks'] for s in subs])
        return render_template('student.html', subjects=subs, prediction=round(avg, 2), student_name=subs[0]['name'])
    return "No Data"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)