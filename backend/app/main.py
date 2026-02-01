"""
CareerGold Backend - FastAPI Application (HARDENED)
=====================================================
Main entry point with security middleware integrated.

Run with: uvicorn app.main:app --reload
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import jobs, scraper
from app.middleware.security import CORS_CONFIG, rate_limiter, RATE_LIMIT_REQUESTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("careergold")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 CareerGold API starting up (HARDENED MODE)...")
    yield
    # Shutdown
    logger.info("👋 CareerGold API shutting down...")


app = FastAPI(
    title="CareerGold API",
    description="Job discovery and application tracking API",
    version="0.2.0-secure",
    lifespan=lifespan,
    # Security: Disable docs in production
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# HARDENED CORS configuration
# Only allow specific origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["allow_origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
    expose_headers=CORS_CONFIG["expose_headers"],
    max_age=CORS_CONFIG["max_age"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # XSS protection (legacy but still useful)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Rate limit headers
    remaining = rate_limiter.get_remaining(request, RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response


# Global exception handler - avoid leaking internal errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions without leaking details."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # In production, never leak stack traces
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CareerGold API",
        "version": "0.2.0-secure",
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "scraper": "ready",
        "security": "hardened",
    }


# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])
