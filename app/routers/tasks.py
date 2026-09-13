from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])
VALID_STATUSES = ("todo", "in_progress", "review", "done")

def _record(db, user_id, event_type, message, task_id=None):
    db.add(models.Activity(user_id=user_id, type=event_type, message=message, task_id=task_id))

def _reindex(db, owner_id, column):
    tasks = (db.query(models.Task)
             .filter(models.Task.owner_id == owner_id, models.Task.status == column)
             .order_by(models.Task.position, models.Task.id).all())
    for index, item in enumerate(tasks):
        item.position = index

def _insert_at(db, task, requested_position):
    siblings = (db.query(models.Task)
                .filter(models.Task.owner_id == task.owner_id,
                        models.Task.status == task.status,
                        models.Task.id != task.id)
                .order_by(models.Task.position, models.Task.id).all())
    position = requested_position if requested_position is not None and 0 <= requested_position <= len(siblings) else len(siblings)
    siblings.insert(position, task)
    for index, item in enumerate(siblings):
        item.position = index

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    values = task.model_dump()
    requested_position = values.pop("position")
    if values.get("category_id") is not None and not db.query(models.Category).filter(
        models.Category.id == values["category_id"], models.Category.user_id == current_user.id
    ).first():
        raise HTTPException(status_code=404, detail="Category not found")
    values["status"] = values["status"] or "todo"
    values["is_completed"] = values["status"] == "done"
    new_task = models.Task(**values, owner_id=current_user.id, position=0)
    db.add(new_task)
    db.flush()
    _insert_at(db, new_task, requested_position)
    _record(db, current_user.id, "task_created", f"Task created: {new_task.title}", new_task.id)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 100, skip: int = 0, search: Optional[str] = None,
              is_completed: Optional[bool] = None):
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
    if is_completed is not None:
        query = query.filter(models.Task.is_completed == is_completed)
    return (query.order_by(models.Task.status, models.Task.position, models.Task.id)
            .offset(skip).limit(min(limit, 1000)).all())

@router.put("/{id}", response_model=schemas.TaskResponse)
def update_task(id: int, updated_task: schemas.TaskUpdate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    values = updated_task.model_dump(exclude_unset=True)
    if values.get("category_id") is not None and not db.query(models.Category).filter(
        models.Category.id == values["category_id"], models.Category.user_id == current_user.id
    ).first():
        raise HTTPException(status_code=404, detail="Category not found")
    old_status = task.status
    requested_position = values.pop("position", None)
    new_status = values.get("status", task.status)
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid task status")
    for key, value in values.items():
        setattr(task, key, value)
    task.status = new_status
    task.is_completed = new_status == "done"
    if old_status != new_status:
        task.position = 0
        _reindex(db, current_user.id, old_status)
        _insert_at(db, task, requested_position)
    elif requested_position is not None:
        _insert_at(db, task, requested_position)
    else:
        _reindex(db, current_user.id, task.status)
    event_type = "task_completed" if task.status == "done" and old_status != "done" else "task_updated"
    _record(db, current_user.id, event_type, f"Task {'completed' if event_type == 'task_completed' else 'updated'}: {task.title}", task.id)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    old_status = task.status
    _record(db, current_user.id, "task_deleted", f"Task deleted: {task.title}", task.id)
    db.delete(task)
    db.flush()
    _reindex(db, current_user.id, old_status)
    db.commit()

@router.get("/admin/all", response_model=List[schemas.TaskResponse])
def get_all_tasks_for_admin(db: Session = Depends(get_db),
                            _admin_user: models.User = Depends(oauth2.require_admin)):
    return db.query(models.Task).order_by(models.Task.status, models.Task.position).all()
