from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Literal, List, Dict


# USER SCHEMAS

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# AUTH / TOKEN SCHEMAS

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    category_id: Optional[int] = None
    user_id: Optional[int] = None


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
    category_id: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[Literal["High", "Medium", "Low"]] = None
    status: Literal["todo", "in_progress", "review", "done"] = "todo"
    position: Optional[int] = None
    is_completed: Optional[bool] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[Literal["High", "Medium", "Low"]] = None
    status: Optional[Literal["todo", "in_progress", "review", "done"]] = None
    position: Optional[int] = None
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int
    category_id: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: str
    position: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None #  Category details related to the task are returned in a nested format.

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None

class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: Optional[datetime] = None

class AdminUserStatusUpdate(BaseModel):
    is_active: bool

class ActivityResponse(BaseModel):
    id: int
    type: str
    message: str
    task_id: Optional[int] = None
    created_at: datetime
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    tasks_by_status: Dict[str, int]
    recent_activity: List[ActivityResponse]
    completion_trend: List[Dict[str, object]]
class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str
