"""
Jobs API Router
================
Endpoints for job CRUD operations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# ============================================================
# Pydantic Models
# ============================================================

class JobBase(BaseModel):
    """Base job schema."""
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    applicants: Optional[int] = None
    match_score: int = 0
    skills_matched: list[str] = []
    source: str = "linkedin"


class JobCreate(JobBase):
    """Schema for creating a job."""
    external_id: Optional[str] = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    status: Optional[str] = None
    match_score: Optional[int] = None
    skills_matched: Optional[list[str]] = None


class JobResponse(JobBase):
    """Schema for job response."""
    id: str
    external_id: Optional[str] = None
    status: str
    scraped_at: datetime
    created_at: datetime


# ============================================================
# Mock Data (Replace with Supabase queries)
# ============================================================

MOCK_JOBS = [
    {
        "id": "job-001",
        "external_id": "linkedin-123456",
        "title": "Software Engineer Intern",
        "company": "Tech Corp Systems",
        "location": "San Francisco, CA (Remote)",
        "description": "Looking for a passionate intern to join our engineering team...",
        "link": "https://linkedin.com/jobs/123456",
        "applicants": 45,
        "match_score": 98,
        "skills_matched": ["Python", "React", "TypeScript"],
        "source": "linkedin",
        "status": "NEW",
        "scraped_at": "2024-01-30T10:00:00Z",
        "created_at": "2024-01-30T10:00:00Z",
    },
    {
        "id": "job-002",
        "external_id": "linkedin-789012",
        "title": "ML Engineer",
        "company": "AI Labs Inc",
        "location": "London, UK",
        "description": "Join our cutting-edge AI team working on foundation models...",
        "link": "https://linkedin.com/jobs/789012",
        "applicants": 120,
        "match_score": 92,
        "skills_matched": ["Python", "PyTorch", "Machine Learning"],
        "source": "linkedin",
        "status": "NEW",
        "scraped_at": "2024-01-30T09:30:00Z",
        "created_at": "2024-01-30T09:30:00Z",
    },
    {
        "id": "job-003",
        "external_id": "linkedin-345678",
        "title": "Robotics Software Developer",
        "company": "Boston Dynamics",
        "location": "Boston, MA",
        "description": "Work on next-generation robotic systems...",
        "link": "https://linkedin.com/jobs/345678",
        "applicants": 78,
        "match_score": 88,
        "skills_matched": ["ROS2", "C++", "Python", "Robotics"],
        "source": "linkedin",
        "status": "SAVED",
        "scraped_at": "2024-01-30T08:00:00Z",
        "created_at": "2024-01-30T08:00:00Z",
    },
]


# ============================================================
# Endpoints
# ============================================================

@router.get("/", response_model=list[dict])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    min_score: int = Query(0, ge=0, le=100, description="Minimum match score"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """
    List all jobs with optional filtering.
    
    - **status**: Filter by job status (NEW, SAVED, APPLIED, etc.)
    - **min_score**: Only return jobs with match_score >= this value
    - **limit**: Maximum number of results (default 50)
    - **offset**: Pagination offset
    """
    jobs = MOCK_JOBS
    
    # Apply filters
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    jobs = [j for j in jobs if j["match_score"] >= min_score]
    
    # Sort by match score descending
    jobs = sorted(jobs, key=lambda x: x["match_score"], reverse=True)
    
    # Pagination
    return jobs[offset : offset + limit]


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get a specific job by ID."""
    for job in MOCK_JOBS:
        if job["id"] == job_id:
            return job
    
    raise HTTPException(status_code=404, detail="Job not found")


@router.post("/", response_model=dict)
async def create_job(job: JobCreate):
    """
    Create a new job (used by scraper).
    Requires service role authentication.
    """
    # TODO: Insert into Supabase
    new_job = {
        "id": f"job-{len(MOCK_JOBS) + 1:03d}",
        **job.model_dump(),
        "status": "NEW",
        "scraped_at": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    return new_job


@router.patch("/{job_id}")
async def update_job(job_id: str, job_update: JobUpdate):
    """Update a job's status or match score."""
    for job in MOCK_JOBS:
        if job["id"] == job_id:
            if job_update.status:
                job["status"] = job_update.status
            if job_update.match_score is not None:
                job["match_score"] = job_update.match_score
            if job_update.skills_matched:
                job["skills_matched"] = job_update.skills_matched
            return job
    
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/stats/summary")
async def get_job_stats():
    """Get summary statistics about jobs."""
    total = len(MOCK_JOBS)
    by_status = {}
    avg_score = 0
    
    for job in MOCK_JOBS:
        status = job["status"]
        by_status[status] = by_status.get(status, 0) + 1
        avg_score += job["match_score"]
    
    return {
        "total_jobs": total,
        "by_status": by_status,
        "average_match_score": round(avg_score / total, 1) if total > 0 else 0,
    }
