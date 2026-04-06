from sqlalchemy.orm import Session
from .models import CodeReview, Issue, PullRequest, Fix


REVIEW_DONE = ["done"]
ISSUE_DONE = ["resolved", "closed"]
PR_DONE = ["merged", "closed"]
FIX_DONE = ["done", "wontfix"]


def get_nav_counts(db: Session) -> dict:
    """Return counts of active (non-done) items for the sidebar badges."""
    return {
        "review_count": db.query(CodeReview)
            .filter(CodeReview.status.notin_(REVIEW_DONE)).count(),
        "issue_count": db.query(Issue)
            .filter(Issue.status.notin_(ISSUE_DONE)).count(),
        "pr_count": db.query(PullRequest)
            .filter(PullRequest.status.notin_(PR_DONE)).count(),
        "fix_count": db.query(Fix)
            .filter(Fix.status.notin_(FIX_DONE)).count(),
    }


def priority_order(priority: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 2)


def dots(n: int, total: int = 5, filled: str = "●", empty: str = "○") -> str:
    """Return a dot-rating string, e.g. ●●●○○ for 3/5."""
    return filled * n + empty * (total - n)
