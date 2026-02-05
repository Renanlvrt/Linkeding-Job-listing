# Python Libraries for LinkedIn Scraping

## Comparison Table

| Library | Method | Login Required | Filters | Reliability | Maintenance |
|---------|--------|----------------|---------|-------------|-------------|
| **linkedin-jobs-scraper** | Selenium/Chrome | Optional (cookies) | ✅ Full | ⭐⭐⭐ | Active |
| **duckduckgo_search** | DDG API | ❌ No | ❌ Basic | ⭐⭐⭐⭐ | Active |
| **httpx + BeautifulSoup** | HTTP | ❌ No | ❌ None | ⭐⭐⭐⭐ | N/A |
| **Playwright** | Browser | ✅ Yes | ✅ Full | ⭐⭐⭐ | Active |
| **Selenium** | Browser | ✅ Yes | ✅ Full | ⭐⭐ | Active |

---

## 1. linkedin-jobs-scraper (Recommended for Direct Scraping)

### Installation

```bash
pip install linkedin-jobs-scraper
```

### Requirements

- Python >= 3.7
- Chrome or Chromium browser
- Chromedriver (matching Chrome version)

### Features

- Full LinkedIn filter support
- Event-driven architecture
- Concurrent scraping
- Proxy support (experimental)
- Cookie-based authentication

### Example

```python
import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters, TimeFilters, TypeFilters,
    ExperienceLevelFilters, OnSiteOrRemoteFilters,
    SalaryBaseFilters
)

logging.basicConfig(level=logging.INFO)

def on_data(data: EventData):
    print(f"Job: {data.title} at {data.company}")
    print(f"Link: {data.link}")
    print(f"Location: {data.location}")
    print(f"Posted: {data.date}")
    print("---")

def on_error(error):
    print(f"Error: {error}")

scraper = LinkedinScraper(
    headless=True,
    max_workers=1,
    slow_mo=1.0,  # 1 second between actions
    page_load_timeout=40
)

scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)

queries = [
    Query(
        query='Software Engineer',
        options=QueryOptions(
            locations=['United States'],
            limit=25,
            skip_promoted_jobs=True,
            apply_link=True,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.WEEK,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE],
                base_salary=SalaryBaseFilters.SALARY_80K
            )
        )
    )
]

scraper.run(queries)
```

### Available Filters

**TimeFilters**:

- `DAY`, `WEEK`, `MONTH`, `ANY`

**TypeFilters**:

- `FULL_TIME`, `PART_TIME`, `TEMPORARY`, `CONTRACT`

**ExperienceLevelFilters**:

- `INTERNSHIP`, `ENTRY_LEVEL`, `ASSOCIATE`, `MID_SENIOR`, `DIRECTOR`

**OnSiteOrRemoteFilters**:

- `ON_SITE`, `REMOTE`, `HYBRID`

**SalaryBaseFilters**:

- `SALARY_40K` through `SALARY_200K`

**IndustryFilters**:

- `IT_SERVICES`, `SOFTWARE_DEVELOPMENT`, `FINANCIAL_SERVICES`, etc.

---

## 2. duckduckgo_search (Recommended for Discovery)

### Installation

```bash
pip install duckduckgo_search
```

### Features

- No authentication needed
- Rate-limit friendly
- Returns job URLs for further parsing
- Works as discovery layer

### Example

```python
from duckduckgo_search import DDGS

def search_linkedin_jobs(
    keywords: str,
    location: str = "",
    max_results: int = 20
) -> list[dict]:
    """Search for LinkedIn jobs via DuckDuckGo"""
    
    query = f'site:linkedin.com/jobs/view "{keywords}"'
    if location:
        query += f' "{location}"'
    
    jobs = []
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results * 3))
    
    for r in results:
        url = r.get('href', '')
        if 'linkedin.com/jobs/view/' in url or 'linkedin.com/jobs/' in url:
            jobs.append({
                'url': url,
                'title': r.get('title', ''),
                'snippet': r.get('body', '')
            })
    
    return jobs[:max_results]

# Usage
jobs = search_linkedin_jobs("Python Developer", "Remote", max_results=10)
for job in jobs:
    print(f"{job['title']}: {job['url']}")
```

---

## 3. httpx + BeautifulSoup (For Public Page Parsing)

### Installation

```bash
pip install httpx beautifulsoup4 lxml
```

### Features

- Fast, async HTTP client
- No browser overhead
- Parse public LinkedIn job pages
- Lightweight

### Example

```python
import httpx
from bs4 import BeautifulSoup
import asyncio

async def parse_linkedin_job(url: str) -> dict:
    """Parse a public LinkedIn job page"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
    
    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}"}
    
    soup = BeautifulSoup(response.text, "lxml")
    
    # Extract data from public page
    title_elem = soup.select_one(".top-card-layout__title, .topcard__title")
    company_elem = soup.select_one(".top-card-layout__company-url, .topcard__org-name-link")
    location_elem = soup.select_one(".top-card-layout__first-subline, .topcard__flavor--bullet")
    
    # Extract description
    desc_elem = soup.select_one(".description__text, .show-more-less-html__markup")
    
    return {
        "url": url,
        "title": title_elem.get_text(strip=True) if title_elem else None,
        "company": company_elem.get_text(strip=True) if company_elem else None,
        "location": location_elem.get_text(strip=True) if location_elem else None,
        "description": desc_elem.get_text(strip=True)[:500] if desc_elem else None,
    }

# Usage
job = asyncio.run(parse_linkedin_job("https://www.linkedin.com/jobs/view/123456789"))
print(job)
```

---

## 4. Playwright (For Full Browser Control)

### Installation

```bash
pip install playwright
playwright install chromium
```

### Features

- Modern browser automation
- Better stealth than Selenium
- Async support
- Auto-wait for elements

### Example

```python
from playwright.async_api import async_playwright
import asyncio

async def scrape_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
        )
        
        page = await context.new_page()
        
        # Navigate to job search
        await page.goto("https://www.linkedin.com/jobs/search/?keywords=python")
        
        # Wait for results
        await page.wait_for_selector(".jobs-search__results-list")
        
        # Extract job cards
        jobs = await page.query_selector_all(".base-card")
        
        for job in jobs[:5]:
            title = await job.query_selector(".base-search-card__title")
            company = await job.query_selector(".base-search-card__subtitle")
            
            print(f"{await title.inner_text()}: {await company.inner_text()}")
        
        await browser.close()

asyncio.run(scrape_with_playwright())
```

---

## Recommendation for This Project

### Hybrid Setup (Best Reliability)

```python
# 1. Use DuckDuckGo for discovery
from duckduckgo_search import DDGS

# 2. Use httpx for public page parsing
import httpx
from bs4 import BeautifulSoup

# 3. Optionally use linkedin-jobs-scraper for authenticated access
# (only when DDG + httpx is insufficient)
```

### Why This Works

1. **DuckDuckGo** - No LinkedIn detection, finds indexed jobs
2. **httpx** - Fast validation of job pages, no browser overhead
3. **linkedin-jobs-scraper** - Fallback for when you need full filter access

This layered approach minimizes LinkedIn detection while maximizing data quality.
