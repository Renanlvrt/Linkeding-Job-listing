import asyncio
import os
import time
import random
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

async def push_test_jobs(count: int = 50):
    """
    Simulates a heavy load of 50 concurrent Job Descriptions for the worker.
    """
    supabase: Client = create_client(
        os.getenv("VITE_SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    
    test_jds = [
        "Software Engineer with Python and AI experience. Senior role.",
        "Junior developer for web apps. React and SQL.",
        "Machine Learning Researcher. BCI and Neural interfaces.",
        "Robotics Engineer. ROS2 and Gazebo specialist.",
        "Data Analyst. SQL and visualization expert."
    ]
    
    print(f"Pushing {count} test jobs to Supabase...")
    
    data = []
    for i in range(count):
        data.append({
            "description": random.choice(test_jds) + f" (Load Test Job #{i})",
            "company": f"TestCorp_{i}",
            "status": "pending",
            "created_by": "00000000-0000-0000-0000-000000000000" # Use a dummy or real ID
        })
    
    res = supabase.table("job_descriptions").insert(data).execute()
    print(f"Successfully pushed {len(res.data)} jobs.")

if __name__ == "__main__":
    asyncio.run(push_test_jobs(50))
