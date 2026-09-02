# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Katja Glass Consulting

"""In-process reads from OSB service classes (no HTTP).

Currently backs the Standards panel (sponsor models + the CDISC IG they extend).
All clinical_mdr_api imports are deferred to method bodies so this module imports
cleanly in the isolated unit-test environment.
"""
from contextlib import contextmanager
from typing import Any


@contextmanager
def _system_user_context():
    """Set a dummy system user in the starlette request context if auth is not set.

    OSB service classes call user() in __init__ to record the author. When auth is
    disabled, context["auth"] is absent and user() returns None, causing an
    AttributeError. This sets a minimal system user for the duration of the call.
    """
    from starlette_context import context
    from common.auth.models import User

    if context.get("auth") is not None:
        yield
        return

    class _SystemAuth:
        user = User(sub="system", azp="system", oid="system",
                    name="System", username="system", email="")

    context["auth"] = _SystemAuth()
    try:
        yield
    finally:
        try:
            del context["auth"]
        except Exception:
            pass


def _build_standards(sponsor_models: list[Any], igs: list[Any]) -> list[dict[str, Any]]:
    """Join each sponsor model with its extended IG's effective date + version.

    Pure mapping (no service calls) so it is unit-testable without OSB. IG lookup is
    by name; a missing IG yields null metadata rather than raising.
    """
    ig_by_name = {ig.name: ig for ig in igs}
    result = []
    for sm in sponsor_models:
        ig = ig_by_name.get(sm.extended_implementation_guide)
        result.append(
            {
                "sponsor_model": sm.name,
                "cdisc_ig": sm.extended_implementation_guide,
                "effective_date": getattr(ig, "start_date", None) if ig else None,
                "version": getattr(ig, "version_number", None) if ig else None,
            }
        )
    return result


class OsbDirectClient:
    """Calls OSB service classes directly instead of making HTTP requests."""

    def get_standards(self) -> list[dict[str, Any]]:
        """Return sponsor models enriched with their extended IG metadata."""
        from clinical_mdr_api.services.standard_data_models.sponsor_model import (
            SponsorModelService,
        )
        from clinical_mdr_api.services.standard_data_models.data_model_ig import (
            DataModelIGService,
        )

        with _system_user_context():
            sponsor_models = SponsorModelService().get_all_items(page_size=0).items
            igs = DataModelIGService().get_all_items(page_size=0).items
        return _build_standards(sponsor_models, igs)
