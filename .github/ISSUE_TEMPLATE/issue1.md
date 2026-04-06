## Problem

In every router (`reviews.py`, `issues.py`, `pull_requests.py`, `fixes.py`), the `GET /{item_id}/card` and `GET /{item_id}/edit` endpoints silently pass `None` to the Jinja2 template when the item is not found:

```python
def issue_card(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(Issue).filter(Issue.id == item_id).first()
    # item is None here if not found – no guard
    return templates.TemplateResponse("partials/issue_card.html", {
        "request": request,
        "item": item,  # ← None
        ...
    })
```

The template then tries to access attributes like `item.title`, which raises `jinja2.exceptions.UndefinedError` and returns a 500 instead of a clean 404.

## Expected Behaviour

Return HTTP 404 with a meaningful message when the item ID does not exist.

## Affected Files

- `app/routers/reviews.py` – `review_card`, `edit_review_form`
- `app/routers/issues.py` – `issue_card`, `edit_issue_form`
- `app/routers/pull_requests.py` – `pr_card`, `edit_pr_form`
- `app/routers/fixes.py` – `fix_card`, `edit_fix_form`

## Fix

Add a not-found guard in each endpoint:

```python
if not item:
    raise HTTPException(status_code=404, detail="Not found")
```
