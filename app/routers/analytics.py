from sqlalchemy import func
from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, Request
from ..templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CodeReview, Issue, PullRequest, Fix
from ..utils import get_nav_counts

router = APIRouter(tags=["analytics"])


@router.get("/", response_class=HTMLResponse)
def analytics(request: Request, db: Session = Depends(get_db)):
    # Status distribution for each category
    def status_dist(model):
        rows = db.query(model.status, func.count(model.id)).group_by(model.status).all()
        return {r[0]: r[1] for r in rows}

    def priority_dist(model):
        rows = db.query(model.priority, func.count(model.id)).group_by(model.priority).all()
        return {r[0]: r[1] for r in rows}

    # Daily activity over last 14 days
    days = [(date.today() - timedelta(days=i)) for i in range(13, -1, -1)]
    day_labels = [d.strftime("%b %d") for d in days]

    def daily_counts(model):
        counts = []
        for d in days:
            start = datetime.combine(d, datetime.min.time())
            end   = datetime.combine(d, datetime.max.time())
            counts.append(
                db.query(model).filter(
                    model.created_at >= start,
                    model.created_at <= end,
                ).count()
            )
        return counts

    total_time_min = db.query(func.sum(Fix.time_spent_minutes)).scalar() or 0

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "active": "analytics",
        "review_status":   status_dist(CodeReview),
        "issue_status":    status_dist(Issue),
        "pr_status":       status_dist(PullRequest),
        "fix_status":      status_dist(Fix),
        "review_priority": priority_dist(CodeReview),
        "issue_priority":  priority_dist(Issue),
        "pr_priority":     priority_dist(PullRequest),
        "fix_priority":    priority_dist(Fix),
        "day_labels":      day_labels,
        "review_daily":    daily_counts(CodeReview),
        "issue_daily":     daily_counts(Issue),
        "pr_daily":        daily_counts(PullRequest),
        "fix_daily":       daily_counts(Fix),
        "total_time_hours": round(total_time_min / 60, 1),
        "total_reviews":    db.query(CodeReview).count(),
        "total_issues":     db.query(Issue).count(),
        "total_prs":        db.query(PullRequest).count(),
        "total_fixes":      db.query(Fix).count(),
        **get_nav_counts(db),
    })
