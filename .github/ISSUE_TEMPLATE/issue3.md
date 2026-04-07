## Problem

`app/routers/dashboard.py` calculates the standup cutoff using UTC time:

```python
cutoff = datetime.utcnow() - timedelta(hours=24)
standup_reviews = db.query(CodeReview).filter(CodeReview.created_at >= cutoff).all()
```

However, SQLite uses the local system clock for `server_default=func.now()` (stored as local time, not UTC). On systems where local time ≠ UTC, the comparison is wrong and the standup section will silently show incorrect results — either missing recent items or showing stale ones.

The same issue exists in `app/routers/analytics.py` with naive `datetime.combine(d, datetime.min.time())` used in date-range filters.

## Expected Behaviour

All datetime comparisons should use the same timezone convention as what is stored in the database.

## Fix

Replace `datetime.utcnow()` with `datetime.now()` (local time, matching SQLite storage), or better, store all timestamps as UTC throughout by using `server_default=text("(strftime('%Y-%m-%dT%H:%M:%S', 'now'))")` and consistently using UTC in Python code.
