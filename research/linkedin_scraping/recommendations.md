# Recommendations for This Project

## Current Issues

The current LinkedIn scraper has several issues:

1. **DuckDuckGo Discovery** - Works but limited data in snippets
2. **HTML Validation** - Import errors breaking the pipeline
3. **Playwright Validation** - Slow and resource-intensive
4. **Filter Application** - Not using LinkedIn-native filters effectively

---

## Recommended Architecture

### Option A: Use linkedin-jobs-scraper Library (Recommended)

**Replace the current discovery + validation approach with the established `linkedin-jobs-scraper` library.**

#### Pros

- Actively maintained
- Full filter support (experience, salary, remote, etc.)
- Event-driven architecture
- Built-in rate limiting
- Cookie-based authentication

#### Cons

- Requires Chrome/Chromedriver
- May need LinkedIn cookies for some environments

#### Implementation

```python
# backend/app/scraper/linkedin_scraper.py

import logging
from typing import Optional
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters, TimeFilters, TypeFilters,
    ExperienceLevelFilters, OnSiteOrRemoteFilters
)

logger = logging.getLogger(__name__)


class JobScraper:
    def __init__(self, li_at_cookie: Optional[str] = None):
        self.jobs = []
        self.scraper = LinkedinScraper(
            headless=True,
            max_workers=1,
            slow_mo=1.0,
            page_load_timeout=40
        )
        self.scraper.on(Events.DATA, self._on_data)
        self.scraper.on(Events.ERROR, self._on_error)
    
    def _on_data(self, data: EventData):
        self.jobs.append({
            "job_id": data.job_id,
            "title": data.title,
            "company": data.company,
            "location": data.location,
            "link": data.link,
            "date": data.date,
            "description": data.description[:500] if data.description else None,
        })
    
    def _on_error(self, error):
        logger.error(f"Scraper error: {error}")
    
    def scrape(
        self,
        keywords: str,
        location: str = "",
        max_results: int = 25,
        posted_within_days: int = 7,
        experience_levels: list[str] = None,
        job_types: list[str] = None,
        remote_only: bool = False,
    ) -> list[dict]:
        """Run scrape with filters"""
        
        self.jobs = []
        
        # Build filter config
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=self._days_to_time_filter(posted_within_days),
        )
        
        if job_types:
            filters.type = [getattr(TypeFilters, t.upper()) for t in job_types]
        
        if experience_levels:
            filters.experience = [
                getattr(ExperienceLevelFilters, e.upper().replace("-", "_"))
                for e in experience_levels
            ]
        
        if remote_only:
            filters.on_site_or_remote = [OnSiteOrRemoteFilters.REMOTE]
        
        query = Query(
            query=keywords,
            options=QueryOptions(
                locations=[location] if location else [],
                limit=max_results,
                skip_promoted_jobs=True,
                filters=filters
            )
        )
        
        self.scraper.run([query])
        return self.jobs
    
    def _days_to_time_filter(self, days: int):
        if days <= 1:
            return TimeFilters.DAY
        elif days <= 7:
            return TimeFilters.WEEK
        elif days <= 30:
            return TimeFilters.MONTH
        return TimeFilters.ANY
```

---

### Option B: Keep Current Architecture (Fix Issues)

If you want to keep the DuckDuckGo + HTML approach, here are the fixes needed:

#### 1. Fix html_validator.py Imports

```python
# Change this:
from app.scraper.anti_detect import (
    get_random_headers,    # WRONG
    async_random_delay,    # WRONG
    rate_limiter,
)

# To this:
from app.scraper.anti_detect import (
    get_browser_headers,   # CORRECT
    random_delay,          # CORRECT  
    rate_limiter,
)
```

#### 2. Fix rate_limiter Method Call

```python
# Change this:
await rate_limiter.check()  # WRONG - method doesn't exist

# To this:
if rate_limiter.can_request():
    rate_limiter.request_count += 1
else:
    return {"passes": True, "reason": "rate_limit"}  # Skip, don't fail
```

#### 3. Simplify the Pipeline

Remove the 3-tier validation (too complex, prone to errors):

```
BEFORE: DDG → Snippet Filter → HTML Validation → Playwright Validation
AFTER:  DDG → Basic Filter → Direct URL Check
```

---

## Feature Comparison

| Feature | Option A (linkedin-jobs-scraper) | Option B (Current + Fixes) |
|---------|----------------------------------|----------------------------|
| Setup Complexity | Medium (needs Chrome) | Low |
| Filter Support | ✅ Full LinkedIn filters | ❌ Limited |
| Rate Limiting | Built-in | Manual |
| Reliability | ⭐⭐⭐⭐ | ⭐⭐ |
| Speed | Slower (browser) | Faster (HTTP) |
| Data Completeness | ✅ Full job details | ⚠️ Partial |
| Risk of Blocking | Medium | Low |

---

## Implementation Priority

### Immediate (Fix Current Issues)

1. ✅ Fix `html_validator.py` import errors
2. ✅ Test backend restart
3. Test a simple scrape

### Short-term (Improve Reliability)

1. Replace DDG discovery with `linkedin-jobs-scraper`
2. Keep HTML validation as backup
3. Remove Playwright tier (redundant with linkedin-jobs-scraper)

### Long-term (Production Ready)

1. Add Chrome/Chromedriver to deployment
2. Implement cookie rotation
3. Add residential proxy support
4. Monitor for LinkedIn changes

---

## Quick Fix (Do This Now)

Run the backend and test with a simple curl:

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Test quick scrape
curl -X POST http://localhost:8000/api/scraper/quick \
  -H "Content-Type: application/json" \
  -d '{"keywords": "software engineer", "location": "Remote", "max_results": 5}'
```

If that fails, check the backend logs for the specific error.
