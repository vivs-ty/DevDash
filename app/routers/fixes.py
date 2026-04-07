from fastapi import APIRouter, Depends, Request, Form, HTTPException
from ..templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Fix
from ..utils import get_nav_counts

router = APIRouter(tags=["fixes"])

STATUS_OPTIONS = ["pending", "in_progress", "testing", "done", "wontfix"]
PRIORITY_OPTIONS = ["low", "medium", "high", "critical"]


@router.get("/", response_class=HTMLResponse)
def list_fixes(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    page = max(1, page)
    limit = max(1, min(limit, 200))
    query = db.query(Fix)
    if status:
        query = query.filter(Fix.status == status)
    if priority:
        query = query.filter(Fix.priority == priority)
    total = query.count()
    items = query.order_by(Fix.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return templates.TemplateResponse("fixes.html", {
        "request": request,
        "items": items,
        "active": "fixes",
        "filter_status": status or "",
        "filter_priority": priority or "",
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "page": page,
        "limit": limit,
        "total": total,
        **get_nav_counts(db),
    })


@router.post("/", response_class=HTMLResponse)
def create_fix(
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    issue_ref: str = Form(""),
    description: str = Form(""),
    difficulty: int = Form(3),
    time_spent_minutes: int = Form(0),
    status: str = Form("pending"),
    priority: str = Form("medium"),
    db: Session = Depends(get_db),
):
    if status not in STATUS_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid status: {status!r}")
    if priority not in PRIORITY_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid priority: {priority!r}")
    item = Fix(
        title=title, repo=repo, issue_ref=issue_ref, description=description,
        difficulty=difficulty, time_spent_minutes=time_spent_minutes,
        status=status, priority=priority,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/fix_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/card", response_class=HTMLResponse)
def fix_card(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(Fix).filter(Fix.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse("partials/fix_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.get("/{item_id}/edit", response_class=HTMLResponse)
def edit_fix_form(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(Fix).filter(Fix.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse("partials/fix_edit.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.put("/{item_id}", response_class=HTMLResponse)
def update_fix(
    item_id: int,
    request: Request,
    title: str = Form(...),
    repo: str = Form(""),
    issue_ref: str = Form(""),
    description: str = Form(""),
    difficulty: int = Form(3),
    time_spent_minutes: int = Form(0),
    status: str = Form("pending"),
    priority: str = Form("medium"),
    db: Session = Depends(get_db),
):
    item = db.query(Fix).filter(Fix.id == item_id).first()
    if not item:
        return HTMLResponse(status_code=404, content="Not found")
    if status not in STATUS_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid status: {status!r}")
    if priority not in PRIORITY_OPTIONS:
        return HTMLResponse(status_code=422, content=f"Invalid priority: {priority!r}")
    item.title = title
    item.repo = repo
    item.issue_ref = issue_ref
    item.description = description
    item.difficulty = difficulty
    item.time_spent_minutes = time_spent_minutes
    item.status = status
    item.priority = priority
    db.commit()
    db.refresh(item)
    return templates.TemplateResponse("partials/fix_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.patch("/{item_id}/status", response_class=HTMLResponse)
def update_fix_status(
    item_id: int,
    request: Request,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    item = db.query(Fix).filter(Fix.id == item_id).first()
    if item:
        item.status = status
        db.commit()
        db.refresh(item)
    return templates.TemplateResponse("partials/fix_card.html", {
        "request": request,
        "item": item,
        "status_options": STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
    })


@router.delete("/{item_id}", response_class=HTMLResponse)
def delete_fix(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Fix).filter(Fix.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return HTMLResponse(content="")
