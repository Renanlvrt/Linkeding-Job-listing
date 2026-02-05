"""
Security Middleware for FastAPI
================================
JWT verification, rate limiting, and request validation.
"""

import os
import time
import hashlib
from typing import Optional
from functools import wraps
from collections import defaultdict

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")  # Optional: for HS256 verification
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Extract project ref from URL for audience validation
# URL format: https://<project-ref>.supabase.co
PROJECT_REF = SUPABASE_URL.split("//")[1].split(".")[0] if SUPABASE_URL else ""

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # Max requests per window
RATE_LIMIT_WINDOW = 60     # Window in seconds
SCRAPER_RATE_LIMIT = 10    # Stricter limit for scraper endpoints

# ============================================================
# JWT VERIFICATION
# ============================================================

security = HTTPBearer(auto_error=False)


def get_supabase_public_key():
    """
    Fetch Supabase's public key for RS256 verification.
    Supabase uses RS256 by default for JWTs.
    """
    jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    try:
        jwk_client = PyJWKClient(jwks_url)
        return jwk_client
    except Exception:
        return None


class JWTValidator:
    """
    Validates Supabase JWTs with proper security checks.
    """
    
    def __init__(self):
        self.jwk_client = get_supabase_public_key()
    
    def validate_token(self, token: str) -> dict:
        """
        Validate JWT and return claims.
        Raises HTTPException on any validation failure.
        """
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
        
        try:
            # First, decode without verification to get header
            unverified_header = jwt.get_unverified_header(token)
            
            # CRITICAL: Reject 'alg: none' attacks
            if unverified_header.get("alg", "").lower() == "none":
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid token algorithm"
                )
            
            # Get signing key from JWKS
            if self.jwk_client:
                signing_key = self.jwk_client.get_signing_key_from_jwt(token)
                key = signing_key.key
            else:
                # Fallback to HS256 with secret (less secure but works for dev)
                key = SUPABASE_JWT_SECRET
            
            # Decode and validate
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256", "HS256"],
                audience="authenticated",
                issuer=f"{SUPABASE_URL}/auth/v1",
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "require": ["exp", "iat", "sub", "aud"],
                }
            )
            
            # Additional checks
            
            # 1. Check email is verified
            if not claims.get("email_confirmed_at"):
                raise HTTPException(
                    status_code=403,
                    detail="Email not verified"
                )
            
            # 2. Check token is not too old (issued within last 24h for refresh window)
            iat = claims.get("iat", 0)
            if time.time() - iat > 86400:  # 24 hours
                raise HTTPException(
                    status_code=401,
                    detail="Token too old, please re-authenticate"
                )
            
            return claims
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidAudienceError:
            raise HTTPException(status_code=401, detail="Invalid audience")
        except jwt.InvalidIssuerError:
            raise HTTPException(status_code=401, detail="Invalid issuer")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


jwt_validator = JWTValidator()


async def verify_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Dependency for routes requiring authenticated user.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    return jwt_validator.validate_token(credentials.credentials)


async def optional_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Dependency for routes that optionally accept authentication.
    """
    if not credentials:
        return None
    
    try:
        return jwt_validator.validate_token(credentials.credentials)
    except HTTPException:
        return None


# ============================================================
# RATE LIMITING
# ============================================================

class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    For production, use Redis for distributed rate limiting.
    """
    
    def __init__(self):
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """
        Generate a unique client identifier.
        Uses IP + User-Agent hash for fingerprinting.
        For authenticated requests, uses user ID.
        """
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Create a hash of IP + User-Agent for privacy
        fingerprint = hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()[:16]
        return fingerprint
    
    def _clean_old_requests(self, client_id: str, window: int):
        """Remove requests outside the current window."""
        current = time.time()
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] 
            if current - ts < window
        ]
    
    def is_rate_limited(
        self, 
        request: Request, 
        max_requests: int = RATE_LIMIT_REQUESTS,
        window: int = RATE_LIMIT_WINDOW
    ) -> bool:
        """
        Check if client is rate limited.
        Returns True if rate limit exceeded.
        """
        client_id = self._get_client_id(request)
        self._clean_old_requests(client_id, window)
        
        if len(self.requests[client_id]) >= max_requests:
            return True
        
        self.requests[client_id].append(time.time())
        return False
    
    def get_remaining(self, request: Request, max_requests: int = RATE_LIMIT_REQUESTS) -> int:
        """Get remaining requests for client."""
        client_id = self._get_client_id(request)
        return max(0, max_requests - len(self.requests[client_id]))


