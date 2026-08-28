from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new task assigned to the logged-in user."""
    new_task = models.Task(**task.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve all tasks owned by the logged-in user."""
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
    return tasks

@router.get("/{id}", response_model=schemas.TaskResponse)
def get_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve a specific task by ID owned by the logged-in user."""
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.put("/{id}", response_model=schemas.TaskResponse)
def update_task(
    id: int,
    updated_task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update a specific task owned by the logged-in user."""
    task_query = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == current_user.id)
    db_task = task_query.first()

    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task_query.update(updated_task.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a specific task owned by the logged-in user."""
    task_query = db.query(models.Task).filter(models.Task.id == id, models.Task.owner_id == current_user.id)
    task = task_query.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task_query.delete(synchronize_session=False)
    db.commit()
    return