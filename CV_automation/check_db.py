import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def check():
    load_dotenv(find_dotenv())
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    sb = await create_async_client(url, key)
    
    # 1. Check pending jobs
    res = await sb.table("job_descriptions").select("id,company,status").in_("status", ["pending", "retry"]).execute()
    print(f"Pending/Retry Jobs: {res.data}")
    
    # 2. If no pending, find the latest and force to pending
    if not res.data:
        latest = await sb.table("job_descriptions").select("id,company,status").order("created_at", desc=True).limit(1).execute()
        if latest.data:
            job_id = latest.data[0]['id']
            print(f"Forcing Job {job_id} ({latest.data[0]['company']}) to pending...")
            await sb.table("job_descriptions").update({"status": "pending"}).eq("id", job_id).execute()
            print("Done.")

if __name__ == "__main__":
    asyncio.run(check())
