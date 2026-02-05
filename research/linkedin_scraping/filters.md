# LinkedIn Job Search URL Filters

## Complete Reference

LinkedIn job search URLs use query parameters to apply filters. Understanding these allows you to construct precise search URLs.

---

## Base URL Structure

```
https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&{filters}
```

---

## Filter Parameters

### `f_TPR` - Time Posted Recency

Filter jobs by how recently they were posted. Uses `r` prefix + seconds.

| Parameter | Description |
|-----------|-------------|
| `f_TPR=r3600` | Last hour (3,600 seconds) |
| `f_TPR=r14400` | Last 4 hours |
| `f_TPR=r86400` | Last 24 hours (1 day) |
| `f_TPR=r604800` | Last week (7 days) |
| `f_TPR=r2592000` | Last month (30 days) |

**Formula**: `r{days * 86400}`

```python
def days_to_linkedin_param(days: int) -> str:
    return f"r{days * 86400}"

# Examples:
# 1 day:  r86400
# 3 days: r259200
# 7 days: r604800
# 14 days: r1209600
```

---

### `f_E` - Experience Level

| Parameter | Description |
|-----------|-------------|
| `f_E=1` | Internship |
| `f_E=2` | Entry level |
| `f_E=3` | Associate |
| `f_E=4` | Mid-Senior level |
| `f_E=5` | Director |
| `f_E=6` | Executive |

**Multiple values**: Combine with `%2C` (URL-encoded comma)

```
f_E=1%2C2  → Internship AND Entry level
f_E=4%2C5%2C6  → Mid-Senior, Director, Executive
```

---

### `f_JT` - Job Type

| Parameter | Description |
|-----------|-------------|
| `f_JT=F` | Full-time |
| `f_JT=P` | Part-time |
| `f_JT=C` | Contract |
| `f_JT=T` | Temporary |
| `f_JT=I` | Internship |
| `f_JT=V` | Volunteer |
| `f_JT=O` | Other |

**Multiple values**: `f_JT=F%2CC` → Full-time AND Contract

---

### `f_WT` - Workplace Type (Remote/On-site/Hybrid)

| Parameter | Description |
|-----------|-------------|
| `f_WT=1` | On-site |
| `f_WT=2` | Remote |
| `f_WT=3` | Hybrid |

**Multiple values**: `f_WT=2%2C3` → Remote AND Hybrid

---

### `f_EA` - Easy Apply

| Parameter | Description |
|-----------|-------------|
| `f_EA=true` | Easy Apply jobs only |

---

### `f_AL` - Actively Hiring / Actively Recruiting

| Parameter | Description |
|-----------|-------------|
| `f_AL=true` | Actively hiring companies |

---

### `f_C` - Company Filter

Filter by specific LinkedIn company IDs.

```
f_C=1441%2C17876832  → Google AND Microsoft
```

Find company IDs from LinkedIn company URLs.

---

### `f_I` - Industry Filter

Filter by industry code.

| Code | Industry |
|------|----------|
| 4 | Computer Software |
| 6 | Internet |
| 96 | IT Services |
| 43 | Financial Services |
| ... | Many more |

---

### `f_SB` - Salary Base Filter

| Parameter | Minimum Salary |
|-----------|----------------|
| `f_SB=1` | $40,000+ |
| `f_SB=2` | $60,000+ |
| `f_SB=3` | $80,000+ |
| `f_SB=4` | $100,000+ |
| `f_SB=5` | $120,000+ |
| `f_SB=6` | $140,000+ |
| `f_SB=7` | $160,000+ |
| `f_SB=8` | $180,000+ |
| `f_SB=9` | $200,000+ |

---

### `sortBy` - Sort Order

| Parameter | Description |
|-----------|-------------|
| `sortBy=DD` | Date Descending (Most Recent) |
| `sortBy=R` | Relevance |

---

### `start` - Pagination

| Parameter | Description |
|-----------|-------------|
| `start=0` | First page (jobs 1-25) |
| `start=25` | Second page (jobs 26-50) |
| `start=50` | Third page (jobs 51-75) |

**Formula**: `start = page_number * 25`

---

### `geoId` - Location Filter

Numeric IDs for geographic locations.

| geoId | Location |
|-------|----------|
| 103644278 | United States |
| 101165590 | United Kingdom |
| 102890883 | San Francisco Bay Area |
| 92000000 | Worldwide |

---

## Complete URL Example

```
https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=United%20States&geoId=103644278&f_TPR=r604800&f_E=2%2C3&f_JT=F&f_WT=2&f_EA=true&sortBy=DD
```

This searches for:

- Keywords: "software engineer"
- Location: United States
- Posted in last week
- Entry level OR Associate
- Full-time only
- Remote only
- Easy Apply
- Sorted by date

---

## Python Function to Build URL

```python
from urllib.parse import urlencode, quote

def build_linkedin_job_url(
    keywords: str,
    location: str = "",
    posted_within_days: int = 7,
    experience_levels: list[int] = None,  # 1-6
    job_types: list[str] = None,  # F, P, C, T, I, V
    workplace_types: list[int] = None,  # 1=onsite, 2=remote, 3=hybrid
    easy_apply: bool = False,
    sort_by_date: bool = True,
    page: int = 0,
) -> str:
    base_url = "https://www.linkedin.com/jobs/search/"
    
    params = {
        "keywords": keywords,
        "f_TPR": f"r{posted_within_days * 86400}",
    }
    
    if location:
        params["location"] = location
    
    if experience_levels:
        params["f_E"] = ",".join(str(e) for e in experience_levels)
    
    if job_types:
        params["f_JT"] = ",".join(job_types)
    
    if workplace_types:
        params["f_WT"] = ",".join(str(w) for w in workplace_types)
    
    if easy_apply:
        params["f_EA"] = "true"
    
    if sort_by_date:
        params["sortBy"] = "DD"
    
    if page > 0:
        params["start"] = page * 25
    
    return f"{base_url}?{urlencode(params)}"


# Example usage:
url = build_linkedin_job_url(
    keywords="Python Developer",
    location="Remote",
    posted_within_days=3,
    experience_levels=[2, 3],  # Entry + Associate
    workplace_types=[2],  # Remote
    easy_apply=True
)
print(url)
```

---

## Notes

1. **Parameter values are case-sensitive** (e.g., `F` not `f` for full-time)
2. **Multiple values** use URL-encoded comma (`%2C`)
3. **Not all filters** are available on public job search
4. **LinkedIn may change** these parameters without notice
5. **Rate limiting** applies - don't hammer the endpoint
