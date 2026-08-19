from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import models
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class TaskCreate(BaseModel):
    title:str
    description: Optional[str] = None
    is_completed:bool = False
 
    
class TaskResponse(TaskCreate): 
      id:int
      class Config:
          from_attributes = True
    


    
@app.get("/")# Welcome Endpoint (GET)
def read_root():
    return {"massage":"Welcome ro Task Tracker API"}    


# Create Task Endpoint (POST) input data from postgrSQL
@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed
    )
    db.add(db_task)# try collect data from this object
    db.commit()
    db.refresh(db_task)
    return db_task


# read task get data from pastgrSQL
@app.get("/tasks/", response_model=List[TaskResponse])
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    # 2. if not task give error 404
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskCreate, db: Session = Depends(get_db)):
    # 1. find need to cahge task in database
    task_query = db.query(models.Task).filter(models.Task.id == task_id)
    db_task = task_query.first()

    # 2. if not give 404 Error 
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # 3. DB Object Values new Values Replace 
    db_task.title = updated_task.title
    db_task.description = updated_task.description
    db_task.is_completed = updated_task.is_completed

    # 4. save changes in database 
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    # 1. if what need to delete in db
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    # 2. if not  404 Error
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # 3. Session Delete  Mark 
    db.delete(task)
    
    # 4. DB data delete premently 
    db.commit()
    return {"message": "Task deleted successfully"}