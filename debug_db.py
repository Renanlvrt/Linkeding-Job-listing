
import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") # Use service key to bypass RLS for debugging
    
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not set in .env")
        return

    supabase: Client = create_client(url, key)
    
    # Check jobs table
    response = supabase.table("jobs").select("count", count="exact").execute()
    count = response.count
    print(f"Total jobs in database: {count}")
    
    # Check newest jobs
    response = supabase.table("jobs").select("*").order("scraped_at", desc=True).limit(15).execute()
    jobs = response.data
    
    print("\nLast 15 jobs scraped:")
    for j in jobs:
        print(f"- [{j.get('status')}] {j.get('title')} @ {j.get('company')} (ID: {j.get('id')}, ExtID: {j.get('external_id')}, Score: {j.get('match_score')})")

    # Check for jobs with match_score > 0
    response = supabase.table("jobs").select("count", count="exact").gt("match_score", 0).execute()
    high_score_count = response.count
    print(f"\nJobs with match_score > 0: {high_score_count}")

if __name__ == "__main__":
    asyncio.run(check_db())
