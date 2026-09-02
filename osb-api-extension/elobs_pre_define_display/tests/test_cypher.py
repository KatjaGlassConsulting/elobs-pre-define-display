# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Katja Glass Consulting

from __future__ import annotations
from unittest.mock import patch

from elobs_pre_define_display import cypher


def test_run_cypher_zips_columns_and_rows_into_dicts():
    """run_cypher maps Neo4j (rows, columns) into a list of dicts."""
    rows = [["Study_000001", "DEV0"], ["Study_000002", None]]
    columns = ["uid", "acronym"]

    with patch.object(cypher, "_cypher_query", return_value=(rows, columns)):
        result = cypher.run_cypher("MATCH (n) RETURN n", {"x": 1})

    assert result == [
        {"uid": "Study_000001", "acronym": "DEV0"},
        {"uid": "Study_000002", "acronym": None},
    ]


def test_run_cypher_defaults_params_to_empty_dict():
    """Calling without params passes an empty dict to the driver."""
    with patch.object(cypher, "_cypher_query", return_value=([], [])) as m:
        cypher.run_cypher("MATCH (n) RETURN n")

    m.assert_called_once_with("MATCH (n) RETURN n", {})
