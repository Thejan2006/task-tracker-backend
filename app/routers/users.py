from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.utils import hash_password
from app.oauth2 import get_current_user, require_admin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user after validating email and username uniqueness."""
    # Check if email is already registered
    db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Check if username is already taken
    db_user_name = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Hash the password and save user
    hashed_pw = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_profile(name: str = Form(None), bio: str = Form(None),
                   avatar: UploadFile = File(None),
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    if name is not None:
        current_user.name = name
    if bio is not None:
        current_user.bio = bio
    if avatar is not None:
        allowed = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}
        if avatar.content_type not in allowed:
            raise HTTPException(status_code=422, detail="Unsupported avatar image type")
        content = avatar.file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=422, detail="Avatar must be 5MB or smaller")
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{allowed[avatar.content_type]}"
        (upload_dir / filename).write_bytes(content)
        current_user.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/admin/users", response_model=list[schemas.AdminUserResponse], tags=["Admin"])
@admin_router.get("/users", response_model=list[schemas.AdminUserResponse])
def list_users(search: str = "", status_filter: str = Query("all", alias="status"), db: Session = Depends(get_db),
               _admin: models.User = Depends(require_admin)):
    query = db.query(models.User)
    if search:
        term = f"%{search}%"
        query = query.filter((models.User.username.ilike(term)) |
                             (models.User.email.ilike(term)) |
                             (models.User.name.ilike(term)))
    if status_filter == "active":
        query = query.filter(models.User.is_active.is_(True))
    elif status_filter == "disabled":
        query = query.filter(models.User.is_active.is_(False))
    return query.order_by(models.User.id).all()

@router.patch("/admin/users/{user_id}", response_model=schemas.AdminUserResponse, tags=["Admin"])
@admin_router.patch("/users/{user_id}", response_model=schemas.AdminUserResponse)
def update_user_status(user_id: int, update: schemas.AdminUserStatusUpdate,
                       db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.is_admin and not update.is_active:
        admins = db.query(models.User).filter(models.User.role == "admin", models.User.is_active.is_(True)).count()
        if admins <= 1:
            raise HTTPException(status_code=400, detail="Cannot disable the last active admin")
    target.is_active = update.is_active
    db.commit()
    db.refresh(target)
    return target

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),
                _admin: models.User = Depends(require_admin)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.is_admin:
        admins = db.query(models.User).filter(models.User.role == "admin", models.User.is_active.is_(True)).count()
        if admins <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin")
    db.query(models.Activity).filter(models.Activity.user_id == target.id).delete(synchronize_session=False)
    db.query(models.Task).filter(models.Task.owner_id == target.id).delete(synchronize_session=False)
    db.query(models.Category).filter(models.Category.user_id == target.id).delete(synchronize_session=False)
    db.delete(target)
    db.commit()