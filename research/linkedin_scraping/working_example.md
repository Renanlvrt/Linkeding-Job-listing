# Working LinkedIn Job Scraper Example

This is a complete, tested example combining DuckDuckGo discovery with public page parsing.

## Complete Working Code

```python
"""
LinkedIn Job Scraper - Working Example
=====================================
Uses DuckDuckGo for discovery + httpx for parsing.
No authentication required.
"""

import asyncio
import logging
import random
import re
from typing import Optional
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== Configuration ====================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

DELAY_RANGE = (1.5, 3.5)  # seconds between requests


# ==================== Data Classes ====================

@dataclass
class Job:
    url: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    posted: Optional[str] = None
    applicants: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


# ==================== Helpers ====================

def get_random_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


async def random_delay():
    delay = random.uniform(*DELAY_RANGE)
    await asyncio.sleep(delay)


def parse_applicant_count(text: str) -> Optional[int]:
    """Extract applicant count from text like '50 applicants' or '100+ applicants'"""
    match = re.search(r'(\d+)\+?\s*applicants?', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_job_id(url: str) -> Optional[str]:
    """Extract LinkedIn job ID from URL"""
    match = re.search(r'/jobs/view/(\d+)', url)
    if match:
        return match.group(1)
    return None


# ==================== Discovery (DuckDuckGo) ====================

def discover_jobs_ddg(
    keywords: str,
    location: str = "",
    max_results: int = 20
) -> list[dict]:
    """
    Discover LinkedIn job URLs via DuckDuckGo.
    
    Args:
        keywords: Job search keywords
        location: Optional location filter
        max_results: Maximum jobs to return
    
    Returns:
        List of job dicts with url, title, snippet
    """
    query_parts = [
        'site:linkedin.com/jobs/view',
        f'"{keywords}"'
    ]
    
    if location:
        query_parts.append(f'"{location}"')
    
    query = " ".join(query_parts)
    logger.info(f"🔍 DDG Query: {query}")
    
    jobs = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results * 3))
        
        for r in results:
            url = r.get('href', '')
            if 'linkedin.com/jobs/view/' in url:
                job_id = extract_job_id(url)
                if job_id:
                    # Normalize URL
                    clean_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                    jobs.append({
                        'url': clean_url,
                        'job_id': job_id,
                        'title': r.get('title', '').replace(' | LinkedIn', ''),
                        'snippet': r.get('body', '')
                    })
        
        # Deduplicate by job_id
        seen = set()
        unique_jobs = []
        for job in jobs:
            if job['job_id'] not in seen:
                seen.add(job['job_id'])
                unique_jobs.append(job)
        
        logger.info(f"✅ Found {len(unique_jobs)} unique jobs")
        return unique_jobs[:max_results]
    
    except Exception as e:
        logger.error(f"❌ DDG discovery failed: {e}")
        return []


# ==================== Parsing (httpx) ====================

async def parse_job_page(url: str, client: httpx.AsyncClient) -> Job:
    """
    Parse a public LinkedIn job page.
    
    Args:
        url: LinkedIn job URL
        client: httpx async client
    
    Returns:
        Job object with extracted data
    """
    job = Job(url=url)
    
    try:
        await random_delay()
        response = await client.get(url, headers=get_random_headers(), follow_redirects=True)
        
        if response.status_code != 200:
            logger.warning(f"⚠️ HTTP {response.status_code}: {url}")
            job.is_active = False
            return job
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True).lower()
        
        # Check if job is closed
        closed_indicators = [
            'no longer accepting applications',
            'this job is no longer available',
            'job closed',
            'application closed'
        ]
        if any(ind in page_text for ind in closed_indicators):
            job.is_active = False
            logger.info(f"⛔ Closed: {url}")
            return job
        
        # Extract title
        title_elem = soup.select_one(
            '.top-card-layout__title, '
            '.topcard__title, '
            'h1.t-24'
        )
        if title_elem:
            job.title = title_elem.get_text(strip=True)
        
        # Extract company
        company_elem = soup.select_one(
            '.top-card-layout__company-url, '
            '.topcard__org-name-link, '
            'a.topcard__org-name-link'
        )
        if company_elem:
            job.company = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = soup.select_one(
            '.top-card-layout__bullet, '
            '.topcard__flavor--bullet, '
            'span.topcard__flavor--bullet'
        )
        if location_elem:
            job.location = location_elem.get_text(strip=True)
        
        # Extract applicants
        applicants_elem = soup.select_one(
            '.num-applicants__caption, '
            '.jobs-unified-top-card__applicant-count, '
            'span[class*="applicant"]'
        )
        if applicants_elem:
            job.applicants = parse_applicant_count(applicants_elem.get_text())
        
        # Extract posted date
        posted_elem = soup.select_one(
            '.posted-time-ago__text, '
            'span[class*="posted-time"]'
        )
        if posted_elem:
            job.posted = posted_elem.get_text(strip=True)
        
        # Extract description (truncated)
        desc_elem = soup.select_one(
            '.description__text, '
            '.show-more-less-html__markup, '
            'div.description'
        )
        if desc_elem:
            job.description = desc_elem.get_text(strip=True)[:1000]
        
        logger.info(f"✅ Parsed: {job.title} at {job.company}")
        return job
    
    except Exception as e:
        logger.error(f"❌ Parse error for {url}: {e}")
        return job


async def parse_jobs_batch(
    job_dicts: list[dict],
    max_concurrent: int = 3
) -> list[Job]:
    """
    Parse multiple job pages concurrently.
    
    Args:
        job_dicts: List of job dicts from discovery
        max_concurrent: Max concurrent requests
    
    Returns:
        List of Job objects
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def parse_with_semaphore(job_dict: dict, client: httpx.AsyncClient) -> Job:
        async with semaphore:
            return await parse_job_page(job_dict['url'], client)
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        tasks = [parse_with_semaphore(j, client) for j in job_dicts]
        jobs = await asyncio.gather(*tasks)
    
    return list(jobs)


# ==================== Main Scraper ====================

async def scrape_linkedin_jobs(
    keywords: str,
    location: str = "",
    max_results: int = 10,
    filter_inactive: bool = True
) -> list[Job]:
    """
    Main scraping function.
    
    Args:
        keywords: Job search keywords
        location: Optional location filter
        max_results: Maximum jobs to return
        filter_inactive: Remove closed/inactive jobs
    
    Returns:
        List of Job objects
    """
    logger.info(f"🚀 Starting scrape: '{keywords}' in '{location}'")
    
    # Step 1: Discover jobs via DDG
    discovered = discover_jobs_ddg(keywords, location, max_results * 2)
    
    if not discovered:
        logger.warning("No jobs discovered")
        return []
    
    # Step 2: Parse job pages
    jobs = await parse_jobs_batch(discovered[:max_results * 2])
    
    # Step 3: Filter inactive jobs
    if filter_inactive:
        jobs = [j for j in jobs if j.is_active]
    
    logger.info(f"🎯 Returning {len(jobs[:max_results])} jobs")
    return jobs[:max_results]


# ==================== CLI Interface ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper")
    parser.add_argument("keywords", help="Job search keywords")
    parser.add_argument("--location", "-l", default="", help="Location filter")
    parser.add_argument("--max", "-m", type=int, default=10, help="Max results")
    
    args = parser.parse_args()
    
    jobs = asyncio.run(scrape_linkedin_jobs(
        keywords=args.keywords,
        location=args.location,
        max_results=args.max
    ))
    
    print("\n" + "="*60)
    print(f"Found {len(jobs)} jobs")
    print("="*60 + "\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Posted: {job.posted}")
        print(f"   Applicants: {job.applicants}")
        print(f"   URL: {job.url}")
        print()


if __name__ == "__main__":
    main()
```

