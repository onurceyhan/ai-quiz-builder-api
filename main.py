from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import create_tables
from app.routers import auth, quizzes

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="AI Quiz Builder API",
    description="API for AI-powered quiz generation and management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vue.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["quizzes"])

@app.get("/")
async def root():
    return {"message": "AI Quiz Builder API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 