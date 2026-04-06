from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Code Review ──────────────────────────────────────────────────────────────

class CodeReviewBase(BaseModel):
    title: str
    repo: Optional[str] = ""
    pr_number: Optional[int] = None
    author: Optional[str] = ""
    complexity: Optional[int] = Field(default=3, ge=1, le=5)
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    notes: Optional[str] = ""
    github_url: Optional[str] = ""


class CodeReviewCreate(CodeReviewBase):
    pass


class CodeReviewUpdate(CodeReviewBase):
    title: Optional[str] = None


class CodeReviewOut(CodeReviewBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Issue ─────────────────────────────────────────────────────────────────────

class IssueBase(BaseModel):
    title: str
    repo: Optional[str] = ""
    issue_number: Optional[int] = None
    labels: Optional[str] = ""
    severity: Optional[str] = "medium"
    status: Optional[str] = "open"
    priority: Optional[str] = "medium"
    description: Optional[str] = ""
    github_url: Optional[str] = ""


class IssueCreate(IssueBase):
    pass


class IssueUpdate(IssueBase):
    title: Optional[str] = None


class IssueOut(IssueBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Pull Request ──────────────────────────────────────────────────────────────

class PullRequestBase(BaseModel):
    title: str
    repo: Optional[str] = ""
    pr_number: Optional[int] = None
    branch: Optional[str] = ""
    status: Optional[str] = "open"
    priority: Optional[str] = "medium"
    description: Optional[str] = ""
    github_url: Optional[str] = ""


class PullRequestCreate(PullRequestBase):
    pass


class PullRequestUpdate(PullRequestBase):
    title: Optional[str] = None


class PullRequestOut(PullRequestBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Fix ────────────────────────────────────────────────────────────────────────

class FixBase(BaseModel):
    title: str
    repo: Optional[str] = ""
    issue_ref: Optional[str] = ""
    description: Optional[str] = ""
    difficulty: Optional[int] = Field(default=3, ge=1, le=5)
    time_spent_minutes: Optional[int] = 0
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"


class FixCreate(FixBase):
    pass


class FixUpdate(FixBase):
    title: Optional[str] = None


class FixOut(FixBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
