from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine, get_db
from datetime import datetime,timedelta, timezone
from passlib.context import CryptContext # password hash
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm # to use in password fastapi 
from fastapi.security import OAuth2PasswordBearer # OAuth2PasswordBearer import to find currect user
from jose import JWTError
from typing import List

models.Base.metadata.create_all(bind=engine)

SECRET_KEY = "mysecretkeyforjwttokengeneration"  # Compelx key
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALGORITHM = "HS256"
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # give acess to frontend
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE
    allow_headers=["*"],
)
# password hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str): #password hash fuction 
    return pwd_context.hash(password)


def verify_password (plain_password: str, hashed_password: str): #password verifycation function 
    return pwd_context.verify(plain_password, hashed_password)
 
 
def create_access_token(data: dict): # jws access token
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        
        if username is None:
            raise credentials_exception
    except JWTError:
         raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

class UserCreate(BaseModel):
    username:str
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:str
    role:str
    class Config:
              from_attributes = True
    
    
    
    
class TaskCreate(BaseModel):
    title:str
    description: Optional[str] = None
    is_completed:bool = False
    due_date:Optional[datetime] = None
    
class TaskResponse(TaskCreate): 
      id:int
      owner_id:int
      class Config:
          from_attributes = True
    
    

    
@app.get("/")# Welcome Endpoint (GET)
def read_root():
    return {"massage":"Welcome ro Task Tracker API"}   

 
@app.post("/login") #Login Endpoint
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    find_user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not find_user or not verify_password(form_data.password, find_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    access_token = create_access_token(data={"sub": find_user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

     
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()  #check same and user dubllicate problem
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Create Task Endpoint (POST) input data from postgrSQL
@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db) ,current_user: models.User = Depends(get_current_user)):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        owner_id=current_user.id
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

@app.get("/tasks/", response_model=List[TaskResponse]) # to get data users task
def get_task(db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
   
    return tasks

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Task ID and Owner ID  check
    task = db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.owner_id == current_user.id
    ).first()
    
    # 2. if Task doest have Error Throw 
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # 3. Delete  Commit 
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}       


@app.put("/tasks/{task_id}", response_model=TaskResponse) # tast upadte endpoit
def update_task(task_id: int, updated_task: TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.owner_id == current_user.id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.title = updated_task.title

    db_task.description = updated_task.description

    db_task.is_completed = updated_task.is_completed   
     
    db.commit()
    db.refresh(db_task)    
    
    return db_task
        
        
        
        