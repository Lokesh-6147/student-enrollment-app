# Student Enrollment Management System

## 1. Project Overview

The Student Enrollment Management System is a web-based application developed using Python, Flask, and MySQL.

The application helps manage student details, course information, and student enrollments in an organized way. It provides a simple user interface to add, view, update, search, and delete records.

The application is designed to reduce manual work and maintain student enrollment information efficiently.

---

## 2. Technologies Used

### Frontend

- HTML
- CSS
- Bootstrap
- Bootstrap Icons
- Jinja2 Templates

### Backend

- Python
- Flask

### Database

- MySQL

### Development Tools

- Visual Studio Code
- MySQL
- Python Virtual Environment
- Web Browser

---

## 3. Main Features

The application provides the following features:

- Dashboard with summary information
- Student management
- Course management
- Enrollment management
- Add student details
- Edit student details
- Delete student details
- Add course details
- Edit course details
- Delete course details
- Create new enrollments
- Edit enrollment details
- Delete enrollment details
- Search students
- Search courses
- Search enrollments
- Filter enrollments by status
- Success and error messages
- Delete confirmation messages
- Form validation
- Duplicate active enrollment protection

---

## 4. Application Modules

### 4.1 Dashboard

The dashboard displays an overview of the application.

It shows:

- Total number of students
- Total number of courses
- Total number of enrollments
- Number of active enrollments
- Recent enrollment records
- Enrollment summary
- Quick action buttons

---

### 4.2 Student Management

The Student Management module is used to manage student information.

Users can:

- View all students
- Add a new student
- Edit existing student details
- Delete a student
- Search students by name or other available details

Student information includes:

- First name
- Last name
- Email
- Phone number
- Gender
- Date of birth
- Qualification
- Address

---

### 4.3 Course Management

The Course Management module is used to manage available courses.

Users can:

- View all courses
- Add a new course
- Edit course information
- Delete a course
- Search courses

Course information includes:

- Course name
- Course duration
- Course fee
- Course description

---

### 4.4 Enrollment Management

The Enrollment Management module is used to register students for courses.

Users can:

- View all enrollments
- Create a new enrollment
- Edit enrollment details
- Delete an enrollment
- Search enrollments
- Filter enrollments by status

Enrollment information includes:

- Student
- Course
- Enrollment date
- Enrollment status

Available enrollment statuses are:

- Active
- Completed
- Cancelled

---

## 5. Database Structure

The application uses a MySQL database named:

```text
student_enrolment