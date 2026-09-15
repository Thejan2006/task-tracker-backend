from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    otp = Column(String, nullable=True)
    otp_code = Column(String, nullable=True)

    tasks = relationship("Task", back_populates="owner")# User Task 
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self):
        return self.role == "admin"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True) 
    priority = Column(String, nullable=True)
    status = Column(String, default="todo", nullable=False)
    position = Column(Integer, default=0, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=utcnow,
        server_default="CURRENT_TIMESTAMP",
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default="CURRENT_TIMESTAMP",
        nullable=False,
    )
    category_id = Column(
        Integer, 
        ForeignKey("categories.id", ondelete="SET NULL"), 
        nullable=True
    )
    # relationships woth other tables
    owner = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name =Column(String,nullable=False)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    owner = relationship("User")
    tasks = relationship("Task", back_populates="category")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="activities")