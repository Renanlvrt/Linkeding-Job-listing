# Anti-Detection Best Practices

## Why LinkedIn Blocks Scrapers

LinkedIn employs sophisticated anti-bot measures:

1. **Behavioral Analysis** - Tracks mouse movements, scroll patterns, click timing
2. **Rate Limiting** - Blocks IPs making too many requests
3. **Browser Fingerprinting** - Detects automation tools
4. **CAPTCHA Challenges** - Triggers on suspicious activity
5. **Account Verification** - Requires phone/email verification
6. **IP Reputation** - Blacklists known proxy/datacenter IPs

---

## Essential Anti-Detection Strategies

### 1. Request Rate Limiting

**Rule**: Max 50-100 requests per day per IP

```python
import asyncio
import random

# Add random delays between requests
async def random_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

# Rate limiter class
class RateLimiter:
    def __init__(self, max_requests: int = 50):
        self.max_requests = max_requests
        self.request_count = 0
    
    def can_request(self) -> bool:
        return self.request_count < self.max_requests
    
    def increment(self):
        self.request_count += 1
```

---

### 2. User-Agent Rotation

**Rule**: Rotate through realistic browser user agents

```python
import random

USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)
```

---

### 3. Browser-Like Headers

**Rule**: Send complete, realistic HTTP headers

```python
def get_browser_headers(referer: str = None) -> dict:
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    if referer:
        headers["Referer"] = referer
        headers["Sec-Fetch-Site"] = "same-origin"
    
    return headers
```

---

### 4. IP Rotation with Proxies

**Rule**: Use residential proxies, rotate frequently

**Recommended Proxy Providers**:

- BrightData (residential)
- IPRoyal (residential)
- Oxylabs (residential)
- SmartProxy

```python
import httpx

PROXY_LIST = [
    "http://user:pass@proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080",
]

async def fetch_with_proxy(url: str) -> str:
    proxy = random.choice(PROXY_LIST)
    async with httpx.AsyncClient(proxies={"all://": proxy}) as client:
        response = await client.get(url, headers=get_browser_headers())
        return response.text
```

**⚠️ Avoid**:

- Free public proxies (already blacklisted)
- Datacenter IPs (easily detected)
- Same proxy for too many requests

---

### 5. Playwright/Selenium Stealth

**Rule**: Override automation detection signals

```python
async def setup_stealth_page(browser):
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=get_random_user_agent(),
        locale="en-US",
        timezone_id="America/New_York",
    )
    
    page = await context.new_page()
    
    # Override navigator.webdriver
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override plugins (robots have empty plugins)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)
    
    return page, context
```

---

### 6. Session Persistence

**Rule**: Reuse cookies/sessions instead of fresh logins

```python
import json

# Save session after login
def save_session(cookies: list, filepath: str = "session.json"):
    with open(filepath, "w") as f:
        json.dump(cookies, f)

# Load session for subsequent requests
def load_session(filepath: str = "session.json") -> list:
    with open(filepath, "r") as f:
        return json.load(f)

# Apply cookies to Playwright context
async def apply_cookies(context, cookies):
    await context.add_cookies(cookies)
```

---

### 7. Human-Like Behavior

**Rule**: Simulate realistic browsing patterns

```python
import random

async def simulate_human_scroll(page):
    """Scroll page like a human would"""
    for _ in range(random.randint(2, 5)):
        await page.evaluate(f"window.scrollBy(0, {random.randint(200, 500)})")
        await asyncio.sleep(random.uniform(0.5, 1.5))

async def simulate_human_delay():
    """Wait before clicking/typing like a human"""
    await asyncio.sleep(random.uniform(0.3, 1.0))

async def browse_naturally(page, url):
    await page.goto(url)
    await simulate_human_delay()
    await simulate_human_scroll(page)
    # Read the page for a bit
    await asyncio.sleep(random.uniform(2, 4))
```

---

## Summary Checklist

| Strategy | Implementation |
|----------|----------------|
| ✅ Rate limiting | Max 50-100 requests/day/IP |
| ✅ Random delays | 2-5 seconds between requests |
| ✅ User-agent rotation | Pool of 5+ realistic UAs |
| ✅ Complete headers | Include all browser headers |
| ✅ Residential proxies | Rotate IPs frequently |
| ✅ Override webdriver | Stealth scripts |
| ✅ Session reuse | Persist cookies |
| ✅ Human-like behavior | Scroll, wait, vary timing |
| ✅ Off-peak hours | Scrape during low-activity times |
| ✅ Error handling | Back off on 429/403 errors |

---

## Detection Signals to Avoid

| Signal | How to Avoid |
|--------|--------------|
| `navigator.webdriver = true` | Override in stealth script |
| Empty `navigator.plugins` | Spoof plugins list |
| Fixed request timing | Add random jitter |
| Missing referer | Set realistic referer |
| Datacenter IP range | Use residential proxies |
| Too many requests | Implement rate limiting |
| No scroll/mouse events | Simulate human behavior |
| Instant page loads | Add artificial delays |
