from fastapi import APIRouter, Depends, Request, Form, HTTPException
from ..templates_config import templates
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import csv
import io

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
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    page = max(1, page)
    limit = max(1, min(limit, 200))
    query = db.query(PullRequest)
    if status:
        query = query.filter(PullRequest.status == status)
    if priority:
        query = query.filter(PullRequest.priority == priority)
    if date_from:
        try:
            query = query.filter(PullRequest.created_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(PullRequest.created_at <= datetime.fromisoformat(date_to + "T23:59:59"))
        except ValueError:
            pass
    total = query.count()
    items = query.order_by(PullRequest.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return templates.TemplateResponse("pull_requests.html", {
        "request": request,
        "items": items,
        "active": "prs",
        "filter_status": status or "",
        "filter_priority": priority or "",
        "filter_date_from": date_from or "",
        "filter_date_to": date_to or "",
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "page": page,
        "limit": limit,
        "total": total,
        **get_nav_counts(db),
    })


@router.get("/export.csv")
def export_prs_csv(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PullRequest)
    if status:
        query = query.filter(PullRequest.status == status)
    if priority:
        query = query.filter(PullRequest.priority == priority)
    if date_from:
        try:
            query = query.filter(PullRequest.created_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(PullRequest.created_at <= datetime.fromisoformat(date_to + "T23:59:59"))
        except ValueError:
            pass
    items = query.order_by(PullRequest.created_at.desc()).all()

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "title", "repo", "pr_number", "branch", "status", "priority", "description", "github_url", "created_at", "updated_at"])
        for item in items:
            writer.writerow([item.id, item.title, item.repo, item.pr_number, item.branch, item.status, item.priority, item.description, item.github_url, item.created_at, item.updated_at])
        yield buf.getvalue()

    return StreamingResponse(generate(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=pull_requests.csv"})


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
    if status not in STATUS_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid status: {status!r}")
    if priority not in PRIORITY_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid priority: {priority!r}")
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
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse("partials/pr_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_pr_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(PullRequest).filter(PullRequest.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
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
    if status not in STATUS_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid status: {status!r}")
    if priority not in PRIORITY_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid priority: {priority!r}")
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
