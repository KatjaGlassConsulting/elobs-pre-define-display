# elobs-pre-define-display — OSB API Extension

A backend extension for [OpenStudyBuilder](https://openstudybuilder.com) that exposes
read-only endpoints for the ELOBS Pre-Define Viewer. Authentication is handled by
OSB's existing middleware — no separate auth configuration required.

The extension calls OSB's internal service layer directly (in-process), so no HTTP
requests are made to the OSB API and no `OSB_API_URL` environment variable is needed.

There is **no separate `core` package** — this extension is self-contained.

## Prerequisites

- OpenStudyBuilder with the extensions API enabled (running on port 8009 by default)
- Python environment for the extensions API

## Installation

Copy the `elobs_pre_define_display/` folder into OpenStudyBuilder's extensions directory:

```
clinical-mdr-api/extensions/elobs_pre_define_display/
```

Restart the extensions API:

```bash
pipenv run extensions-api-dev
```

The extension is loaded automatically. Endpoints are mounted under:

```
http://localhost:8009/elobs-pre-define-display/
```

## API

The extension reproduces panels 3–5 of the OSB NeoDash "Pre-Define" report. Panels
1–2 (study list, versions, metadata) are served by native OSB endpoints and consumed
directly by the frontend.

### `GET /elobs-pre-define-display/standards`

Sponsor models joined with the CDISC IG they extend (panel 3). In-process via
`SponsorModelService` + `DataModelIGService`.

Returns `[{ sponsor_model, cdisc_ig, effective_date, version }]`.

### `GET /elobs-pre-define-display/studies/{uid}/datasets?sponsor_model=&version=`

Datasets (domains) used by the study's activities for the given sponsor model
(panel 4). Version-aware: omit `version` for latest. Cypher via `neomodel`.

Returns `[{ Dataset, Description, Class, Structure, Purpose, Keys, Documentation, Location }]`.

### `GET /elobs-pre-define-display/datasets/{dataset}/variables?sponsor_model=`

Variables of a dataset as defined by the sponsor model (panel 5). Cypher via
`neomodel`. Study-version independent.

Returns `[{ Variable, Cdisc, Label, Type, Length, DisplayFormat, Codelist, Term, Core, Origin, Role, Comment, Order }]`.

## Running Extension Tests

This repo's tests are self-contained (they mount the router on a minimal FastAPI app
and require only `fastapi` + `pytest`):

```bash
cd osb-api-extension
python -m pytest elobs_pre_define_display
```
