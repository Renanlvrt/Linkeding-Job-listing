
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.scraper.orchestrator import orchestrator
from app.config import settings

async def debug_scrape():
    print("--- Debug Scrape Start ---")
    print(f"Playwright Available: {orchestrator.use_rapidapi}")
    print(f"Gemini API Key: {'Set' if settings.gemini_api_key else 'Not Set'}")
    
    try:
        def on_progress(p, msg):
            print(f"[{p}%] {msg}")

        # Run a small scrape
        result = await orchestrator.run_scrape(
            keywords="Python Developer",
            location="Remote",
            max_jobs=2,
            posted_within_days=7,
            max_applicants=250, # Relaxed for popular "Python" search
            on_progress=on_progress
        )
        print("\n✅ Scrape completed successfully!")
        print(f"Jobs found: {len(result.get('jobs', []))}")
        
        if "filter_stats" in result:
            print(f"Discovery Stats: {result['filter_stats']}")
        if "html_validation_stats" in result:
            print(f"HTML Validation Stats: {result['html_validation_stats']}")
        
        if not result.get("jobs"):
            print("\n🔍 No jobs passed the filters. This usually happens if:")
            print("1. The jobs are older than the 'posted_within_days' limit.")
            print("2. The jobs have more than 100 applicants (default limit).")
            print("3. The job postings are actually closed/expired.")
        
        # Test sanitization
        from app.middleware.security import sanitize_job_data
        if result.get("jobs"):
            print("\nTesting sanitization on first job...")
            sanitized = sanitize_job_data(result["jobs"][0])
            print(f"✅ Sanitization passed. Title: {sanitized['title']}")
            
    except Exception as e:
        print("\n❌ SCRAPE FAILED!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_scrape())
