import sqlite3
from flask import session
from auth import get_connection , is_company
import student

def dashboard_data():
    if not is_company():
        return None
    company_id = session.get('user_id')
    conn = get_connection()
    drives_count = conn.execute("select count(*) as c from placement_drive where company_id = ?", (company_id,)).fetchone()["c"]
    applications_count = conn.execute("select count(*) as c from application a join placement_drive d on a.drive_id = d.drive_id where d.company_id=?", (company_id,)).fetchone()["c"]
    conn.close()
    return {"drives": drives_count, "applications": applications_count}

def create_drive(title,description,skills,experience,salary,eligibility,deadline):
    if not is_company():
        return False

    company_id = session.get("user_id")
    conn = get_connection()

    company = conn.execute("select approval_status from company where company_id=?",(company_id,)).fetchone()

    if company["approval_status"] != "approved":
        conn.close()
        return False
    if not title or not deadline:
        return False

    cursor = conn.execute("insert into job_position(company_id,title,description,required_skills,experience_required,salary_range)values(?,?,?,?,?,?)",(company_id,title,description,skills,experience,salary))

    position_id = cursor.lastrowid

    conn.execute("insert into placement_drive(company_id,position_id,eligibility,application_deadline,status)values(?,?,?,?, 'pending')",(company_id,position_id,eligibility,deadline))
    conn.commit()
    conn.close()
    return True

def update_drive(drive_id,title,description):
    if not is_company():
        return False
    company_id = session.get('user_id')
    conn = get_connection()
    drive = conn.execute("select status from placement_drive where drive_id=? and company_id=?", (drive_id,company_id)).fetchone()
    if not drive:
        conn.close()
        return False
    if drive["status"] != "pending":
        conn.close()
        return False
    conn.execute("update job_position set title=?, description=? where position_id in (select position_id from placement_drive where drive_id=?)", (title, description, drive_id))
    conn.commit()
    conn.close()
    return True

def list_drives():
    if not is_company():
        return None
    student.update_drive_status()
    company_id = session.get('user_id')
    conn = get_connection()
    drives = conn.execute("select d.drive_id, p.title,p.required_skills,p.experience_required,p.salary_range,d.eligibility, d.application_deadline, d.status from placement_drive d join job_position p on d.position_id = p.position_id where d.company_id = ?", (company_id,)).fetchall()
    conn.close()
    return drives

def close_drives(drive_id):
    if not is_company():
        return False
    company_id = session.get('user_id')
    conn = get_connection()
    conn.execute("update placement_drive set status='closed' where drive_id =? and company_id = ?", (drive_id,company_id,))
    conn.commit()
    conn.close()
    return True

def view_applications_by_drive(drive_id):
    if not is_company():
        return None
    company_id = session.get('user_id')
    conn = get_connection()
    applications = conn.execute("select a.application_id, s.name,s.roll_no,s.cgpa,s.resume_link, p.title, a.application_status from application a join student s on a.student_id = s.student_id join placement_drive d on a.drive_id = d.drive_id join job_position p on d.position_id = p.position_id where d.drive_id=? and d.company_id = ? and a.application_status!='placed' ", (drive_id,company_id)).fetchall()
    conn.close()
    return applications

def update_application_status(application_id,new_status):
    if not is_company():
        return False
    if new_status not in ['placed', 'rejected','shortlisted']:
        return False
    company_id = session.get('user_id')
    conn = get_connection()
    student = conn.execute("select student_id from application where application_id=?",(application_id,)).fetchone()
    student_id=student["student_id"]
    placed = conn.execute("select application_id from application where student_id=? and application_status='placed'",(student_id,)).fetchone()
    if placed:
        conn.close()
        return False
    conn.execute("update application set application_status=? where application_id =? and drive_id in (select drive_id from placement_drive where company_id = ?)", (new_status,application_id,company_id,))
    if new_status=="placed":
        conn.execute("insert into placement(application_id,placed_on)values(?,date('now'))",(application_id,))
    conn.commit()
    conn.close()
    return True

def view_shortlisted_students(drive_id):
    if not is_company():
        return None
    company_id = session.get('user_id')
    conn = get_connection()
    students = conn.execute("select s.name,s.roll_no,s.email,s.cgpa,s.phone,s.resume_link,p.title from application a join student s on a.student_id = s.student_id join placement_drive d on a.drive_id = d.drive_id join job_position p on d.position_id = p.position_id where a.application_status in ('shortlisted','placed') and d.drive_id = ? and d.company_id = ?", (drive_id,company_id,)).fetchall()
    conn.close()
    return students

def place_student(application_id,offer_letter_link,remarks):

    if not is_company():
        return False

    conn = get_connection()
    student = conn.execute("select student_id from application where application_id=?",(application_id,)).fetchone()
    student_id = student["student_id"]

    conn.execute("update application set application_status='placed' where application_id=?",(application_id,))
    conn.execute("update application set application_status='rejected' where student_id=? and application_id!=?",(student_id,application_id))
    conn.execute("insert into placement(application_id,placed_on,remarks,offer_letter_link)values (?,date('now'),?,?)",(application_id,remarks,offer_letter_link))
    conn.commit()
    conn.close()

    return True

def company_placements():

    if not is_company():
        return None
    company_id = session.get("user_id")
    conn = get_connection()

    placements = conn.execute("select s.name,s.roll_no,p.title,pl.placed_on,pl.remarks,pl.offer_letter_link from placement pl join application a on pl.application_id = a.application_id join student s on a.student_id = s.student_id join placement_drive d on a.drive_id = d.drive_id join job_position p on d.position_id = p.position_id where d.company_id = ?",(company_id,)).fetchall()
    conn.close()
    return placements