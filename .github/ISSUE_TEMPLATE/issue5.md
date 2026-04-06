## Problem

`app/routers/github_sync.py` loads **every row** of each table into memory just to build a set of existing URLs for deduplication:

```python
existing_review_urls = {r.github_url for r in db.query(CodeReview).all()}
existing_issue_urls  = {i.github_url for i in db.query(Issue).all()}
existing_pr_urls     = {p.github_url for p in db.query(PullRequest).all()}
```

As the database grows, this performs a full table scan and hydrates complete ORM objects (all columns) for the sole purpose of reading one field. This will become slow and memory-intensive.

## Expected Behaviour

Only the `github_url` column should be fetched, and only columns needed for comparison should be loaded.

## Fix

Query only the URL column:

```python
from sqlalchemy import select

existing_review_urls = {
    row[0] for row in db.execute(select(CodeReview.github_url)).all()
}
```

This avoids full ORM object hydration and is significantly more efficient at scale.
