from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Literal, Union
from pydantic import BaseModel
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="/Users/atunwa/something/static"), name="static")
templates = Jinja2Templates(directory="templates")

class Exercise(BaseModel):
    exercise: str
    sets: int = 0
    reps: int = 0
    weight: int = 0
    type: Literal["Exercise"]


class Workout(BaseModel):
    name: str
    date: str
    type: Literal["Workout"]

PostResponse = Union[Exercise, Workout]


def init_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   date TEXT NOT NULL
                   )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
                   exercise TEXT NOT NULL,
                   sets INTEGER,
                   reps INTEGER,
                   weight REAL,
                   workout_id INTEGER NOT NULL,
                   FOREIGN KEY (workout_id) REFERENCES workouts(id)
                   )
    """)

    conn.commit()
    conn.close()
    return conn

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        yield conn
    finally:
        conn.close()

init_db()


@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/workouts")
def add_workout(data: PostResponse):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if data.type == "Exercise":
        print("This is an exercise entry")
        cursor.execute("SELECT MAX(id) FROM workouts")
        row = cursor.fetchone()
        workout_id = row[0] if row and row[0] is not None else 0
        cursor.execute("INSERT INTO exercises (exercise, sets, reps, weight, workout_id) VALUES (?,?,?,?,?)",
            (data.exercise, data.sets, data.reps, data.weight, workout_id))
        
    if data.type == "Workout":
        print("This is a workout")
        cursor.execute("SELECT MAX(id) FROM workouts")
        workout_id = cursor.fetchone()
        cursor.execute("INSERT INTO workouts (name, date) VALUES (?,?)",
            (data.name, data.date))
    
    
    conn.commit()
    conn.close()
    return {"workout_id": workout_id}

@app.get("/workouts/{date}", response_class=HTMLResponse)
def get_workout(date: str, request: Request):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, id FROM workouts WHERE date = ?",
                   (date,))
    
    data = cursor.fetchall()
    print(data)
    conn.close()

    return templates.TemplateResponse(
        "workouts.html",
        {"request": request, "data": data, "date": date}
    )
    
    




