from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    task_id : int
    task_name : str
    task_description : Optional[str] = None
    task_status : bool = False

class CreateTask(BaseModel):
    task_name : str
    task_description : Optional[str] = None
    task_status : Optional[bool] = False

tasks_db = [
    {"task_id": 1, "task_name": "Buy Groceries", "task_description": "2% from the store", "task_status": False},
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


@app.get('/tasks/{task_id}')
def getTaskById(task_id: int):
    for task in tasks_db:
        if task["task_id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post('/tasks', status_code=201)
def createTask(task : CreateTask):
    if not task.task_name.strip():
        raise HTTPException(status_code=400, detail="Task name required")
    new_id = max([t["task_id"] for t in tasks_db]) + 1 if tasks_db else 1

    new_task = {
        "task_id" : new_id,
        "task_name" : task.task_name,
        "task_description" : task.task_description,
        "task_status" : False,
    }

    tasks_db.append(new_task)
    return new_task

@app.put('/tasks/{task_id}')
def updateTask(task_id: int, updated: CreateTask):
    for task in tasks_db:
        if task["task_id"] == task_id:
            if not updated.task_name.strip():
                raise HTTPException(status_code=400, detail="Task name required")
            task["task_name"] = updated.task_name
            task["task_description"] = updated.task_description
            task["task_status"] = updated.task_status
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} Not Found! ")

@app.delete('/tasks/{task_id}', status_code=204)
def deleteTask(task_id : int):
    for task in tasks_db:
        if task["task_id"] == task_id:
            tasks_db.remove(task)
            return {f"Task Removed {task_id}"}
    raise HTTPException(status_code=404, detail=f"Task {task_id} Not Found! ")

