
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# HOME PAGE
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')


# ==========================================
# GET ONE SAMPLE STUDENT
# ==========================================
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-0279",
        "name": "John Mark Alarba",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# ==========================================
# GREETING API
# ==========================================
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==========================================
# GET ALL STUDENTS FROM DATABASE
# ==========================================
@app.route('/students')
def get_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            'SELECT * FROM students ORDER BY id'
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# GET ONE STUDENT BY DATABASE ID
# ==========================================
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify(dict(student))

    finally:
        conn.close()


# ==========================================
# ADDITIONAL API: GET STUDENTS BY YEAR LEVEL
# Example: /students/year/2
# ==========================================
@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    conn = get_db_connection()

    try:
        students = conn.execute(
            'SELECT * FROM students WHERE year = ? ORDER BY id',
            (year,)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# RUN FLASK APPLICATION
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