## Usage

### Command Line

```bash
# Basic search
python linkedin_scraper.py "Software Engineer"

# With location
python linkedin_scraper.py "Python Developer" --location "Remote"

# With max results
python linkedin_scraper.py "Data Scientist" --location "New York" --max 20
```

### As Module

```python
import asyncio
from linkedin_scraper import scrape_linkedin_jobs

jobs = asyncio.run(scrape_linkedin_jobs(
    keywords="Machine Learning Engineer",
    location="San Francisco",
    max_results=15
))

for job in jobs:
    print(f"{job.title} at {job.company}")
```

## Requirements

```
httpx>=0.25.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
duckduckgo_search>=4.0.0
```

Install:

```bash
pip install httpx beautifulsoup4 lxml duckduckgo_search
```

## Notes

1. **Rate Limiting**: Built-in delays (1.5-3.5s) between requests
2. **No Login Required**: Uses public pages only
3. **Deduplication**: Removes duplicate job IDs
4. **Inactive Filter**: Automatically removes closed jobs
5. **Error Handling**: Graceful handling of HTTP errors

## Limitations

- Limited to jobs indexed by DuckDuckGo
- Some job details may be incomplete on public pages
- Can't apply LinkedIn-native filters (use keywords instead)
- May miss very new jobs not yet indexed
