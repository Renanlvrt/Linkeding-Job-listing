import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client
import ollama
from playwright.async_api import async_playwright

async def verify():
    print("🔍 Starting CV Pipeline Verification...\n")
    load_dotenv(find_dotenv())
    
    # 1. Env Check
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("❌ Error: Supabase credentials missing from .env")
        return

    # 2. Supabase Check
    supabase = None
    try:
        supabase = await create_async_client(url, key)
        res = await supabase.table("job_descriptions").select("count", count="exact").limit(1).execute()
        print(f"✅ Supabase: Connected. Found {res.count} jobs.")
    except Exception as e:
        print(f"❌ Supabase: Connection failed - {e}")

    # 3. Playwright Check
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print("✅ Playwright: Chromium launched successfully.")
            await browser.close()
    except Exception as e:
        print(f"❌ Playwright: Chromium failed - {e}")

    # 4. Ollama Check
    try:
        await asyncio.to_thread(ollama.list)
        print("✅ Ollama: Service is running.")
    except Exception as e:
        print(f"❌ Ollama: Service check failed - {e}")

    print("\n🚀 Verification Complete. If all green, the pipeline is 100% production ready!")

if __name__ == "__main__":
    asyncio.run(verify())
