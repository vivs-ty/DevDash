from fastapi import APIRouter, Depends, Request, Form
from ..templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Issue
from ..utils import get_nav_counts

router = APIRouter(tags=["issues"])

STATUS_OPTIONS = ["open", "in_progress", "resolved", "closed", "blocked"]
PRIORITY_OPTIONS = ["low", "medium", "high", "critical"]
SEVERITY_OPTIONS = ["low", "medium", "high", "critical"]


@router.get("/", response_class=HTMLResponse)
def list_issues(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Issue)
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    items = query.order_by(Issue.created_at.desc()).all()
    return templates.TemplateResponse("issues.html", {
        "request": request,
        "items": items,
        "active": "issues",
        "filter_status": status or "",
        "filter_priority": priority or "",
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "severity_options": SEVERITY_OPTIONS,
        **get_nav_counts(db),
    })


@router.post("/", response_class=HTMLResponse)
def create_issue(
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    issue_number: Optional[int] = Form(None),
    labels: str = Form(""),
    severity: str = Form("medium"),
    status: str = Form("open"),
    priority: str = Form("medium"),
    description: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = Issue(
        title=title, repo=repo, issue_number=issue_number, labels=labels,
        severity=severity, status=status, priority=priority,
        description=description, github_url=github_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/issue_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "severity_options": SEVERITY_OPTIONS,
    })


@router.get("/{item_id}/card", response_class=HTMLResponse)
def issue_card(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(Issue).filter(Issue.id == item_id).first()
    return templates.TemplateResponse("partials/issue_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "severity_options": SEVERITY_OPTIONS,
    })


@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_issue_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(Issue).filter(Issue.id == item_id).first()
    return templates.TemplateResponse("partials/issue_edit.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "severity_options": SEVERITY_OPTIONS,
    })


@router.put("/{item_id}", response_class=HTMLResponse)
def update_issue(
    item_id: int,
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    issue_number: Optional[int] = Form(None),
    labels: str = Form(""),
    severity: str = Form("medium"),
    status: str = Form("open"),
    priority: str = Form("medium"),
    description: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = db.query(Issue).filter(Issue.id == item_id).first()
    if not item:
        return HTMLResponse(status_code=404, content="Not found")
    item.title = title
    item.repo = repo
    item.issue_number = issue_number
    item.labels = labels
    item.severity = severity
    item.status = status
    item.priority = priority
    item.description = description
    item.github_url = github_url
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/issue_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "severity_options": SEVERITY_OPTIONS,
    })


@router.patch("/{item_id}/status", response_class=HTMLResponse)
def update_issue_status(
    item_id: int,
    request: Request,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    item = db.query(Issue).filter(Issue.id == item_id).first()
    if item:
        item.status = status
        db.commit()
        db.refresh(item)
    return templates.TemplateResponse("partials/issue_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "severity_options": SEVERITY_OPTIONS,
    })


@router.delete("/{item_id}", response_class=HTMLResponse)
def delete_issue(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Issue).filter(Issue.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return HTMLResponse(content="")
