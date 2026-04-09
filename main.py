from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Literal, Union, Annotated
from pydantic import BaseModel
import sqlite3
import os, io, uuid, datetime, json
from PIL import Image
import garminconnect as gc


# I think a cool idea would be to be able to take pictures of your meal and then somehow with 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

upload_directory = "user-uploads"
parent_directory = "/Users/ade/atunwa/Projects/fitness-app/static"

path = os.path.join(parent_directory, upload_directory)
os.makedirs(path, exist_ok=True)


class Exercise(BaseModel):
    exercise: str
    sets: int 
    reps: int 
    weight: int
    type: Literal["Exercise"]


class Workout(BaseModel):
    name: str
    date: str
    type: Literal["Workout"]

class GarminFormData(BaseModel):
    username: str
    password: str
    garminDataStartDate: str

    
    model_config = {"extra": "forbid"}

PostResponse = Union[Exercise, Workout]


def init_db():
    print("The database has been initialised")
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
                   filename TEXT NOT NULL,
                   date TEXT NOT NULL
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


@app.get("/")
def home():
    init_db()
    return FileResponse("templates/index.html")

@app.post("/workouts")
def add_workout(data: PostResponse):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if data.type == "Exercise":
        print("This is an exercise entry")
        cursor.execute("SELECT MAX(id) FROM workouts")
        row = cursor.fetchone()
        workout_id = row[0] if row and row[0] is not None else 0 #what does this line even do
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

    # this is me getting the name of the workout
    cursor.execute("SELECT name, id FROM workouts WHERE date = ?",
                   (date,))
    
    data = cursor.fetchone()
    workout_title, workout_id = data[0], data[1]

    # this is me getting all of the exercises whihc are linked to that workout by the id
    cursor.execute("SELECT exercise, sets, reps, weight FROM exercises WHERE workout_id = ?",
                   (workout_id,))
    
    exercises = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "workouts.html",
        {"request": request, "workout": workout_title, "date": date, "exercises": exercises}
    )



@app.get("/view-workouts")
def view_workouts(request: Request):

    print("This was accessed")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("""SELECT *
                    FROM workouts
                    JOIN exercises ON exercises.workout_id = workouts.id""")
    
    data = cursor.fetchall()

    cursor.execute("SELECT name, date, id  FROM workouts")
    entries = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "view_workouts.html",
        {"request": request, "data": data, "entries": entries}
    )

@app.post("/uploads")
async def handle_file_upload(file: UploadFile = File(...)):
    print(file)
    user_upload_directory = "/Users/ade/atunwa/Projects/fitness app/static/user-uploads"
    os.makedirs(user_upload_directory, exist_ok=True)

    file_bytes = await file.read()

    image = Image.open(io.BytesIO(file_bytes))
    image = image.resize((150,150))

    filename = f"{uuid.uuid4()}.jpg"
    filepath = f"{user_upload_directory}/{filename}"
    print(filename)
    image.save(filepath)

    filename = f"/static/user-uploads/{filename}"

    date = datetime.datetime.now().strftime("%d-%m-%y")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO files (filename, date) VALUES (?,?)",
                   (filename, date))
    
    conn.commit()
    conn.close()

    return "got"

@app.get("/timeline")
def timeline(request: Request):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM files")
    filepaths = cursor.fetchall()
    dates = list(set([i[1] for i in filepaths]))


    print(filepaths)
    print(dates)

    return templates.TemplateResponse(
        "timeline.html",
        {"request": request, "filepaths": filepaths, "dates": dates}
    )

@app.get('/external-wearable')
def externable_wearable(request:Request):
    return templates.TemplateResponse(
        "external_wearable.html",
        {"request" : request}
    )

@app.post('/external-wearable')
async def user_information_external_wearable(data : Annotated[GarminFormData, Form()], request: Request):

    client = gc.Garmin(data.username, data.password)
    try:
        client.login()
        user_data = client.get_steps_data(data.garminDataStartDate)
    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


    return templates.TemplateResponse(
        "user_data.html",
        {"request": request, "data": user_data}
    )


    
    
    




