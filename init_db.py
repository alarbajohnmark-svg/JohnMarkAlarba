
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create students table with source column
cursor.execute("""
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

# Add source column if the existing table does not have it
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

if "source" not in columns:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'"
    )

# Remove existing records before inserting sample data
cursor.execute("DELETE FROM students")

# Five sample student records
students = [
    ("2026-00126", "John Mark Alarba", "BSIT", 3, "A", "Local"),
    ("2026-00127", "Mark Anthony Garcia", "BSIT", 1, "B", "Local"),
    ("2026-00128", "Sofia Claire Mendoza", "BSIT", 2, "A", "Local"),
    ("2026-00129", "Joy Agtas", "BSIT", 4, "A", "Local"),
    ("2026-00130", "Patricia Anne Flores", "BSIT", 3, "A", "Local")
]

# Insert records, including their source
cursor.executemany("""
INSERT INTO students
(student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
""", students)

# Save changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully!")
print("5 sample student records inserted.")
print("All sample records have source = Local.")
