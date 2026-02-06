import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def insert_test():
    load_dotenv(find_dotenv())
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    print("🚀 Inserting test job into Supabase...")
    
    test_job = {
        "company": "Antigravity AI (Test)",
        "description": """We are looking for a Python Developer who loves automation. 
        Skills required: Python, Asyncio, Supabase, and a passion for building agentic tools. 
        Seniority: Mid-Level.""",
        "status": "pending"
    }

    try:
        supabase = await create_async_client(url, key)
        res = await supabase.table("job_descriptions").insert(test_job).execute()
        job_id = res.data[0]['id']
        print(f"✅ Success! Job inserted with ID: {job_id}")
        print("\n👇 Now, start your worker in a new terminal to see it process:")
        print("python cv_worker.py")
    except Exception as e:
        print(f"❌ Failed to insert job: {e}")

if __name__ == "__main__":
    asyncio.run(insert_test())
