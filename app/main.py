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

# Create Task Endpoint (POST)
@app.post("/tasks/")
def create_task(task: TaskCreate):
    return {"status": "Task received successfully", "data": task}


