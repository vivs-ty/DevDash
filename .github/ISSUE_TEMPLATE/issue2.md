## Problem

`app/routers/github_sync.py` accepts the GitHub personal access token as a plaintext HTML form field:

```python
@router.post("/github", response_class=HTMLResponse)
async def do_github_sync(
    request: Request,
    token: str = Form(""),   # ← token in HTTP body
    ...
):
    gh_token = token or os.getenv("GITHUB_TOKEN", "")
```

This means the token travels in the HTTP POST body and may appear in:
- Web server access/error logs
- Browser history (form re-submission)
- Proxy/CDN logs

Even though this is a local app, the pattern is a security anti-pattern and should be avoided.

## Expected Behaviour

The token should only be read from the environment variable (`GITHUB_TOKEN` in `.env`). The sync form should not accept a raw token input; instead it should confirm the token is configured via env and rely on that.

## Fix

Remove the `token` form field from `do_github_sync`. Always read from `os.getenv("GITHUB_TOKEN")` and return a clear error if it is not set, prompting the user to configure `.env`.
