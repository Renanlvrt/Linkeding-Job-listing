"""
Phase 10 Filter Verification
=============================
Tests closed/reposted detection patterns and tiered validation.

Run: python verify_filters.py
"""

import re
import sys
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, ".")

from app.scraper.filters import (
    CLOSED_PATTERNS,
    REPOSTED_PATTERNS,
    parse_applicant_count,
    parse_posted_time,
    build_ddg_exclude_query,
)
from app.scraper.discovery import JobDiscovery


# ================== TEST DATA ==================

# Mock snippets that should be FILTERED OUT
MOCK_CLOSED_SNIPPETS = [
    "Senior Developer at TechCorp - No longer accepting applications",
    "Job posting has expired. Applications are closed.",
    "This job is no longer available. View similar jobs.",
    "Plus d'applications acceptees - candidatures fermees",  # French
    "Ya no acepta solicitudes",  # Spanish
]

MOCK_REPOSTED_SNIPPETS = [
    "Software Engineer - Reposted 5 years ago - 200+ applicants",
    "Reposted 3 weeks ago - Apply now!",
    "Data Analyst - reposte il y a 2 mois",  # French
    "This job was reposted recently",
]

# Mock snippets that should PASS (good jobs)
MOCK_GOOD_SNIPPETS = [
    "Software Engineer at StartupXYZ - Posted 2 days ago - 15 applicants",
    "Junior Developer - Remote - Posted this week - Be an early applicant",
    "Machine Learning Engineer - Posted 1 day ago - 45 applicants",
    "Full Stack Developer - London - 3 days ago",
]


def test_closed_patterns():
    """Test that closed patterns detect closed jobs."""
    print("\n[CLOSED] Testing CLOSED_PATTERNS...")
    results = []
    
    for snippet in MOCK_CLOSED_SNIPPETS:
        matched = False
        for pattern in CLOSED_PATTERNS:
            if re.search(pattern, snippet.lower(), re.IGNORECASE):
                matched = True
                break
        
        status = "[PASS] BLOCKED" if matched else "[FAIL] MISSED"
        results.append(matched)
        print(f"  {status}: {snippet[:60]}...")
    
    success = all(results)
    print(f"\n  Result: {sum(results)}/{len(results)} closed jobs detected")
    return success


def test_reposted_patterns():
    """Test that reposted patterns detect reposted jobs."""
    print("\n[REPOSTED] Testing REPOSTED_PATTERNS...")
    results = []
    
    for snippet in MOCK_REPOSTED_SNIPPETS:
        matched = False
        for pattern in REPOSTED_PATTERNS:
            if re.search(pattern, snippet.lower(), re.IGNORECASE):
                matched = True
                break
        
        status = "[PASS] BLOCKED" if matched else "[FAIL] MISSED"
        results.append(matched)
        print(f"  {status}: {snippet[:60]}...")
    
    success = all(results)
    print(f"\n  Result: {sum(results)}/{len(results)} reposted jobs detected")
    return success


def test_good_snippets_pass():
    """Test that good snippets are NOT filtered."""
    print("\n[GOOD] Testing GOOD_SNIPPETS (should pass)...")
    results = []
    
    for snippet in MOCK_GOOD_SNIPPETS:
        is_closed = any(
            re.search(p, snippet.lower(), re.I) for p in CLOSED_PATTERNS
        )
        is_reposted = any(
            re.search(p, snippet.lower(), re.I) for p in REPOSTED_PATTERNS
        )
        
        passed = not is_closed and not is_reposted
        status = "[PASS] PASSED" if passed else "[FAIL] WRONGLY BLOCKED"
        results.append(passed)
        print(f"  {status}: {snippet[:60]}...")
    
    success = all(results)
    print(f"\n  Result: {sum(results)}/{len(results)} good jobs passed")
    return success


