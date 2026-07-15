from __future__ import annotations
import logging
from fastapi import APIRouter
try:
    from .models import StudySummary  # package import (tests)
except ImportError:
    from models import StudySummary  # top-level import (OSB extensions loader)
try:
    from .osb_direct_client import OsbDirectClient  # package import (tests)
except ImportError:
    from osb_direct_client import OsbDirectClient  # top-level import (OSB extensions loader)

log = logging.getLogger(__name__)

router = APIRouter(
    tags=["ElobsPreDefineDisplay"],
)


@router.get(
    "/hello",
    summary="Dummy greeting endpoint",
    response_description="A static greeting message",
)
async def hello() -> dict[str, str]:
    """Return a static greeting. Placeholder for the first walking skeleton."""
    return {"message": "hallo world"}


@router.get(
    "/studies",
    summary="List studies",
    response_description="Study summaries (uid, study_id, acronym) from OpenStudyBuilder",
    response_model=list[StudySummary],
)
async def list_studies() -> list[StudySummary]:
    """Return a minimal summary of every study, read directly from OSB in-process."""
    client = OsbDirectClient()
    studies = await client.get_studies()
    return [StudySummary(**s) for s in studies]
