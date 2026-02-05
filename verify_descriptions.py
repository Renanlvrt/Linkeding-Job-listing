import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.scraper.discovery import job_discovery

async def test_enrichment():
    logging.basicConfig(level=logging.INFO)
    
    keywords = "Software Engineer"
    location = "United States"
    
    print(f"🔍 Testing job discovery and enrichment for: {keywords} in {location}")
    
    result = await job_discovery.search_linkedin_jobs(
        keywords=keywords,
        location=location,
        max_results=3,
        posted_within_days=1
    )
    
    jobs = result.get("jobs", [])
    print(f"\n✅ Found {len(jobs)} jobs via {result.get('search_method')}")
    
    for i, job in enumerate(jobs):
        title = job.get("title")
        company = job.get("company")
        desc = job.get("description", "")
        
        print(f"\n--- Job {i+1}: {title} at {company} ---")
        if desc:
            print(f"Description length: {len(desc)} characters")
            print(f"Preview: {desc[:200]}...")
            if len(desc) > 500:
                print("✅ Description looks complete!")
            else:
                print("⚠️ Description seems short, verify if it's just a snippet.")
        else:
            print("❌ NO DESCRIPTION FOUND")

if __name__ == "__main__":
    asyncio.run(test_enrichment())
