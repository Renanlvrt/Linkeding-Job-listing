import asyncio
import os
import inspect
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client

async def test_storage():
    load_dotenv(find_dotenv())
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase = await create_async_client(url, key)
    storage = supabase.storage.from_('cv-pdfs')
    
    print(f"Testing get_public_url type...")
    res = storage.get_public_url("test.pdf")
    
    if inspect.iscoroutine(res):
        print("ALERT: get_public_url is ASYNC")
    else:
        print("get_public_url is SYNC")
    
    print(f"Result: {res}")
    
    # Also check if it's a coroutine function
    if inspect.iscoroutinefunction(storage.get_public_url):
         print("ALERT: get_public_url IS a coroutine function")

if __name__ == "__main__":
    asyncio.run(test_storage())
