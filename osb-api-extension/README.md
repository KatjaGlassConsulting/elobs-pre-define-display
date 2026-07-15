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

### `GET /elobs-pre-define-display/hello`

Dummy walking-skeleton endpoint.

**Response** — `application/json`:

```json
{ "message": "hallo world" }
```

## Running Extension Tests

This repo's tests are self-contained (they mount the router on a minimal FastAPI app
and require only `fastapi` + `pytest`):

```bash
cd osb-api-extension
python -m pytest elobs_pre_define_display
```
