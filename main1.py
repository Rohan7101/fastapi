import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field


# --------------------------------
# DATABASE CONFIGURATION
# --------------------------------

DATABASE_FILE = Path(__file__).parent / "students.db"


# --------------------------------
# DATABASE INITIALIZATION
# --------------------------------

def create_database():

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            marks REAL CHECK(marks >= 0 AND marks <= 100)
        )
    """)

    connection.commit()
    connection.close()

    print("Database and table initialized!")


# --------------------------------
# DATABASE CONNECTION
# --------------------------------

def get_db():

    connection = sqlite3.connect(DATABASE_FILE)

    # Return rows as dictionary-like objects
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()


# --------------------------------
# FASTAPI LIFESPAN
# --------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_database()

    yield

    print("Application shutting down...")


app = FastAPI(lifespan=lifespan)


# --------------------------------
# PYDANTIC MODEL
# --------------------------------

class Student(BaseModel):

    name: str = Field(min_length=2)
    roll_no: str
    marks: float = Field(ge=0, le=100)


# --------------------------------
# HOME ROUTE
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "FastAPI SQLite Application Running"
    }


# --------------------------------
# CREATE STUDENT
# --------------------------------

@app.post("/students")
def create_student(
    student: Student,
    db: sqlite3.Connection = Depends(get_db)
):

    try:

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO students (name, roll_no, marks)
            VALUES (?, ?, ?)
            """,
            (student.name, student.roll_no, student.marks)
        )

        db.commit()

        return {
            "message": "Student created successfully",
            "student_id": cursor.lastrowid
        }

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=400,
            detail="Roll number already exists or invalid data"
        )


# --------------------------------
# READ ALL STUDENTS
# --------------------------------

@app.get("/students")
def get_students(
    db: sqlite3.Connection = Depends(get_db)
):

    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    return [dict(student) for student in students]


# --------------------------------
# READ SINGLE STUDENT
# --------------------------------

@app.get("/students/{student_id}")
def get_student(
    student_id: int,
    db: sqlite3.Connection = Depends(get_db)
):

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return dict(student)


# --------------------------------
# UPDATE STUDENT
# --------------------------------

@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student: Student,
    db: sqlite3.Connection = Depends(get_db)
):

    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE students
        SET name = ?, roll_no = ?, marks = ?
        WHERE id = ?
        """,
        (
            student.name,
            student.roll_no,
            student.marks,
            student_id
        )
    )

    if cursor.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    try:
        db.commit()

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=400,
            detail="Roll number already exists or invalid data"
        )

    return {
        "message": "Student updated successfully"
    }


# --------------------------------
# DELETE STUDENT
# --------------------------------

@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: sqlite3.Connection = Depends(get_db)
):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    if cursor.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.commit()

    return {
        "message": "Student deleted successfully"
    }