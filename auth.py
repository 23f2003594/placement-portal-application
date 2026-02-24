import sqlite3
from flask import (request , session , redirect , url_for, flash,render_template)

from werkzeug.security import generate_password_hash , check_password_hash 

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

DB_NAME = 'placement_portal.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def student_registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hash_password(password)
        roll_no = request.form['roll_no']
        phone = request.form['phone']
        resume_link = request.form['resume_link']
        cgpa = request.form['cgpa']
        education = request.form['education']
        skills = request.form['skills']
        graduation_year = request.form['graduation_year']
        conn = get_connection()
        try:
            conn.execute("insert into student (name, email, password, roll_no ,phone, resume_link, cgpa, education, skills, graduation_year) values (?,?,?,?,?,?,?,?,?,?)",(name,email,hashed_password,roll_no,phone,resume_link,cgpa,education,skills,graduation_year))
            conn.commit()
            conn.close()
            flash('Student has been registered successfully!','success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists. Please use a different email.','danger')
    return render_template('student_registration.html')

def company_registration():
    if request.method == 'POST':
        c_name = request.form['company_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hash_password(password)
        hr_contact = request.form['hr_contact']
        website = request.form['website']
        industry = request.form['industry']
        conn = get_connection()
        try:
            conn.execute("insert into company (company_name, email, password, hr_contact, website, industry) values (?,?,?,?,?,?)",(c_name,email,hashed_password,hr_contact,website,industry))
            conn.commit()
            conn.close()
            flash('Company has been registered successfully!','success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists. Please use a different email.','danger')
    return render_template('company_registration.html')


def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_connection()

        admin = conn.execute("select * from admin where email = ?", (email,)).fetchone()
        if admin and verify_password(admin['password'],password):
            session.clear()
            session['user_id'] = admin['admin_id']
            session['user_type'] = 'admin'
            flash('Logged in successfully as Admin!','success')
            conn.close()
            return redirect(url_for('admin_dashboard'))
    
        company = conn.execute("select * from company where email = ? and is_active=1", (email,)).fetchone()
        if company:
            if company["approval_status"] != "approved":
                flash("Company not approved yet","warning")
                conn.close()
                return redirect(url_for('login'))
            if verify_password(company['password'],password):
                session.clear()
                session['user_id'] = company['company_id']
                session['user_type'] = 'company'
                flash('Logged in successfully as Company!','success')
                conn.close()
                return redirect(url_for('company_dashboard'))
        
        student = conn.execute("select * from student where email = ? and is_active=1 and is_blacklisted=0", (email,)).fetchone()
        if student and verify_password(student['password'],password):
            session.clear()
            session['user_id'] = student['student_id']
            session['user_type'] = 'student'
            flash('Logged in successfully as Student!','success')
            conn.close()
            return redirect(url_for('student_dashboard'))
        conn.close()
        flash('Invalid credentials or inactive account. Please try again.','danger')
    return render_template('login.html')

def logout():
    session.clear()
    flash('Logged out successfully!','success')
    return redirect(url_for('login'))

def is_admin():
    return session.get('user_type') == 'admin'

def is_company():
    return session.get('user_type') == 'company'

def is_student():
    return session.get('user_type') == 'student'