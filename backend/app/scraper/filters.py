"""
LinkedIn Filter Utilities
==========================
Core filter logic for LinkedIn job scraping.

Converts user-friendly inputs (days, max applicants) to LinkedIn URL parameters.
"""

import re
from typing import Optional
from urllib.parse import urlencode, quote_plus


# LinkedIn f_TPR (Time Posted Range) values in seconds
TIME_FILTERS = {
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2592000,
}

# LinkedIn f_E (Experience Level) values
EXPERIENCE_LEVELS = {
    "internship": "1",
    "entry": "2",
    "associate": "3",
    "mid-senior": "4",
    "director": "5",
    "executive": "6",
}

# LinkedIn f_JT (Job Type) values
JOB_TYPES = {
    "full-time": "F",
    "part-time": "P",
    "contract": "C",
    "temporary": "T",
    "internship": "I",
    "volunteer": "V",
}

# LinkedIn f_WT (Workplace Type) values
WORKPLACE_TYPES = {
    "on-site": "1",
    "remote": "2",
    "hybrid": "3",
}



# Patterns for detecting CLOSED jobs (multi-language)
CLOSED_PATTERNS = [
    r"no longer accepting",
    r"applications?\s+(are\s+)?closed",
    r"(this\s+)?job\s+(is\s+)?no longer available",
    r"posting\s+(has\s+)?expired",
    r"plus\s+d.applications?\s+accept[ée]es",  # French
    r"candidatures?\s+ferm[ée]es",  # French
    r"ya no acepta",  # Spanish
]

# Patterns for detecting REPOSTED jobs
REPOSTED_PATTERNS = [
    r"reposted\s+\d+\s*(day|week|month|year)s?\s*ago",
    r"repost[ée]",  # French
    r"reposted",
    r"republished",
]


def build_ddg_exclude_query(keywords: str, location: str) -> str:
    """
    Build DuckDuckGo query with Boolean exclusions for closed/reposted.
    
    Note: DDG Boolean operators are ~70% effective; use as pre-filter only.
    
    Args:
        keywords: Job search keywords
        location: Location filter
    
    Returns:
        DDG query string with exclusions
    """
    # Key exclusion terms (keep short for DDG limits)
    exclude_terms = [
        "no longer accepting",
        "reposted",
        "closed",
        "expired",
    ]
    
    exclude_clause = " ".join(f'-"{term}"' for term in exclude_terms)
    
    return f'site:linkedin.com/jobs "{keywords}" {location} {exclude_clause}'



def days_to_linkedin_param(days: int) -> str:
    """
    Convert days to LinkedIn f_TPR parameter (seconds).
    
    LinkedIn uses 'r' prefix + seconds since posting.
    Example: 7 days = r604800
    
    Args:
        days: Number of days (1-30)
    
    Returns:
        LinkedIn f_TPR value (e.g., "r604800")
    """
    if days <= 0:
        days = 1  # Minimum 1 day
    if days > 30:
        days = 30  # Max 30 days (LinkedIn limit)
    
    seconds = days * 86400
    return f"r{seconds}"


def build_linkedin_search_url(
    keywords: str,
    location: str = "",
    posted_within_days: int = 7,
    easy_apply: bool = False,
    sort_by_date: bool = True,
    page: int = 0,
    experience_levels: list[str] = None,  # ["entry", "mid-senior"]
    job_types: list[str] = None,  # ["full-time", "contract"]
    workplace_types: list[str] = None,  # ["remote", "hybrid"]
) -> str:
    """
    Build properly parameterized LinkedIn job search URL.
    
    Args:
        keywords: Job search keywords
        location: Location filter
        posted_within_days: Max job age in days
        easy_apply: Filter to Easy Apply only
        sort_by_date: Sort by most recent
        page: Pagination (0-indexed, 25 jobs per page)
        experience_levels: List of experience levels (entry, mid-senior, etc.)
        job_types: List of job types (full-time, contract, etc.)
        workplace_types: List of workplace types (remote, hybrid, on-site)
    
    Returns:
        Full LinkedIn search URL with params
    """
    base_url = "https://www.linkedin.com/jobs/search"
    
    params = {
        "keywords": keywords,
        "f_TPR": days_to_linkedin_param(posted_within_days),
        "f_AL": "true",  # Actively hiring
    }
    
    if location:
        params["location"] = location
    
    if easy_apply:
        params["f_EA"] = "true"
    
    if sort_by_date:
        params["sortBy"] = "DD"  # Date descending
    
    if page > 0:
        params["start"] = page * 25
    
    # Experience level filter (e.g., f_E=2,4 for Entry+Mid-Senior)
    if experience_levels:
        codes = [EXPERIENCE_LEVELS.get(e.lower(), "") for e in experience_levels]
        codes = [c for c in codes if c]  # Remove empty
        if codes:
            params["f_E"] = ",".join(codes)
    
    # Job type filter (e.g., f_JT=F,C for Full-time+Contract)
    if job_types:
        codes = [JOB_TYPES.get(jt.lower(), "") for jt in job_types]
        codes = [c for c in codes if c]
        if codes:
            params["f_JT"] = ",".join(codes)
    
    # Workplace type filter (e.g., f_WT=2 for Remote)
    if workplace_types:
        codes = [WORKPLACE_TYPES.get(wt.lower(), "") for wt in workplace_types]
        codes = [c for c in codes if c]
        if codes:
            params["f_WT"] = ",".join(codes)
    
    return f"{base_url}?{urlencode(params)}"