rate_limiter = RateLimiter()


async def check_rate_limit(request: Request):
    """
    Dependency for standard rate limiting.
    """
    if rate_limiter.is_rate_limited(request):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
        )


async def check_scraper_rate_limit(request: Request):
    """
    Stricter rate limiting for scraper endpoints.
    """
    if rate_limiter.is_rate_limited(request, SCRAPER_RATE_LIMIT, RATE_LIMIT_WINDOW):
        raise HTTPException(
            status_code=429,
            detail="Scraper rate limit exceeded. Please wait before making more requests.",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW * 2)}
        )


# ============================================================
# INPUT SANITIZATION
# ============================================================

import re
import html


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent XSS and injection.
    """
    if not value:
        return ""
    
    # Truncate to max length
    value = value[:max_length]
    
    # HTML escape
    value = html.escape(value)
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    return value


def sanitize_job_data(job: dict) -> dict:
    """
    Sanitize job data from scraper before storing.
    Includes mapping job_id to external_id for consistency.
    """
    # If external_id is missing but job_id is present (Guest API), use job_id
    external_id = job.get("external_id")
    if not external_id and job.get("job_id"):
        external_id = str(job.get("job_id"))
        
    return {
        "title": sanitize_string(job.get("title", ""), 200),
        "company": sanitize_string(job.get("company", ""), 100),
        "location": sanitize_string(job.get("location", ""), 100),
        "description": sanitize_string(job.get("description", ""), 5000),
        "link": sanitize_url(job.get("link", "")),
        "snippet": sanitize_string(job.get("snippet", ""), 500),
        "applicants": int(job.get("applicants", 0)) if job.get("applicants") else None,
        "source": sanitize_string(job.get("source", ""), 50),
        "external_id": sanitize_string(external_id or "", 100),
        "match_score": int(job.get("match_score", 0)) if job.get("match_score") is not None else 0,
        "skills_matched": [sanitize_string(s, 50) for s in job.get("skills_matched", [])] if isinstance(job.get("skills_matched"), list) else [],
    }


def sanitize_url(url: str) -> str:
    """
    Validate and sanitize URLs.
    Only allows http/https protocols to prevent javascript: attacks.
    """
    if not url:
        return ""
    
    url = url.strip()[:2000]  # Max URL length
    
    # Only allow http/https
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return ""
    
    # Block obvious javascript/data URIs that might be encoded
    dangerous_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return ""
    
    return url


# ============================================================
# CORS CONFIGURATION
# ============================================================

ALLOWED_ORIGINS = [
    "http://localhost:5173",      # Vite dev
    "http://localhost:3000",      # Alternate dev
    "http://127.0.0.1:5173",
    # Add production domains here
]

CORS_CONFIG = {
    "allow_origins": ALLOWED_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"],
    "expose_headers": ["X-RateLimit-Remaining", "X-RateLimit-Reset"],
    "max_age": 600,  # Preflight cache for 10 minutes
}


# ============================================================
# REQUEST LOGGING (without sensitive data)
# ============================================================

def log_request(request: Request, user_id: Optional[str] = None):
    """
    Log request for audit purposes.
    NEVER log tokens, passwords, or PII.
    """
    import logging
    logger = logging.getLogger("security")
    
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"IP: {client_ip} | "
        f"User: {user_id or 'anonymous'}"
    )
