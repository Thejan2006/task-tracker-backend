from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base  # app module import




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="Member")
  
    tasks = relationship("Task", back_populates="owner")# User Task 
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True) 
    owner_id = Column(Integer, ForeignKey("users.id")) 
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