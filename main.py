import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timezone
from uuid import uuid4

app = FastAPI(title="API de Tareas")

@app.exception_handler(RequestValidationError)
async def validation_400(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Status(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

class TaskCreate(BaseModel):
    title: str
    priority: Priority
    description: str = ""

class TaskUpdate(BaseModel):
    status: Status

def init_db():
    conn = sqlite3.connect("tareas.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_all_tasks(page, limit):
    conn = sqlite3.connect("tareas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    total = len(rows)
    start = (page - 1) * limit
    end = start + limit
    return [dict(r) for r in rows[start:end]], total

def get_task_by_id(item_id):
    conn = sqlite3.connect("tareas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_task(task):
    new_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect("tareas.db")
    conn.execute(
        "INSERT INTO tasks (id, title, priority, status, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (new_id, task.title, task.priority.value, "pending", task.description, now)
    )
    conn.commit()
    conn.close()
    return {
        "id": new_id,
        "title": task.title,
        "priority": task.priority.value,
        "status": "pending",
        "description": task.description,
        "createdAt": now
    }

def update_task(item_id, status):
    conn = sqlite3.connect("tareas.db")
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status.value, item_id))
    conn.commit()
    conn.close()

@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.get("/items")
def list_items(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    items, total = get_all_tasks(page, limit)
    return {"items": items, "total": total, "page": page, "limit": limit}

@app.get("/items/{item_id}")
def get_item(item_id: str):
    task = get_task_by_id(item_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.post("/items", status_code=201)
def create_item(task: TaskCreate):
    return create_task(task)

@app.patch("/items/{item_id}")
def update_item(item_id: str, update: TaskUpdate):
    existing = get_task_by_id(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    update_task(item_id, update.status)
    updated = get_task_by_id(item_id)
    return updated