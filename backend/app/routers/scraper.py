"""
Scraper API Router
===================
Endpoints for triggering and monitoring scrape jobs.
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.scraper.orchestrator import orchestrator
from app.scraper.discovery import job_discovery
from app.scraper.linkedin_api import linkedin_client

router = APIRouter()


# ============================================================
# Pydantic Models
# ============================================================

class ScrapeRequest(BaseModel):
    """Request to start a scrape job."""
    keywords: str
    location: Optional[str] = "Remote"
    user_skills: Optional[list[str]] = None  # For match scoring
    max_results: int = 20
    use_rapidapi: bool = False  # Uses quota if True!


class QuickSearchRequest(BaseModel):
    """Request for quick discovery (free, no enrichment)."""
    keywords: str
    location: Optional[str] = ""
    max_results: int = 10


class ScrapeResponse(BaseModel):
    """Response from starting a scrape job."""
    run_id: str
    status: str
    message: str


class ScrapeStatus(BaseModel):
    """Status of a scrape run."""
    run_id: str
    status: str
    jobs_found: int
    progress: int  # 0-100
    started_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    jobs: Optional[list] = None


# ============================================================
# In-memory store for scrape runs
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
):
    """Background task to run a full scrape job."""
    try:
        SCRAPE_RUNS[run_id]["status"] = "RUNNING"
        SCRAPE_RUNS[run_id]["progress"] = 10
        
        # Run the orchestrator
        result = await orchestrator.run_scrape(
            keywords=keywords,
            location=location,
            user_skills=user_skills or [],
            max_jobs=max_results,
            use_rapidapi=use_rapidapi,
        )
        
        SCRAPE_RUNS[run_id]["status"] = "COMPLETED"
        SCRAPE_RUNS[run_id]["progress"] = 100
        SCRAPE_RUNS[run_id]["jobs_found"] = result.get("jobs_found", 0)
        SCRAPE_RUNS[run_id]["jobs"] = result.get("jobs", [])
        SCRAPE_RUNS[run_id]["completed_at"] = datetime.utcnow().isoformat()
        SCRAPE_RUNS[run_id]["sources"] = result.get("sources", {})
        SCRAPE_RUNS[run_id]["rapidapi_remaining"] = result.get("rapidapi_remaining")
        
    except Exception as e:
        SCRAPE_RUNS[run_id]["status"] = "FAILED"
        SCRAPE_RUNS[run_id]["error"] = str(e)
        SCRAPE_RUNS[run_id]["completed_at"] = datetime.utcnow().isoformat()


# ============================================================
# Endpoints
# ============================================================

@router.post("/start", response_model=ScrapeResponse)
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Start a new scrape job.
    
    - **keywords**: Job title or keywords to search
    - **location**: Location filter (default: Remote)
    - **user_skills**: Your skills for match scoring (optional)
    - **max_results**: Maximum jobs to return (default: 20)
    - **use_rapidapi**: Set to true to use RapidAPI (USES QUOTA!)
    
    Returns a run_id to check status.
    """
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
    }
    
    # Start background task
    background_tasks.add_task(
        run_scrape_job,
        run_id,
        request.keywords,
        request.location,
        request.user_skills or [],
        request.max_results,
        request.use_rapidapi,
    )
    
    return ScrapeResponse(
        run_id=run_id,
        status="QUEUED",
        message=f"Scrape started for '{request.keywords}' in {request.location}",
    )


@router.post("/quick")
async def quick_search(request: QuickSearchRequest):
    """
    Quick job discovery - FREE and INSTANT.
    
    Uses DuckDuckGo only (no RapidAPI, no Gemini).
    Great for testing or quick searches.
    """
    jobs = job_discovery.search_linkedin_jobs(
        keywords=request.keywords,
        location=request.location,
        max_results=request.max_results,
    )
    
    return {
        "status": "OK",
        "keywords": request.keywords,
        "location": request.location,
        "jobs_found": len(jobs),
        "jobs": jobs,
    }


@router.get("/status/{run_id}")
async def get_scrape_status(run_id: str):
    """Get the status of a scrape job."""
    if run_id not in SCRAPE_RUNS:
        return {
            "run_id": run_id,
            "status": "NOT_FOUND",
            "error": "Run not found",
        }
    
    return SCRAPE_RUNS[run_id]


@router.get("/runs")
async def list_scrape_runs():
    """List all scrape runs (without full job data)."""
    return [
        {k: v for k, v in run.items() if k != "jobs"}
        for run in SCRAPE_RUNS.values()
    ]


@router.get("/quota")
async def get_rapidapi_quota():
    """Check RapidAPI quota status."""
    return {
        "requests_remaining": linkedin_client.requests_remaining,
        "monthly_limit": 100,
        "api_configured": bool(linkedin_client.api_key),
    }


@router.post("/cancel/{run_id}")
async def cancel_scrape(run_id: str):
    """Cancel a running scrape job."""
    if run_id in SCRAPE_RUNS:
        SCRAPE_RUNS[run_id]["status"] = "CANCELLED"
        SCRAPE_RUNS[run_id]["completed_at"] = datetime.utcnow().isoformat()
        return {"message": "Scrape cancelled", "run_id": run_id}
    
    return {"error": "Run not found", "run_id": run_id}
