import os
import httpx
from typing import Optional


GITHUB_API = "https://api.github.com"
HEADERS_BASE = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def _auth_headers(token: str) -> dict:
    return {**HEADERS_BASE, "Authorization": f"Bearer {token}"}


async def _paginate_list(client: httpx.AsyncClient, url: str, headers: dict, params: dict) -> list[dict]:
    """Collect all pages from a GitHub list endpoint."""
    results: list[dict] = []
    page = 1
    per_page = 100
    while True:
        r = await client.get(url, headers=headers, params={**params, "per_page": per_page, "page": page})
        r.raise_for_status()
        batch = r.json()
        results.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return results


async def _paginate_search(client: httpx.AsyncClient, url: str, headers: dict, params: dict) -> list[dict]:
    """Collect all pages from a GitHub search endpoint (max 1000 items)."""
    results: list[dict] = []
    page = 1
    per_page = 100
    while True:
        r = await client.get(url, headers=headers, params={**params, "per_page": per_page, "page": page})
        r.raise_for_status()
        data = r.json()
        batch = data.get("items", [])
        results.extend(batch)
        if len(batch) < per_page or len(results) >= data.get("total_count", 0):
            break
        page += 1
    return results


async def fetch_assigned_issues(token: str, username: str) -> list[dict]:
    """Fetch open issues assigned to the user across all repos."""
    url = f"{GITHUB_API}/issues"
    params = {"filter": "assigned", "state": "open"}
    async with httpx.AsyncClient(timeout=20) as client:
        return await _paginate_list(client, url, _auth_headers(token), params)


async def fetch_review_requests(token: str) -> list[dict]:
    """Fetch pull requests where the user has been requested as a reviewer."""
    url = f"{GITHUB_API}/search/issues"
    params = {"q": "is:open is:pr review-requested:@me"}
    async with httpx.AsyncClient(timeout=20) as client:
        return await _paginate_search(client, url, _auth_headers(token), params)


async def fetch_authored_prs(token: str, username: str) -> list[dict]:
    """Fetch open PRs authored by the user."""
    url = f"{GITHUB_API}/search/issues"
    params = {"q": f"is:open is:pr author:{username}"}
    async with httpx.AsyncClient(timeout=20) as client:
        return await _paginate_search(client, url, _auth_headers(token), params)


def repo_name_from_url(html_url: str) -> str:
    """Extract 'owner/repo' from a GitHub HTML URL."""
    parts = html_url.rstrip("/").split("/")
    if len(parts) >= 5:
        return f"{parts[-4]}/{parts[-3]}"
    return ""
