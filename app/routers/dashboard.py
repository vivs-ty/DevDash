from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Request
from ..templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CodeReview, Issue, PullRequest, Fix
from ..utils import get_nav_counts

router = APIRouter(tags=["dashboard"])

REVIEW_ACTIVE = ["pending", "in_review"]
ISSUE_ACTIVE = ["open", "in_progress", "blocked"]
PR_ACTIVE = ["open", "draft", "in_review"]
FIX_ACTIVE = ["pending", "in_progress", "testing"]


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    today_start = datetime.combine(date.today(), datetime.min.time())

    # priority items (not done) sorted critical → high → medium → low
    PRIO = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    reviews = db.query(CodeReview).filter(CodeReview.status.in_(REVIEW_ACTIVE)).limit(10).all()
    issues = db.query(Issue).filter(Issue.status.in_(ISSUE_ACTIVE)).limit(10).all()
    prs = db.query(PullRequest).filter(PullRequest.status.in_(PR_ACTIVE)).limit(10).all()
    fixes = db.query(Fix).filter(Fix.status.in_(FIX_ACTIVE)).limit(10).all()

    all_active = (
        [("review", r) for r in reviews]
        + [("issue", i) for i in issues]
        + [("pr", p) for p in prs]
        + [("fix", f) for f in fixes]
    )
    all_active.sort(key=lambda x: PRIO.get(x[1].priority, 2))

    # running totals
    total_reviews = db.query(CodeReview).count()
    total_issues  = db.query(Issue).count()
    total_prs     = db.query(PullRequest).count()
    total_fixes   = db.query(Fix).count()

    done_reviews = db.query(CodeReview).filter(CodeReview.status == "done").count()
    done_issues  = db.query(Issue).filter(Issue.status.in_(["resolved", "closed"])).count()
    done_prs     = db.query(PullRequest).filter(PullRequest.status.in_(["merged", "closed"])).count()
    done_fixes   = db.query(Fix).filter(Fix.status.in_(["done", "wontfix"])).count()

    # standup data: items created or updated in the last 24 h
    cutoff = datetime.utcnow() - timedelta(hours=24)
    standup_reviews = db.query(CodeReview).filter(CodeReview.created_at >= cutoff).all()
    standup_issues  = db.query(Issue).filter(Issue.created_at >= cutoff).all()
    standup_prs     = db.query(PullRequest).filter(PullRequest.created_at >= cutoff).all()
    standup_fixes   = db.query(Fix).filter(Fix.created_at >= cutoff).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active": "dashboard",
        "today": date.today().strftime("%A, %B %d, %Y"),  # %d gives zero-padded day, works cross-platform
        "all_active": all_active[:10],
        "total_reviews": total_reviews, "done_reviews": done_reviews,
        "total_issues":  total_issues,  "done_issues":  done_issues,
        "total_prs":     total_prs,     "done_prs":     done_prs,
        "total_fixes":   total_fixes,   "done_fixes":   done_fixes,
        "standup_reviews": standup_reviews,
        "standup_issues":  standup_issues,
        "standup_prs":     standup_prs,
        "standup_fixes":   standup_fixes,
        **get_nav_counts(db),
    })
