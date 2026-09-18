from flask import Flask, render_template, request, redirect, url_for, flash
from db_connection import get_connection
import re
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


# ---------------- HOME ----------------
@app.route("/")
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Total students
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]

    # Total courses
    cursor.execute("SELECT COUNT(*) AS total FROM courses")
    total_courses = cursor.fetchone()["total"]

    # Total enrollments
    cursor.execute("SELECT COUNT(*) AS total FROM enrollments")
    total_enrollments = cursor.fetchone()["total"]

    # Active enrollments
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM enrollments
        WHERE status = 'Active'
    """)
    active_enrollments = cursor.fetchone()["total"]

    # Enrollment summary
    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM enrollments
        GROUP BY status
    """)

    enrollment_summary = cursor.fetchall()

    # Recent enrollments
    cursor.execute("""
        SELECT
            e.enrollment_id,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            c.course_name,
            e.enrollment_date,
            e.status
        FROM enrollments e
        JOIN students s
            ON e.student_id = s.student_id
        JOIN courses c
            ON e.course_id = c.course_id
        ORDER BY e.enrollment_id DESC
        LIMIT 5
    """)

    recent_enrollments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        total_students=total_students,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        active_enrollments=active_enrollments,
        enrollment_summary=enrollment_summary,
        recent_enrollments=recent_enrollments
    )

# ---------------- STUDENTS ----------------

@app.route("/students")
def students():

    search = request.args.get("search", "").strip()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        query = """
            SELECT *
            FROM students
            WHERE
                first_name LIKE %s
                OR last_name LIKE %s
                OR email LIKE %s
                OR phone LIKE %s
            ORDER BY student_id DESC
        """

        search_value = "%" + search + "%"

        cursor.execute(
            query,
            (
                search_value,
                search_value,
                search_value,
                search_value
            )
        )

    else:

        cursor.execute("""
            SELECT *
            FROM students
            ORDER BY student_id DESC
        """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "students.html",
        students=students,
        search=search
    )


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        qualification = request.form.get("qualification", "").strip()
        passing_year = request.form.get("passing_year", "").strip()

        # Required fields
        if not first_name or not last_name or not email or not phone:
            flash(
                "First name, last name, email and phone are required.",
                "danger"
            )
            return redirect(url_for("add_student"))

        # First name validation
        if not re.fullmatch(r"[A-Za-z ]+", first_name):
            flash(
                "First name should contain only letters and spaces.",
                "danger"
            )
            return redirect(url_for("add_student"))

        # Last name validation
        if not re.fullmatch(r"[A-Za-z ]+", last_name):
            flash(
                "Last name should contain only letters and spaces.",
                "danger"
            )
            return redirect(url_for("add_student"))

        # Email validation
        if not re.fullmatch(
            r"^[\w\.-]+@[\w\.-]+\.\w+$",
            email
        ):
            flash(
                "Please enter a valid email address.",
                "danger"
            )
            return redirect(url_for("add_student"))

        # Phone validation
        if not re.fullmatch(r"\d{10}", phone):
            flash(
                "Phone number must contain exactly 10 digits.",
                "danger"
            )
            return redirect(url_for("add_student"))

        # Pincode validation
        if pincode and not re.fullmatch(r"\d{6}", pincode):
            flash(
                "Pincode must contain exactly 6 digits.",
                "danger"
            )
            return redirect(url_for("add_student"))

        # Passing year validation
        if passing_year and not passing_year.isdigit():
            flash(
                "Passing year must contain only numbers.",
                "danger"
            )
            return redirect(url_for("add_student"))

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # Check duplicate email
            cursor.execute("""
                SELECT student_id
                FROM students
                WHERE email = %s
            """, (email,))

            existing_student = cursor.fetchone()

            if existing_student:
                flash(
                    "A student is already registered with this email.",
                    "danger"
                )
                return redirect(url_for("add_student"))

            # Insert student
            cursor.execute("""
                INSERT INTO students
                (
                    first_name,
                    last_name,
                    dob,
                    gender,
                    email,
                    phone,
                    address,
                    city,
                    state,
                    pincode,
                    qualification,
                    passing_year
                )
                VALUES
                (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """, (
                first_name,
                last_name,
                dob if dob else None,
                gender,
                email,
                phone,
                address,
                city,
                state,
                pincode,
                qualification,
                int(passing_year) if passing_year else None
            ))

            connection.commit()

            flash(
                "Student added successfully.",
                "success"
            )

        except Exception as e:

            connection.rollback()

            flash(
    "Unable to add student. Please try again.",
    "danger"
)

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("students"))

    return render_template("add_student.html")

