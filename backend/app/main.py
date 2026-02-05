from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.auth import router as auth_router
from .routes.user import router as user_router
from .routes.tasks import router as tasks_router
from .database import create_db_and_tables

app = FastAPI(
    title="Todo API",
    description="Authentication & Task Management API",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    create_db_and_tables()

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://to-do-webapp-chrb.vercel.app",
        "http://localhost:3002",
        "http://localhost:3003",  # Frontend origin (fallback ports)
        "http://localhost:3004",
        "http://localhost:3005"
    ],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Todo API - Authentication & Task Management"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
