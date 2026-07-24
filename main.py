from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    task_id : int
    task_name : str
    task_description : Optional[str] = None
    task_status : bool = False

tasks_db = [
    {"task_id": 1, "task_name": "Buy milk", "task_description": "2% from the store", "task_status": False},
    {"task_id": 2, "task_name": "Make Assignment", "task_description": "Make coding Assignment", "task_status": True},
    {"task_id": 3, "task_name": "Study AI", "task_description": "Build AI Agentic Model", "task_status": False}
]


@app.get('/health')
def health():
    return {"status": "OK"}

@app.get('/')
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get('/tasks')
def getAllTasks():
    return tasks_db


@app.get('/tasks/{tasks_id}')
def getTaskById(task_id : int):
    for task in tasks_db:
        if task["task_id"] == task_id:
            return task
        raise HTTPException(status_code=404, detail=f"Task {task_id} Not Found")