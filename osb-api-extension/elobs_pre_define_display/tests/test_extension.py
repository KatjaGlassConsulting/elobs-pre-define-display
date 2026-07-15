from __future__ import annotations
import importlib
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

# For isolated unit testing we mount the extension router on a minimal app.
# In OSB the same router is loaded from clinical-mdr-api/extensions/.
from elobs_pre_define_display.elobs_pre_define_display_main import router

app = FastAPI()
app.include_router(router, prefix="/elobs-pre-define-display")
client = TestClient(app)


def test_hello_returns_message():
    """The dummy hello endpoint returns the expected greeting as JSON."""
    response = client.get("/elobs-pre-define-display/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "hallo world"}


def test_loads_as_top_level_module_like_osb():
    """OSB's loader imports `<ext>_main` as a TOP-LEVEL module with only the
    extension folder on sys.path (see extensions_api.load_extensions). Relative
    imports have no parent package there, so every sibling import must fall back
    to a top-level import. This reproduces that load and guards against the 502.
    """
    ext_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, ext_dir)
    # Drop package-context copies so the top-level import actually re-executes.
    for name in ("elobs_pre_define_display_main", "models", "osb_direct_client"):
        sys.modules.pop(name, None)
    try:
        module = importlib.import_module("elobs_pre_define_display_main")
        assert hasattr(module, "router")
    finally:
        sys.path.remove(ext_dir)


def test_studies_returns_summaries():
    """The studies endpoint returns normalized study summaries from OSB."""
    sample = [
        {"uid": "Study_000001", "study_id": "CDISC DEV-0", "acronym": "DEV0"},
        {"uid": "Study_000002", "study_id": "CDISC DEV-1", "acronym": None},
    ]
    mock_client = MagicMock()
    mock_client.get_studies = AsyncMock(return_value=sample)

    with patch(
        "elobs_pre_define_display.elobs_pre_define_display_main.OsbDirectClient",
        return_value=mock_client,
    ):
        response = client.get("/elobs-pre-define-display/studies")

    assert response.status_code == 200
    assert response.json() == sample
