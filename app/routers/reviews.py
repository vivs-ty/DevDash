from fastapi import APIRouter, Depends, Request, Form, HTTPException
from ..templates_config import templates
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import csv
import io

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
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    page = max(1, page)
    limit = max(1, min(limit, 200))
    query = db.query(CodeReview)
    if status:
        query = query.filter(CodeReview.status == status)
    if priority:
        query = query.filter(CodeReview.priority == priority)
    if date_from:
        try:
            query = query.filter(CodeReview.created_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(CodeReview.created_at <= datetime.fromisoformat(date_to + "T23:59:59"))
        except ValueError:
            pass
    total = query.count()
    items = query.order_by(CodeReview.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return templates.TemplateResponse("reviews.html", {
        "request": request,
        "items": items,
        "active": "reviews",
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
def export_reviews_csv(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(CodeReview)
    if status:
        query = query.filter(CodeReview.status == status)
    if priority:
        query = query.filter(CodeReview.priority == priority)
    if date_from:
        try:
            query = query.filter(CodeReview.created_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(CodeReview.created_at <= datetime.fromisoformat(date_to + "T23:59:59"))
        except ValueError:
            pass
    items = query.order_by(CodeReview.created_at.desc()).all()

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "title", "repo", "pr_number", "author", "complexity", "status", "priority", "notes", "github_url", "created_at", "updated_at"])
        for item in items:
            writer.writerow([item.id, item.title, item.repo, item.pr_number, item.author, item.complexity, item.status, item.priority, item.notes, item.github_url, item.created_at, item.updated_at])
        yield buf.getvalue()

    return StreamingResponse(generate(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=reviews.csv"})


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
    if status not in STATUS_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid status: {status!r}")
    if priority not in PRIORITY_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid priority: {priority!r}")
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
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse("partials/review_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_review_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(CodeReview).filter(CodeReview.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
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
    if status not in STATUS_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid status: {status!r}")
    if priority not in PRIORITY_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid priority: {priority!r}")
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
