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


def _summarize_study(study: dict[str, Any]) -> dict[str, Any]:
    """Reduce a full OSB study dict to the fields the viewer displays.

    Reads defensively so a missing metadata branch yields None rather than raising.
    """
    identification = (
        (study.get("current_metadata") or {}).get("identification_metadata") or {}
    )
    return {
        "uid": study.get("uid"),
        "study_id": identification.get("study_id"),
        "acronym": identification.get("study_acronym"),
    }


class OsbDirectClient:
    """Calls OSB service classes directly instead of making HTTP requests.

    All clinical_mdr_api imports are deferred to method bodies so this module can be
    imported in environments where clinical_mdr_api is not installed (e.g. the
    isolated unit tests in this repo).
    """

    async def get_studies(self, page_size: int = 0) -> list[dict[str, Any]]:
        """Return a normalized summary (uid, study_id, acronym) for every study."""
        from clinical_mdr_api.services.studies.study import StudyService
        with _system_user_context():
            result = StudyService().get_all(page_size=page_size)
        return [_summarize_study(item.model_dump()) for item in result.items]
