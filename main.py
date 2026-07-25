import sqlite3


from fastapi import FastAPI, HTTPException, Depends, Response
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(title="Integration CRUT w SQL")


DB_PATH = "tasks.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row          # Rows be like dicts
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("DROP TABLE IF EXISTS tasks")

    conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks
        (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            task_description TEXT,
            task_status BOOLEAN NOT NULL DEFAULT 0
            )
            """)

    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
    if count[0] == 0:
        try:
            conn.execute("BEGIN")
            conn.executemany(
                "INSERT INTO tasks (task_name, task_description, task_status) VALUES (?, ?, ?)",
                [
                    ("Buy Groceries", "2% from the store", 0),
                    ("Make Assignment", "Make coding Assignment", 1),
                    ("Study AI", "Build AI Agentic Model", 0),
                ],
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    conn.close()

@app.on_event("startup")
def startup():
    init_db()

class CreateTask(BaseModel):
    task_name : str
    task_description : Optional[str] = None
    task_status : Optional[bool] = False


class TaskResponse(BaseModel):
    task_id : int
    task_name: str
    task_description: Optional[str] = None
    task_status: Optional[bool] = False

    class Config:
        from_attributes = True

                        #### EndPoints ###

@app.get('/health')
def health():
    return {"status": "OK"}

@app.get('/')
def root():
    return {"Message": "Intro to FastAPI w/ raw SQL"}


@app.get('/tasks', response_model=List[TaskResponse])
def get_all_tasks(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM tasks").fetchall()
    return [dict(row) for row in rows]

@app.get('/tasks/{task_id}', response_model=TaskResponse)
def getTaskById(task_id: int, db:sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return dict(row)

@app.post('/tasks', response_model=TaskResponse, status_code=201)
def createTask(task: CreateTask, db:sqlite3.Connection = Depends(get_db)):
    if not task.task_name.strip():
        raise HTTPException(status_code=400, detail="Task name required")
    cursor = db.execute(
        "INSERT INTO tasks (task_name, task_description, task_status) VALUES (?, ? ,?)",
        (task.task_name, task.task_description, task.task_status)
    )
    db.commit()
    new_id = cursor.lastrowid

    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (new_id)).fetchone()
    return dict(row)

@app.put('/tasks/{task_id}', response_model=TaskResponse)
def updateTask(task_id: int, task: CreateTask, db: sqlite3.Connection = Depends(get_db)):
    existing = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Task does not exist!")
    if not task.task_name.strip():
        raise HTTPException(status_code=400, detail="Task Name Required!")

    db.execute("UPDATE tasks SET task_name = ?, task_description = ? , task_status = ? WHERE task_id = ?",
               (task.task_name, task.task_description, task.task_status, task_id),
               )
    db.commit()

    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id)).fetchone()
    return dict(row)



@app.delete('/tasks/{task_id}', status_code=204)
def deleteTask(task_id : int, db: sqlite3.Connection = Depends(get_db)):
    existing = db.execute("SELECT * FROM tasks WHERE task_id = ? ", (task_id)).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="Task does not exist! ")

    db.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    db.commit()
    return Response(status_code=204)


