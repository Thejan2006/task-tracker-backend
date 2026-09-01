from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List,Optional
from app import oauth2
from app.exceptions import TaskNotFoundException
from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user
from app.oauth2 import require_admin
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



@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    limit: int = 10,                          # Pagination:එ
    skip: int = 0,                           # Pagination: Skip  (Offset)
    search: Optional[str] = "",              # Search: Title 
    is_completed: Optional[bool] = None      # Filtering: Complete true/flase
):
   
    
    #  Base Query: User  Tasks Select 
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    
    # 2. Filtering: is_completed Filter
    if is_completed is not None:
        query = query.filter(models.Task.is_completed == is_completed)
        
    # 3. Search: Search term  Title  (Case-insensitive)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
        
    # 4. Pagination: Offset  Limit 
    tasks = query.offset(skip).limit(limit).all()
    
    return tasks



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
        raise TaskNotFoundException(task_id=id)
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
        raise TaskNotFoundException(task_id=id)

    task_query.delete(synchronize_session=False)
    db.commit()
    return

@router.get("/admin/all", response_model=List[schemas.TaskResponse])
def get_all_tasks_for_admin(
    db: Session = Depends(get_db),
    _admin_user: models.User = Depends(oauth2.require_admin)
):
    get_all_task = db.query(models.Task).all()
    
    return get_all_task
    