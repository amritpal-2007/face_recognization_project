from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import subprocess
import os

app = Flask(__name__)

# Database
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "attendance.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -------------------------
# Student Table
# -------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)


# -------------------------
# Attendance Table
# -------------------------
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    status = db.Column(db.String(20))


# -------------------------
# Home
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "12345":
            return redirect("/dashboard")

        return "Wrong Username or Password"

    return render_template("login.html")


# -------------------------
# Dashboard
# -------------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# -------------------------
# Add Student
# -------------------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        student = Student(
            name=request.form["name"],
            roll=request.form["roll"],
            department=request.form["department"]
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/students")

    return render_template("add_student.html")


# -------------------------
# View Students
# -------------------------
@app.route("/students")
def students():

    students = Student.query.all()

    return render_template(
        "students.html",
        students=students
    )

@app.route("/delete_student/<int:id>")
def delete_student(id):

    # delete attendance records
    Attendance.query.filter_by(student_id=id).delete()

    # delete student
    student = Student.query.get(id)

    if student:
        db.session.delete(student)
        db.session.commit()

    # delete face images
    import os
    import shutil

    folder = f"faces/{id}"

    if os.path.exists(folder):
        shutil.rmtree(folder)

    return redirect("/students")


# -------------------------
# Register Face
# -------------------------
@app.route("/register_face/<int:id>")
def register_face(id):

    try:

        project_folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "cmd",
                "/k",
                "py",
                "-3.11",
                "ai\\capture.py",
                str(id)
            ],
            cwd=project_folder
        )

        return redirect("/students")

    except Exception as e:

        return str(e)



# -------------------------
# Take Attendance
# -------------------------
@app.route("/take_attendance")
def take_attendance():

    project_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "cmd",
            "/k",
            "py",
            "-3.11",
            "ai\\recognize.py"
        ],
        cwd=project_folder
    )

    return redirect("/dashboard")


# -------------------------
# Attendance Records
# -------------------------
@app.route("/attendance")
def attendance():

    records = db.session.query(
        Attendance.id,
        Student.name,
        Student.roll,
        Student.department,
        Attendance.date,
        Attendance.time,
        Attendance.status
    ).join(
        Student,
        Attendance.student_id == Student.id
    ).all()

    return render_template(
        "attendance.html",
        records=records
    )


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        print("DATABASE CREATED")

    app.run(debug=True)



