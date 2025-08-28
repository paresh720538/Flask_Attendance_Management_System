Flask Attendance Management System
This is an Attendance Management System backend built using the Flask framework. It provides a RESTful API to manage users, departments, courses, students, and attendance records. The system includes JWT-based authentication, logging, and error handling, with a SQLite database for data persistence.
Features

User Management: Create, retrieve, and update users (admins and teachers).
Department Management: Manage departments for courses and students.
Course Management: Create, retrieve, and update course details.
Student Management: Manage student records.
Attendance Tracking: Mark and retrieve attendance for students in specific courses.
Reporting: Generate attendance reports for a specified date range.
Security: JWT-based authentication for all APIs except login.
Logging: Logs errors and the initial admin user credentials.
Functional Programming: Used in report generation for efficiency.
First User Creation: Automatically creates an admin user on first run, with credentials logged.

Prerequisites

Python 3.8+
virtualenv or poetry for managing dependencies
curl or Postman for testing APIs
Git for version control

Setup Instructions

Clone the Repository
git clone <repository-url>
cd Flask_Attendance_Management_System


Create a Virtual EnvironmentUsing virtualenv:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Alternatively, using poetry:
poetry install
poetry shell


Install DependenciesCreate a requirements.txt file with the following content:
flask
flask_sqlalchemy
pyjwt
werkzeug

Install dependencies:
pip install -r requirements.txt


Run the Application
python app.py

The application will start on http://localhost:5000. On first run, an admin user is created with:


Verify Admin User CreationCheck the console logs for the admin credentials:
INFO:root:First user created: username=admin, password=HDGRK1cPciJd



API Usage
Authentication

All endpoints except /api/login require a JWT token.
Obtain the token by calling the /api/login endpoint.
Include the token in the Authorization header: Authorization: <JWT_TOKEN>.

Testing APIs

Use the curl commands below to test the APIs.
Replace <JWT_TOKEN> with the token from the /api/login response.
Ensure the server is running (python app.py) before executing commands.
Test endpoints in the following order to satisfy dependencies:
Login to get the JWT token.
Create a department.
Create a user (teacher).
Create a course.
Create a student.
Mark attendance.
Retrieve attendance and reports.



API cURL Commands
# Base URL: http://localhost:5000
# Note: Replace <JWT_TOKEN> with the actual token from the /api/login response

# 1. Login
# Authenticate user and obtain JWT token
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "HDGRK1cPciJd"}'

# 2. User APIs

# Create a new user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"type": "teacher", "full_name": "John Doe", "username": "johndoe", "email": "john.doe@example.com", "password": "securepassword123"}'

# Get all users
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: <JWT_TOKEN>"

# Get user by ID (e.g., user_id=2)
curl -X GET http://localhost:5000/api/users/2 \
  -H "Authorization: <JWT_TOKEN>"

# Update user (e.g., user_id=2)
curl -X PUT http://localhost:5000/api/users/2 \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"full_name": "John A. Doe", "email": "john.a.doe@example.com", "password": "newpassword123", "type": "admin"}'

# 3. Department APIs

# Create a new department
curl -X POST http://localhost:5000/api/departments \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"department_name": "Computer Science"}'

# Get all departments
curl -X GET http://localhost:5000/api/departments \
  -H "Authorization: <JWT_TOKEN>"

# Get department by ID (e.g., dept_id=1)
curl -X GET http://localhost:5000/api/departments/1 \
  -H "Authorization: <JWT_TOKEN>"

# Update department (e.g., dept_id=1)
curl -X PUT http://localhost:5000/api/departments/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"department_name": "Computer Engineering"}'

# 4. Course APIs

# Create a new course
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"course_name": "Introduction to Python", "department_id": 1, "semester": "Fall 2025", "class_hours": 30, "lecture_id": 2}'

# Get all courses
curl -X GET http://localhost:5000/api/courses \
  -H "Authorization: <JWT_TOKEN>"

# Get course by ID (e.g., course_id=1)
curl -X GET http://localhost:5000/api/courses/1 \
  -H "Authorization: <JWT_TOKEN>"

# Update course (e.g., course_id=1)
curl -X PUT http://localhost:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"course_name": "Advanced Python", "semester": "Spring 2026"}'

# 5. Student APIs

# Create a new student
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"full_name": "Jane Smith", "department_id": 1, "class": "Freshman"}'

# Get all students
curl -X GET http://localhost:5000/api/students \
  -H "Authorization: <JWT_TOKEN>"

# Get student by ID (e.g., student_id=1)
curl -X GET http://localhost:5000/api/students/1 \
  -H "Authorization: <JWT_TOKEN>"

# Update student (e.g., student_id=1)
curl -X PUT http://localhost:5000/api/students/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"full_name": "Jane A. Smith", "class": "Sophomore"}'

# 6. Attendance APIs

# Mark attendance
curl -X POST http://localhost:5000/api/attendance \
  -H "Content-Type: application/json" \
  -H "Authorization: <JWT_TOKEN>" \
  -d '{"student_id": 1, "course_id": 1, "present": true}'

# Get attendance for a student (e.g., student_id=1)
curl -X GET http://localhost:5000/api/attendance/1 \
  -H "Authorization: <JWT_TOKEN>"

# Get attendance report
curl -X GET "http://localhost:5000/api/report?start_date=2025-08-01&end_date=2025-08-28" \
  -H "Authorization: <JWT_TOKEN>"

Error Handling

401 Unauthorized: Missing or invalid JWT token.
400 Bad Request: Missing required fields or invalid data (e.g., duplicate username/email, invalid date format).
404 Not Found: Resource (user, department, course, student) not found.
500 Internal Server Error: Database or server issues (check logs for details).

Logging

Logs are output to the console.
The initial admin user's credentials are logged on first run.
Errors (e.g., database failures, invalid tokens) are logged with details.

Submission

The project is hosted on a Git repository (GitLab/GitHub).
Invite eshwar.natarajan@nuagebiz.tech to the repository for review.

Notes

The application uses SQLite for simplicity, but you can modify SQLALCHEMY_DATABASE_URI for other databases.
The reduce function is used in the /api/report endpoint for functional programming.
No delete operations are implemented as per the assignment requirements.
For production, consider securing the SECRET_KEY and using a more robust database.
