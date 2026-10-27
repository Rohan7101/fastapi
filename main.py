from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Student Management API")

students = []


class StudentCreate(BaseModel):
    name: str = Field(min_length=2)
    roll_no: str
    marks: float = Field(ge=0, le=100)


@app.get("/")
def home():
    return {"message": "Student API is running"}


@app.get("/students")
def get_students():
    return students


@app.post("/students", status_code=201)
def add_student(student: StudentCreate):
    if any(s["roll_no"] == student.roll_no for s in students):
        raise HTTPException(
            status_code=409,
            detail="Roll number already exists",
        )

    record = {
        "id": len(students) + 1,
        **student.model_dump(),
    }

    students.append(record)
    return record


@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(status_code=404, detail="Student not found")