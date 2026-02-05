# LinkedIn Scraping Research

This folder contains comprehensive research on LinkedIn job scraping techniques, filters, and best practices.

---

## 📚 Table of Contents

### 1. [Approaches](./approaches.md)

**Different methods to scrape LinkedIn jobs**

- Direct browser automation (Selenium/Playwright)
- Public page scraping (no login)
- DuckDuckGo discovery + HTML parsing
- Third-party APIs (paid services)
- Pros/cons comparison and code examples

### 2. [URL Filters](./filters.md)

**Complete LinkedIn job URL parameter reference**

- `f_TPR` - Time posted filter
- `f_E` - Experience level
- `f_JT` - Job type (full-time, contract, etc.)
- `f_WT` - Workplace type (remote/hybrid/onsite)
- `f_SB` - Salary filter
- Pagination and sorting parameters
- Python function to build filter URLs

### 3. [Anti-Detection](./anti_detection.md)

**Strategies to avoid getting blocked**

- Rate limiting implementation
- User-agent rotation
- Browser-like headers
- IP rotation with proxies
- Playwright/Selenium stealth scripts
- Human behavior simulation
- Session persistence

### 4. [Python Libraries](./libraries.md)

**Tools and libraries comparison**

- `linkedin-jobs-scraper` - Full-featured Selenium scraper
- `duckduckgo_search` - Discovery via search engine
- `httpx` + `BeautifulSoup` - Lightweight HTTP parsing
- `Playwright` - Modern browser automation
- Installation and usage examples

### 5. [Working Example](./working_example.md)

**Complete, tested scraper implementation**

- Full Python script with DuckDuckGo + httpx
- Command-line interface
- Module usage example
- Built-in rate limiting and error handling
- No authentication required

### 6. [Recommendations](./recommendations.md)

**Strategic advice for this project**

- Option A: Use `linkedin-jobs-scraper` library
- Option B: Fix current architecture
- Feature comparison table
- Implementation priorities
- Quick fix steps

---

## 🔑 Key Takeaways

1. **Best Free Approach**: DuckDuckGo discovery + public page parsing
2. **Best Full Approach**: `linkedin-jobs-scraper` library with cookies
3. **Critical**: Always implement rate limiting (max 50-100 req/day/IP)
4. **Essential**: Use realistic browser headers and user agents
5. **Recommended**: Use residential proxies for production

---

## 📅 Research Date

February 2026
