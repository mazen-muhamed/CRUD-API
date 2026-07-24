from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple CRUD task API built with FastAPI",
)

# ──────────────────────────────────────────────
# In-memory "database" — just a Python list
# ──────────────────────────────────────────────
tasks: list[dict] = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Deploy to production", "done": False},
]

_next_id = 4  # tracks the next free id


def _get_next_id() -> int:
    """Return the next id and increment the counter."""
    global _next_id
    current = _next_id
    _next_id += 1
    return current


def _find_task(task_id: int) -> tuple[int, dict] | None:
    """Find a task by id. Returns (index, task) or None."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            return i, task
    return None


# ──────────────────────────────────────────────
# Pydantic schemas — input validation
# ──────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 1 — Root & Health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/")
def root():
    """API front door — describes what this service is."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health():
    """Liveness probe — real companies use exactly this."""
    return {"status": "ok"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 2 — Read: list & single task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/tasks")
def list_tasks():
    """Return every task in the list."""
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Return one task by its id."""
    result = _find_task(task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
        )
    _, task = result
    return task


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 3 — Create: POST a new task
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    """Create a new task. Returns 201 with the created task."""
    # Validate: title must exist and not be blank
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty",
        )

    new_task = {
        "id": _get_next_id(),
        "title": payload.title.strip(),
        "done": False,
    }
    tasks.append(new_task)
    return new_task


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 4 — Update & Delete
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    """Replace a task's title and/or done flag."""
    # Reject completely empty body
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body must contain at least 'title' or 'done'",
        )

    result = _find_task(task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
        )

    idx, task = result

    # Validate title if provided
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty",
            )
        task["title"] = payload.title.strip()

    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Remove a task. Returns 204 No Content on success."""
    result = _find_task(task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
        )
    idx, _ = result
    tasks.pop(idx)
    return  # FastAPI sends 204 with empty body when status_code=204