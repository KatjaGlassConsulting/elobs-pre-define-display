from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class StudySummary(BaseModel):
    """A minimal, display-oriented summary of an OpenStudyBuilder study."""

    uid: str = Field(..., description="OpenStudyBuilder study UID (e.g. Study_000001)")
    study_id: Optional[str] = Field(None, description="Human-readable study identifier")
    acronym: Optional[str] = Field(None, description="Study acronym, if defined")
