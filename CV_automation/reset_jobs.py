import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def reset_jobs():
    load_dotenv(find_dotenv())
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    try:
        supabase = await create_async_client(url, key)
        # Reset all failed jobs to pending
        res = await supabase.table("job_descriptions")\
            .update({"status": "pending", "error_log": None})\
            .eq("status", "failed")\
            .execute()
        
        print(f"✅ Reset {len(res.data)} failed jobs to 'pending'")
        
    except Exception as e:
        print(f"❌ Error resetting jobs: {e}")

if __name__ == "__main__":
    asyncio.run(reset_jobs())
