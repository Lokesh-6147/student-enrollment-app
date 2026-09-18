CREATE DATABASE IF NOT EXISTS student_enrolment;

USE student_enrolment;


-- ============================================
-- STUDENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,

    dob DATE,

    gender VARCHAR(20),

    email VARCHAR(150) NOT NULL UNIQUE,

    phone VARCHAR(15) NOT NULL,

    address TEXT,

    city VARCHAR(100),

    state VARCHAR(100),

    pincode VARCHAR(10),

    qualification VARCHAR(150),

    passing_year INT
);


-- ============================================
-- COURSES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,

    course_name VARCHAR(150) NOT NULL UNIQUE,

    duration VARCHAR(50) NOT NULL,

    fee DECIMAL(10, 2) NOT NULL,

    description TEXT
);


-- ============================================
-- ENROLLMENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    course_id INT NOT NULL,

    enrollment_date DATE NOT NULL,

    status VARCHAR(20) NOT NULL,

    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollment_course
        FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
        ON DELETE CASCADE
);