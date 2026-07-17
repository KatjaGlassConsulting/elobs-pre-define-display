# ELOBS Pre-Define Viewer — Design

**Date:** 2026-07-15
**Status:** Approved (structure), pending implementation planning

## Purpose

An OpenStudyBuilder (OSB) extension that provides a **read-only viewer** for
predefined display data that already exists in OpenStudyBuilder. The extension
adds a page inside StudyBuilder (under *Studies*) where a user selects a study
and views its predefined display information.

It is modelled on the existing `elobs-word-updater` extension
but is deliberately simpler: **no reusable `core` Python package, no file upload,
no document generation, no downloads.** It reads from OSB and renders.

## Pre-Define feature (concrete scope)

The viewer reproduces the OSB **NeoDash "Pre-Define" report**
(`neo4j-mdr-db/neodash/neodash_reports/pre_define.json`), panels 1–5. The
"Codelist/Terms" panel (panel 6) is explicitly out of scope.

Report flow: **study → version → standard → dataset → variables**.

### Data-access strategy (hybrid, all in-process — no HTTP)

| Panel | Data | Mechanism |
|---|---|---|
| 1 Study list | studies | **native OSB** `/studies/list` (frontend `repository`) |
| — Versions | study versions | **native OSB** `/studies/{uid}/snapshot-history` |
| 2 Study metadata | name / description / protocol / version | **native OSB** `/studies/{uid}?study_value_version=` |
| 3 Standards | sponsor models + extended IG | **extension** — in-process `SponsorModelService.get_all_items(page_size=0)` joined by name with `DataModelIGService.get_all_items()` for IG effective_date + version |
| 4 Datasets | domains used by the study's activities | **extension** — Cypher via `neomodel db.cypher_query`, version-aware |
| 5 Variables | dataset variables from the sponsor model | **extension** — Cypher via `neomodel db.cypher_query` |

Panels 1–2 reuse native OSB endpoints from the frontend (the word-updater pattern),
so the extension is not re-implementing study reads. The extension owns only
standards + datasets + variables.

Panel 5 (variables) is driven by the **sponsor model + dataset**, not the study, so
study-version has no effect on it — inherent to the graph, not a shortcut.

### Version-awareness

Study selection is keyed by `StudyRoot.uid` + `study_value_version` (like
word-updater). The two study-dependent Cypher queries (panels 2-equivalent metadata
is native; **panel 4 datasets** is the Cypher one) build the study match dynamically:

```cypher
-- latest:
MATCH (sr:StudyRoot {uid:$uid})-[:LATEST]->(sv:StudyValue)
-- specific version:
MATCH (sr:StudyRoot {uid:$uid})-[hv:HAS_VERSION {version:$version}]->(sv:StudyValue)
```

`HAS_VERSION` carries `version` (string), `status` (DRAFT/RELEASED/LOCKED),
`start_date`. Keying on `uid` avoids any `uid`↔`study_number` mapping.

### Extension endpoints

| Endpoint | Returns |
|---|---|
| `GET /standards` | `[{sponsor_model, cdisc_ig, effective_date, version}]` |
| `GET /studies/{uid}/datasets?sponsor_model=&version=` | `[{dataset, description, class, structure, purpose, keys, documentation, location}]` |
| `GET /datasets/{dataset}/variables?sponsor_model=` | `[{variable, cdisc, label, type, length, display_format, codelist, term, core, origin, role, comment, order}]` |

### Modules (API extension)

- `osb_direct_client.py` — in-process service calls (`SponsorModelService`,
  `DataModelIGService`) with the `_system_user_context()` helper.
- `cypher.py` — `run_cypher(query, params) -> list[dict]` over `neomodel db.cypher_query`.
- `predefine_repository.py` — the two version-aware Cypher builders (datasets, variables).
- `models.py` — response models.
- `elobs_pre_define_display_main.py` — router; every sibling import uses the
  top-level fallback (see loader-contract section).

### UI (single view)

Study autocomplete + version dropdown → metadata card → standard autocomplete →
datasets table (click a row to select a domain) → variables table. Study/standard
are autocompletes; datasets are a clickable table.

## Scope

**In scope**
- A thin FastAPI extension exposing **`GET`** endpoints that return JSON, reading
  data from OSB service classes in-process.
- A Vue 3 frontend extension that injects a viewer page under *Studies*.

**Out of scope**
- Any pip-installable `core` package (the reference project had one; this does not).
- File upload / parsing.
- Document generation or file downloads.
- Write operations against OSB (viewer is strictly read-only).

## Reference architecture (`elobs-word-updater`)

The reference project has three parts:

1. **`core/`** — a standalone pip-installable package (`elobs_word_updater`) holding
   all business logic: OSB API client, document manipulation, CLI, tests.
