## Summary

Implements all code-review fixes identified in PR #7. Resolves issues #1, #2, #3, #4, and #5.

---

### Fix #1 — 404 on missing items (`GET /{id}/card`, `GET /{id}/edit`)

**Files:** `reviews.py`, `issues.py`, `pull_requests.py`, `fixes.py`

All `card` and `edit` GET routes now raise `HTTPException(status_code=404)` when the queried item does not exist, instead of passing `None` to the Jinja2 template and causing a 500.

---

### Fix #2 — Remove GitHub token from form submission (security)

**Files:** `github_sync.py`, `templates/sync.html`

`do_github_sync` no longer accepts `token` as an HTML form field. The token is now read **exclusively** from the `GITHUB_TOKEN` environment variable. The sync page now shows a green/amber indicator for whether the token is configured, rather than a password input.

---

### Fix #3 — Timezone mismatch in standup cutoff

**File:** `dashboard.py`

Replaced `datetime.utcnow()` with `datetime.now()`. SQLite stores timestamps in local time (`func.now()`), so UTC comparisons produced wrong results on any system where UTC ≠ local time. The standup "last 24 h" filter now uses the correct local-time baseline.

---

### Fix #4 — Enum validation for `status` / `priority` / `severity`

**Files:** `reviews.py`, `issues.py`, `pull_requests.py`, `fixes.py`

`POST` (create) and `PUT` (update) endpoints now validate enum-like string fields against the existing `STATUS_OPTIONS`, `PRIORITY_OPTIONS`, and `SEVERITY_OPTIONS` lists. Invalid values return HTTP 422 instead of being persisted to the database.

---

### Fix #5 — Efficient deduplication in GitHub sync

**File:** `github_sync.py`

Replaced `{r.github_url for r in db.query(Model).all()}` (full ORM object hydration) with `set(db.scalars(select(Model.github_url)).all())`, which fetches only the `github_url` column. Avoids loading all columns for every row just to build a URL set.

---

### Closes

Resolves #1, #2, #3, #4, #5
