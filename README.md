# elobs-pre-define-display

OpenStudyBuilder extension that provides a read-only viewer for _[TODO: describe the predefined display data — what it is and why teams need to view it]_ directly from live study data.

ELOBS is a new **E**xtension **L**ine for **O**penStudy**B**uilder **S**olution! This extension _[TODO: one-sentence summary of what the viewer shows and the problem it solves]_ from [OpenStudyBuilder](https://openstudybuilder.com).

_[TODO: 1–2 paragraphs of context. What predefined display data is maintained in OpenStudyBuilder (OSB), how this viewer surfaces it, and who uses it.]_

**For end users:** view _[TODO: the predefined display]_ from within OpenStudyBuilder via the integrated UI extension.

<!-- ![Extension Demonstration](./img/elobs_pre_define_display_demo.gif) -->
_[TODO: add a demo GIF/screenshot under ./img/ and link it here]_

---

## Repository structure

This is a monorepo containing two independent but related parts. Unlike some other
ELOBS extensions, there is **no standalone `core` package** — the viewer is read-only
and self-contained, so all logic lives inside the two extensions.

```
elobs-pre-define-display/
├── osb-api-extension/       # OpenStudyBuilder backend extension (FastAPI, read-only)
└── osb-frontend-extension/  # OpenStudyBuilder frontend extension (Vue 3)
```

### `osb-api-extension/` — OSB backend extension

A FastAPI extension that plugs into OpenStudyBuilder's extensions API. It exposes
read-only endpoints that call OSB's internal service layer in-process (no HTTP round
trip, no `OSB_API_URL`) and return JSON.

→ [osb-api-extension/README.md](osb-api-extension/README.md)

### `osb-frontend-extension/` — OSB frontend extension

A Vue 3 extension for the OpenStudyBuilder UI. Adds an **ELOBS Pre-Define Viewer**
page under Studies that reads from the API extension and renders the data read-only.

→ [osb-frontend-extension/README.md](osb-frontend-extension/README.md)

---

## How the parts relate

The frontend extension calls the API extension, which reads directly from OSB's
service layer. No logic is duplicated and no data leaves the OSB process.

```
osb-frontend-extension   →   osb-api-extension   →   OpenStudyBuilder services
(Vue 3 UI)                   (FastAPI endpoints)      (in-process, read-only)
```

---

## Endpoints

The extension reproduces panels 3–5 of the OSB NeoDash "Pre-Define" report. Panels
1–2 (study list, versions, metadata) use native OSB endpoints from the frontend.

| Method & path | Purpose |
|---|---|
| `GET /elobs-pre-define-display/standards` | Sponsor models + extended CDISC IG (panel 3). |
| `GET /elobs-pre-define-display/studies/{uid}/datasets?sponsor_model=&version=` | Datasets/domains used by the study, version-aware (panel 4). |
| `GET /elobs-pre-define-display/datasets/{dataset}/variables?sponsor_model=` | Dataset variables from the sponsor model (panel 5). |

---

## Local Docker setup (quick start)

To integrate both extensions into a locally running OpenStudyBuilder Docker Compose
stack built from source:

**1. Copy the API and GUI extension into the OSB source:**

```
osb-api-extension/elobs_pre_define_display/   →  clinical-mdr-api/extensions/elobs_pre_define_display/
osb-frontend-extension/elobs-pre-define-display/  →  studybuilder/src/extensions/elobs-pre-define-display/
```

> No `compose.override.yaml` is needed — there is no external package to install into
> the container. The extension folder is self-contained.

**2. Restart the containers:**

```bash
docker compose up -d --build --force-recreate --no-deps extensionsapi
docker compose up -d --build --force-recreate --no-deps frontend
```

The frontend view is available at `http://localhost:5005/studies/elobs-pre-define-display`.

The backend Swagger Extension API is available at `http://localhost:5005/extensions-api/docs#/ElobsPreDefineDisplay`.

---

## Requirements

- Python 3.11+
- A running OpenStudyBuilder instance (for live data)
- For the OSB extensions: OpenStudyBuilder with the extensions API enabled

---

## Acknowledgements

_[TODO: acknowledgements — upstream inspiration, licensing notices, etc.]_

This project was developed with [Claude](https://claude.ai) by Anthropic.

---

## License

_[TODO: choose a license and add a LICENSE file. Suggested: MIT License - Copyright (c) 2026 Katja Glass Consulting.]_
