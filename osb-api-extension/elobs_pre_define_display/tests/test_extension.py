# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Katja Glass Consulting

from __future__ import annotations
import importlib
import os
import sys
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

# For isolated unit testing we mount the extension router on a minimal app.
# In OSB the same router is loaded from clinical-mdr-api/extensions/.
from elobs_pre_define_display import elobs_pre_define_display_main as main

app = FastAPI()
app.include_router(main.router, prefix="/elobs-pre-define-display")
client = TestClient(app)


def test_loads_as_top_level_module_like_osb():
    """OSB's loader imports `<ext>_main` as a TOP-LEVEL module with only the
    extension folder on sys.path (see extensions_api.load_extensions). Relative
    imports have no parent package there, so every sibling import must fall back
    to a top-level import. This reproduces that load and guards against the 502.
    """
    ext_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, ext_dir)
    for name in (
        "elobs_pre_define_display_main",
        "models",
        "osb_direct_client",
        "cypher",
        "predefine_repository",
    ):
        sys.modules.pop(name, None)
    try:
        module = importlib.import_module("elobs_pre_define_display_main")
        assert hasattr(module, "router")
    finally:
        sys.path.remove(ext_dir)


def test_standards_endpoint_returns_sponsor_models():
    """GET /standards returns the joined sponsor-model + IG rows."""
    sample = [
        {"sponsor_model": "sm_x", "cdisc_ig": "sdtmig 3.2", "effective_date": None, "version": "3.2"},
    ]
    mock_client = MagicMock()
    mock_client.get_standards.return_value = sample

    with patch.object(main, "OsbDirectClient", return_value=mock_client):
        response = client.get("/elobs-pre-define-display/standards")

    assert response.status_code == 200
    assert response.json() == sample


def test_datasets_endpoint_passes_params_through():
    """GET datasets forwards uid, sponsor_model and version to the repository."""
    with patch.object(main, "get_datasets", return_value=[{"Dataset": "VS"}]) as m:
        response = client.get(
            "/elobs-pre-define-display/studies/Study_000001/datasets",
            params={"sponsor_model": "sm_x", "version": "2"},
        )

    assert response.status_code == 200
    assert response.json() == [{"Dataset": "VS"}]
    m.assert_called_once_with("Study_000001", sponsor_model="sm_x", version="2")


def test_datasets_endpoint_requires_sponsor_model():
    """Omitting the required sponsor_model query param is a validation error."""
    response = client.get("/elobs-pre-define-display/studies/Study_000001/datasets")
    assert response.status_code == 422


def test_variables_endpoint_passes_params_through():
    """GET variables forwards dataset + sponsor_model to the repository."""
    with patch.object(main, "get_variables", return_value=[{"Variable": "VSTEST"}]) as m:
        response = client.get(
            "/elobs-pre-define-display/datasets/VS/variables",
            params={"sponsor_model": "sm_x"},
        )

    assert response.status_code == 200
    assert response.json() == [{"Variable": "VSTEST"}]
    m.assert_called_once_with("VS", sponsor_model="sm_x")