2. **`osb-api-extension/`** — a thin FastAPI router (`elobs_word_updater_ext`) that OSB
   loads as an extension. It calls OSB service classes in-process via `OsbDirectClient`
   and delegates heavy lifting to `core/`.
3. **`osb-frontend-extension/`** — a Vue 3 extension that injects a page into
   StudyBuilder's *Studies* section (view + router + store + locales + api client).

This design **drops part 1** and reshapes parts 2 and 3 for a read-only viewer.

## Target structure

```
elobs-pre-define-display/
├── README.md
├── osb-api-extension/
│   ├── README.md
│   └── elobs_pre_define_display/
│       ├── __init__.py
│       ├── elobs_pre_define_display_main.py   # FastAPI APIRouter — GET endpoints
│       ├── osb_direct_client.py               # calls OSB service classes in-process
│       ├── models.py                          # pydantic response models
│       └── tests/
│           ├── __init__.py
│           └── test_extension.py
└── osb-frontend-extension/
    └── elobs-pre-define-display/
        ├── api/extensions.js                  # thin repository wrapper (GET → JSON)
        ├── router/index.js                    # adds route under Studies
        ├── stores/app.js                      # sidebar menu item
        ├── locales/en/
        │   ├── index.js
        │   └── app.json                       # i18n strings
        └── views/ElobsPreDefineDisplayView.vue  # the viewer page
```

## Naming conventions

| Item | Value | Rationale |
|---|---|---|
| Python package folder | `elobs_pre_define_display` | No `_ext` suffix needed — there is no `core` package to collide with. |
| Main module | `elobs_pre_define_display_main.py` | Follows the reference `<package>_main.py` convention (see Open Questions). |
| Mounted route prefix | `/elobs-pre-define-display` | OSB loader derives the prefix from the folder name. Drops the `-ext` the reference carried. |
| Frontend extension folder | `elobs-pre-define-display` | Matches reference kebab-case convention. |
| Vue view | `ElobsPreDefineDisplayView.vue` | Matches reference PascalCase view naming. |

## What changes vs. `elobs-word-updater` (and why)

### Dropped entirely
- **`core/`** — the pip-installable package existed to hold heavy, reusable,
  CLI-driven document logic. A read-only viewer has almost no business logic, so
  there is nothing to package. Any small data-access logic lives directly in the
  extension.

### API extension — kept, reshaped
- Endpoints become **`GET`** returning **JSON**, not `POST` returning a `.docx`.
  No `UploadFile` / `Form`, no `tempfile`, no file-download `Response`.
- `osb_direct_client.py` is **retained** — it is the pattern that replaces `core`'s
  API client. It keeps the `_system_user_context()` helper and calls OSB `Service`
  classes in-process, exposing read methods (e.g. `get_studies()`, plus the
  predefined-display read method(s)). Routing stays thin; data-access stays isolated
  here. All `clinical_mdr_api` imports remain deferred to method bodies so the module
  imports cleanly in the isolated test environment.
- `models.py` holds pydantic **response** models (the reference held a request model).

### Frontend extension — same skeleton, simpler view
- Identical file layout (`api / router / stores / locales / views`) and the same
  integration points: route injected under `/studies`, sidebar menu item,
  `STUDY_READ` permission, i18n via `app.json`.
- `extensions.js` performs `GET` with `responseType: 'json'` instead of building
  `FormData` and requesting a blob.
- The view has **no upload / no download** — a study selector plus a display area.

## Components

### API extension

**`elobs_pre_define_display_main.py`** — defines an `APIRouter` with read-only
endpoints. Each endpoint instantiates `OsbDirectClient`, calls a read method, and
returns a pydantic response model (JSON). No file handling.

**`osb_direct_client.py`** — `OsbDirectClient` class with async read methods that
call OSB service classes inside `_system_user_context()`. Carries over from the
reference:
- `_system_user_context()` — sets a dummy system user in the starlette request
  context when auth is disabled, so OSB service `__init__` does not fail.
- `get_studies(page_size=0)` — for the study selector.
- Predefined-display read method(s) — exact OSB service class(es) to be confirmed
  during implementation (depends on where "predefined display" data lives in OSB).

**`models.py`** — pydantic response models describing the JSON returned by each
endpoint.

**`tests/test_extension.py`** — builds a minimal FastAPI app that mounts the router,
mocks `OsbDirectClient` methods, and asserts endpoints return 200 + expected JSON
shape, plus validation errors (404 for unknown study, etc.). Mirrors the reference
test approach (isolated app, mocked OSB layer, no database). Includes a regression
test that imports `_main` the way the OSB loader does (see below).

