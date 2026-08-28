from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, tasks

# Initialize FastAPI application
app = FastAPI(
    title="Task Tracker API",
    description="Task Tracker Backend Application using FastAPI, PostgreSQL & SQLAlchemy",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS)
origins = ["*"]

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
app.include_router(tasks.router)

@app.get("/")
def root():
    """Welcome root endpoint."""
    return {
        "message": "Welcome to Task Tracker API",
        "docs": "Go to /docs for interactive API documentation"
    }