# DevDash – Developer Workflow Hub

A self-hosted web dashboard for tracking your developer workflow: code reviews, GitHub issues, pull requests, and fixes — all in one place, with optional GitHub sync.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-local%20DB-lightgrey?logo=sqlite)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

---

## Features

- **Code Reviews** – Track every PR review you owe or own, with complexity ratings, author, status, and priority.
- **Issues** – Manage GitHub issues assigned to you with severity, labels, and status flow.
- **Pull Requests** – Monitor your authored PRs from open → merged.
- **Fixes** – Log bugs you're working on, with difficulty rating and time tracking.
- **Analytics** – Visual charts for status/priority distributions and 14-day activity history.
- **GitHub Sync** – One-click import of assigned issues, review requests, and authored PRs directly from the GitHub API.
- **Dashboard** – Priority-sorted overview of all active items + daily standup summary.
- **HTMX-powered UI** – Inline editing and instant updates without full page reloads.

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | [FastAPI](https://fastapi.tiangolo.com/) |
| Database   | SQLite via [SQLAlchemy 2](https://docs.sqlalchemy.org/) |
| Templating | [Jinja2](https://jinja.palletsprojects.com/) + [HTMX](https://htmx.org/) |
| HTTP       | [httpx](https://www.python-httpx.org/) (async GitHub API calls) |
| Server     | [Uvicorn](https://www.uvicorn.org/) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vivs-ty/DevDash.git
cd DevDash

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure GitHub sync
cp .env.example .env
# Edit .env with your GitHub token and username
```

### Running the App

```bash
python run.py
```

Open your browser at **http://localhost:8000**.

The SQLite database (`devdash.db`) is created automatically on first run.

---

## Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```env
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_USERNAME=your_github_username
```

The GitHub token requires **read-only** scopes: `repo` (or at minimum `public_repo`) and `read:user`.

> The `.env` file is gitignored. Never commit your token.

---

## Project Structure

```
DevDash/
├── run.py                  # Entry point – starts Uvicorn
├── requirements.txt
├── .env.example
├── app/
│   ├── main.py             # FastAPI app factory, router registration
│   ├── database.py         # SQLAlchemy engine + session setup
│   ├── models.py           # ORM models: CodeReview, Issue, PullRequest, Fix
│   ├── schemas.py          # Pydantic schemas (validation)
│   ├── utils.py            # Shared helpers (nav counts, priority sort, dots)
│   ├── templates_config.py # Jinja2 templates instance
│   ├── routers/
│   │   ├── dashboard.py    # GET / — overview & standup
│   │   ├── reviews.py      # CRUD for code reviews
│   │   ├── issues.py       # CRUD for issues
│   │   ├── pull_requests.py# CRUD for pull requests
│   │   ├── fixes.py        # CRUD for fixes
│   │   ├── github_sync.py  # GitHub API sync endpoint
│   │   └── analytics.py    # Charts data
│   ├── services/
│   │   └── github_service.py # GitHub API client helpers
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── reviews.html
│   │   ├── issues.html
│   │   ├── pull_requests.html
│   │   ├── fixes.html
│   │   ├── analytics.html
│   │   ├── sync.html
│   │   └── partials/       # HTMX partial templates (cards, edit forms)
│   └── static/
│       ├── css/style.css
│       └── js/app.js
└── devdash.db              # SQLite database (auto-created, gitignored)
```

---

## Usage

### Adding Items Manually

Each section (Reviews, Issues, PRs, Fixes) has an **Add** form at the top of the page. Fill in the title and optional fields, then submit. Cards appear instantly via HTMX.

### Inline Editing

Click the **Edit** button on any card to expand an inline form. Save to update immediately without a page refresh.

### Quick Status Updates

Use the status dropdown directly on each card to move an item through its workflow without opening the full edit form.

### GitHub Sync

1. Go to **Sync** in the sidebar.
2. Enter your GitHub token and username (or set them in `.env`).
3. Click **Sync from GitHub** — DevDash will import:
   - PRs where you are a requested reviewer → Code Reviews
   - Issues assigned to you → Issues
   - Open PRs you authored → Pull Requests

Sync is **additive**: existing items (matched by `github_url`) are not duplicated.

---

## Known Limitations / Roadmap

- [ ] Add `.env.example` file
- [ ] Pagination for list views (currently all records are returned at once)
- [ ] Input validation for enum fields (status, priority, severity)
- [ ] Fix timezone handling: standup cutoff uses `datetime.utcnow()` but SQLite stores local time
- [ ] Return HTTP 404 from card/edit GET routes when item ID does not exist
- [ ] Replace loading all records into memory for deduplication in GitHub sync

---

## Contributing

1. Fork the repo and create your feature branch (`git checkout -b feature/my-change`).
2. Commit your changes with a clear message.
3. Open a pull request describing what you changed and why.

---

## License

MIT © vivs-ty
