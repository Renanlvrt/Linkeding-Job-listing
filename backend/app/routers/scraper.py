"""
Scraper API Router (HARDENED)
==============================
Endpoints with authentication, rate limiting, and input sanitization.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import uuid
import re

from app.scraper.orchestrator import orchestrator
from app.scraper.discovery import job_discovery
from app.scraper.linkedin_api import linkedin_client
from app.middleware.security import (
    verify_jwt, 
    optional_jwt,
    check_rate_limit, 
    check_scraper_rate_limit,
    sanitize_string,
    sanitize_job_data,
    log_request,
)

router = APIRouter()


# ============================================================
# Pydantic Models with Validation
# ============================================================

class ScrapeRequest(BaseModel):
    """Request to start a scrape job - with input validation."""
    keywords: str = Field(..., min_length=2, max_length=100)
    location: Optional[str] = Field("Remote", max_length=100)
    user_skills: Optional[list[str]] = Field(None, max_length=50)
    max_results: int = Field(20, ge=1, le=100)
    use_rapidapi: bool = False

    @field_validator('keywords', 'location', mode='before')
    @classmethod
    def sanitize_text(cls, v):
        if isinstance(v, str):
            # Remove any potential injection attempts
            v = sanitize_string(v, 100)
            # Block suspicious patterns
            if re.search(r'[<>{}|\\^~\[\]]', v):
                raise ValueError("Invalid characters in input")
        return v

    @field_validator('user_skills', mode='before')
    @classmethod
    def sanitize_skills(cls, v):
        if isinstance(v, list):
            return [sanitize_string(s, 50) for s in v[:50]]
        return v


class QuickSearchRequest(BaseModel):
    """Quick discovery request with validation."""
    keywords: str = Field(..., min_length=2, max_length=100)
    location: Optional[str] = Field("", max_length=100)
    max_results: int = Field(10, ge=1, le=50)
    date_filter: str = Field("week", pattern="^(day|week|month)$")

    @field_validator('keywords', 'location', mode='before')
    @classmethod
    def sanitize_text(cls, v):
        if isinstance(v, str):
            v = sanitize_string(v, 100)
            if re.search(r'[<>{}|\\^~\[\]]', v):
                raise ValueError("Invalid characters in input")
        return v


class ScrapeResponse(BaseModel):
    """Response from starting a scrape job."""
    run_id: str
    status: str
    message: str


# ============================================================
# In-memory store (consider Redis for production)
# ============================================================

SCRAPE_RUNS: dict[str, dict] = {}


# ============================================================
# Background Task
# ============================================================

async def run_scrape_job(
    run_id: str,
    keywords: str,
    location: str,
    user_skills: list[str],
    max_results: int,
    use_rapidapi: bool,
    user_id: Optional[str],
):
    """Background task for scraping - logs user who initiated."""
    try:
        SCRAPE_RUNS[run_id]["status"] = "RUNNING"
        SCRAPE_RUNS[run_id]["progress"] = 10
        
        result = await orchestrator.run_scrape(
            keywords=keywords,
            location=location,
            user_skills=user_skills or [],
            max_jobs=max_results,
            use_rapidapi=use_rapidapi,
        )
        
        # Sanitize job data before storing
        sanitized_jobs = [sanitize_job_data(job) for job in result.get("jobs", [])]
        
        SCRAPE_RUNS[run_id]["status"] = "COMPLETED"
        SCRAPE_RUNS[run_id]["progress"] = 100
        SCRAPE_RUNS[run_id]["jobs_found"] = len(sanitized_jobs)
        SCRAPE_RUNS[run_id]["jobs"] = sanitized_jobs
        SCRAPE_RUNS[run_id]["completed_at"] = datetime.utcnow().isoformat()
        SCRAPE_RUNS[run_id]["sources"] = result.get("sources", {})
        SCRAPE_RUNS[run_id]["rapidapi_remaining"] = result.get("rapidapi_remaining")
        
    except Exception as e:
        SCRAPE_RUNS[run_id]["status"] = "FAILED"
        SCRAPE_RUNS[run_id]["error"] = "Scrape failed"  # Don't leak internal errors
        SCRAPE_RUNS[run_id]["completed_at"] = datetime.utcnow().isoformat()
        
        import logging
        logging.getLogger("scraper").error(f"Scrape {run_id} failed: {e}", exc_info=True)


# ============================================================
# Endpoints (with security dependencies)
# ============================================================

@router.post("/start", response_model=ScrapeResponse, dependencies=[Depends(check_scraper_rate_limit)])
async def start_scrape(
    request: ScrapeRequest, 
    background_tasks: BackgroundTasks,
    req: Request,
    claims: dict = Depends(verify_jwt),  # REQUIRE authentication
):
    """
    Start a new scrape job. REQUIRES AUTHENTICATION.
    
    Rate limited: 10 requests per minute.
    """
    user_id = claims.get("sub")
    log_request(req, user_id)
    
    run_id = str(uuid.uuid4())
    
    SCRAPE_RUNS[run_id] = {
        "run_id": run_id,
        "keywords": request.keywords,
        "location": request.location,
        "status": "QUEUED",
        "jobs_found": 0,
        "progress": 0,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "error": None,
        "jobs": [],
        "user_id": user_id,  # Track who started it
    }
    
    background_tasks.add_task(
        run_scrape_job,
        run_id,
        request.keywords,
        request.location,
        request.user_skills or [],
        request.max_results,
        request.use_rapidapi,
        user_id,
    )
    
    return ScrapeResponse(
        run_id=run_id,
        status="QUEUED",
        message=f"Scrape started for '{request.keywords}'",
    )


@router.post("/quick", dependencies=[Depends(check_rate_limit)])
async def quick_search(
    request: QuickSearchRequest,
    req: Request,
    claims: Optional[dict] = Depends(optional_jwt),  # Optional auth
):
    """
    Quick job discovery - FREE and INSTANT.
    
    Optional authentication. Rate limited: 100 requests per minute.
    """
    user_id = claims.get("sub") if claims else None
    log_request(req, user_id)
    
    jobs = job_discovery.search_linkedin_jobs(
        keywords=request.keywords,
        location=request.location,
        max_results=request.max_results,
        date_filter=request.date_filter,
    )
    
    # Sanitize scraped data
    sanitized_jobs = [sanitize_job_data(job) for job in jobs]
    
    return {
        "status": "OK",
        "keywords": request.keywords,
        "location": request.location,
        "jobs_found": len(sanitized_jobs),
        "jobs": sanitized_jobs,
    }


@router.get("/status/{run_id}", dependencies=[Depends(check_rate_limit)])
async def get_scrape_status(
    run_id: str,
    req: Request,
    claims: dict = Depends(verify_jwt),  # REQUIRE auth
):
    """Get scrape status. User can only see their own runs."""
    user_id = claims.get("sub")
    
    if run_id not in SCRAPE_RUNS:
        return {"run_id": run_id, "status": "NOT_FOUND", "error": "Run not found"}
    
    run = SCRAPE_RUNS[run_id]
    
    # SECURITY: Only allow users to see their own scrape runs
    if run.get("user_id") != user_id:
        return {"run_id": run_id, "status": "NOT_FOUND", "error": "Run not found"}
    
    return run


@router.get("/runs", dependencies=[Depends(check_rate_limit)])
async def list_scrape_runs(
    claims: dict = Depends(verify_jwt),  # REQUIRE auth
):
    """List user's scrape runs (without full job data)."""
    user_id = claims.get("sub")
    
    # Only return runs belonging to this user
    user_runs = [
        {k: v for k, v in run.items() if k != "jobs"}
        for run in SCRAPE_RUNS.values()
        if run.get("user_id") == user_id
    ]
    
    return user_runs


@router.get("/quota")
async def get_rapidapi_quota():
    """Check RapidAPI quota status. Public endpoint."""
    return {
        "requests_remaining": linkedin_client.requests_remaining,
        "monthly_limit": 100,
        "api_configured": bool(linkedin_client.api_key),
    }


@router.post("/cancel/{run_id}", dependencies=[Depends(check_rate_limit)])
async def cancel_scrape(
    run_id: str,
    claims: dict = Depends(verify_jwt),  # REQUIRE auth
):
    """Cancel a running scrape job. User can only cancel their own."""
    user_id = claims.get("sub")
    
    if run_id not in SCRAPE_RUNS:
        return {"error": "Run not found", "run_id": run_id}
    
    run = SCRAPE_RUNS[run_id]
    
    # SECURITY: Only allow users to cancel their own runs
    if run.get("user_id") != user_id:
        return {"error": "Run not found", "run_id": run_id}
    
    SCRAPE_RUNS[run_id]["status"] = "CANCELLED"
    SCRAPE_RUNS[run_id]["completed_at"] = datetime.utcnow().isoformat()
    
    return {"message": "Scrape cancelled", "run_id": run_id}
