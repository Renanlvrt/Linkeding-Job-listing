import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def reset_jobs():
    # Force loading from root
    root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    load_dotenv(root_env)
    
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        load_dotenv(find_dotenv())
        url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Error: Supabase URL or Key missing.")
        return

    try:
        supabase = await create_async_client(url, key)
        # Reset all jobs by using a filter that always matches (neq null)
        # Supabase requires a filter for updates to prevent accidental wipes.
        res = await supabase.table("job_descriptions")\
            .update({"status": "pending", "error_log": None, "tailored_cv": None})\
            .neq("id", "00000000-0000-0000-0000-000000000000")\
            .execute()
        
        print(f"✅ Reset {len(res.data)} jobs to 'pending'")
        
    except Exception as e:
        print(f"❌ Error resetting jobs: {e}")

if __name__ == "__main__":
    asyncio.run(reset_jobs())
