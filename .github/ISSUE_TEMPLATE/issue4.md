## Problem

Form endpoints across all routers accept enum-like string fields (`status`, `priority`, `severity`) without any validation. Any arbitrary string can be submitted and persisted to the database:

```python
@router.post("/", response_class=HTMLResponse)
def create_issue(
    ...
    status: str = Form("open"),      # ← accepts any string
    priority: str = Form("medium"),  # ← accepts any string
    severity: str = Form("medium"),  # ← accepts any string
    ...
):
```

This means a crafted POST request can set `status="hacked"` or inject unexpected data that breaks filter logic, UI rendering, and analytics grouping.

## Expected Behaviour

Only values defined in `STATUS_OPTIONS`, `PRIORITY_OPTIONS`, and `SEVERITY_OPTIONS` should be accepted. Invalid values should return HTTP 422.

## Affected Files

- `app/routers/reviews.py`
- `app/routers/issues.py`
- `app/routers/pull_requests.py`
- `app/routers/fixes.py`

## Fix

Use `Literal` types in Pydantic schemas, or add explicit `Enum` classes and validate form inputs before writing to the database. Alternatively use FastAPI's `Query`/`Form` with a validator.
