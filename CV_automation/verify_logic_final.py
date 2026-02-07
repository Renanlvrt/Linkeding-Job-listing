import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def verify():
    load_dotenv(find_dotenv())
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    sb = await create_async_client(url, key)
    
    # Check the latest finished job
    res = await sb.table("job_descriptions")\
        .select("id,company,status,keywords_found,missing_keywords")\
        .order("updated_at", desc=True)\
        .limit(1)\
        .execute()
    
    if res.data:
        job = res.data[0]
        print(f"--- Job Verification: {job['id']} ---")
        print(f"Company: {job['company']}")
        print(f"Status:  {job['status']}")
        print(f"Found:   {job['keywords_found']}")
        print(f"Missing: {job['missing_keywords']}")
    else:
        print("No jobs found.")

if __name__ == "__main__":
    asyncio.run(verify())
