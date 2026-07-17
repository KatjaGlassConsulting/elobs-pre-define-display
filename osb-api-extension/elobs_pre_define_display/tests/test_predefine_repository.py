from __future__ import annotations
from unittest.mock import patch

from elobs_pre_define_display import predefine_repository as repo


def test_get_datasets_latest_uses_latest_match():
    """Without a version, the study match uses the LATEST relationship."""
    with patch.object(repo, "run_cypher", return_value=[{"Dataset": "VS"}]) as m:
        result = repo.get_datasets("Study_000001", sponsor_model="sm_x")

    assert result == [{"Dataset": "VS"}]
    query, params = m.call_args.args
    assert "[:LATEST]->" in query
    assert "HAS_VERSION" not in query
    assert params == {"uid": "Study_000001", "sponsor_model": "sm_x"}


def test_get_datasets_specific_version_uses_has_version_match():
    """With a version, the study match uses HAS_VERSION and passes the version param."""
    with patch.object(repo, "run_cypher", return_value=[]) as m:
        repo.get_datasets("Study_000001", sponsor_model="sm_x", version="2")

    query, params = m.call_args.args
    assert "HAS_VERSION" in query
    assert "$version" in query
    assert params == {"uid": "Study_000001", "sponsor_model": "sm_x", "version": "2"}


def test_get_variables_filters_by_sponsor_model_and_dataset():
    """Variables are keyed by sponsor model + dataset (study-version independent)."""
    with patch.object(repo, "run_cypher", return_value=[{"Variable": "VSTEST"}]) as m:
        result = repo.get_variables("VS", sponsor_model="sm_x")

    assert result == [{"Variable": "VSTEST"}]
    query, params = m.call_args.args
    assert "$sponsor_model" in query and "$dataset" in query
    assert params == {"sponsor_model": "sm_x", "dataset": "VS"}
