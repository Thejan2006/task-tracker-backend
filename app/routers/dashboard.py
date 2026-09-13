from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    total = tasks.count()
    completed = tasks.filter((models.Task.is_completed.is_(True)) | (models.Task.status == "done")).count()
    today = datetime.now(timezone.utc)
    overdue = tasks.filter(models.Task.is_completed.is_(False), models.Task.due_date < today).count()
    grouped = dict(db.query(models.Task.status, func.count(models.Task.id))
                   .filter(models.Task.owner_id == current_user.id).group_by(models.Task.status).all())
    by_status = {key: int(grouped.get(key, 0)) for key in ("todo", "in_progress", "review", "done")}
    activities = (db.query(models.Activity).filter(models.Activity.user_id == current_user.id)
                  .order_by(models.Activity.created_at.desc()).limit(10).all())
    start = today - timedelta(days=29)
    rows = (db.query(func.date(models.Task.updated_at), func.count(models.Task.id))
            .filter(models.Task.owner_id == current_user.id, models.Task.status == "done",
                    models.Task.updated_at >= start)
            .group_by(func.date(models.Task.updated_at)).order_by(func.date(models.Task.updated_at)).all())
    return {"total_tasks": total, "completed_tasks": completed, "pending_tasks": total - completed,
            "overdue_tasks": overdue, "tasks_by_status": by_status, "recent_activity": activities,
            "completion_trend": [{"date": str(day), "completed": int(count)} for day, count in rows]}
