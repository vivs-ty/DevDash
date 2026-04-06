import os
import httpx
from typing import Optional


GITHUB_API = "https://api.github.com"
HEADERS_BASE = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def _auth_headers(token: str) -> dict:
    return {**HEADERS_BASE, "Authorization": f"Bearer {token}"}


async def fetch_assigned_issues(token: str, username: str) -> list[dict]:
    """Fetch open issues assigned to the user across all repos."""
    url = f"{GITHUB_API}/issues"
    params = {"filter": "assigned", "state": "open", "per_page": 50}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers=_auth_headers(token), params=params)
        r.raise_for_status()
    return r.json()


async def fetch_review_requests(token: str) -> list[dict]:
    """Fetch pull requests where the user has been requested as a reviewer."""
    url = f"{GITHUB_API}/search/issues"
    params = {"q": "is:open is:pr review-requested:@me", "per_page": 50}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers=_auth_headers(token), params=params)
        r.raise_for_status()
    return r.json().get("items", [])


async def fetch_authored_prs(token: str, username: str) -> list[dict]:
    """Fetch open PRs authored by the user."""
    url = f"{GITHUB_API}/search/issues"
    params = {"q": f"is:open is:pr author:{username}", "per_page": 50}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers=_auth_headers(token), params=params)
        r.raise_for_status()
    return r.json().get("items", [])


def repo_name_from_url(html_url: str) -> str:
    """Extract 'owner/repo' from a GitHub HTML URL."""
    parts = html_url.rstrip("/").split("/")
    if len(parts) >= 5:
        return f"{parts[-4]}/{parts[-3]}"
    return ""
