from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key for flash messages
app.config["SECRET_KEY"] = "student-management-secret"

# SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Student table
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)


# Home page
@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    if search:
        students = Student.query.filter(
            (Student.name.ilike(f"%{search}%")) |
            (Student.roll_number.ilike(f"%{search}%")) |
            (Student.department.ilike(f"%{search}%"))
        ).all()
    else:
        students = Student.query.order_by(Student.id.desc()).all()

    total_students = Student.query.count()

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        search=search
    )


# Add student
@app.route("/add", methods=["POST"])
def add_student():

    name = request.form.get("name", "").strip()
    roll_number = request.form.get("roll_number", "").strip()
    department = request.form.get("department", "").strip()

    if not name or not roll_number or not department:
        flash("Please fill all fields.", "error")
        return redirect(url_for("index"))

    existing_student = Student.query.filter_by(
        roll_number=roll_number
    ).first()

    if existing_student:
        flash("Roll number already exists.", "error")
        return redirect(url_for("index"))

    new_student = Student(
        name=name,
        roll_number=roll_number,
        department=department
    )

    db.session.add(new_student)
    db.session.commit()

    flash("Student added successfully!", "success")

    return redirect(url_for("index"))


# Delete student
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):

    student = db.session.get(Student, id)

    if student:
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted successfully!", "success")
    else:
        flash("Student not found.", "error")

    return redirect(url_for("index"))


# Edit student page
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    student = db.session.get(Student, id)

    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not roll_number or not department:
            flash("Please fill all fields.", "error")
            return redirect(url_for("edit_student", id=id))

        # Check whether another student has the same roll number
        existing_student = Student.query.filter(
            Student.roll_number == roll_number,
            Student.id != id
        ).first()

        if existing_student:
            flash("Roll number already exists.", "error")
            return redirect(url_for("edit_student", id=id))

        student.name = name
        student.roll_number = roll_number
        student.department = department

        db.session.commit()

        flash("Student updated successfully!", "success")

        return redirect(url_for("index"))

    return render_template("edit.html", student=student)


# Create database automatically
with app.app_context():
    db.create_all()


# Run application
if __name__ == "__main__":
    app.run(debug=True)