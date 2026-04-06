import os
from fastapi import APIRouter, Depends, Request, Form
from ..templates_config import templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ..database import get_db
from ..models import CodeReview, Issue, PullRequest
from ..utils import get_nav_counts
from ..services.github_service import (
    fetch_assigned_issues,
    fetch_review_requests,
    fetch_authored_prs,
    repo_name_from_url,
)

load_dotenv()

router = APIRouter(tags=["sync"])


@router.get("/", response_class=HTMLResponse)
def sync_page(request: Request, db: Session = Depends(get_db)):
    token    = os.getenv("GITHUB_TOKEN", "")
    username = os.getenv("GITHUB_USERNAME", "")
    return templates.TemplateResponse("sync.html", {
        "request": request,
        "active": "sync",
        "token_set": bool(token),
        "username": username,
        "message": None,
        **get_nav_counts(db),
    })


@router.post("/github", response_class=HTMLResponse)
async def do_github_sync(
    request: Request,
    username: str = Form(""),
    db: Session = Depends(get_db),
):
    gh_token    = os.getenv("GITHUB_TOKEN", "")
    gh_username = username or os.getenv("GITHUB_USERNAME", "")

    if not gh_token:
        return templates.TemplateResponse("sync.html", {
            "request": request,
            "active": "sync",
            "token_set": False,
            "username": gh_username,
            "message": "error: No GitHub token provided.",
            **get_nav_counts(db),
        })

    added_reviews = added_issues = added_prs = 0

    try:
        # Review requests → CodeReview
        review_items = await fetch_review_requests(gh_token)
        existing_review_urls = set(db.scalars(select(CodeReview.github_url)).all())
        for item in review_items:
            if item.get("html_url") not in existing_review_urls:
                repo = repo_name_from_url(item.get("html_url", ""))
                db.add(CodeReview(
                    title=item.get("title", ""),
                    repo=repo,
                    pr_number=item.get("number"),
                    author=item.get("user", {}).get("login", ""),
                    status="pending",
                    priority="medium",
                    github_url=item.get("html_url", ""),
                ))
                added_reviews += 1

        # Assigned issues → Issue
        issue_items = await fetch_assigned_issues(gh_token, gh_username)
        existing_issue_urls = set(db.scalars(select(Issue.github_url)).all())
        for item in issue_items:
            if item.get("html_url") not in existing_issue_urls and "pull_request" not in item:
                repo = repo_name_from_url(item.get("html_url", ""))
                labels = ", ".join(l["name"] for l in item.get("labels", []))
                db.add(Issue(
                    title=item.get("title", ""),
                    repo=repo,
                    issue_number=item.get("number"),
                    labels=labels,
                    status="open",
                    priority="medium",
                    github_url=item.get("html_url", ""),
                ))
                added_issues += 1

        # Authored open PRs → PullRequest
        pr_items = await fetch_authored_prs(gh_token, gh_username)
        existing_pr_urls = set(db.scalars(select(PullRequest.github_url)).all())
        for item in pr_items:
            if item.get("html_url") not in existing_pr_urls:
                repo = repo_name_from_url(item.get("html_url", ""))
                db.add(PullRequest(
                    title=item.get("title", ""),
                    repo=repo,
                    pr_number=item.get("number"),
                    status="open",
                    priority="medium",
                    github_url=item.get("html_url", ""),
                ))
                added_prs += 1

        db.commit()
        message = f"ok: Synced {added_reviews} review(s), {added_issues} issue(s), {added_prs} PR(s)."
    except Exception as exc:
        db.rollback()
        message = f"error: GitHub sync failed — {exc}"

    return templates.TemplateResponse("sync.html", {
        "request": request,
        "active": "sync",
        "token_set": bool(gh_token),
        "username": gh_username,
        "message": message,
        **get_nav_counts(db),
    })
