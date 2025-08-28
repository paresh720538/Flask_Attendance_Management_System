from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps, reduce
import logging
import random
import string
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).hex()
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)

# Models
class User(db.Model):
    """User model representing teachers or admins."""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitter = db.relationship('User', remote_side=[id], backref='submitted_users')

class Department(db.Model):
    """Department model."""
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Course(db.Model):
    """Course model."""
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    semester = db.Column(db.String(20))
    class_hours = db.Column(db.Integer)
    lecture_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Student(db.Model):
    """Student model."""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    class_ = db.Column(db.String(50))
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AttendanceLog(db.Model):
    """AttendanceLog model."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    present = db.Column(db.Boolean, nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    student = db.relationship('Student', backref='attendance_logs', lazy=True)
    course = db.relationship('Course', backref='attendance_logs', lazy=True)

# Create database and first user
with app.app_context():
    db.drop_all()
    db.create_all()
    if User.query.count() == 0:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        admin = User(
            type='admin',
            full_name='Admin User',
            username='admin',
            email='admin@gmail.com',
            password_hash=generate_password_hash(password),
            updated_at=datetime.utcnow()
        )
        db.session.add(admin)
        try:
            db.session.commit()
            logging.info(f'First user created: username=admin, password={password}')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error creating first user: {str(e)}')

# Helper function to validate date
def validate_date(date_text):
    """Validate date string in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Token required decorator
def token_required(f):
    """Decorator to ensure API is protected by JWT token."""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except Exception as e:
            logging.error(f'Invalid token: {str(e)}')
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorator

# Login
@app.route('/api/login', methods=['POST'])
def login():
    """Login API to generate JWT token."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = jwt.encode({'id': user.id}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200

# User APIs
@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    """Create a new user."""
    data = request.get_json()
    required_fields = ['type', 'full_name', 'username', 'email', 'password']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    user = User(
        type=data['type'],
        full_name=data['full_name'],
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        submitted_by=current_user.id,
        updated_at=datetime.utcnow()
    )
    db.session.add(user)
    try:
        db.session.commit()
        return jsonify({
            'id': user.id,
            'type': user.type,
            'full_name': user.full_name,
            'username': user.username,
            'email': user.email
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating user: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users."""
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'type': u.type,
        'full_name': u.full_name,
        'username': u.username,
        'email': u.email
    } for u in users]), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Get a specific user by ID."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'type': user.type,
        'full_name': user.full_name,
        'username': user.username,
        'email': user.email
    }), 200

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """Update a user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        if User.query.filter_by(email=data['email']).first() and user.email != data['email']:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    if 'type' in data:
        user.type = data['type']
    user.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error updating user: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

# Department APIs
@app.route('/api/departments', methods=['POST'])
@token_required
def create_department(current_user):
    """Create a new department."""
    data = request.get_json()
    if not data or 'department_name' not in data:
        return jsonify({'error': 'Missing department_name'}), 400
    dept = Department(
        department_name=data['department_name'],
        submitted_by=current_user.id,
        updated_at=datetime.utcnow()
    )
    db.session.add(dept)
    try:
        db.session.commit()
        return jsonify({
            'id': dept.id,
            'department_name': dept.department_name
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating department: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/departments', methods=['GET'])
@token_required
def get_departments(current_user):
    """Get all departments."""
    depts = Department.query.all()
    return jsonify([{
        'id': d.id,
        'department_name': d.department_name
    } for d in depts]), 200

@app.route('/api/departments/<int:dept_id>', methods=['GET'])
@token_required
def get_department(current_user, dept_id):
    """Get a specific department by ID."""
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({'error': 'Department not found'}), 404
    return jsonify({
        'id': dept.id,
        'department_name': dept.department_name
    }), 200

@app.route('/api/departments/<int:dept_id>', methods=['PUT'])
@token_required
def update_department(current_user, dept_id):
    """Update a department."""
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({'error': 'Department not found'}), 404
    data = request.get_json()
    if 'department_name' in data:
        dept.department_name = data['department_name']
    dept.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({'message': 'Department updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error updating department: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

# Course APIs
@app.route('/api/courses', methods=['POST'])
@token_required
def create_course(current_user):
    """Create a new course."""
    data = request.get_json()
    required_fields = ['course_name', 'department_id']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    if not Department.query.get(data['department_id']):
        return jsonify({'error': 'Department not found'}), 404
    if 'lecture_id' in data and not User.query.get(data['lecture_id']):
        return jsonify({'error': 'Lecture not found'}), 404
    course = Course(
        course_name=data['course_name'],
        department_id=data['department_id'],
        semester=data.get('semester'),
        class_hours=data.get('class_hours'),
        lecture_id=data.get('lecture_id'),
        submitted_by=current_user.id,
        updated_at=datetime.utcnow()
    )
    db.session.add(course)
    try:
        db.session.commit()
        return jsonify({
            'id': course.id,
            'course_name': course.course_name,
            'department_id': course.department_id,
            'semester': course.semester,
            'class_hours': course.class_hours,
            'lecture_id': course.lecture_id
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating course: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/courses', methods=['GET'])
@token_required
def get_courses(current_user):
    """Get all courses."""
    courses = Course.query.all()
    return jsonify([{
        'id': c.id,
        'course_name': c.course_name,
        'department_id': c.department_id,
        'semester': c.semester,
        'class_hours': c.class_hours,
        'lecture_id': c.lecture_id
    } for c in courses]), 200

@app.route('/api/courses/<int:course_id>', methods=['GET'])
@token_required
def get_course(current_user, course_id):
    """Get a specific course by ID."""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    return jsonify({
        'id': course.id,
        'course_name': course.course_name,
        'department_id': course.department_id,
        'semester': course.semester,
        'class_hours': course.class_hours,
        'lecture_id': course.lecture_id
    }), 200

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@token_required
def update_course(current_user, course_id):
    """Update a course."""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    data = request.get_json()
    if 'course_name' in data:
        course.course_name = data['course_name']
    if 'department_id' in data:
        if not Department.query.get(data['department_id']):
            return jsonify({'error': 'Department not found'}), 404
        course.department_id = data['department_id']
    if 'semester' in data:
        course.semester = data['semester']
    if 'class_hours' in data:
        course.class_hours = data['class_hours']
    if 'lecture_id' in data:
        if not User.query.get(data['lecture_id']):
            return jsonify({'error': 'Lecture not found'}), 404
        course.lecture_id = data['lecture_id']
    course.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({'message': 'Course updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error updating course: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

# Student APIs
@app.route('/api/students', methods=['POST'])
@token_required
def create_student(current_user):
    """Create a new student."""
    data = request.get_json()
    required_fields = ['full_name', 'department_id']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    if not Department.query.get(data['department_id']):
        return jsonify({'error': 'Department not found'}), 404
    student = Student(
        full_name=data['full_name'],
        department_id=data['department_id'],
        class_=data.get('class'),
        submitted_by=current_user.id,
        updated_at=datetime.utcnow()
    )
    db.session.add(student)
    try:
        db.session.commit()
        return jsonify({
            'id': student.id,
            'full_name': student.full_name,
            'department_id': student.department_id,
            'class': student.class_
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating student: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/students', methods=['GET'])
@token_required
def get_students(current_user):
    """Get all students."""
    students = Student.query.all()
    return jsonify([{
        'id': s.id,
        'full_name': s.full_name,
        'department_id': s.department_id,
        'class': s.class_
    } for s in students]), 200

@app.route('/api/students/<int:student_id>', methods=['GET'])
@token_required
def get_student(current_user, student_id):
    """Get a specific student by ID."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({
        'id': student.id,
        'full_name': student.full_name,
        'department_id': student.department_id,
        'class': student.class_
    }), 200

