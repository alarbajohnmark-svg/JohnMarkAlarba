
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table if it does not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Remove existing records before inserting the sample data
cursor.execute("DELETE FROM students")

# Five realistic sample student records
students = [
    ('2026-00126', 'John Mark Alarba', 'BSIT', 3, 'A'),
    ('2026-00127', 'Mark Anthony Garcia', 'BSIT', 1, 'B'),
    ('2026-00128', 'Sofia Claire Mendoza', 'BSIT', 2, 'A'),
    ('2026-00129', 'Joy Agtas', 'BSIT', 4, 'A'),
    ('2026-00130', 'Patricia Anne Flores', 'BSIT', 3, 'A')
]

# Insert the records into the database
cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

# Save changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully!")
print("5 sample student records inserted.")
