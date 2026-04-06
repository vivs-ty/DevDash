## Problem

All list endpoints return every record in the database with no pagination:

```python
items = query.order_by(Issue.created_at.desc()).all()  # ← all rows
```

Similarly, the dashboard loads up to all active items and slices to 10 in Python (`all_active[:10]`) after loading everything from the DB. As the dataset grows, this will cause slow page loads and high memory usage.

## Expected Behaviour

List views should support cursor- or offset-based pagination (e.g. `?page=1&limit=50`) so that large datasets don't degrade performance.

## Affected Files

- `app/routers/reviews.py` – `list_reviews`
- `app/routers/issues.py` – `list_issues`
- `app/routers/pull_requests.py` – `list_prs`
- `app/routers/fixes.py` – `list_fixes`
- `app/routers/dashboard.py` – `dashboard` (active items should use `.limit()` in the query)

## Fix

Add `limit` / `offset` query parameters and apply them with SQLAlchemy's `.limit(n).offset(m)`, combined with a total count for page navigation.
