import json
import re

with open("debug_job_full.json", "r", encoding="utf-8") as f:
    job = json.load(f)

cv = job["tailored_cv"]

print("--- DIAGNOSTIC: ATS FORMATTING ---")
prohibited = [
    ("pipe", r"\|"),
    ("image", r"!\[\]"),
    ("table", r"<table"),
    ("col", r"\{col\}")
]

for name, pattern in prohibited:
    matches = re.findall(pattern, cv)
    if matches:
        print(f"FOUND: {name} (Count: {len(matches)})")
    else:
        print(f"NOT FOUND: {name}")

print("\n--- DIAGNOSTIC: KEYWORDS ---")
# Since we don't have jd_extraction keywords here, let's look at the JD text
jd = job["description"]
potential_kws = ["python", "asyncio", "supabase", "agentic"]
for kw in potential_kws:
    found = kw.lower() in cv.lower()
    print(f"Keyword '{kw}': {'FOUND' if found else 'MISSING'}")

print("\n--- CV PREVIEW (RAW) ---")
print(repr(cv[:500]))
