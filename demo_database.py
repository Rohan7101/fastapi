import sqlite3

# Establish database connection
connection = sqlite3.connect("students.db")

print("Database connected successfully!")

# Create a cursor
cursor = connection.cursor()

# Create a table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    marks REAL CHECK(marks >= 0 AND marks <= 100)
)
""")

# Save changes
connection.commit()

# Close connection
connection.close()

print("Students table created successfully!")