@app.route('/api/students/<int:student_id>', methods=['PUT'])
@token_required
def update_student(current_user, student_id):
    """Update a student."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    data = request.get_json()
    if 'full_name' in data:
        student.full_name = data['full_name']
    if 'department_id' in data:
        if not Department.query.get(data['department_id']):
            return jsonify({'error': 'Department not found'}), 404
        student.department_id = data['department_id']
    if 'class' in data:
        student.class_ = data['class']
    student.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({'message': 'Student updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error updating student: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

# AttendanceLog APIs
@app.route('/api/attendance', methods=['POST'])
@token_required
def mark_attendance(current_user):
    """Mark attendance for a student in a course."""
    data = request.get_json()
    required_fields = ['student_id', 'course_id', 'present']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    student = Student.query.get(data['student_id'])
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    course = Course.query.get(data['course_id'])
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    # Optional: Check if attendance already marked today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing = AttendanceLog.query.filter(
        AttendanceLog.student_id == data['student_id'],
        AttendanceLog.course_id == data['course_id'],
        AttendanceLog.updated_at >= today_start
    ).first()
    if existing:
        return jsonify({'error': 'Attendance already marked today'}), 400
    attendance = AttendanceLog(
        student_id=data['student_id'],
        course_id=data['course_id'],
        present=data['present'],
        submitted_by=current_user.id,
        updated_at=datetime.utcnow()
    )
    db.session.add(attendance)
    try:
        db.session.commit()
        return jsonify({
            'id': attendance.id,
            'student_id': attendance.student_id,
            'course_id': attendance.course_id,
            'present': attendance.present,
            'updated_at': attendance.updated_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error marking attendance: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/attendance/<int:student_id>', methods=['GET'])
@token_required
def get_attendance(current_user, student_id):
    """Get attendance records for a student."""
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    attendances = AttendanceLog.query.filter_by(student_id=student_id).all()
    return jsonify([{
        'id': a.id,
        'course_id': a.course_id,
        'present': a.present,
        'updated_at': a.updated_at.isoformat()
    } for a in attendances]), 200

@app.route('/api/report', methods=['GET'])
@token_required
def get_report(current_user):
    """Get attendance report for a date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date or not validate_date(start_date) or not validate_date(end_date):
        return jsonify({'error': 'Invalid or missing date parameters, use YYYY-MM-DD'}), 400
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    if start > end:
        return jsonify({'error': 'Start date must be before end date'}), 400
    attendances = AttendanceLog.query.filter(AttendanceLog.updated_at.between(start, end)).all()
    # Use functional style with reduce for bonus points
    def accumulate_report(report, a):
        name = a.student.full_name
        status = 'present' if a.present else 'absent'
        report[name][status] += 1
        return report
    initial_report = defaultdict(lambda: {'present': 0, 'absent': 0})
    report = reduce(accumulate_report, attendances, initial_report)
    return jsonify(dict(report)), 200

if __name__ == '__main__':
    app.run(debug=True)