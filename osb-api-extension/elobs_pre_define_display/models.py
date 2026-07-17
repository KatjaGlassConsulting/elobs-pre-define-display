from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class Standard(BaseModel):
    """A sponsor model and the CDISC Implementation Guide it extends (panel 3)."""

    sponsor_model: str = Field(..., description="Sponsor model name (selection value)")
    cdisc_ig: Optional[str] = Field(None, description="Extended CDISC IG name")
    effective_date: Optional[Any] = Field(None, description="Extended IG effective date")
    version: Optional[str] = Field(None, description="Extended IG version number")
