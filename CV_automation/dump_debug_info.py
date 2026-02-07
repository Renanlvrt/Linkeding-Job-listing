import asyncio
import os
import json
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def dump():
    load_dotenv(find_dotenv())
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    supabase = await create_async_client(url, key)
    
    res = await supabase.table("job_descriptions").select("*").eq("id", "75d1f618-3c52-47c8-9a09-877c21e91f29").execute()
    if res.data:
        job = res.data[0]
        with open("debug_job_full.json", "w", encoding="utf-8") as f:
            json.dump(job, f, indent=2)
        print("Success: Full job data dumped to debug_job_full.json")
    else:
        print("Error: Job not found.")

if __name__ == "__main__":
    asyncio.run(dump())
