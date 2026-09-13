from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.routers import auth, users, tasks, categories, dashboard
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.exceptions import AppException
from app.error_handlers import app_exception_handler,validation_exception_handler
# Initialize FastAPI application
app = FastAPI(
    title="Task Tracker API",
    description="Task Tracker Backend Application using FastAPI, PostgreSQL & SQLAlchemy",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS)
origins = [settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include application routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(users.admin_router)
app.include_router(tasks.router)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(categories.router)
app.include_router(dashboard.router)
Path("uploads/avatars").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/")
def root():
    """Welcome root endpoint."""
    return {
        "message": "Welcome to Task Tracker API",
        "docs": "Go to /docs for interactive API documentation"
    }
    
    
    