#!/usr/bin/env python3
"""
Project & Token Monitor Dashboard - Data Collector
Scans .md files, calculates tokens, fetches GitHub data, outputs JSON
"""

import os
import json
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORKSPACE_PATH = r"C:\Users\sean\.openclaw\workspace"
OUTPUT_JSON_PATH = r"C:\Users\sean\.openclaw\workspace\project-token-monitor\data\dashboard-data.json"
TOKEN_WARNING_THRESHOLD = 5000  # Tokens

# GitHub Configuration (if needed)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = "openclawsean024-create"
REPO_NAME = "project-token-monitor"

def calculate_token_count(content: str) -> int:
    """
    Calculate token count based on MiniMax Chinese/English ratio
    - Chinese: 1 char ≈ 1 token
    - English: 1 char ≈ 0.3 token
    """
    chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
    english_chars = sum(1 for c in content if c.isascii() and c.isalpha())
    other_chars = len(content) - chinese_chars - english_chars
    
    return chinese_chars + int(english_chars * 0.3) + other_chars

def scan_markdown_files(root_path: str) -> list:
    """Scan all .md files and calculate their token counts"""
    md_files = []
    
    for root, dirs, files in os.walk(root_path):
        # Skip node_modules and .git
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.next', 'dist']]
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    size_bytes = os.path.getsize(file_path)
                    size_kb = round(size_bytes / 1024, 2)
                    tokens = calculate_token_count(content)
                    
                    status = "normal"
                    if tokens > TOKEN_WARNING_THRESHOLD:
                        status = "warning"
                    if tokens > TOKEN_WARNING_THRESHOLD * 2:
                        status = "critical"
                    
                    md_files.append({
                        "path": rel_path,
                        "size_kb": size_kb,
                        "est_tokens": tokens,
                        "status": status,
                        "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    # Sort by token count descending
    md_files.sort(key=lambda x: x["est_tokens"], reverse=True)
    return md_files

def get_github_status() -> dict:
    """Fetch GitHub repository status"""
    # Use GitHub CLI if available, otherwise return mock data
    try:
        result = subprocess.run(
            ["gh", "repo", "view", f"{REPO_OWNER}/{REPO_NAME}", "--json", "defaultBranchRef,issues, pullRequests"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "branch": data.get("defaultBranchRef", {}).get("name", "main"),
                "open_issues": len([i for i in data.get("issues", {}) if i.get("state") == "OPEN"]),
                "pending_prs": len([p for p in data.get("pullRequests", {}) if p.get("state") == "OPEN"])
            }
    except Exception as e:
        print(f"GitHub CLI not available: {e}")
    
    # Return default/mock data if GitHub CLI not available
    return {
        "branch": "main",
        "open_issues": 0,
        "pending_prs": 0,
        "recent_commits": []
    }

def get_recent_commits(limit: int = 3) -> list:
    """Get recent commits"""
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/{REPO_OWNER}/{REPO_NAME}/commits", "-f", f"per_page={limit}", "--jq", ".[].{message: .commit.message, author: .commit.author.name, date: .commit.author.date}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"GitHub API error: {e}")
    
    return []

def get_token_metrics() -> dict:
    """
    Generate token metrics - in production, this would read from actual logs
    For now, generate realistic mock data based on past usage patterns
    """
    today = datetime.now()
    daily_usage = []
    
    # Generate last 5 days of data
    for i in range(4, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%m-%d")
        
        # Simulate realistic usage patterns
        abab65s = 10000 + (i * 1000) + (hash(date_str) % 5000)
        abab7 = 4000 + (i * 500) + (hash(date_str + "v") % 2000)
        
        daily_usage.append({
            "date": date_str,
            "abab6_5s": abab65s,
            "abab7": abab7
        })
    
    # Calculate averages
    total_tokens = sum(d["abab6_5s"] + d["abab7"] for d in daily_usage)
    avg_daily = total_tokens / 5
    
    return {
        "session_avg": 4500,
        "cron_avg": 1200,
        "daily_usage": daily_usage,
        "monthly_projection": int(avg_daily * 30),
        "monthly_cost_usd": round((avg_daily * 30) * 0.0001, 2)  # Approximate cost
    }

def get_project_list() -> list:
    """Get list of all projects in workspace"""
    projects = []
    workspace = Path(WORKSPACE_PATH)
    
    for item in workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name not in ['memory', 'skills']:
            # Check if it's a git repo
            is_git = (item / '.git').exists()
            
            # Count .md files
            md_count = len(list(item.rglob("*.md")))
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file() and 'node_modules' not in str(f))
            
            projects.append({
                "name": item.name,
                "path": str(item.relative_to(workspace)),
                "is_git_repo": is_git,
                "md_files": md_count,
                "size_kb": round(total_size / 1024, 2)
            })
    
    projects.sort(key=lambda x: x["size_kb"], reverse=True)
    return projects

def main():
    """Main data collection function"""
    print("Starting data collection...")
    
    # Collect all data
    data = {
        "last_updated": datetime.now().isoformat(),
        "github_status": get_github_status(),
        "recent_commits": get_recent_commits(),
        "token_metrics": get_token_metrics(),
        "file_explorer": scan_markdown_files(WORKSPACE_PATH),
        "projects": get_project_list()
    }
    
    # Write to JSON file
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Data collected and saved to {OUTPUT_JSON_PATH}")
    print(f"- Projects: {len(data['projects'])}")
    print(f"- MD Files: {len(data['file_explorer'])}")
    print(f"- Total Tokens: {sum(f['est_tokens'] for f in data['file_explorer'])}")

if __name__ == "__main__":
    main()
