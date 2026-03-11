import sqlite3
from flask import session
from auth import is_student , get_connection

def get_profile():
    if not is_student():
        return "Access denied",403
    student_id = session.get("student_id")
    conn = get_connection()
    student = conn.execute("Select * from student where student_id=?",(student_id,)).fetchone()
    conn.close()
    return student

def update_profile(education=None , skills=None , resume_link=None,cgpa=None):
    if not is_student():
        return False
    student_id = session.get("user_id")
    conn = get_connection()
    fields =[]
    values = []
    if education is not None:
        fields.append("education=?")
        values.append(education)
    if skills is not None:
        fields.append("skills=?")
        values.append(skills)
    if resume_link is not None:
        fields.append("resume_link=?")
        values.append(resume_link)
    if cgpa is not None:
        fields.append("cgpa=?")
        values.append(cgpa)
    if not fields:
        conn.close()
        return False
    query = f"update student set {','.join(fields)} where student_id=?" 
    values.append(student_id)
    conn.execute(query,tuple(values))
    conn.commit()
    conn.close()
    return True 



def view_active_drives():
    if not is_student():
        return "Access denied",403
    conn = get_connection()
    student_id = session.get("user_id")
    drives = conn.execute("select d.drive_id , c.company_name , c.industry , p.title , p.description , p.salary_range , p.required_skills , p.experience_required , d.eligibility , d.application_deadline,exists(select 1 from application a where a.student_id=? and a.drive_id=d.drive_id) as applied from placement_drive d join company c on d.company_id = c.company_id join job_position p on d.position_id = p.position_id where d.status='active' and not exists(select 1 from application a where a.student_id=? and a.application_status='placed')",(student_id,student_id)).fetchall()
    conn.close()
    return drives

def search_drives(keyword):
    if not is_student():
        return "Access denied",403
    conn = get_connection()
    drives = conn.execute("select d.drive_id , c.company_name , c.industry , p.title , p.description , p.salary_range , p.required_skills , p.experience_required , d.eligibility , d.application_deadline from placement_drive d join company c on d.company_id = c.company_id join job_position p on d.position_id = p.position_id where d.status='active' and (c.company_name like ? or p.title like ? or p.required_skills like ?)",(f"%{keyword}%",f"%{keyword}%",f"%{keyword}%")).fetchall()
    conn.close()
    return drives

def apply_for_drive(drive_id):
    if not is_student():
        return "access_Denied"

    student_id = session.get("user_id")
    conn = get_connection()

    drive = conn.execute("select status from placement_drive where drive_id=?",(drive_id,)).fetchone()

    placed = conn.execute("select application_id from application where student_id=? and application_status='placed'",(student_id,)).fetchone()
    if placed:
        conn.close()
        return "already_placed"

    if not drive or drive["status"] != "active":
        conn.close()
        return "drive_not_active"
    
    existing = conn.execute("select application_id from application where student_id=? and drive_id=?",(student_id,drive_id)).fetchone()
    if existing:
        conn.close()
        return "already_applied"

    try:
        conn.execute("insert into application(student_id,drive_id) values(?,?)",(student_id,drive_id))
        conn.commit()
        conn.close()
        return "applied"

    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_drive_status():
    conn = get_connection()

    conn.execute("update placement_drive set status='closed' where application_deadline < date('now') and status='active'")

    conn.commit()
    conn.close()

def view_applications():
    if not is_student():
        return None
    student_id = session.get("user_id")
    conn = get_connection()
    applications = conn.execute("select a.application_id , c.company_name , p.title , a.application_status from application a join placement_drive d on a.drive_id = d.drive_id join company c on d.company_id = c.company_id join job_position p on d.position_id = p.position_id where a.student_id=?",(student_id,)).fetchall()
    conn.close()
    return applications

def get_profile():
    if not is_student():
        return None
    student_id = session.get("user_id")
    conn = get_connection()
    student = conn.execute("select name,email,roll_no,phone,resume_link,cgpa,graduation_year,education,skills from student where student_id=?", (student_id,)).fetchone()
    conn.close()
    return student

def view_application_history():
    if not is_student():
        return None

    student_id = session.get("user_id")
    conn = get_connection()

    history = conn.execute("select a.application_id,c.company_name,p.title,d.application_deadline,a.application_status from application a join placement_drive d on a.drive_id = d.drive_id join company c on d.company_id = c.company_id join job_position p on d.position_id = p.position_id where a.student_id = ? order by a.application_id desc", (student_id,)).fetchall()
    conn.close()
    return history
