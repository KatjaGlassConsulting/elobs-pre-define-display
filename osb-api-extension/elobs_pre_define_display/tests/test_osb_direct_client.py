from __future__ import annotations
from types import SimpleNamespace

from elobs_pre_define_display.osb_direct_client import _build_standards


def test_build_standards_joins_ig_metadata_by_name():
    """Each sponsor model is enriched with its extended IG's effective date + version."""
    sponsor_models = [
        SimpleNamespace(name="sm_3.2_NN15", extended_implementation_guide="sdtmig 3.2"),
    ]
    igs = [
        SimpleNamespace(name="sdtmig 3.2", start_date="2020-01-01", version_number="3.2"),
    ]

    result = _build_standards(sponsor_models, igs)

    assert result == [
        {
            "sponsor_model": "sm_3.2_NN15",
            "cdisc_ig": "sdtmig 3.2",
            "effective_date": "2020-01-01",
            "version": "3.2",
        }
    ]


def test_build_standards_tolerates_missing_ig():
    """A sponsor model whose IG isn't found yields null IG metadata, not an error."""
    sponsor_models = [
        SimpleNamespace(name="sm_x", extended_implementation_guide="unknown ig"),
    ]

    result = _build_standards(sponsor_models, igs=[])

    assert result == [
        {
            "sponsor_model": "sm_x",
            "cdisc_ig": "unknown ig",
            "effective_date": None,
            "version": None,
        }
    ]
