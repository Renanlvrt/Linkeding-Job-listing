# LinkedIn Scraping Approaches

## Overview

There are 4 main approaches to scraping LinkedIn job data:

1. **Direct Scraping with Headless Browser** (Selenium/Playwright)
2. **Public Listings Scraping** (No login required)
3. **DuckDuckGo Discovery + HTML Parsing**
4. **Third-Party APIs** (Paid services)

---

## Approach 1: Direct Scraping with Headless Browser

### How It Works

- Use Selenium or Playwright to control a browser
- Login with LinkedIn credentials (or use cookies)
- Navigate and extract data

### Pros

- Full access to LinkedIn data
- Can apply any filter

### Cons

- **High risk of account ban**
- Requires Chrome/Chromedriver setup
- Slow (must wait for page loads)
- LinkedIn actively detects automation

### Recommended Library

**linkedin-jobs-scraper** by spinlud

```bash
pip install linkedin-jobs-scraper
```

```python
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters, TimeFilters, TypeFilters,
    ExperienceLevelFilters, OnSiteOrRemoteFilters
)

scraper = LinkedinScraper(
    headless=True,
    max_workers=1,
    slow_mo=0.5,  # Avoid rate limiting
    page_load_timeout=40
)

queries = [
    Query(
        query='Software Engineer',
        options=QueryOptions(
            locations=['United States'],
            limit=50,
            skip_promoted_jobs=True,
            filters=QueryFilters(
                time=TimeFilters.WEEK,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE]
            )
        )
    )
]

scraper.run(queries)
```

### Authentication Required

Set `LI_AT_COOKIE` environment variable with your LinkedIn session cookie:

1. Login to LinkedIn in Chrome
2. Open DevTools → Application → Cookies → linkedin.com
3. Copy the `li_at` cookie value
4. Export: `LI_AT_COOKIE=<value> python scrape.py`

---

## Approach 2: Public Listings Scraping (No Login)

### How It Works

- LinkedIn job pages are publicly accessible at `linkedin.com/jobs/view/<job_id>`
- Can fetch HTML directly with httpx/requests + BeautifulSoup
- No authentication needed

### Pros

- No account risk
- Faster (no browser overhead)
- Legal for public data

### Cons

- Limited data compared to logged-in view
- LinkedIn may block IPs
- Some fields may be obscured

### Example

```python
import httpx
from bs4 import BeautifulSoup

async def scrape_public_job(job_url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(job_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract job data from public page
        title = soup.select_one('.top-card-layout__title')
        company = soup.select_one('.top-card-layout__company')
        location = soup.select_one('.top-card-layout__first-subline')
        
        return {
            "title": title.get_text(strip=True) if title else None,
            "company": company.get_text(strip=True) if company else None,
            "location": location.get_text(strip=True) if location else None,
        }
```

---

## Approach 3: DuckDuckGo Discovery + HTML Parsing

### How It Works

1. Use DuckDuckGo to search `site:linkedin.com/jobs <keywords>`
2. Extract job URLs from search results
3. Fetch public job pages for details

### Pros

- No LinkedIn API needed
- Respects rate limits naturally
- Gets recent, indexed jobs

### Cons

- Limited to what DuckDuckGo has indexed
- Can't apply LinkedIn-specific filters
- May miss some jobs

### Example

```python
from duckduckgo_search import DDGS

def discover_linkedin_jobs(keywords: str, location: str, max_results: int = 20):
    query = f'site:linkedin.com/jobs "{keywords}" "{location}"'
    
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results * 2))
    
    jobs = []
    for r in results:
        url = r.get('href', '')
        if 'linkedin.com/jobs/view/' in url:
            jobs.append({
                'url': url,
                'title': r.get('title', ''),
                'snippet': r.get('body', '')
            })
    
    return jobs[:max_results]
```

---

## Approach 4: Third-Party APIs (Paid)

### Recommended Services

| Service | Pricing | Features |
|---------|---------|----------|
| **Bright Data** | Pay-per-use | LinkedIn Jobs API, proxy included |
| **Proxycurl** | $0.01/request | LinkedIn data enrichment |
| **RapidAPI** | Varies | Multiple LinkedIn scrapers |
| **Apify** | Credits | No-login LinkedIn scraper |
| **TheirStack** | Subscription | Aggregated job data |

### Example with RapidAPI

```python
import requests

url = "https://linkedin-job-search-api.p.rapidapi.com/jobs"

querystring = {
    "keywords": "software engineer",
    "location": "Remote",
    "posted_date": "past_week"
}

headers = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "linkedin-job-search-api.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
jobs = response.json()
```

---

## Recommendation for This Project

**Best Approach: Hybrid Strategy**

1. **Primary**: DuckDuckGo discovery (low risk, free)
2. **Secondary**: linkedin-jobs-scraper with cookies (more data)
3. **Fallback**: Public HTML scraping for job details

This balances reliability, cost, and risk.
