from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ================================
# USER SCHEMAS
# ================================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"  # Default role  user 
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


# ================================
# AUTH / TOKEN SCHEMAS
# ================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ================================
# TASK SCHEMAS
# ================================
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None

class TaskResponse(TaskCreate): 
    id: int
    owner_id: int

    class Config:
        from_attributes = True