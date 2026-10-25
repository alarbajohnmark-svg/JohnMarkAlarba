
import os
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)

# Allow browser requests to your public API
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Classmate's public Render API
CLASSMATE_API_URL = (
    "https://jasminerose-2.onrender.com/api/students"
)

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "students.db"
)


# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# ENSURE DATABASE AND SOURCE COLUMN EXIST
# ==========================================
def ensure_database():
    conn = get_db_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL,
                source TEXT DEFAULT 'Local'
            )
        """)

        columns = conn.execute(
            "PRAGMA table_info(students)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "source" not in column_names:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

        conn.commit()

    finally:
        conn.close()


# ==========================================
# VALIDATE STUDENT DATA
# ==========================================
def validate_student(data):
    if not isinstance(data, dict):
        return None, "A valid JSON object is required"

    fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    for field in fields:
        if field not in data or data[field] is None:
            return None, f"Missing field: {field}"

        if isinstance(data[field], str) and not data[field].strip():
            return None, f"{field} cannot be empty"

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return None, "Year must be a valid integer"

    student = {
        "student_id": str(data["student_id"]).strip(),
        "name": str(data["name"]).strip(),
        "program": str(data["program"]).strip(),
        "year": year,
        "section": str(data["section"]).strip()
    }

    return student, None


# ==========================================
# HOME PAGE
# GET /
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# GET ONE SAMPLE STUDENT
# GET /student
# ==========================================
@app.route("/student", methods=["GET"])
def get_student():
    return jsonify({
        "student_id": "2026-00126",
        "name": "John Mark Alarba",
        "program": "BSIT",
        "year": 3,
        "section": "A",
        "source": "Local"
    })


# ==========================================
# GREETING API
# GET /hello?name=John
# ==========================================
@app.route("/hello", methods=["GET"])
def say_hello():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


# ==========================================
# GET ALL LOCAL DATABASE STUDENTS
# GET /students
# ==========================================
@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# GET ALL STUDENTS AS JSON
# GET /api/students
# ==========================================
@app.route("/api/students", methods=["GET"])
def api_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# GET CLASSMATE'S RECORDS
# GET /api/classmate-students
# ==========================================
@app.route("/api/classmate-students", methods=["GET"])
def get_classmate_students():
    try:
        response = requests.get(
            CLASSMATE_API_URL,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return jsonify({
                "error": "Classmate API did not return a list of records"
            }), 502

        records = []

        for record in data:
            if isinstance(record, dict):
                record = dict(record)
                record["source"] = "Partner"
                records.append(record)

        return jsonify(records), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Classmate API request timed out"
        }), 504

    except requests.exceptions.RequestException as error:
        app.logger.error(
            "Classmate API request failed: %s", error
        )

        return jsonify({
            "error": "Unable to connect to classmate API"
        }), 502

    except ValueError:
        return jsonify({
            "error": "Classmate API did not return valid JSON"
        }), 502


# ==========================================
# PARTNER RECORDS ENDPOINT
# GET /partner-records
# ==========================================
@app.route("/partner-records", methods=["GET"])
def partner_records():
    try:
        response = requests.get(
            CLASSMATE_API_URL,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return jsonify({
                "error": "Partner API did not return a list of records"
            }), 502

        records = []

        for record in data:
            if isinstance(record, dict):
                record = dict(record)
                record["source"] = "Partner"
                records.append(record)

        return jsonify(records), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Partner API request timed out"
        }), 504

    except requests.exceptions.RequestException as error:
        app.logger.error(
            "Partner API request failed: %s", error
        )

        return jsonify({
            "error": "Unable to retrieve partner data"
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner API did not return valid JSON"
        }), 502


# ==========================================
# IMPORT A PARTNER RECORD INTO YOUR DATABASE
# POST /api/import-student
# ==========================================
@app.route("/api/import-student", methods=["POST"])
def import_student():
    data, error = validate_student(
        request.get_json(silent=True)
    )

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
                (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, 'Partner')
            """,
            (
                data["student_id"],
                data["name"],
                data["program"],
                data["year"],
                data["section"]
            )
        )

        conn.commit()

        return jsonify({
            "message": "Partner record saved successfully",
            "id": cursor.lastrowid,
            "student_id": data["student_id"],
            "source": "Partner"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Could not save record. The student ID may already exist."
        }), 409

    except sqlite3.OperationalError:
        app.logger.exception("Import database error")

        return jsonify({
            "error": "Database error while saving partner record"
        }), 500

    finally:
        conn.close()


# ==========================================
# GET ONE STUDENT BY DATABASE ID
# GET /students/<id>
# ==========================================
@app.route("/students/<int:id>", methods=["GET"])
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
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
# GET STUDENTS BY YEAR
# GET /students/year/<year>
# ==========================================
@app.route("/students/year/<int:year>", methods=["GET"])
def get_students_by_year(year):
    conn = get_db_connection()

    try:
        students = conn.execute(
            """
            SELECT * FROM students
            WHERE year = ?
            ORDER BY id
            """,
            (year,)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# CREATE A LOCAL STUDENT
# POST /api/students
# ==========================================
@app.route("/api/students", methods=["POST"])
def add_student():
    data, error = validate_student(
        request.get_json(silent=True)
    )

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
                (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, 'Local')
            """,
            (
                data["student_id"],
                data["name"],
                data["program"],
                data["year"],
                data["section"]
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student added successfully",
            "id": cursor.lastrowid,
            "source": "Local"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Could not add student. Check for duplicate student IDs."
        }), 400

    except sqlite3.OperationalError:
        app.logger.exception("Student insert database error")

        return jsonify({
            "error": "Database is not ready. Check the students table."
        }), 500

    finally:
        conn.close()


# ==========================================
# UPDATE A STUDENT
# PUT /api/students/<id>
# ==========================================
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data, error = validate_student(
        request.get_json(silent=True)
    )

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if existing is None:
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
                data["student_id"],
                data["name"],
                data["program"],
                data["year"],
                data["section"],
                id
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student updated successfully"
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
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted successfully"
        }), 200

    finally:
        conn.close()


# ==========================================
# START APPLICATION
# ==========================================
# Ensure the database and source column exist on startup.
ensure_database()

if __name__ == "__main__":
    app.run(debug=True)
