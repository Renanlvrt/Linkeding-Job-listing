"""
Anti-Detection Utilities
=========================
Prevent LinkedIn blocking via:
- User-agent rotation
- Random delays
- Request headers mimicking real browsers
- Stealth Playwright configuration

2026 Best Practices:
- Max 50 requests/day per IP
- 2-5 second delays between requests
- Residential proxies for production
"""

import random
import asyncio
from typing import Optional
import time


# Chrome/Firefox user agents (2026 versions)
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Delay range between requests (seconds)
DELAY_RANGE = (2.0, 5.0)

# Max requests per session (conservative)
MAX_REQUESTS_PER_SESSION = 50


def get_random_user_agent() -> str:
    """Get a random user agent string."""
    return random.choice(USER_AGENTS)


def get_browser_headers(referer: Optional[str] = None) -> dict:
    """
    Generate headers that mimic a real browser.
    
    Args:
        referer: Optional referer URL
    
    Returns:
        Headers dict
    """
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


async def random_delay(min_seconds: float = None, max_seconds: float = None) -> None:
    """
    Async sleep for a random duration.
    
    Args:
        min_seconds: Minimum delay (default from DELAY_RANGE)
        max_seconds: Maximum delay (default from DELAY_RANGE)
    """
    min_s = min_seconds or DELAY_RANGE[0]
    max_s = max_seconds or DELAY_RANGE[1]
    delay = random.uniform(min_s, max_s)
    await asyncio.sleep(delay)


def sync_random_delay(min_seconds: float = None, max_seconds: float = None) -> None:
    """Synchronous version of random_delay."""
    min_s = min_seconds or DELAY_RANGE[0]
    max_s = max_seconds or DELAY_RANGE[1]
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)


class RateLimiter:
    """
    Simple rate limiter for scraping.
    
    Tracks requests per session and enforces delays.
    """
    
    def __init__(self, max_requests: int = MAX_REQUESTS_PER_SESSION):
        self.max_requests = max_requests
        self.request_count = 0
        self.last_request_time = 0
    
    def can_request(self) -> bool:
        """Check if we can make another request."""
        return self.request_count < self.max_requests
    
    @property
    def requests_remaining(self) -> int:
        """Remaining requests in this session."""
        return max(0, self.max_requests - self.request_count)
    
    async def wait_and_increment(self) -> bool:
        """
        Wait for rate limit and increment counter.
        
        Returns:
            True if request allowed, False if limit reached
        """
        if not self.can_request():
            return False
        
        # Ensure minimum delay between requests
        now = time.time()
        elapsed = now - self.last_request_time
        min_delay = DELAY_RANGE[0]
        
        if elapsed < min_delay:
            await asyncio.sleep(min_delay - elapsed)
        
        # Add random jitter
        await random_delay()
        
        self.request_count += 1
        self.last_request_time = time.time()
        return True
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        self.request_count = 0
        self.last_request_time = 0


# Playwright stealth configuration
STEALTH_BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-accelerated-2d-canvas",
    "--disable-gpu",
    "--window-size=1920,1080",
]

# Viewport variations (to avoid fingerprinting)
VIEWPORT_OPTIONS = [
    {"width": 1920, "height": 1080},
    {"width": 1680, "height": 1050},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
]


def get_random_viewport() -> dict:
    """Get a random viewport configuration."""
    return random.choice(VIEWPORT_OPTIONS)


async def setup_stealth_page(browser):
    """
    Create a stealth browser page with anti-detection measures.
    
    Args:
        browser: Playwright browser instance
    
    Returns:
        Configured page
    """
    viewport = get_random_viewport()
    
    context = await browser.new_context(
        viewport=viewport,
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
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)
    
    return page, context


# Proxy configuration (for production use)
class ProxyConfig:
    """
    Proxy configuration for LinkedIn scraping.
    
    For production, use residential proxies:
    - BrightData
    - IPRoyal
    - Oxylabs
    """
    
    def __init__(self, proxy_url: Optional[str] = None):
        """
        Args:
            proxy_url: Proxy URL (e.g., "http://user:pass@proxy.com:8080")
        """
        self.proxy_url = proxy_url
    
    def get_playwright_proxy(self) -> Optional[dict]:
        """Get proxy config for Playwright."""
        if not self.proxy_url:
            return None
        
        return {"server": self.proxy_url}
    
    def get_httpx_proxy(self) -> Optional[str]:
        """Get proxy config for httpx/aiohttp."""
        return self.proxy_url


# Singleton rate limiter
rate_limiter = RateLimiter()
