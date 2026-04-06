from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routers import dashboard, reviews, issues, pull_requests, fixes, github_sync, analytics

BASE_DIR = Path(__file__).parent  # DevDash/app/


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="DevDash – Developer Workflow Hub", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(dashboard.router)
app.include_router(reviews.router,       prefix="/reviews")
app.include_router(issues.router,        prefix="/issues")
app.include_router(pull_requests.router, prefix="/pull-requests")
app.include_router(fixes.router,         prefix="/fixes")
app.include_router(github_sync.router,   prefix="/sync")
app.include_router(analytics.router,     prefix="/analytics")