def test_applicant_parsing():
    """Test applicant count parsing."""
    print("\n[APPLICANTS] Testing applicant parsing...")
    
    test_cases = [
        ("45 applicants have applied", 45),
        ("Over 100 applicants", 101),
        ("200+ applicants", 201),
        ("1,234 applicants", 1234),
        ("Be an early applicant", 0),
        ("50 candidats ont postule", 50),  # French
    ]
    
    results = []
    for text, expected in test_cases:
        actual = parse_applicant_count(text)
        passed = actual == expected
        status = "[PASS]" if passed else "[FAIL]"
        results.append(passed)
        print(f"  {status}: '{text[:40]}' -> {actual} (expected: {expected})")
    
    success = all(results)
    print(f"\n  Result: {sum(results)}/{len(results)} tests passed")
    return success


def test_posted_time_parsing():
    """Test posted time parsing."""
    print("\n[TIME] Testing posted time parsing...")
    
    test_cases = [
        ("Posted 1 hour ago", 1),
        ("Posted 2 days ago", 48),
        ("1 week ago", 168),
        ("3 weeks ago", 504),
        ("1 month ago", 720),
    ]
    
    results = []
    for text, expected in test_cases:
        actual = parse_posted_time(text)
        passed = actual == expected
        status = "[PASS]" if passed else "[FAIL]"
        results.append(passed)
        print(f"  {status}: '{text}' -> {actual}h (expected: {expected}h)")
    
    success = all(results)
    print(f"\n  Result: {sum(results)}/{len(results)} tests passed")
    return success


def test_ddg_query_builder():
    """Test DDG exclude query builder."""
    print("\n[DDG] Testing DDG query builder...")
    
    query = build_ddg_exclude_query("software engineer", "London")
    
    # Should contain exclusions
    has_exclusions = (
        '-"no longer accepting"' in query
        and '-"reposted"' in query
        and 'site:linkedin.com/jobs' in query
    )
    
    status = "[PASS]" if has_exclusions else "[FAIL]"
    print(f"  {status}: Query = {query[:80]}...")
    print(f"  Contains exclusions: {has_exclusions}")
    
    return has_exclusions


def test_discovery_snippet_filter():
    """Test the JobDiscovery snippet filter method."""
    print("\n[DISCOVERY] Testing JobDiscovery._filter_by_snippet()...")
    
    discovery = JobDiscovery()
    
    test_cases = [
        # (snippet, should_pass, expected_reason_contains)
        ("Software Engineer - 20 applicants - Posted today", True, "passed"),
        ("No longer accepting applications", False, "closed"),
        ("Reposted 5 years ago", False, "reposted"),
        ("Plus d'applications acceptees", False, "closed"),
    ]
    
    results = []
    for snippet, should_pass, expected_reason in test_cases:
        passes, reason = discovery._filter_by_snippet(snippet)
        correct = (passes == should_pass) and (expected_reason in reason)
        status = "[PASS]" if correct else "[FAIL]"
        results.append(correct)
        print(f"  {status}: '{snippet[:40]}...' -> passes={passes}, reason={reason}")
    
    success = all(results)
    print(f"\n  Result: {sum(results)}/{len(results)} tests passed")
    return success


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("PHASE 10: CLOSED/REPOSTED FILTER VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Closed Patterns", test_closed_patterns),
        ("Reposted Patterns", test_reposted_patterns),
        ("Good Snippets Pass", test_good_snippets_pass),
        ("Applicant Parsing", test_applicant_parsing),
        ("Posted Time Parsing", test_posted_time_parsing),
        ("DDG Query Builder", test_ddg_query_builder),
        ("Discovery Snippet Filter", test_discovery_snippet_filter),
    ]
    
    results = {}
    for name, test_fn in tests:
        try:
            results[name] = test_fn()
        except Exception as e:
            print(f"  [ERROR]: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status}: {name}")
    
    print(f"\n{'ALL TESTS PASSED!' if passed == total else f'{total - passed} TESTS FAILED'}")
    print(f"Result: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

