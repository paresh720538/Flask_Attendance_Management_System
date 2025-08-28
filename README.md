# Flask_Attendance_Management_System
This is an Attendance management system using  Flask Framework.

APIS curl- 

# Attendance Management System API cURL Commands
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
