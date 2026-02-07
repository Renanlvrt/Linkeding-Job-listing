import asyncio
import os
import json
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client
from secure_cv_loader import SecureCVLoader

async def check():
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
    
    print(f"--- Checking Supabase Table: job_descriptions ---")
    
    try:
        supabase = await create_async_client(url, key)
        res = await supabase.table("job_descriptions").select("*").execute()
        
        jobs = res.data
        print(f"Total Jobs Found: {len(jobs)}")
        
        loader = SecureCVLoader("c:/Users/renan/Desktop/Side_projects/Ai agent/cold email agent/CV_automation/master_CV.md")
        master_cv = loader.load_and_sanitize()
        print(f"Master CV Length: {len(master_cv)} chars")

        for job in jobs:
            print(f"\n- ID: {job['id']}")
            print(f"  Company: {job.get('company')}")
            print(f"  Status: {job.get('status')}")
            print(f"  ATS Score: {job.get('ats_score')}")
            print(f"  Error Log: {job.get('error_log')}")
            print(f"  Metrics (RAW): {job.get('keyword_match_json')}")
            tailored = job.get('tailored_cv') or ""
            print(f"  Tailored CV Length: {len(tailored)} chars")
            if tailored:
                print(f"  Tailored CV Preview (first 500): \n{tailored[:500]}...")
            print(f"  Created At: {job.get('created_at')}")
            
    except Exception as e:
        print(f"❌ Error query database: {e}")

if __name__ == "__main__":
    asyncio.run(check())
