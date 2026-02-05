import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_single_job():
    # Use a recent job ID - let's try a common pattern or a real one if we have it
    # I'll use a placeholder or try to find one from previous logs if any
    job_id = "4155122154" 
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobListing/{job_id}"
    
    print(f"📡 Fetching from: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }
    
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            desc_elem = soup.select_one("div.show-more-less-html__markup, .description__text, .job-view-main-content")
            
            if desc_elem:
                desc = desc_elem.get_text(separator="\n").strip()
                print(f"✅ Found description! Length: {len(desc)}")
                print(f"Preview: {desc[:200]}...")
            else:
                print("❌ Description element not found")
                # Print available classes for debugging
                all_divs = soup.find_all("div", limit=10)
                print(f"First few divs: {[d.get('class') for d in all_divs]}")
        else:
            print(f"❌ Failed fetch: {response.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_single_job())
