from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# 1. Creating a Category
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CategoryResponse)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_category = models.Category(
        user_id=current_user.id, 
        **category.model_dump() # category.dict() if Pydantic v1
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# 2. Getting all the User's Categories
@router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return db.query(models.Category).filter(models.Category.user_id == current_user.id).all()