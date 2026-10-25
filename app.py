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
# GET /student
# ==========================================
@app.route('/student', methods=['GET'])
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
# GET /hello?name=John
# ==========================================
@app.route('/hello', methods=['GET'])
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==========================================
# GET ALL STUDENTS
# GET /students
# ==========================================
@app.route('/students', methods=['GET'])
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
# STEP 6: READ-ONLY STUDENTS API
# GET /api/students
# Returns all practice records as JSON
# ==========================================
@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            'SELECT * FROM students ORDER BY id'
        ).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


# ==========================================
# GET ONE STUDENT BY DATABASE ID
# GET /students/<id>
# ==========================================
@app.route('/students/<int:id>', methods=['GET'])
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
# GET STUDENTS BY YEAR LEVEL
# GET /students/year/<year>
# Example: /students/year/2
# ==========================================
@app.route('/students/year/<int:year>', methods=['GET'])
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
# CREATE A NEW STUDENT
# POST /api/students
# ==========================================
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    required_fields = [
        'student_id', 'name', 'program', 'year', 'section'
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({
                "error": f"Missing field: {field}"
            }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section']
            )
        )

        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "message": "Student added",
            "id": new_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Could not add student. Check for duplicate student IDs."
        }), 400

    finally:
        conn.close()


# ==========================================
# UPDATE A STUDENT
# PUT /api/students/<id>
# ==========================================
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    required_fields = [
        'student_id', 'name', 'program', 'year', 'section'
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({
                "error": f"Missing field: {field}"
            }), 400

    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT id FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.execute(
            """
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
            """,
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                id
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student updated"
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Could not update student. Check for duplicate student IDs."
        }), 400

    finally:
        conn.close()


# ==========================================
# DELETE A STUDENT
# DELETE /api/students/<id>
# ==========================================
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            'DELETE FROM students WHERE id = ?',
            (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted"
        }), 200

    finally:
        conn.close()


# ==========================================
# RUN FLASK APPLICATION
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