# ---------------- EDIT STUDENT ----------------

@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    # Handle form submission
    if request.method == "POST":

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        qualification = request.form.get("qualification", "").strip()
        passing_year = request.form.get("passing_year", "").strip()

        # Required fields
        if not first_name or not last_name or not email or not phone:
            flash(
                "First name, last name, email and phone are required.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        # First name validation
        if not re.fullmatch(r"[A-Za-z ]+", first_name):
            flash(
                "First name should contain only letters and spaces.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        # Last name validation
        if not re.fullmatch(r"[A-Za-z ]+", last_name):
            flash(
                "Last name should contain only letters and spaces.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        # Email validation
        if not re.fullmatch(
            r"^[\w\.-]+@[\w\.-]+\.\w+$",
            email
        ):
            flash(
                "Please enter a valid email address.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        # Phone validation
        if not re.fullmatch(r"\d{10}", phone):
            flash(
                "Phone number must contain exactly 10 digits.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        # Pincode validation
        if pincode and not re.fullmatch(r"\d{6}", pincode):
            flash(
                "Pincode must contain exactly 6 digits.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        # Passing year validation
        if passing_year and not passing_year.isdigit():
            flash(
                "Passing year must contain only numbers.",
                "danger"
            )
            return redirect(
                url_for("edit_student", student_id=student_id)
            )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # Check duplicate email
            cursor.execute("""
                SELECT student_id
                FROM students
                WHERE email = %s
                AND student_id != %s
            """, (email, student_id))

            existing_student = cursor.fetchone()

            if existing_student:
                flash(
                    "Another student is already registered with this email.",
                    "danger"
                )
                return redirect(
                    url_for("edit_student", student_id=student_id)
                )

            # Update student
            cursor.execute("""
                UPDATE students
                SET
                    first_name = %s,
                    last_name = %s,
                    dob = %s,
                    gender = %s,
                    email = %s,
                    phone = %s,
                    address = %s,
                    city = %s,
                    state = %s,
                    pincode = %s,
                    qualification = %s,
                    passing_year = %s
                WHERE student_id = %s
            """, (
                first_name,
                last_name,
                dob if dob else None,
                gender,
                email,
                phone,
                address,
                city,
                state,
                pincode,
                qualification,
                int(passing_year) if passing_year else None,
                student_id
            ))

            connection.commit()

            flash(
                "Student details updated successfully.",
                "success"
            )

        except Exception as e:

            connection.rollback()

            flash(
                "Error updating student: " + str(e),
                "danger"
            )

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("students"))

    # Display existing student details
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM students
            WHERE student_id = %s
        """, (student_id,))

        student = cursor.fetchone()

    finally:

        cursor.close()
        connection.close()

    # Student not found
    if not student:
        flash(
            "Student not found.",
            "danger"
        )
        return redirect(url_for("students"))

    return render_template(
        "edit_student.html",
        student=student
    )
# ---------------- DELETE STUDENT ----------------

@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check whether the student exists
        cursor.execute(
            """
            SELECT student_id
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:

            flash(
                "Student not found.",
                "warning"
            )

            return redirect(url_for("students"))

        # Delete the student
        cursor.execute(
            """
            DELETE FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        connection.commit()

        flash(
            "Student deleted successfully. Related enrollment records were also removed.",
            "success"
        )

    except Exception:

        connection.rollback()

        flash(
            "Unable to delete the student. Please try again.",
            "danger"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(url_for("students"))


# ---------------- COURSES ----------------

# ---------------- COURSES ----------------

@app.route("/courses")
def courses():

    search = request.args.get("search", "").strip()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        query = """
            SELECT *
            FROM courses
            WHERE
                course_name LIKE %s
                OR duration LIKE %s
            ORDER BY course_id DESC
        """

        search_value = "%" + search + "%"

        cursor.execute(
            query,
            (
                search_value,
                search_value
            )
        )

    else:

        cursor.execute("""
            SELECT *
            FROM courses
            ORDER BY course_id DESC
        """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "courses.html",
        courses=courses,
        search=search
    )


# ---------------- ADD COURSE ----------------
@app.route("/add_course", methods=["GET", "POST"])
def add_course():

    if request.method == "POST":

        course_name = request.form["course_name"].strip()
        duration = request.form["duration"].strip()
        fee = request.form["fee"].strip()
        description = request.form["description"].strip()


        # -----------------------------
        # Required field validation
        # -----------------------------

        if not course_name or not duration or not fee:

            flash(
                "Please fill all required course fields.",
                "warning"
            )

            return redirect(url_for("add_course"))


        # -----------------------------
        # Course name validation
        # -----------------------------

        if not re.fullmatch(r"[A-Za-z0-9 .&+-]+", course_name):

            flash(
                "Course name contains invalid characters.",
                "warning"
            )

            return redirect(url_for("add_course"))


        # -----------------------------
        # Duration validation
        # -----------------------------

        if len(duration) > 50:

            flash(
                "Duration is too long.",
                "warning"
            )

            return redirect(url_for("add_course"))


        # -----------------------------
        # Fee validation
        # -----------------------------

        try:

            fee_value = float(fee)

            if fee_value <= 0:

                flash(
                    "Course fee must be greater than 0.",
                    "warning"
                )

                return redirect(url_for("add_course"))

        except ValueError:

            flash(
                "Course fee must be a valid number.",
                "warning"
            )

            return redirect(url_for("add_course"))


        connection = get_connection()
        cursor = connection.cursor()


        # -----------------------------
        # Duplicate course check
        # -----------------------------

        cursor.execute(
            """
            SELECT course_id
            FROM courses
            WHERE LOWER(course_name) = LOWER(%s)
            """,
            (course_name,)
        )

        existing_course = cursor.fetchone()


        if existing_course:

            cursor.close()
            connection.close()

            flash(
                "A course with this name already exists.",
                "warning"
            )

            return redirect(url_for("add_course"))


        # -----------------------------
        # Insert course
        # -----------------------------

        insert_query = """
            INSERT INTO courses
            (
                course_name,
                duration,
                fee,
                description
            )
            VALUES
            (
                %s, %s, %s, %s
            )
        """


        values = (
            course_name,
            duration,
            fee_value,
            description
        )


        try:

            cursor.execute(
                insert_query,
                values
            )

            connection.commit()

            flash(
                "Course added successfully!",
                "success"
            )

        except Exception as e:

            connection.rollback()

            flash(
                "Error adding course: " + str(e),
                "danger"
            )

        finally:

            cursor.close()
            connection.close()


        return redirect(url_for("courses"))


    return render_template("add_course.html")

# ---------------- EDIT COURSE ----------------
# ---------------- EDIT COURSE ----------------

@app.route("/edit_course/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):

    # Handle form submission
    if request.method == "POST":

        course_name = request.form.get("course_name", "").strip()
        duration = request.form.get("duration", "").strip()
        fee = request.form.get("fee", "").strip()
        description = request.form.get("description", "").strip()

        # Required fields
        if not course_name or not duration or not fee:
            flash(
                "Course name, duration and fee are required.",
                "danger"
            )
            return redirect(
                url_for("edit_course", course_id=course_id)
            )

        # Course name validation
        if not re.fullmatch(r"[A-Za-z0-9 .&+-]+", course_name):
            flash(
                "Course name contains invalid characters.",
                "danger"
            )
            return redirect(
                url_for("edit_course", course_id=course_id)
            )

        # Duration validation
        if len(duration) > 50:
            flash(
                "Duration must not exceed 50 characters.",
                "danger"
            )
            return redirect(
                url_for("edit_course", course_id=course_id)
            )

        # Fee validation
        try:
            fee_value = float(fee)

            if fee_value <= 0:
                flash(
                    "Course fee must be greater than 0.",
                    "danger"
                )
                return redirect(
                    url_for("edit_course", course_id=course_id)
                )

        except ValueError:
            flash(
                "Course fee must be a valid number.",
                "danger"
            )
            return redirect(
                url_for("edit_course", course_id=course_id)
            )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # Check duplicate course name
            cursor.execute("""
                SELECT course_id
                FROM courses
                WHERE LOWER(course_name) = LOWER(%s)
                AND course_id != %s
            """, (course_name, course_id))

            existing_course = cursor.fetchone()

            if existing_course:
                flash(
                    "Another course already exists with this name.",
                    "danger"
                )
                return redirect(
                    url_for("edit_course", course_id=course_id)
                )

            # Update course
            cursor.execute("""
                UPDATE courses
                SET
                    course_name = %s,
                    duration = %s,
                    fee = %s,
                    description = %s
                WHERE course_id = %s
            """, (
                course_name,
                duration,
                fee_value,
                description,
                course_id
            ))

            connection.commit()

            flash(
                "Course details updated successfully.",
                "success"
            )

        except Exception as e:

            connection.rollback()

            flash(
                "Error updating course: " + str(e),
                "danger"
            )

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("courses"))

    # Display existing course details
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM courses
            WHERE course_id = %s
        """, (course_id,))

        course = cursor.fetchone()

    finally:

        cursor.close()
        connection.close()

    # Course not found
    if not course:
        flash(
            "Course not found.",
            "danger"
        )
        return redirect(url_for("courses"))

    return render_template(
        "edit_course.html",
        course=course
    )
# ---------------- DELETE COURSE ----------------

@app.route("/delete_course/<int:course_id>")
def delete_course(course_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check whether the course exists
        cursor.execute(
            """
            SELECT course_id
            FROM courses
            WHERE course_id = %s
            """,
            (course_id,)
        )

        course = cursor.fetchone()

        if not course:

            flash(
                "Course not found.",
                "warning"
            )

            return redirect(url_for("courses"))

        # Delete the course
        cursor.execute(
            """
            DELETE FROM courses
            WHERE course_id = %s
            """,
            (course_id,)
        )

        connection.commit()

        flash(
            "Course deleted successfully. Related enrollment records were also removed.",
            "success"
        )

    except Exception:

        connection.rollback()

        flash(
            "Unable to delete the course. Please try again.",
            "danger"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(url_for("courses"))


# ---------------- ENROLLMENTS ----------------
@app.route("/enrollments")
def enrollments():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            e.enrollment_id,
            CONCAT(s.first_name, ' ', s.last_name) AS student_name,
            c.course_name,
            e.enrollment_date,
            e.status
        FROM enrollments e
        JOIN students s
            ON e.student_id = s.student_id
        JOIN courses c
            ON e.course_id = c.course_id
        WHERE 1=1
    """

    params = []

    # Search by student name or course name
    if search:

        query += """
            AND (
                CONCAT(s.first_name, ' ', s.last_name) LIKE %s
                OR c.course_name LIKE %s
            )
        """

        search_value = "%" + search + "%"

        params.extend([
            search_value,
            search_value
        ])

    # Filter by enrollment status
    if status:

        query += """
            AND e.status = %s
        """

        params.append(status)

    query += """
        ORDER BY e.enrollment_id DESC
    """

    cursor.execute(
        query,
        tuple(params)
    )

    enrollments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "enrollments.html",
        enrollments=enrollments,
        search=search,
        status=status
    )

# ---------------- EDIT ENROLLMENT ----------------

# ---------------- EDIT ENROLLMENT ----------------

@app.route("/edit_enrollment/<int:enrollment_id>", methods=["GET", "POST"])
def edit_enrollment(enrollment_id):

    # Handle form submission
    if request.method == "POST":

        student_id = request.form.get("student_id", "").strip()
        course_id = request.form.get("course_id", "").strip()
        enrollment_date = request.form.get("enrollment_date", "").strip()
        status = request.form.get("status", "").strip()

        # Required fields
        if not student_id or not course_id or not enrollment_date or not status:
            flash(
                "Student, course, enrollment date and status are required.",
                "danger"
            )
            return redirect(
                url_for("edit_enrollment", enrollment_id=enrollment_id)
            )

        # Student ID validation
        if not student_id.isdigit():
            flash(
                "Invalid student selection.",
                "danger"
            )
            return redirect(
                url_for("edit_enrollment", enrollment_id=enrollment_id)
            )

        # Course ID validation
        if not course_id.isdigit():
            flash(
                "Invalid course selection.",
                "danger"
            )
            return redirect(
                url_for("edit_enrollment", enrollment_id=enrollment_id)
            )

        # Status validation
        allowed_statuses = ["Active", "Completed", "Cancelled"]

        if status not in allowed_statuses:
            flash(
                "Invalid enrollment status.",
                "danger"
            )
            return redirect(
                url_for("edit_enrollment", enrollment_id=enrollment_id)
            )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # Check whether student exists
            cursor.execute("""
                SELECT student_id
                FROM students
                WHERE student_id = %s
            """, (int(student_id),))

            student = cursor.fetchone()

            if not student:
                flash(
                    "Selected student does not exist.",
                    "danger"
                )
                return redirect(
                    url_for("edit_enrollment", enrollment_id=enrollment_id)
                )

            # Check whether course exists
            cursor.execute("""
                SELECT course_id
                FROM courses
                WHERE course_id = %s
            """, (int(course_id),))

            course = cursor.fetchone()

            if not course:
                flash(
                    "Selected course does not exist.",
                    "danger"
                )
                return redirect(
                    url_for("edit_enrollment", enrollment_id=enrollment_id)
                )

            # Check duplicate active enrollment
            if status == "Active":

                cursor.execute("""
                    SELECT enrollment_id
                    FROM enrollments
                    WHERE student_id = %s
                    AND course_id = %s
                    AND status = 'Active'
                    AND enrollment_id != %s
                """, (
                    int(student_id),
                    int(course_id),
                    enrollment_id
                ))

                existing_enrollment = cursor.fetchone()

                if existing_enrollment:
                    flash(
                        "This student is already actively enrolled in this course.",
                        "danger"
                    )
                    return redirect(
                        url_for(
                            "edit_enrollment",
                            enrollment_id=enrollment_id
                        )
                    )

            # Update enrollment
            cursor.execute("""
                UPDATE enrollments
                SET
                    student_id = %s,
                    course_id = %s,
                    enrollment_date = %s,
                    status = %s
                WHERE enrollment_id = %s
            """, (
                int(student_id),
                int(course_id),
                enrollment_date,
                status,
                enrollment_id
            ))

            connection.commit()

            flash(
                "Enrollment details updated successfully.",
                "success"
            )

        except Exception as e:

            connection.rollback()

            flash(
                "Error updating enrollment: " + str(e),
                "danger"
            )

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("enrollments"))

    # Display existing enrollment details
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # Get enrollment
        cursor.execute("""
            SELECT *
            FROM enrollments
            WHERE enrollment_id = %s
        """, (enrollment_id,))

        enrollment = cursor.fetchone()

        # Get students
        cursor.execute("""
            SELECT
                student_id,
                first_name,
                last_name
            FROM students
            ORDER BY first_name, last_name
        """)

        students = cursor.fetchall()

        # Get courses
        cursor.execute("""
            SELECT
                course_id,
                course_name
            FROM courses
            ORDER BY course_name
        """)

        courses = cursor.fetchall()

    finally:

        cursor.close()
        connection.close()

    # Enrollment not found
    if not enrollment:
        flash(
            "Enrollment not found.",
            "danger"
        )
        return redirect(url_for("enrollments"))

    return render_template(
        "edit_enrollment.html",
        enrollment=enrollment,
        students=students,
        courses=courses
    )

# ---------------- DELETE ENROLLMENT ----------------

@app.route("/delete_enrollment/<int:enrollment_id>")
def delete_enrollment(enrollment_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM enrollments
            WHERE enrollment_id = %s
            """,
            (enrollment_id,)
        )

        connection.commit()

        flash(
            "Enrollment deleted successfully!",
            "success"
        )

    except Exception as e:

        connection.rollback()

        flash(
            "Error deleting enrollment: " + str(e),
            "danger"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(url_for("enrollments"))
# ---------------- ADD ENROLLMENT ----------------
@app.route("/add_enrollment", methods=["GET", "POST"])
def add_enrollment():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form.get("student_id", "").strip()
        course_id = request.form.get("course_id", "").strip()
        enrollment_date = request.form.get("enrollment_date", "").strip()
        status = request.form.get("status", "").strip()


        # --------------------------------
        # Required field validation
        # --------------------------------

        if not student_id or not course_id or not enrollment_date or not status:

            cursor.close()
            connection.close()

            flash(
                "Please fill all required enrollment fields.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Student ID validation
        # --------------------------------

        if not student_id.isdigit():

            cursor.close()
            connection.close()

            flash(
                "Please select a valid student.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Course ID validation
        # --------------------------------

        if not course_id.isdigit():

            cursor.close()
            connection.close()

            flash(
                "Please select a valid course.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Status validation
        # --------------------------------

        allowed_statuses = [
            "Active",
            "Completed",
            "Cancelled"
        ]

        if status not in allowed_statuses:

            cursor.close()
            connection.close()

            flash(
                "Invalid enrollment status.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Check student exists
        # --------------------------------

        cursor.execute(
            """
            SELECT student_id
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        student_exists = cursor.fetchone()

        if not student_exists:

            cursor.close()
            connection.close()

            flash(
                "Selected student does not exist.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Check course exists
        # --------------------------------

        cursor.execute(
            """
            SELECT course_id
            FROM courses
            WHERE course_id = %s
            """,
            (course_id,)
        )

        course_exists = cursor.fetchone()

        if not course_exists:

            cursor.close()
            connection.close()

            flash(
                "Selected course does not exist.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Duplicate active enrollment check
        # --------------------------------

        cursor.execute(
            """
            SELECT enrollment_id
            FROM enrollments
            WHERE student_id = %s
            AND course_id = %s
            AND status = 'Active'
            """,
            (student_id, course_id)
        )

        existing_enrollment = cursor.fetchone()


        if existing_enrollment:

            cursor.close()
            connection.close()

            flash(
                "Student is already actively enrolled in this course.",
                "warning"
            )

            return redirect(url_for("add_enrollment"))


        # --------------------------------
        # Insert enrollment
        # --------------------------------

        insert_query = """
            INSERT INTO enrollments
            (
                student_id,
                course_id,
                enrollment_date,
                status
            )
            VALUES
            (
                %s, %s, %s, %s
            )
        """

        values = (
            student_id,
            course_id,
            enrollment_date,
            status
        )


        try:

            cursor.execute(
                insert_query,
                values
            )

            connection.commit()

            flash(
                "Enrollment added successfully!",
                "success"
            )

        except Exception as e:

            connection.rollback()

            flash(
                "Error adding enrollment: " + str(e),
                "danger"
            )

        finally:

            cursor.close()
            connection.close()


        return redirect(url_for("enrollments"))


    # --------------------------------
    # Load students and courses
    # --------------------------------

    cursor.execute(
        """
        SELECT
            student_id,
            first_name,
            last_name
        FROM students
        ORDER BY first_name
        """
    )

    students = cursor.fetchall()


    cursor.execute(
        """
        SELECT
            course_id,
            course_name
        FROM courses
        ORDER BY course_name
        """
    )

    courses = cursor.fetchall()


    cursor.close()
    connection.close()


    return render_template(
        "add_enrollment.html",
        students=students,
        courses=courses
    )

# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run()