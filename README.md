# MediGraph 🩺⚡

> **Privacy-First Clinical Intake, Multi-Modal Document Intelligence & Longitudinal Patient Timeline Orchestrator**

MediGraph is an enterprise-grade clinical intake and medical document processing platform. It ingests bilingual patient voices, clinical questionnaires, prescriptions, and diagnostic lab reports, transforms unstructured health data into a provenance-backed longitudinal clinical timeline, runs deterministic safety checks, and exports validated HL7 FHIR R4 bundles compliant with the Ayushman Bharat Digital Mission (ABDM).

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Prerequisites](#-prerequisites)
- [Quickstart & Installation](#-quickstart--installation)
  - [1. Clone & Environment Setup](#1-clone--environment-setup)
  - [2. Backend Setup (`apps/api`)](#2-backend-setup-appsapi)
  - [3. Frontend Setup (`apps/web`)](#3-frontend-setup-appsweb)
  - [4. Docker Services (Optional)](#4-docker-services-optional)
  - [5. Local AI Models (Ollama)](#5-local-ai-models-ollama)
- [Default Login Credentials](#-default-login-credentials)
- [LangGraph Orchestration Pipeline](#-langgraph-orchestration-pipeline)
- [API Reference](#-api-reference)
- [Evaluation & Quality Metrics](#-evaluation--quality-metrics)
- [Clinical Safety & Privacy Principles](#-clinical-safety--privacy-principles)
- [Contributing & Development Commands](#-contributing--development-commands)
- [License](#-license)

---

## ✨ Key Features

### 🎙️ Multi-Modal Patient Intake (Voice & Questionnaire)
- **Local Multilingual Speech-to-Text**: Powered by `faster-whisper` (runs fully on CPU/GPU without third-party audio cloud leakage), featuring auto-detection and high accuracy for English, Hindi, and Hinglish.
- **Bilingual Intake Flow**: Patient questionnaires available in both English and Hindi with dynamic symptom-specific branches and voice response capabilities.
- **Explicit Patient Consent & Auditing**: Granular consent recording with verifiable actor and timestamp audit trails.

### 📄 Intelligent Document Processing & OCR
- **Computer Vision Preprocessing**: OpenCV-driven grayscale, denoising (`fastNlMeansDenoising`), and adaptive thresholding to handle low-light or degraded mobile captures.
- **PaddleOCR Engine**: Robust character recognition supporting English and Hindi text in printed reports, laboratory results, and clinical prescriptions.
- **Local LLM OCR Verifier**: Self-correcting OCR pass using local `medgemma:4b` to recover distorted pharmaceutical names, calculate bounding-box confidence scores, and flag suspicious extractions.
- **Smart Drug Resolver**: Clinical pharmacology lookup combining dictionary matching, LRU disk caching, and local LLM reasoning to map local brand names (e.g., *Crocin*, *Betaloc*, *Glycomet*) to generic INN formulations (*Paracetamol*, *Metoprolol*, *Metformin*).

### 🕒 Provenance-Linked Longitudinal Timeline
- **Unified Medical Facts**: Aggregates disparate facts across voice transcripts, intake surveys, and medical records into a single chronological timeline.
- **Zero Hallucination Traceability**: Every clinical event maintains an immutable link back to its raw source document ID, bounding box, or intake excerpt.
- **Non-Destructive Conflict Detection**: Conflicting observations (e.g., conflicting allergy statements or differing dosage records across hospitals) are linked via `conflict_group` IDs side-by-side rather than silently overwritten.

### 🛡️ Deterministic Red-Flag Alert Engine
- **Zero-Hallucination Safety Rules**: Deterministic pattern matching over timeline facts (avoiding stochastic LLM decision-making for critical vitals).
- **Critical Warning Presets**: Immediate detection of possible Acute Coronary Syndrome (ACS), Stroke/TIA indicators, Sepsis risks, and dangerous medication contraindications with clear severity badges (`urgent`, `caution`, `info`).

### 👨‍⚕️ Clinician Review & Draft Generation
- **Clinical Summary Synthesizer**: Generates comprehensive intake and discharge notes, chief complaint chronologies, and active medication matrices.
- **Human-in-the-Loop Safeguards**: AI drafts are strictly marked as unverified until reviewed, edited, and digitally signed off by an authorized clinician.
- **ReportLab PDF Export**: One-click generation of branded, publication-ready clinical summary PDFs.

### 🌐 ABDM & HL7 FHIR R4 Interoperability
- **FHIR R4 Bundle Mapping**: Maps timeline events and patient demographics to standardized ABDM (NRCES NDHM) profiles: `Patient`, `Encounter`, `Condition`, `Observation`, and `MedicationRequest`.
- **HAPI FHIR Validation**: Built-in validation integration using the official HL7 `validator_cli.jar` to ensure schema compliance before EHR export.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph INTAKE["1. Multi-Modal Intake"]
        A1[Patient Voice Audio] -->|faster-whisper| B1[Transcribed Intake]
        A2[Prescription / Lab PDF/IMG] -->|OpenCV + PaddleOCR| B2[Raw OCR Regions]
        A3[Bilingual Questionnaire] --> B3[Structured Answers]
    end

    subgraph ORCHESTRATION["2. LangGraph Clinical Pipeline"]
        B2 --> C1[extract: OCR + AI Verification]
        C1 --> C2{validate: Confidence >= 0.8?}
        C2 -- No / Flagged Meds --> C3[review: Clinician HITL Queue]
        C2 -- Yes --> C4[timeline: Provenance Builder]
        C3 -->|Clinician Sign-off| C4
        B1 --> C4
        B3 --> C4
        C4 --> C5[summarize: Clinical Note Draft]
        C4 --> C6[alerts: Deterministic Safety Rules]
        C5 --> C7[fhir: ABDM R4 Bundle Generation]
        C6 --> C7
        C7 --> C8[HAPI FHIR R4 Validator]
    end

    subgraph CONSUMERS["3. Clinical & Interoperability Layer"]
        C8 --> D1[Clinician Dashboard & PDF Export]
        C8 --> D2[ABDM / EHR Interoperability]
        C8 --> D3[Audit Trail & Security Log]
    end
```

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | [Next.js 14](https://nextjs.org/) (App Router), React 18, TypeScript, Tailwind CSS |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/), Python 3.10+, Pydantic v2, Uvicorn |
| **Pipeline & AI Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph), [Ollama](https://ollama.ai/) (`medgemma:4b`) |
| **Speech Processing** | [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2, small multilingual model) |
| **OCR & Computer Vision** | [PaddleOCR 3.x](https://github.com/PaddlePaddle/PaddleOCR), [OpenCV](https://opencv.org/), [pypdfium2](https://pypi.org/project/pypdfium2/) |
| **Database & Persistence** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/), SQLite (local) / [PostgreSQL 16](https://www.postgresql.org/) (Docker) |
| **Document Generation** | [ReportLab](https://www.reportlab.com/) (Vector PDF Generation) |
| **Interoperability** | HL7 FHIR R4, ABDM Profiles, HAPI FHIR Validator CLI (`validator_cli.jar`) |
| **Security & Auth** | JWT (`python-jose`), Passlib (`bcrypt`), PBAC (Role-Based Access Control) |
| **DevOps & Containers** | Docker Compose (PostgreSQL, Redis 7, MinIO S3 Object Storage), GNU Make |

---

## 📁 Repository Structure

```text
medigraph/
├── apps/
│   ├── api/                         # FastAPI Python Backend
│   │   ├── app/
│   │   │   ├── api/v1/              # Versioned API routes
│   │   │   │   ├── auth.py          # User authentication & token issuance
│   │   │   │   ├── patients.py      # Patient record management & stats
│   │   │   │   ├── intake_sessions.py # Patient questionnaire session flow
│   │   │   │   ├── documents.py     # File upload, OCR execution & verification
│   │   │   │   ├── speech.py        # Voice intake & Faster-Whisper transcription
│   │   │   │   ├── questionnaires.py # Multilingual questions metadata
│   │   │   │   ├── timeline.py      # Chronological timeline query & conflict inspection
│   │   │   │   ├── summary.py       # Clinical summary drafting, review, PDF export
│   │   │   │   ├── ai_review.py     # AI queue & clinician HITL decision endpoints
│   │   │   │   ├── fhir.py          # ABDM FHIR R4 export & validation
│   │   │   │   ├── consents.py      # Consent tracking & compliance audit logs
│   │   │   │   ├── orchestrate.py   # LangGraph execution endpoint
│   │   │   │   └── health.py        # Service health checks
│   │   │   ├── core/                # App config, settings & JWT security
│   │   │   ├── db/                  # SQLAlchemy session setup & Base models
│   │   │   ├── models/              # Database entities (Patient, Document, Fact, Timeline, etc.)
│   │   │   ├── orchestration/       # LangGraph state machine (graph.py, state.py)
│   │   │   ├── services/            # Business logic & AI algorithms
│   │   │   │   ├── alert_rules.py   # Deterministic clinical safety rules
│   │   │   │   ├── clinical_summary_generator.py # Ollama clinical narrative generator
│   │   │   │   ├── document_ai.py   # OpenCV filters & PaddleOCR caller
│   │   │   │   ├── drug_resolver.py # Brand-to-generic drug normalization
│   │   │   │   ├── entity_extractor.py # Regex & deterministic clinical fact extraction
│   │   │   │   ├── fhir_mapper.py   # ABDM FHIR R4 Bundle constructor
│   │   │   │   ├── fhir_validator.py# Subprocess bridge for HL7 validator_cli.jar
│   │   │   │   ├── ocr_verifier.py  # Local LLM OCR correction & confidence evaluator
│   │   │   │   ├── pdf_renderer.py  # ReportLab clinical summary PDF layout
│   │   │   │   ├── speech.py        # Faster-Whisper loader & audio transcriber
│   │   │   │   └── timeline_builder.py # Fact merging & conflict tracking
│   │   │   └── schemas/             # Pydantic request/response schemas
│   │   ├── data/                    # Local cache files & uploaded document samples
│   │   ├── tools/                   # HL7 FHIR validator_cli.jar
│   │   ├── requirements.txt         # Python package dependencies
│   │   └── seed_users.py            # Initial user seeding script
│   │
│   └── web/                         # Next.js 14 Frontend Application
│       ├── src/
│       │   ├── app/
│       │   │   ├── page.tsx         # Modern interactive landing page & feature demos
│       │   │   ├── login/           # Authentication portal
│       │   │   ├── intake/          # Patient intake wizard (Bilingual EN/HI + Voice)
│       │   │   ├── clinician/       # Clinician dashboard, patient directory & AI review queue
│       │   │   │   └── [patientId]/ # Individual patient charts, timeline, documents, summary
│       │   │   └── admin/           # Administrative audit trails & user management
│       │   ├── components/          # Reusable UI widgets, badges, modal dialogs
│       │   └── lib/                 # Client utilities & API fetch wrappers
│       ├── package.json             # Node dependencies & build scripts
│       └── next.config.js           # Next.js reverse-proxy rewrite rules to backend
│
├── data/
│   └── eval/                        # Evaluation ground-truth CSV & performance reports
├── scripts/
│   ├── evaluate.py                  # Extractor precision/recall/F1 benchmarking script
│   └── dump_facts.py                # Database facts inspection utility
├── docker-compose.yml               # PostgreSQL 16, Redis 7, MinIO S3 services
├── Makefile                         # Unified automation commands
├── .env.example                     # Environment template
└── README.md                        # Project documentation
```

---

## 📋 Prerequisites

Before running MediGraph, ensure your system has the following installed:

1. **Python 3.10 or 3.11** (recommended for AI package compatibility).
2. **Node.js 18+ & npm** (for Next.js frontend).
3. **Ollama** ([ollama.ai](https://ollama.ai/)) with `medgemma:4b` installed.
4. **Docker & Docker Compose** (optional, for running PostgreSQL, Redis, and MinIO).
5. **Java Runtime Environment (JRE 17+)** (optional, required only for official HAPI FHIR validation CLI).

---

## 🚀 Quickstart & Installation

### 1. Clone & Environment Setup

Copy the sample environment file in the project root:

```bash
# In the repository root
cp .env.example .env
```

Ensure `.env` matches your local configuration:
```ini
APP_ENV=development
APP_NAME=MediGraph
APP_PORT=8000
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./medigraph.db
JWT_SECRET=your-secure-jwt-secret-here
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=medgemma:4b
```

---

### 2. Backend Setup (`apps/api`)

1. Open a terminal and navigate to `apps/api`:
   ```bash
   cd apps/api
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   > 💡 On first startup, the database tables and default admin/clinician/patient users are created automatically.
   > The API docs are available at **http://localhost:8000/docs**.

---

### 3. Frontend Setup (`apps/web`)

1. Open a second terminal and navigate to `apps/web`:
   ```bash
   cd apps/web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Next.js development server:
   ```bash
   npm run dev
   ```

4. Open **http://localhost:3000** in your web browser.

---

### 4. Docker Services (Optional)

If you prefer using PostgreSQL, Redis, and MinIO rather than local SQLite:

```bash
# Start Docker services
make up
# Or: docker compose up -d
```

Update your `DATABASE_URL` in `.env`:
```ini
DATABASE_URL=postgresql+psycopg://medigraph:medigraph@localhost:5432/medigraph
```

---

### 5. Local AI Models (Ollama)

MediGraph relies on local privacy-preserving LLM inference for OCR verification, clinical drug resolution, and summary drafting:

1. Install and start [Ollama](https://ollama.ai/).
2. Pull the medical Gemma model:
   ```bash
   ollama pull medgemma:4b
   ```
3. Test that the Ollama server is responding:
   ```bash
   curl http://localhost:11434/api/tags
   ```

---

## 👥 Default Login Credentials

MediGraph seeds three default user accounts on first startup:

| Role | Email Address | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin@medigraph.example.com` | `admin123` | Full system access, audit trail, user role management |
| **Clinician** | `clinician@medigraph.example.com` | `clinic123` | Patient charts, AI review queue, timeline editing, PDF sign-off, FHIR export |
| **Patient** | `patient@medigraph.example.com` | `patient123` | Self-intake portal, bilingual questionnaire, consent records |

---

## 🔄 LangGraph Orchestration Pipeline

The clinical pipeline is modeled as a state machine (`apps/api/app/orchestration/graph.py`):

```text
[extract]  ──> OCR + AI verification on prescription / report
    │
    ▼
[validate] ──> Evaluates confidence score & flagged medications
    │
    ├─► (Confidence < 0.8 OR low-conf meds) ──► [review] (Human-In-The-Loop Pause)
    │                                              │
    └─► (Confidence >= 0.8)                        ▼ (Clinician Approval)
    │                                              │
    └──────────────────────────────────────────────┘
    │
    ▼
[timeline] ──> Provenance-linked chronological facts + conflict grouping
    │
    ▼
[summarize]──> Synthesizes evidence-based draft note
    │
    ▼
[alerts]   ──> Runs deterministic red-flag safety rules
    │
    ▼
[fhir]     ──> Constructs standard ABDM HL7 FHIR R4 Bundle
    │
    ▼
[finalize] ──> Persists outputs and records audit log
```

Execute the full pipeline programmatically via:
```http
POST /api/v1/orchestrate/{patient_id}
Content-Type: application/json

{
  "document_id": "optional-document-uuid",
  "actor": "clinician"
}
```

---

## 🔌 API Reference

MediGraph exposes comprehensive REST APIs documented via OpenAPI at `/docs`. Below are key endpoints:

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/login` — Login with email/password; returns JWT access token.
- `POST /api/v1/auth/register` — Register a new patient or clinical account.
- `GET /api/v1/auth/me` — Retrieve the currently authenticated user profile.

### Patient Management (`/api/v1/patients`)
- `GET /api/v1/patients` — List all registered patients.
- `POST /api/v1/patients` — Register a new patient profile.
- `GET /api/v1/patients/{patient_id}` — Retrieve specific patient details.
- `GET /api/v1/patients/stats` — Summary metrics for the clinician dashboard.

### Document Processing (`/api/v1/documents`)
- `POST /api/v1/documents/upload` — Upload a medical PDF or image.
- `POST /api/v1/documents/{doc_id}/ocr` — Execute OpenCV preprocessing and PaddleOCR.
- `POST /api/v1/documents/{doc_id}/verify` — Run local LLM verification and extract medication entities.
- `GET /api/v1/documents/{doc_id}` — Retrieve document details, OCR bounding boxes, and extracted facts.

### Speech & Audio Intake (`/api/v1/speech`)
- `POST /api/v1/speech/transcribe` — Upload `.wav`/`.mp3` audio; returns Faster-Whisper transcript, detected language, and confidence score.

### Timeline & Facts (`/api/v1/timeline`, `/api/v1/facts`)
- `GET /api/v1/timeline/{patient_id}` — Chronological timeline with source provenance and conflict groups.
- `GET /api/v1/facts/{patient_id}` — Extracted clinical entities (medications, vitals, labs, diagnoses).
- `GET /api/v1/facts/{patient_id}/conflicts` — List conflicting records requiring clinician review.

### Clinical Summary & PDF (`/api/v1/summary`)
- `GET /api/v1/summary/{patient_id}` — Get synthesized clinical draft and active safety alerts.
- `POST /api/v1/summary/{patient_id}/draft` — Create or update a clinician-reviewed draft note.
- `GET /api/v1/summary/{patient_id}/pdf` — Generate and download a formatted clinical summary PDF.

### ABDM FHIR R4 Interoperability (`/api/v1/fhir`)
- `POST /api/v1/fhir/export/{patient_id}` — Construct and download an ABDM-compliant FHIR R4 Bundle.
- `POST /api/v1/fhir/validate/{patient_id}` — Run official HAPI FHIR validator against the patient's bundle.

### Auditing & Consents (`/api/v1/consents`)
- `GET /api/v1/consents/audit` — Immutable audit log of patient views, edits, and exports.
- `POST /api/v1/consents` — Record signed patient intake consent.

---

## 📊 Evaluation & Quality Metrics

MediGraph includes an automated benchmarking script to assess entity extraction accuracy against a hand-labeled ground-truth dataset (`data/eval/ground_truth.csv`):

```bash
# Run the evaluation benchmark
python scripts/evaluate.py
```

The script evaluates:
- **Precision, Recall, and F1-Score** across entity types (`medication`, `demographic`, `investigation`, `date`).
- **Normalized Brand-to-Generic Resolution Accuracy**.
- Writes detailed entity-level metrics to `data/eval/report.json`.

---

## 🛡️ Clinical Safety & Privacy Principles

1. **Local-First Privacy**: MediGraph does not transmit Protected Health Information (PHI) to third-party proprietary LLM APIs. Voice recognition (`faster-whisper`), document OCR (`paddleocr`), and LLM reasoning (`medgemma:4b` via Ollama) execute entirely on-premises.
2. **Never Auto-Diagnose**: The AI summary assistant produces organized clinical narratives and working impressions clearly labeled for clinician verification. It never asserts conclusive diagnoses without human review.
3. **Auditable Deterministic Alerts**: Safety-critical alerts (e.g. cardiac symptoms, sepsis signs) use transparent, deterministic rule logic rather than probabilistic LLMs to eliminate hallucination risks.
4. **Immutable Audit Trails**: Every clinical action (fact extraction, clinician edit, PDF generation, FHIR export) generates an immutable audit entry detailing the actor, timestamp, and target resource.

---

## 🛠️ Contributing & Development Commands

A `Makefile` is included in the project root for common developer tasks:

```bash
# Start all containerized background services (DB, Redis, MinIO)
make up

# Stop all background services
make down

# Follow Docker service logs
make logs

# Run FastAPI backend standalone
make api

# Run Next.js frontend standalone
make web

# Connect to the PostgreSQL interactive shell
make db-shell

# Run backend unit tests
make test

# Format code (black for Python, prettier/npm for web)
make fmt
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
#   M e d i g r a p h  
 