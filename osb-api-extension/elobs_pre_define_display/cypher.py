# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Katja Glass Consulting

from __future__ import annotations
from typing import Any


def _cypher_query(query: str, params: dict[str, Any]) -> tuple[list[list[Any]], list[str]]:
    """Thin seam over neomodel's driver so tests can patch it without a live Neo4j.

    Deferred import: neomodel is only available inside the OSB runtime, not in the
    isolated unit-test environment.
    """
    from neomodel import db

    return db.cypher_query(query, params)


def run_cypher(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a Cypher query in-process and return rows as a list of column->value dicts."""
    rows, columns = _cypher_query(query, params or {})
    return [dict(zip(columns, row)) for row in rows]
