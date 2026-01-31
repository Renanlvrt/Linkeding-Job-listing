"""
Quick test script to debug DuckDuckGo search.
Run with: python test_ddg.py
"""

from ddgs import DDGS

def test_search():
    print("Testing DDGS (new package) search...")
    
    # Test 1: Basic search
    print("\n1. Basic search for 'Python developer jobs':")
    try:
        results = DDGS().text("Python developer jobs", max_results=5)
        print(f"   Found {len(results)} results")
        for r in results[:3]:
            print(f"   - {r.get('title', 'No title')[:60]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: LinkedIn-specific search
    print("\n2. LinkedIn job search:")
    try:
        results = DDGS().text("site:linkedin.com/jobs Software Engineer", max_results=5)
        print(f"   Found {len(results)} results")
        for r in results[:3]:
            print(f"   - {r.get('href', 'No URL')[:80]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: General job search
    print("\n3. General job search:")
    try:
        results = DDGS().text("software engineer remote job 2024", max_results=5)
        print(f"   Found {len(results)} results")
        for r in results[:3]:
            print(f"   - {r.get('title', 'No title')[:60]}")
    except Exception as e:
        print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_search()
