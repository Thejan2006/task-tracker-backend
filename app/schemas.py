from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

 
# USER SCHEMAS

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


# AUTH / TOKEN SCHEMAS

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    category_id: Optional[int] = None


# Base Category Schema
class CategoryBase(BaseModel):
    name: str

# Request Schema: Data sent when creating a Category
class CategoryCreate(CategoryBase):
    pass

# Response Schema: Data returned to the Client
class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  # Use from_attributes = True for Pydantic v2 (orm_mode = True for v1)


# TASK SCHEMAS

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None

class TaskResponse(TaskCreate): 
    id: int
    owner_id: int
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None #  Category details related to the task are returned in a nested format.

    class Config:
        from_attributes = True     