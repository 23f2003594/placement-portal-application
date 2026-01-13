import sqlite3

from datetime import datetime

DB_NAME = "placement_portal.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

# Creating tables for thr placement portal application
def create_admin(conn):
    conn.execute("create table if not exists admin( admin_id integer primary key autoincrement , username text unique not null , password text not null,email text unique not null )")

def create_company(conn):
    conn.execute("create table if not exists company(company_id integer primary key autoincrement , company_name text not null ,email text unique not null,password text not null, hr_contact text , website text , approval_status text default 'pending' , is_active integer default 1,registered_on text default current_timestamp , check(approval_status in ('pending','approved','rejected')))")

def create_student(conn):
    conn.execute("create table if not exists student(student_id integer primary key autoincrement , name text not null , email text unique not null ,password text not null , phone text, resume_link text , cgpa real ,graduation_year integer ,is_active integer default 1, is_blacklisted integer default 0, registered_on text default current_timestamp )")

def create_job_position(conn):
    conn.execute("create table if not exists job_position(position_id integer primary key autoincrement , company_id integer not null , title text not null , description text , salary_range text ,location text , job_type text ,  foreign key (company_id) references company(company_id) on delete cascade)")

def create_placement_drive(conn):
    conn.execute("create table if not exists placement_drive (drive_id integer primary key autoincrement,company_id integer not null , position_id integer not null , eligibility text , application_deadline text not null , status text default 'pending',foreign key (company_id) references company(company_id) on delete cascade,foreign key(position_id) references job_position(position_id) on delete cascade, check(status in ('pending','active','closed')) )")
                 
def create_application(conn):
    conn.execute("create table if not exists application(application_id integer primary key autoincrement,student_id integer not null , drive_id integer not null , applied_on text default current_timestamp, application_status text default 'applied', foreign key (student_id) references student(student_id) on delete cascade, foreign key (drive_id) references placement_drive(drive_id) on delete cascade, check(application_status in ('applied','shortlisted','rejected','placed')) , unique(student_id, drive_id) )")

def create_placement(conn):
    conn.execute("create table if not exists placement(placement_id integer primary key autoincrement,application_id integer unique not null,placed_on text , remarks text,offer_letter_link text ,  foreign key (application_id) references application(application_id) on delete cascade)")


def insert_default_admin(conn):
    default_username = "Admin"
    default_password ="admin@2026"
    default_email = "admin@iitm.edu"
    try:
        conn.execute("insert into admin (username, password,email) values (?, ?, ?)", (default_username, default_password,default_email))
    except sqlite3.IntegrityError:
        pass  # Admin already exists

def initialize_database():
    conn = get_connection()
    create_admin(conn)
    create_company(conn)
    create_student(conn)
    create_job_position(conn)
    create_placement_drive(conn)
    create_application(conn)
    create_placement(conn)

    insert_default_admin(conn)

    conn.commit()
    conn.close()

if __name__=="__main__":
    initialize_database()
    print("Database created successfully")