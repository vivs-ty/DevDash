from fastapi import APIRouter, Depends, Request, Form
from ..templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import PullRequest
from ..utils import get_nav_counts

router = APIRouter(tags=["pull_requests"])

STATUS_OPTIONS = ["open", "draft", "in_review", "approved", "merged", "closed"]
PRIORITY_OPTIONS = ["low", "medium", "high", "critical"]


@router.get("/", response_class=HTMLResponse)
def list_prs(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PullRequest)
    if status:
        query = query.filter(PullRequest.status == status)
    if priority:
        query = query.filter(PullRequest.priority == priority)
    items = query.order_by(PullRequest.created_at.desc()).all()
    return templates.TemplateResponse("pull_requests.html", {
        "request": request,
        "items": items,
        "active": "prs",
        "filter_status": status or "",
        "filter_priority": priority or "",
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        **get_nav_counts(db),
    })


@router.post("/", response_class=HTMLResponse)
def create_pr(
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    pr_number: Optional[int] = Form(None),
    branch: str = Form(""),
    status: str = Form("open"),
    priority: str = Form("medium"),
    description: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = PullRequest(
        title=title, repo=repo, pr_number=pr_number, branch=branch,
        status=status, priority=priority, description=description,
        github_url=github_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/pr_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/card", response_class=HTMLResponse)
def pr_card(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(PullRequest).filter(PullRequest.id == item_id).first()
    return templates.TemplateResponse("partials/pr_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_pr_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(PullRequest).filter(PullRequest.id == item_id).first()
    return templates.TemplateResponse("partials/pr_edit.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.put("/{item_id}", response_class=HTMLResponse)
def update_pr(
    item_id: int,
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    pr_number: Optional[int] = Form(None),
    branch: str = Form(""),
    status: str = Form("open"),
    priority: str = Form("medium"),
    description: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = db.query(PullRequest).filter(PullRequest.id == item_id).first()
    if not item:
        return HTMLResponse(status_code=404, content="Not found")
    item.title = title
    item.repo = repo
    item.pr_number = pr_number
    item.branch = branch
    item.status = status
    item.priority = priority
    item.description = description
    item.github_url = github_url
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/pr_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.patch("/{item_id}/status", response_class=HTMLResponse)
def update_pr_status(
    item_id: int,
    request: Request,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    item = db.query(PullRequest).filter(PullRequest.id == item_id).first()
    if item:
        item.status = status
        db.commit()
        db.refresh(item)
    return templates.TemplateResponse("partials/pr_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.delete("/{item_id}", response_class=HTMLResponse)
def delete_pr(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PullRequest).filter(PullRequest.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return HTMLResponse(content="")
