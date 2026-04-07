# DevDash — Developer Workflow Hub

A self-hosted web dashboard for developers to track code reviews, issues, pull requests, and fixes — all in one place, with GitHub sync and analytics.

Built with **FastAPI**, **SQLite**, **HTMX**, and **Tailwind CSS**.

---

## Features

| Area | What it does |
|------|-------------|
| **Dashboard** | Priority queue of active items across all categories; standup text generator (copy last 24 h of activity to clipboard) |
| **Code Reviews** | Track PR reviews in your queue with status, priority, complexity, and notes |
| **Issues** | Track bugs, blockers, and tasks with severity, labels, and GitHub links |
| **Pull Requests** | Track open and in-review PRs with branch info and priority |
| **Fixes** | Track bug fixes and patches with difficulty rating and time-spent logging |
| **GitHub Sync** | One-click sync that pulls your assigned issues, review requests, and authored PRs from GitHub (all pages, not just the first 50) |
| **Analytics** | Status & priority distribution charts; daily activity chart with configurable windows (7 / 14 / 30 / 90 days); total time logged |
| **Pagination** | All list views support `?page=` and `?limit=` (default 50, max 200) |
| **Filtering** | Filter any list by status, priority, and/or date range (`date_from` / `date_to`) |
| **CSV Export** | Download any filtered list as a CSV file from the Export CSV button |

---

## Tech Stack

- **Backend** — [FastAPI](https://fastapi.tiangolo.com/) + [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite)
- **Templates** — [Jinja2](https://jinja.palletsprojects.com/) + [HTMX](https://htmx.org/) (partial updates without a build step)
- **Styles** — [Tailwind CSS](https://tailwindcss.com/) (CDN, dark theme)
- **GitHub API** — [HTTPX](https://www.python-httpx.org/) async client with full pagination

---

## Getting Started

### Prerequisites

- Python 3.12+
- A GitHub Personal Access Token (for the GitHub Sync feature)

### Local setup

```bash
# 1. Clone the repo
git clone https://github.com/vivs-ty/DevDash.git
cd DevDash

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Edit .env and set GITHUB_TOKEN and GITHUB_USERNAME

# 5. Start the dev server
python run.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

The SQLite database (`devdash.db`) is created automatically on first run.

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | For sync | Personal Access Token with `repo` and `read:user` scopes |
| `GITHUB_USERNAME` | For sync | Your GitHub username (used to query authored PRs) |
| `DATABASE_URL` | Optional | Override the default SQLite path (e.g. for production) |

---

## Project Structure

```
app/
├── main.py               # FastAPI app + router registration
├── database.py           # SQLAlchemy engine (SQLite locally, env-driven in prod)
├── models.py             # ORM models: CodeReview, Issue, PullRequest, Fix
├── schemas.py            # Pydantic schemas
├── utils.py              # Shared helpers (nav counts, etc.)
├── templates_config.py   # Jinja2 template configuration
├── routers/
│   ├── dashboard.py      # GET / — priority queue + standup
│   ├── reviews.py        # CRUD + CSV export for code reviews
│   ├── issues.py         # CRUD + CSV export for issues
│   ├── pull_requests.py  # CRUD + CSV export for PRs
│   ├── fixes.py          # CRUD + CSV export for fixes
│   ├── github_sync.py    # GitHub one-click sync
│   └── analytics.py      # Charts and metrics
├── services/
│   └── github_service.py # Paginated GitHub API calls
├── templates/            # Jinja2 HTML templates
│   └── partials/         # HTMX partial fragments (cards, edit forms)
└── static/               # CSS and JS assets
```

---

## Deployment

### Render (recommended — free tier)

The repo includes a `render.yaml` blueprint and a `Dockerfile`.

1. Go to [render.com](https://render.com) → **New → Blueprint** → connect this repo.  
   Render reads `render.yaml` and creates the service automatically with a 1 GB persistent disk for the database.

2. In the Render service dashboard → **Settings → Deploy Hook** → copy the URL.

3. In GitHub → **Settings → Secrets and variables → Actions** → add a secret:
   ```
   RENDER_DEPLOY_HOOK_URL = <paste the hook URL>
   ```

4. In the Render **Environment** tab, set `GITHUB_TOKEN` and `GITHUB_USERNAME`.

After that, every push to `master` triggers the CI workflow and then auto-deploys to Render.

### Docker (self-hosted)

```bash
docker build -t devdash .
docker run -p 8000:8000 \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_USERNAME=your_username \
  devdash
```

---

## CI / CD

`.github/workflows/deploy.yml` runs on every push and pull request:

| Job | Trigger | What it does |
|-----|---------|-------------|
| **ci** | Every push / PR | Installs deps and runs an app-import smoke test |
| **deploy** | Push to `master` only (after CI passes) | Calls the Render deploy hook to ship the latest code |

---

## API Endpoints (quick reference)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Dashboard |
| `GET/POST` | `/reviews` | List / create code reviews |
| `GET` | `/reviews/export.csv` | Export reviews as CSV |
| `GET/POST` | `/issues` | List / create issues |
| `GET` | `/issues/export.csv` | Export issues as CSV |
| `GET/POST` | `/pull-requests` | List / create PRs |
| `GET` | `/pull-requests/export.csv` | Export PRs as CSV |
| `GET/POST` | `/fixes` | List / create fixes |
| `GET` | `/fixes/export.csv` | Export fixes as CSV |
| `GET` | `/analytics` | Analytics page (`?days=7\|14\|30\|90`) |
| `GET/POST` | `/sync` | GitHub sync page / trigger sync |

All list endpoints accept: `?status=`, `?priority=`, `?date_from=YYYY-MM-DD`, `?date_to=YYYY-MM-DD`, `?page=`, `?limit=`

---

## License

MIT