### OSB extensions loader contract (CRITICAL)

Confirmed from `clinical-mdr-api/extensions/extensions_api.py` (`load_extensions()`):

1. **Discovery** — the loader iterates every subfolder of `extensions/` and loads
   `<folder>/<folder>_main.py`. The main module **must** be named
   `elobs_pre_define_display_main.py` (i.e. `<folder>_main.py`). A plain `main.py`
   is not discovered.

2. **Top-level import, NOT a package** — the loader puts the extension folder on
   `sys.path` and does `importlib.import_module("elobs_pre_define_display_main")`.
   The module therefore has **no parent package**, so plain relative imports
   (`from .models import ...`) raise `ImportError: attempted relative import with
   no known parent package`.

   **Rule:** every sibling-module import in `_main.py` (and any module it pulls in)
   MUST use the dual-import fallback so it works both under pytest (package context)
   and under the OSB loader (top-level context):

   ```python
   try:
       from .models import StudySummary          # package import (tests)
   except ImportError:
       from models import StudySummary           # top-level import (OSB loader)
   ```

3. **Fail-fast, blast radius = whole API** — `load_extensions()` re-raises on any
   extension import error. A single broken extension takes down the entire
   extensions API, surfacing as a **502 on every path, including `/docs`**. Check
   the extensions-api container logs for the traceback when this happens.

4. **Route prefix** — derived from the folder name with `_` replaced by `-`. So
   folder `elobs_pre_define_display` mounts at `/elobs-pre-define-display`. The
   frontend `extensions.js` must use that exact prefix.

### Frontend extension

**`views/ElobsPreDefineDisplayView.vue`** — the viewer page. Contains a study
selector (reusing the reference's ID/acronym autocomplete pattern against
`/studies/list`) and a display area for the predefined-display data. The exact
rendering (data table / tree / detail sections) is deferred; the view is structured
to accommodate any of them.

**`api/extensions.js`** — thin wrapper over `repositoryExtensions` issuing `GET`
requests to the `/elobs-pre-define-display` endpoints, returning parsed JSON.

**`router/index.js`** — `addExtensionRoutes()` pushes the viewer route into the
`/studies` children, with `authRequired`, `section: 'Studies'`, and
`requiredPermission: roles.STUDY_READ`.

**`stores/app.js`** — adds the sidebar menu item under *Studies*.

**`locales/en/app.json`** + **`index.js`** — i18n strings (title, description,
study selector labels, empty/error states).

## Data flow

```
StudyBuilder UI (ElobsPreDefineDisplayView.vue)
  → api/extensions.js  (GET /elobs-pre-define-display/...)
    → OSB extensions API  (elobs_pre_define_display_main.router)
      → OsbDirectClient  (in-process call to OSB Service classes)
        → OSB domain / database
  ← JSON response ← rendered read-only in the view
```

No HTTP calls leave the OSB process for data; the extension calls OSB service
classes directly, exactly like the reference `OsbDirectClient`.

## Error handling

- **Unknown / missing study** → endpoint returns `404`; the view shows an empty/error
  state.
- **OSB service error** → endpoint surfaces a `500` with a safe message; the view
  shows a non-blocking error notification (as the reference uses `notificationHub`).
- **Auth** → handled by OSB's existing middleware; no separate auth config. The
  `_system_user_context()` fallback covers the auth-disabled dev case.
- **Study list load failure** (frontend) → best-effort, matching the reference: the
  selector simply shows no options rather than crashing the page.

## Testing

- **API:** isolated FastAPI `TestClient` app mounting the router, with
  `OsbDirectClient` methods mocked (`AsyncMock`). Assert status codes and JSON shape.
  No database, no `clinical_mdr_api` install required (imports are deferred).
- **Frontend:** manual verification in the StudyBuilder dev server (`yarn dev`),
  plus `yarn format` / `yarn lint`, consistent with the reference project.

## Resolved (confirmed against OSB source)

1. **Main-module naming** — RESOLVED. The loader requires `<folder>_main.py`, so
   `elobs_pre_define_display_main.py`. A plain `main.py` is not discovered. See the
   *OSB extensions loader contract* section.
2. **Route-prefix derivation** — RESOLVED. The loader derives the prefix from the
   folder name, replacing `_` with `-` → `/elobs-pre-define-display`.

## Open questions (to resolve during implementation)

1. **Predefined-display data source** — identify the exact OSB service class(es) and
   method(s) that expose the "predefined display" data to read. (The `get_studies`
   summary read is implemented and assumes `current_metadata.identification_metadata`
   fields `study_id` / `study_acronym` — verify against live OSB.)
2. **UI rendering** — decide table vs. tree vs. detail-sections once the data shape
   from (1) is known.
```