# elobs-pre-define-display — OSB Frontend Extension

A Vue 3 extension for [OpenStudyBuilder](https://openstudybuilder.com) that adds an
**ELOBS Pre-Define Viewer** page under Studies. The page reads data from the
[OSB API extension](../osb-api-extension/README.md) and renders it read-only.

Requires the OSB API extension to be installed and running on port 8009.

## Prerequisites

- OpenStudyBuilder frontend (studybuilder)
- OSB API extension installed and running on port 8009

## Installation

Copy the `elobs-pre-define-display/` folder into the StudyBuilder extensions directory:

```
studybuilder/src/extensions/elobs-pre-define-display/
```

The extension is loaded automatically when the StudyBuilder dev server starts or the
application is built. The page appears in the **Studies** sidebar menu.

## Development

Start the StudyBuilder development server from the `studybuilder/` directory:

```bash
yarn dev
```

The extension will be available at:

```
http://localhost:5173/studies/elobs-pre-define-display
```

Run code quality checks:

```bash
yarn format
yarn lint
```

---

## License

MIT — Copyright (c) 2026 Katja Glass Consulting.
See [LICENSE](https://github.com/KatjaGlassConsulting/elobs-pre-define-display/blob/main/LICENSE) and [NOTICE.md](https://github.com/KatjaGlassConsulting/elobs-pre-define-display/blob/main/NOTICE.md).
