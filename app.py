from flask import Flask , render_template,request,redirect,url_for
import auth
import admin
import company
import student

app = Flask(__name__)

app.secret_key = "shakthi_key_2026"


@app.route("/")
def home():
    return "Placement portal is running"

@app.route("/login",methods=["GET","POST"])
def login():
    return auth.login()

@app.route("/logout")
def logout():
    return auth.logout()

@app.route("/register/student",methods=["GET","POST"])
def student_registration():
    return auth.student_registration()

@app.route("/register/company",methods=["GET","POST"])
def company_registration():
    return auth.company_registration()

@app.route("/admin/dashboard")
def admin_dashboard():
    if not auth.is_admin():
        return "Access denied", 403
    
    data = admin.admin_dashboard_data()
    return render_template("admin_dashboard.html", data=data)

@app.route("/company/dashboard")
def company_dashboard():
    if not auth.is_company():
        return "Access denied", 403
    data=company.dashboard_data()
    return render_template("company_dashboard.html", data=data)

@app.route("/company/drive/create", methods=["POST","GET"])
def create_drive():
    if not auth.is_company():
        return "Access denied", 403
    if request.method == "POST":
        if company.create_drive(request.form["title"], request.form["description"], request.form["skills"],request.form["experience"],request.form["salary"], request.form["eligibility"], request.form["deadline"]):
            return redirect(url_for("company_drives"))
    return render_template("company_create_drive.html")

@app.route("/company/drives")
def company_drives():
    if not auth.is_company():
        return "Access denied", 403
    drives = company.list_drives()
    return render_template("company_drives.html", drives=drives)

@app.route("/company/drive/<int:drive_id>/shortlisted")
def shortlisted_students(drive_id):
    if not auth.is_company():
        return "Access denied", 403
    students = company.view_shortlisted_students(drive_id)
    return render_template("company_shortlisted.html", students=students)


@app.route("/company/drive/close/<int:drive_id>")
def close_company_drive(drive_id):
    if company.close_drives(drive_id):
        return "Drive closed successfully"
    return "access denied",403

@app.route("/company/drive/<int:drive_id>/applications")
def company_applications(drive_id):
    if not auth.is_company():
        return "Access denied", 403
    applications = company.view_applications_by_drive(drive_id)
    return render_template("company_applications.html", applications=applications)

@app.route("/company/application/<int:application_id>/update_status/<status>")
def update_application_status(application_id,status):
    if company.update_application_status(application_id,status):
        return "Application status updated successfully"
    return "access denied",403

@app.route("/student/dashboard")
def student_dashboard():
    if not auth.is_student():
        return "Access denied", 403
    apps = student.view_applications()
    notifications = [a for a in apps if a["application_status"] != "applied"]
    return render_template("student_dashboard.html", notifications=notifications)

@app.route("/student/drives")
def student_drives():
    if not auth.is_student():
        return "Access denied", 403
    drives = student.view_active_drives()
    return render_template("student_drives.html", drives=drives)

@app.route("/student/search",methods=["GET","POST"])
def student_search():
    if not auth.is_student():
        return "Access denied", 403
    keyword = request.form["keyword"]
    drives = student.search_drives(keyword)
    return render_template("student_drives.html", drives=drives)

@app.route("/student/apply/<int:drive_id>")
def student_apply(drive_id):
    result = student.apply_for_drive(drive_id)

    if result == "success":
        return "applied successfully"

    elif result == "already_applied":
        return "you have already applied"

    else:
        return "application failed"


@app.route("/student/applications")
def student_applications():
    if not auth.is_student():
        return "Access denied", 403
    applications = student.view_applications()
    return render_template("student_applications.html", apps=applications)

@app.route("/student/view_profile")
def view_profile():
    if not auth.is_student():
        return "Access denied", 403
    profile = student.get_profile()
    return render_template("student_view_profile.html", profile=profile)



@app.route("/student/profile", methods=["GET","POST"])
def student_profile():
    if not auth.is_student():
        return "Access denied", 403
    if request.method == "POST":
        education = request.form.get("education")
        skills = request.form.get("skills")
        resume_link = request.form.get("resume_link")
        cgpa = request.form.get("cgpa")
        student.update_profile(education, skills, resume_link, cgpa)
        return "Profile updated successfully"
    profile = student.get_profile()
    return render_template("student_profile.html", profile=profile)

@app.route("/admin/company/approve/<int:company_id>")
def approve_company(company_id):
    if admin.approve(company_id):
        return "Company approved"
    return "Access denied", 403

@app.route("/admin/company/reject/<int:company_id>")
def reject_company(company_id):
    if admin.reject(company_id):
        return "Company rejected"
    return "Access denied", 403

@app.route("/admin/drives")
def admin_drives():
    if not auth.is_admin():
        return "Access denied", 403
    d=admin.list_drives()
    return render_template("admin_drives.html", drives=d)

@app.route("/admin/drive/approve/<int:drive_id>")
def approve_drive(drive_id):
    if admin.approve_drive(drive_id):
        return "Drive approved"
    return "Access denied", 403

@app.route("/admin/drive/close/<int:drive_id>")
def close_drive(drive_id):
    if admin.close_drive(drive_id):
        return "Drive closed"
    return "Access denied", 403

@app.route("/admin/applications")
def admin_applications():
    if not auth.is_admin():
        return "Access denied", 403
    company_id = request.args.get('company_id')
    drive_id = request.args.get('drive_id')
    a=admin.applications_filtered(company_id=company_id, drive_id=drive_id)
    companies = admin.list_companies()
    drives = admin.list_drives()
    return render_template("admin_applications.html", applications=a,companies=companies, drives=drives)

@app.route("/admin/students")
def admin_students():
    if not auth.is_admin():
        return "Access denied", 403
    s = admin.list_students()
    return render_template("admin_students.html", students=s)

@app.route("/admin/student/toggle/active/<int:student_id>")
def toggle_student_active(student_id):
    if admin.toggle_student_active(student_id):
        return "Student active status toggled"
    return "Access denied", 403

@app.route("/admin/student/toggle/blacklist/<int:student_id>")
def toggle_student_blacklist(student_id):
    if admin.toggle_student_blacklist(student_id):
        return "Student blacklist status toggled"
    return "Access denied", 403

@app.route("/admin/companies")
def admin_companies():
    if not auth.is_admin():
        return "Access denied", 403
    c= admin.list_companies()
    return render_template("admin_companies.html", companies=c)

@app.route("/admin/search/students/<keyword>")
def search_students(keyword):
    if not auth.is_admin():
        return "Access denied", 403
    c=admin.search_students(keyword)
    return render_template("admin_students.html", students=c)

@app.route("/admin/search/companies/<keyword>")
def search_companies(keyword):
    if not auth.is_admin():
        return "Access denied", 403
    s=admin.search_companies(keyword)
    return render_template("admin_companies.html", companies=s)

@app.route("/admin/company/toggle/active/<int:company_id>")
def toggle_company_active(company_id):
    if admin.toggle_company_active(company_id):
        return "Company active status toggled"
    return "Access denied", 403

if __name__ == "__main__":
    app.run(debug=True)
