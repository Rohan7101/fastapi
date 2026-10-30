import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Student Management API")

DATA_FILE = Path(__file__).with_name("students.json")


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    roll_no: str = Field(min_length=1, max_length=20)
    marks: float = Field(ge=0, le=100)


def load_students():
    if not DATA_FILE.exists():
        return []

    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_students(students):
    DATA_FILE.write_text(
        json.dumps(students, indent=4),
        encoding="utf-8",
    )


@app.get("/")
def home():
    return {"message": "Student API is running"}


@app.get("/students")
def get_students():
    return load_students()


@app.post("/students", status_code=201)
def add_student(student: StudentCreate):
    students = load_students()

    if any(s["roll_no"] == student.roll_no for s in students):
        raise HTTPException(status_code=409, detail="Roll number already exists")

    new_id = max((s["id"] for s in students), default=0) + 1

    record = {"id": new_id, **student.model_dump()}
    students.append(record)
    save_students(students)

    return record


@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in load_students():
        if student["id"] == student_id:
            return student

    raise HTTPException(status_code=404, detail="Student not found")


@app.put("/students/{student_id}")
def update_student(student_id: int, updated: StudentCreate):
    students = load_students()

    for index, student in enumerate(students):
        if student["id"] == student_id:
            if any(
                s["roll_no"] == updated.roll_no
                and s["id"] != student_id
                for s in students
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Roll number already exists",
                )

            students[index] = {
                "id": student_id,
                **updated.model_dump(),
            }

            save_students(students)
            return students[index]

    raise HTTPException(status_code=404, detail="Student not found")


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    students = load_students()

    remaining = [
        student for student in students
        if student["id"] != student_id
    ]

    if len(remaining) == len(students):
        raise HTTPException(status_code=404, detail="Student not found")

    save_students(remaining)
    return Response(status_code=204)