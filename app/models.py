from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    repo = Column(String(255), default="")
    pr_number = Column(Integer, nullable=True)
    author = Column(String(100), default="")
    complexity = Column(Integer, default=3)          # 1–5
    status = Column(String(30), default="pending")   # pending | in_review | approved | changes_requested | done
    priority = Column(String(20), default="medium")  # low | medium | high | critical
    notes = Column(Text, default="")
    github_url = Column(String(500), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    repo = Column(String(255), default="")
    issue_number = Column(Integer, nullable=True)
    labels = Column(String(500), default="")
    severity = Column(String(20), default="medium")  # low | medium | high | critical
    status = Column(String(30), default="open")      # open | in_progress | resolved | closed | blocked
    priority = Column(String(20), default="medium")
    description = Column(Text, default="")
    github_url = Column(String(500), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    repo = Column(String(255), default="")
    pr_number = Column(Integer, nullable=True)
    branch = Column(String(255), default="")
    status = Column(String(30), default="open")      # open | draft | in_review | approved | merged | closed
    priority = Column(String(20), default="medium")
    description = Column(Text, default="")
    github_url = Column(String(500), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Fix(Base):
    __tablename__ = "fixes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    repo = Column(String(255), default="")
    issue_ref = Column(String(100), default="")
    description = Column(Text, default="")
    difficulty = Column(Integer, default=3)          # 1–5
    time_spent_minutes = Column(Integer, default=0)
    status = Column(String(30), default="pending")   # pending | in_progress | testing | done | wontfix
    priority = Column(String(20), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
