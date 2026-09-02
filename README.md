<div align="center">

# NER Annotation Workbench Prototype

### A Web Prototype for Named Entity Recognition Annotation

A Vue 3 and Django project scaffold for exploring a web-based NER data annotation workflow.

[![Vue](https://img.shields.io/badge/Vue-3.5-42b883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.0-646cff?logo=vite&logoColor=white)](https://vite.dev/)
[![Django](https://img.shields.io/badge/Django-4.2-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-Planned-a30000)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Archived-lightgrey.svg)](#project-status)

**English** | [简体中文](README.zh-CN.md)

</div>

> [!IMPORTANT]
> This is a practice project for learning front-end/back-end separation and NER workflow design. It remains at the scaffold stage, is no longer maintained, and is not suitable for production use.

## Overview

NER Annotation Workbench Prototype was created to explore the structure of a web-based data annotation workbench for named entity recognition. Its intended workflow covered raw-text import, entity annotation, dataset overview, and annotation export.

The repository currently contains an initialized Vue front end, a Django back end, and placeholder business modules. It does not include a complete annotation interface, data models, or REST APIs. The code is preserved as a learning record and project-structure reference.

## Intended Workflow

```text
Text Import → Named Entity Annotation → Dataset Overview → Annotation Export
```

| Module | Intended responsibility | Current status |
| --- | --- | :---: |
| Data import | Import and parse text for annotation | Django app scaffold only |
| Data annotation | Select text spans and assign entity labels | Django app scaffold only |
| Data overview | Display dataset, label, and progress statistics | Django app scaffold only |
| Data export | Export structured annotation results | Django app scaffold only |
| Web front end | Provide annotation and management interfaces | Default Vue page |
| REST API | Connect front-end and back-end functionality | Not implemented |

## Technology Stack

| Layer | Technology |
| --- | --- |
| Front end | Vue 3, Vite |
| Back end | Python, Django, Django REST Framework |
| Database | SQLite (default Django configuration) |
| Architecture | Separated front end and back end |

## Repository Structure

```text
ner-annotation-workbench-prototype/
├── backend/
│   ├── config/                 # Django project configuration
│   ├── data_import/            # Data import module (scaffold)
│   ├── data_annotation/        # Data annotation module (scaffold)
│   ├── data_overview/          # Dataset overview module (scaffold)
│   ├── data_export/            # Data export module (scaffold)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.vue             # Default Vue example page
│   │   └── main.js             # Front-end entry point
│   ├── package.json
│   └── vite.config.js
├── docs/                       # Project documentation
├── LICENSE
├── README.md                   # English documentation
└── README.zh-CN.md             # Simplified Chinese documentation
```

## Quick Start

These steps run the current scaffold only; they do not provide a complete NER annotation application.

### Requirements

- Python 3.9 or later
- Node.js 20.19+ or 22.12+
- npm

### Back End

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The server starts at `http://127.0.0.1:8000/` by default. Only the Django Admin route is configured; no business API is available.

### Front End

```bash
cd frontend
npm install
npm run dev
```

Open the local address shown by Vite. The current interface is the default Vue starter page.

### Production Build

```bash
cd frontend
npm run build
```

## Known Limitations

- No data models for documents, entity labels, or annotations.
- No import, annotation, statistics, or export logic.
- No serializers, REST APIs, or business routes.
- No interactive NER annotation interface.
- No NER model integration, training, inference, or automatic pre-annotation.
- No complete automated test or deployment setup.
- The Django configuration is for development and is not production-ready.

## Project Status

**Archived**

Development of this personal practice project has ended. No further features or maintenance are planned, and the repository reflects its actual implementation state when work stopped.

## Learning Scope

- Initializing Vue and Django applications.
- Organizing a Django project into multiple business apps.
- Decomposing an NER annotation workflow into modules.
- Structuring a separated front-end/back-end repository.

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Preserved as a learning record.

</div>
