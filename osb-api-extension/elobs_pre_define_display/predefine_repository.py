# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Katja Glass Consulting

"""Cypher-backed reads for the two study/standard-derived Pre-Define panels.

Adapted from the OSB NeoDash "Pre-Define" report (panels 4 & 5). The study match
is keyed on StudyRoot.uid and is version-aware, mirroring how OSB selects a specific
StudyValue (LATEST vs HAS_VERSION {version}).

The Cypher in this module is derived from the OpenStudyBuilder NeoDash "Pre-Define"
report (neo4j-mdr-db/neodash/neodash_reports/pre_define.json),
Copyright (C) 2022 Novo Nordisk A/S, Danish company registration no. 24256790,
licensed under the MIT License. See NOTICE.md in the project root for the full
upstream copyright notice.
"""
from __future__ import annotations
from typing import Any

try:
    from .cypher import run_cypher  # package import (tests)
except ImportError:
    from cypher import run_cypher  # top-level import (OSB extensions loader)


def _study_match(version: str | None) -> str:
    """Return the study-selection MATCH fragment binding `n2` (StudyValue).

    Keyed on StudyRoot.uid (the frontend passes uid), version-aware: LATEST when no
    version is given; otherwise the specific HAS_VERSION value. This replaces the
    NeoDash `()-[:LATEST]->(n2:StudyValue {study_number: $neodash_studyid})` line.
    """
    if version:
        return (
            "MATCH (sr:StudyRoot {uid:$uid})-[hv:HAS_VERSION {version:$version}]->(n2:StudyValue)"
        )
    return "MATCH (sr:StudyRoot {uid:$uid})-[:LATEST]->(n2:StudyValue)"


# Panel 4 — datasets. Verbatim from the corrected NeoDash query
# (.support/cypher_queries.md), with two edits only: the study-selection line is
# replaced by __STUDY_MATCH__ (version-aware, keyed on uid) and $neodash_sponsor_model
# -> $sponsor_model. The activity-item -> DOMAIN -> dataset block stays commented out
# (it used an invalid inline relationship property referencing a variable).
_DATASETS_QUERY = """
// Study selection with applicable Visits and Study Activities and Grouping New Version
__STUDY_MATCH__-[r2:HAS_STUDY_VISIT]->(n3:StudyVisit)-[r3:STUDY_VISIT_HAS_SCHEDULE]->(n4:StudyActivitySchedule)<-[r4:STUDY_ACTIVITY_HAS_SCHEDULE]-(n5:StudyActivity)
// Connection between Study Activities to Library Activities and back to the Study Visits
WITH DISTINCT n5
MATCH (n5)-[r9:HAS_SELECTED_ACTIVITY]->(n10:ActivityValue)-[r10:HAS_GROUPING]->(n11:ActivityGrouping)<-[r11:HAS_ACTIVITY]-(n12:ActivityInstanceValue)<-[r12:HAS_SELECTED_ACTIVITY_INSTANCE]-(n13:StudyActivityInstance)
WITH DISTINCT n12
// Looking at the SDTMIG and the connected MasterModel
MATCH (n27:DataModelIGValue)<-[r28:EXTENDS_VERSION]-(n28:SponsorModelValue)
WHERE n28.name=$sponsor_model
// Display the Domain connected to the ActivityInstance
//OPTIONAL MATCH (n12)-[r29:CONTAINS_ACTIVITY_ITEM]->(n29:ActivityItem)<-[r30:HAS_ACTIVITY_ITEM]-(n30:ActivityItemClassRoot)-[r31:MAPS_VARIABLE_CLASS]->(n31:VariableClass {uid:'DOMAIN'})-[r32:HAS_INSTANCE]->(n32:VariableClassInstance)<-[r33:IMPLEMENTS_VARIABLE{version_number:n27.version_number}]-(n33:DatasetVariableInstance)<-[r34:HAS_DATASET_VARIABLE {version_number:n27.version_number}]-(n34:DatasetInstance)<-[r35:HAS_INSTANCE]-(n35:Dataset) ,
//               (n29)-[r36:HAS_CT_TERM]->(n36:CTTermRoot)-[r37:HAS_ATTRIBUTES_ROOT]->(n37:CTTermAttributesRoot)-[r38:LATEST]->(n38:CTTermAttributesValue)
//WHERE n35.uid = n38.code_submission_value
//WITH DISTINCT n34, n35
MATCH (n35)-[r57:HAS_INSTANCE]->(n48:SponsorModelDatasetInstance)
MATCH (n34)-[r58:IMPLEMENTS_DATASET_CLASS]->(n54:DatasetClassInstance)
RETURN DISTINCT n35.uid AS Dataset, n48.label AS Description, n54.label AS Class, n48.structure AS Structure, "Tabulation" AS Purpose, "To be Specify" AS Keys, n34.description AS Documentation, TOLOWER(n35.uid)||".xpt" AS Location
"""


# Panel 5 — variables of a dataset as defined by the sponsor model. Independent of
# the study and therefore of the study version.
_VARIABLES_QUERY = """
MATCH (sm:SponsorModelValue)-[:HAS_DATASET]->(smd:SponsorModelDatasetInstance)<-[:HAS_INSTANCE]-(ds:Dataset)
WHERE sm.name=$sponsor_model AND ds.uid=$dataset
MATCH (smd)-[hdv:HAS_DATASET_VARIABLE]->(smv:SponsorModelDatasetVariableInstance)<-[:HAS_INSTANCE]-(dv:DatasetVariable)
OPTIONAL MATCH (dv)<-[:HAS_KEY]-(smd)
RETURN DISTINCT
  dv.uid AS Variable,
  smv.is_basic_std AS Cdisc,
  smv.label AS Label,
  (smv.xml_datatype+" ["+smv.variable_type+"]") AS Type,
  smv.length AS Length,
  smv.display_format AS DisplayFormat,
  smv.xml_codelist AS Codelist,
  smv.term AS Term,
  smv.core AS Core,
  smv.origin AS Origin,
  smv.role AS Role,
  smv.ig_comment AS Comment,
  hdv.ordinal AS Order
ORDER BY toInteger(Order)
"""


def get_datasets(uid: str, sponsor_model: str, version: str | None = None) -> list[dict[str, Any]]:
    """Datasets (domains) used by the study, for the given sponsor model and version."""
    query = _DATASETS_QUERY.replace("__STUDY_MATCH__", _study_match(version))
    params: dict[str, Any] = {"uid": uid, "sponsor_model": sponsor_model}
    if version:
        params["version"] = version
    return run_cypher(query, params)


def get_variables(dataset: str, sponsor_model: str) -> list[dict[str, Any]]:
    """Variables of a dataset as defined by the sponsor model."""
    params = {"sponsor_model": sponsor_model, "dataset": dataset}
    return run_cypher(_VARIABLES_QUERY, params)
