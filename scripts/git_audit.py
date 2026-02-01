#!/usr/bin/env python3
"""
Git Security Audit Script
============================
Scans git history for accidentally committed secrets.

Usage: python git_audit.py [path_to_repo]
"""

import subprocess
import sys
import re
from pathlib import Path


# Patterns that indicate secrets
SECRET_PATTERNS = [
    (r'SUPABASE_SERVICE_KEY\s*=\s*["\']?[a-zA-Z0-9_\-]{50,}', 'Supabase Service Key'),
    (r'GEMINI_API_KEY\s*=\s*["\']?[a-zA-Z0-9_\-]{30,}', 'Gemini API Key'),
    (r'RAPIDAPI_KEY\s*=\s*["\']?[a-zA-Z0-9_\-]{30,}', 'RapidAPI Key'),
    (r'supabase_service_key\s*=\s*["\']?[a-zA-Z0-9_\-]{50,}', 'Supabase Service Key'),
    (r'service_role\s*["\']?\s*:\s*["\']?[a-zA-Z0-9_\-]{50,}', 'Service Role Key'),
    (r'sk_live_[a-zA-Z0-9]{30,}', 'Stripe Live Key'),
    (r'aws_secret.*=.*[a-zA-Z0-9/+]{40}', 'AWS Secret'),
    (r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----', 'Private Key'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Token'),
    (r'xox[baprs]-[a-zA-Z0-9\-]+', 'Slack Token'),
]

# Files to always scan
SENSITIVE_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    'credentials.json',
    'token.json',
]


def run_git_command(cmd: list, cwd: str) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout or ""


def check_current_files(repo_path: str) -> list:
    """Check current files for secrets."""
    findings = []
    
    for pattern, name in SECRET_PATTERNS:
        regex = re.compile(pattern, re.IGNORECASE)
        
        for file_path in Path(repo_path).rglob('*'):
            if file_path.is_file() and '.git' not in str(file_path):
                try:
                    content = file_path.read_text(errors='ignore')
                    if regex.search(content):
                        findings.append({
                            'type': 'current',
                            'file': str(file_path),
                            'secret_type': name,
                        })
                except Exception:
                    pass
    
    return findings


def check_git_history(repo_path: str) -> list:
    """Check git history for committed secrets."""
    findings = []
    
    # Get all commits
    log_output = run_git_command(
        ['git', 'log', '--all', '--pretty=format:%H', '-n', '100'],
        repo_path
    )
    
    if not log_output:
        return findings
    
    commits = log_output.strip().split('\n')
    
    for commit in commits:
        if not commit:
            continue
            
        # Get diff for this commit
        diff_output = run_git_command(
            ['git', 'show', '--no-patch', '--format=%s', commit],
            repo_path
        )
        
        for file_name in SENSITIVE_FILES:
            show_output = run_git_command(
                ['git', 'show', f'{commit}:{file_name}'],
                repo_path
            )
            
            if show_output:
                for pattern, name in SECRET_PATTERNS:
                    if re.search(pattern, show_output, re.IGNORECASE):
                        findings.append({
                            'type': 'history',
                            'commit': commit[:8],
                            'file': file_name,
                            'secret_type': name,
                            'message': diff_output.strip(),
                        })
    
    return findings


def check_gitignore(repo_path: str) -> list:
    """Verify .gitignore includes sensitive files."""
    issues = []
    
    gitignore_path = Path(repo_path) / '.gitignore'
    
    if not gitignore_path.exists():
        issues.append("No .gitignore file found!")
        return issues
    
    content = gitignore_path.read_text()
    
    required_patterns = [
        '.env',
        '.env.local',
        '.env.production',
        'credentials.json',
        'token.json',
        'node_modules',
        '__pycache__',
    ]
    
    for pattern in required_patterns:
        if pattern not in content:
            issues.append(f"Missing from .gitignore: {pattern}")
    
    return issues


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print("=" * 60)
    print("🔒 GIT SECURITY AUDIT")
    print("=" * 60)
    print(f"\nScanning: {Path(repo_path).absolute()}\n")
    
    # Check .gitignore
    print("📋 Checking .gitignore...")
    gitignore_issues = check_gitignore(repo_path)
    if gitignore_issues:
        print("  ⚠️  Issues found:")
        for issue in gitignore_issues:
            print(f"     - {issue}")
    else:
        print("  ✅ .gitignore looks good")
    
    # Check current files
    print("\n📁 Scanning current files...")
    current_findings = check_current_files(repo_path)
    if current_findings:
        print("  🚨 SECRETS FOUND IN CURRENT FILES:")
        for finding in current_findings:
            print(f"     - {finding['secret_type']} in {finding['file']}")
    else:
        print("  ✅ No secrets in current tracked files")
    
    # Check git history
    print("\n📜 Scanning git history (last 100 commits)...")
    history_findings = check_git_history(repo_path)
    if history_findings:
        print("  🚨 SECRETS FOUND IN GIT HISTORY:")
        for finding in history_findings:
            print(f"     - {finding['secret_type']} in {finding['file']}")
            print(f"       Commit: {finding['commit']} - {finding.get('message', '')[:50]}")
        print("\n  ⚠️  TO FIX: You need to rewrite git history!")
        print("     See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository")
    else:
        print("  ✅ No secrets found in recent history")
    
    # Summary
    total_issues = len(gitignore_issues) + len(current_findings) + len(history_findings)
    
    print("\n" + "=" * 60)
    if total_issues > 0:
        print(f"❌ AUDIT FAILED: {total_issues} issue(s) found")
        sys.exit(1)
    else:
        print("✅ AUDIT PASSED: No secrets detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
