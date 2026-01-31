"""
CareerGold Backend - FastAPI Application
=========================================
Main entry point for the API server.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import jobs, scraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("🚀 CareerGold API starting up...")
    yield
    # Shutdown
    print("👋 CareerGold API shutting down...")


app = FastAPI(
    title="CareerGold API",
    description="Job discovery and application tracking API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vite dev server
        "http://localhost:5173",  # Vite default
        settings.frontend_url,     # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CareerGold API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "scraper": "ready",
    }


# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])
