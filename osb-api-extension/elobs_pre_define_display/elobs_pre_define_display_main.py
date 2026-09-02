# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Katja Glass Consulting

from __future__ import annotations
import logging
from typing import Any
from fastapi import APIRouter, Query

# Sibling imports MUST use the top-level fallback: the OSB loader imports this file
# as a top-level module (no parent package), so plain relative imports would raise
# and 502 the whole extensions API. See the design spec's loader-contract section.
try:
    from .models import Standard  # package import (tests)
except ImportError:
    from models import Standard  # top-level import (OSB extensions loader)
try:
    from .osb_direct_client import OsbDirectClient
except ImportError:
    from osb_direct_client import OsbDirectClient
try:
    from .predefine_repository import get_datasets, get_variables
except ImportError:
    from predefine_repository import get_datasets, get_variables

log = logging.getLogger(__name__)

router = APIRouter(
    tags=["ElobsPreDefineDisplay"],
)


@router.get(
    "/standards",
    summary="List sponsor models (standards)",
    response_description="Sponsor models with their extended CDISC IG",
    response_model=list[Standard],
)
def list_standards() -> list[dict[str, Any]]:
    """Panel 3 — sponsor models joined with their extended IG's date + version."""
    return OsbDirectClient().get_standards()


@router.get(
    "/studies/{uid}/datasets",
    summary="List datasets (domains) for a study",
    response_description="Domains used by the study's activities for the given standard",
)
def list_datasets(
    uid: str,
    sponsor_model: str = Query(..., description="Sponsor model name"),
    version: str | None = Query(None, description="Study version. Omit for latest."),
) -> list[dict[str, Any]]:
    """Panel 4 — datasets used by the study, version-aware, for the selected standard."""
    return get_datasets(uid, sponsor_model=sponsor_model, version=version or None)


@router.get(
    "/datasets/{dataset}/variables",
    summary="List variables of a dataset",
    response_description="Dataset variables as defined by the sponsor model",
)
def list_variables(
    dataset: str,
    sponsor_model: str = Query(..., description="Sponsor model name"),
) -> list[dict[str, Any]]:
    """Panel 5 — variables of a dataset as defined by the sponsor model."""
    return get_variables(dataset, sponsor_model=sponsor_model)