def parse_applicant_count(text: str) -> Optional[int]:
    """
    Parse applicant count from various text formats.
    
    Handles:
    - "45 applicants"
    - "Over 100 applicants" -> 101
    - "100+ applicants" -> 101
    - "1,234 applicants" -> 1234
    - "Be an early applicant" -> 0
    - French: "45 candidats"
    
    Args:
        text: Text containing applicant info
    
    Returns:
        Applicant count as int, or None if not found
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Early applicant = very few
    if "early applicant" in text_lower or "be among the first" in text_lower:
        return 0
    
    # "100+" or "Over 100" patterns
    over_pattern = r'(?:over|plus de|\+)\s*(\d+(?:,\d+)?)\s*(?:applicants?|candidats?|candidatures?)'
    over_match = re.search(over_pattern, text_lower)
    if over_match:
        num_str = over_match.group(1).replace(",", "")
        return int(num_str) + 1  # "Over 100" = 101
    
    # Explicit "100+" format
    plus_pattern = r'(\d+(?:,\d+)?)\+\s*(?:applicants?|candidats?|candidatures?)?'
    plus_match = re.search(plus_pattern, text_lower)
    if plus_match:
        num_str = plus_match.group(1).replace(",", "")
        return int(num_str) + 1
    
    # Standard "N applicants" pattern (multi-language)
    standard_pattern = r'(\d+(?:,\d+)?)\s*(?:applicants?|candidats?|candidatures?|postulantes?)'
    standard_match = re.search(standard_pattern, text_lower)
    if standard_match:
        num_str = standard_match.group(1).replace(",", "")
        return int(num_str)
    
    return None


def parse_posted_time(text: str) -> Optional[int]:
    """
    Parse posted time from text to hours ago.
    
    Handles:
    - "1 hour ago" -> 1
    - "2 days ago" -> 48
    - "1 week ago" -> 168
    - "3 weeks ago" -> 504
    - "1 month ago" -> 720
    
    Args:
        text: Text containing time info
    
    Returns:
        Hours since posting, or None if not found
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Pattern: "N unit(s) ago"
    pattern = r'(\d+)\s*(hour|day|week|month)s?\s*ago'
    match = re.search(pattern, text_lower)
    
    if not match:
        return None
    
    num = int(match.group(1))
    unit = match.group(2)
    
    multipliers = {
        "hour": 1,
        "day": 24,
        "week": 168,
        "month": 720,
    }
    
    return num * multipliers.get(unit, 24)


def job_passes_filters(
    job: dict,
    max_applicants: int = 100,
    max_hours_old: int = 168,  # 7 days default
) -> tuple[bool, str]:
    """
    Check if a job passes all filters.
    
    Args:
        job: Job dict with applicants, posted_ago, etc.
        max_applicants: Max applicant count allowed
        max_hours_old: Max age in hours
    
    Returns:
        (passes, reason) - True if passes, reason if not
    """
    # Check applicant count
    applicants = job.get("applicants") or job.get("applicant_count")
    if applicants is not None:
        if applicants > max_applicants:
            return False, f"too_many_applicants:{applicants}"
    
    # Check posted time
    posted_ago = job.get("posted_ago") or job.get("posted_hours_ago")
    if isinstance(posted_ago, str):
        hours = parse_posted_time(posted_ago)
        if hours is not None and hours > max_hours_old:
            return False, f"too_old:{hours}h"
    elif isinstance(posted_ago, (int, float)):
        if posted_ago > max_hours_old:
            return False, f"too_old:{posted_ago}h"
    
    # Check if active (if field exists)
    is_active = job.get("is_active")
    if is_active is False:
        return False, "job_closed"
    
    return True, "passed"


# CSS selectors for LinkedIn job page scraping (config-driven)
LINKEDIN_SELECTORS = {
    # Applicant count selectors (fallback chain)
    "applicants": [
        "[data-test-id='job-applicants']",
        "span.jobs-unified-top-card__applicant-count",
        "span:has-text('applicants')",
        "span:has-text('candidats')",
    ],
    
    # Apply button selectors
    "apply_button": [
        "[data-test-id='job-apply-button']",
        "button.jobs-apply-button",
        "button:has-text('Apply')",
        "button:has-text('Easy Apply')",
    ],
    
    # Posted time selectors
    "posted_time": [
        "time[datetime]",
        "span.jobs-unified-top-card__posted-date",
        "span:has-text('ago')",
    ],
    
    # Job CLOSED selectors (Playwright Tier 3)
    "closed": [
        ".jobs-unified-top-card__capped-applications-badge",
        "text=No longer accepting applications",
        "text=This job is no longer available",
        "text=Applications are closed",
        "text=Plus d'applications acceptées",  # French
    ],
    
    # Job REPOSTED selectors (Playwright Tier 3)
    "reposted": [
        "text=Reposted",
        "span:has-text('Reposted')",
        "span:has-text('Reposté')",  # French
    ],
    
    # Legacy: closed_indicators (for backward compatibility)
    "closed_indicators": [
        "No longer accepting applications",
        "This job is no longer available",
        "Applications are closed",
    ],
}
