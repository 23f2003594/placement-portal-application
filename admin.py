import sqlite3
from flask import redirect , url_for , flash
from auth import is_admin

DB_NAME ="placement_portal.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def list_companies():
    if not is_admin():
        return None
    conn = get_connection()
    companies = conn.execute("select company_id , company_name , email , industry, approval_status , is_active  from company").fetchall()
    conn.close()
    return companies

def list_students():
    if not is_admin():
        return None
    conn = get_connection()
    students = conn.execute("select  student_id , name , email ,roll_no , is_active , is_blacklisted from student").fetchall()
    conn.close()
    return students

def list_drives():
    if not is_admin():
        return None
    conn = get_connection()
    drives = conn.execute("select d.drive_id , c.company_name , jp.title as job_title ,jp.description,jp.required_skills,jp.experience_required,jp.salary_range,d.eligibility, d.status , d.application_deadline from placement_drive d join company c on d.company_id = c.company_id join job_position jp on d.position_id = jp.position_id").fetchall()
    conn.close()
    return drives

def list_applications():
    if not is_admin():
        return None
    conn = get_connection()
    applications = conn.execute("select a.application_id , s.name as student_name , c.company_name , jp.title as job_title , a.application_status from application a join student s on a.student_id = s.student_id join placement_drive d on a.drive_id = d.drive_id join company c on d.company_id = c.company_id join job_position jp on d.position_id = jp.position_id ").fetchall()
    conn.close()
    return applications

def search_students(keyword):
    if not is_admin():
        return None
    conn = get_connection()
    students = conn.execute("select student_id , name , email ,roll_no , is_active , is_blacklisted from student where name like ? or email like ? or roll_no like ?", ('%'+keyword+'%','%'+keyword+'%','%'+keyword+'%')).fetchall()
    conn.close()
    return students

def search_companies(keyword):
    if not is_admin():
        return None
    conn = get_connection()
    companies = conn.execute("select company_id , company_name , email , industry , approval_status , is_active from company where company_name like ? or industry like ?", ('%'+keyword+'%','%'+keyword+'%')).fetchall()
    conn.close()
    return companies

def approve_drive(drive_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update placement_drive set status = 'active' where drive_id = ?", (drive_id,))
    conn.commit()
    conn.close()
    flash('Placement Drive approved successfully!','success')
    return True

def close_drive(drive_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update placement_drive set status = 'closed' where drive_id = ?", (drive_id,))
    conn.commit()
    conn.close()
    return True

def admin_dashboard_data():
    if not is_admin():
        return None
    conn = get_connection()
    data = {"students":conn.execute("select count(*) as c from student").fetchone()["c"],"companies":conn.execute("select count(*) as c from company").fetchone()["c"],"drives":conn.execute("select count(*) as c from placement_drive").fetchone()["c"],"applications":conn.execute("select count(*) as c from application").fetchone()["c"],"pending_companies":conn.execute("select * from company where approval_status = 'pending'").fetchall()}
    conn.close()
    return data

def toggle_company_active(company_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update company set is_active = case when is_active = 1 then 0 else 1 end where company_id = ?", (company_id,))
    conn.commit()
    conn.close()
    return True

def toggle_student_active(student_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update student set is_active = case when is_active = 1 then 0 else 1 end where student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True

def toggle_student_blacklist(student_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update student set is_blacklisted = case when is_blacklisted = 1 then 0 else 1 end where student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True

def approve(company_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update company set approval_status = 'approved' where company_id = ?", (company_id,))
    conn.commit()
    conn.close()
    flash('Company approved successfully!','success')
    return True

def reject(company_id):
    if not is_admin():
        return False
    conn = get_connection()
    conn.execute("update company set approval_status = 'rejected' where company_id = ?", (company_id,))
    conn.commit()
    conn.close()
    flash('Company rejected successfully!','warning')
    return True

def applications_filtered(company_id = None , drive_id=None):
    if not is_admin():
        return None
    conn = get_connection()
    query = "select a.application_id , s.name as student_name , s.roll_no ,c.company_name , p.title as job_title , d.drive_id,a.application_status from application a join student s on a.student_id = s.student_id join placement_drive d on a.drive_id = d.drive_id join company c on d.company_id = c.company_id join job_position p on d.position_id = p.position_id where 1=1"
    params = []
    if company_id:
        query += " and c.company_id = ?"
        params.append(company_id)
    if drive_id:
        query += " and d.drive_id = ?"
        params.append(drive_id)
    applications = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return applications
