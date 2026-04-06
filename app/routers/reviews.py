from fastapi import APIRouter, Depends, Request, Form
from ..templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import CodeReview
from ..utils import get_nav_counts

router = APIRouter(tags=["reviews"])

STATUS_OPTIONS = ["pending", "in_review", "approved", "changes_requested", "done"]
PRIORITY_OPTIONS = ["low", "medium", "high", "critical"]


@router.get("/", response_class=HTMLResponse)
def list_reviews(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(CodeReview)
    if status:
        query = query.filter(CodeReview.status == status)
    if priority:
        query = query.filter(CodeReview.priority == priority)
    items = query.order_by(CodeReview.created_at.desc()).all()
    return templates.TemplateResponse("reviews.html", {
        "request": request,
        "items": items,
        "active": "reviews",
        "filter_status": status or "",
        "filter_priority": priority or "",
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        **get_nav_counts(db),
    })


@router.post("/", response_class=HTMLResponse)
def create_review(
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    pr_number: Optional[int] = Form(None),
    author: str = Form(""),
    complexity: int = Form(3),
    status: str = Form("pending"),
    priority: str = Form("medium"),
    notes: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = CodeReview(
        title=title, repo=repo, pr_number=pr_number, author=author,
        complexity=complexity, status=status, priority=priority,
        notes=notes, github_url=github_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/review_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/card", response_class=HTMLResponse)
def review_card(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(CodeReview).filter(CodeReview.id == item_id).first()
    return templates.TemplateResponse("partials/review_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_review_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(CodeReview).filter(CodeReview.id == item_id).first()
    return templates.TemplateResponse("partials/review_edit.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.put("/{item_id}", response_class=HTMLResponse)
def update_review(
    item_id: int,
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    pr_number: Optional[int] = Form(None),
    author: str = Form(""),
    complexity: int = Form(3),
    status: str = Form("pending"),
    priority: str = Form("medium"),
    notes: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    item = db.query(CodeReview).filter(CodeReview.id == item_id).first()
    if not item:
        return HTMLResponse(status_code=404, content="Not found")
    item.title = title
    item.repo = repo
    item.pr_number = pr_number
    item.author = author
    item.complexity = complexity
    item.status = status
    item.priority = priority
    item.notes = notes
    item.github_url = github_url
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/review_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.patch("/{item_id}/status", response_class=HTMLResponse)
def update_review_status(
    item_id: int,
    request: Request,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    item = db.query(CodeReview).filter(CodeReview.id == item_id).first()
    if item:
        item.status = status
        db.commit()
        db.refresh(item)
    return templates.TemplateResponse("partials/review_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.delete("/{item_id}", response_class=HTMLResponse)
def delete_review(item_id: int, db: Session = Depends(get_db)):
    item = db.query(CodeReview).filter(CodeReview.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return HTMLResponse(content="")
