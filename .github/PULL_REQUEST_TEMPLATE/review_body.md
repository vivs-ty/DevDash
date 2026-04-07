## Code Review – DevDash Codebase

Great baseline project. The architecture is clean (FastAPI + SQLAlchemy + HTMX) and the router-per-resource structure is consistent and easy to navigate.

Below is a summary of the issues I found during this review. Each one has been filed as a separate GitHub issue so they can be addressed individually.

---

### 🔴 Bugs

**Issue #1 – Missing 404 guards on `GET /{id}/card` and `GET /{id}/edit`**

All four routers (`reviews`, `issues`, `pull_requests`, `fixes`) perform a `db.query().first()` without checking the result before passing it to a Jinja2 template. When the item doesn't exist, `None` is passed into the template context which causes `jinja2.exceptions.UndefinedError` → HTTP 500. The update (`PUT`) handlers already have the correct guard – it just needs to be added to the GET routes too.

**Issue #3 – `datetime.utcnow()` used against SQLite local-time timestamps**

In `dashboard.py`, the standup cutoff is calculated with `datetime.utcnow()`:

```python
cutoff = datetime.utcnow() - timedelta(hours=24)
standup_reviews = db.query(CodeReview).filter(CodeReview.created_at >= cutoff).all()
```

But `server_default=func.now()` in the SQLAlchemy models stores the **system local time** in SQLite. On any machine where UTC ≠ local time, this comparison is silently wrong. The same naive datetime issue affects `analytics.py`.

---

### 🟠 Security

**Issue #2 – GitHub PAT transmitted as a form field**

`/sync/github` accepts `token: str = Form("")` which puts the personal access token in the HTTP request body. Even in a local-only deployment this is a bad pattern – the token can be captured by proxy tools or appear in server logs. The field should be removed; the token must only be read from the environment.

---

### 🟡 Enhancements

**Issue #4 – No validation on enum-like string fields**

`status`, `priority`, and `severity` fields are plain strings with no constraint. A crafted POST (e.g. with curl) can persist arbitrary values that break filter logic, analytics aggregation, and UI rendering. Using `Literal` types in Pydantic schemas or FastAPI `Enum` validation would fix this.

**Issue #5 – Full table scan for deduplication in GitHub sync**

```python
existing_review_urls = {r.github_url for r in db.query(CodeReview).all()}
```

This loads complete ORM objects for every row just to extract a single column. Replace with a column-only query to avoid unnecessary memory and I/O.

**Issue #6 – No pagination on list views**

All list endpoints call `.all()` unconditionally. Adding `?page=` / `?limit=` query params with `.limit().offset()` in SQLAlchemy is low-effort and prevents future performance degradation.

---

### ✅ What's working well

- Consistent router + schema + model structure across all four resources
- HTMX partial-rendering pattern is well-implemented (card ↔ edit form swaps)
- `get_nav_counts()` utility correctly filters out "done" states from badges
- `lifespan` context manager for DB init is the correct modern FastAPI pattern
- GitHub service is properly async with `httpx.AsyncClient`

---

All issues above have been filed at https://github.com/vivs-ty/DevDash/issues and are listed in the roadmap section of the README added in this PR.
