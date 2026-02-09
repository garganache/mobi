#!/usr/bin/env python3
"""Print latest GitHub Actions run status for this repo (or a given repo).

Usage:
  GITHUB_TOKEN=... ./scripts/check_actions_status.py [owner/repo]

- If owner/repo is omitted, defaults to garganache/mobi.
- Prints: status, conclusion, event, branch, run id, and URL.
"""

import os
import sys
import json
import urllib.request
import urllib.error

API_URL = "https://api.github.com"
DEFAULT_REPO = "garganache/mobi"


def get_repo_from_args() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    return DEFAULT_REPO


def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN env var is required")
    return token


def fetch_latest_run(repo: str, token: str) -> dict:
    url = f"{API_URL}/repos/{repo}/actions/runs?branch=main&per_page=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def main() -> None:
    repo = get_repo_from_args()
    token = get_github_token()

    try:
        payload = fetch_latest_run(repo, token)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP error {e.code} from GitHub API: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error talking to GitHub API: {e}", file=sys.stderr)
        sys.exit(1)

    runs = payload.get("workflow_runs") or []
    if not runs:
        print(f"No workflow runs found for {repo} on branch main")
        return

    run = runs[0]
    status = run.get("status")
    conclusion = run.get("conclusion")
    html_url = run.get("html_url")
    event = run.get("event")
    branch = run.get("head_branch")
    run_id = run.get("id")

    print(f"Repo:       {repo}")
    print(f"Run ID:     {run_id}")
    print(f"Event:      {event}")
    print(f"Branch:     {branch}")
    print(f"Status:     {status}")
    print(f"Conclusion: {conclusion}")
    print(f"URL:        {html_url}")


if __name__ == "__main__":
    main()
