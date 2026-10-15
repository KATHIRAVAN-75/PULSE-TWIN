# PulseTwin — AI-assisted Education Continuity Platform

A responsive, runnable prototype for exploring how extreme weather, power disruptions and transport delays may affect education access. This repository implements the product loop described in the PulseTwin development specification: weather input → town disruption → campus functionality → Learning Access Index (LAI) → intervention comparison → trust workflow.

> **Important:** The bundled frontend runs on synthetic, deterministic demo data. Scores, forecasts, costs, emissions, routes and sensor events are illustrative. The risk estimate is a transparent weighted rule model, **not a trained AI model**, a calibrated probability, an official forecast, or an emergency-warning service. Do not use the prototype as the sole basis for operational safety decisions.

## Included

- React + TypeScript + Vite frontend with responsive dashboard and 12 navigable sections.
- Overview KPIs and charts, risk estimate form with range validation and factor breakdown, weather scenarios, energy/sensor health, transport routes, aggregated learning-access estimates, scenario lab, twin explorer, intervention comparison, trust center, data catalog and settings.
- Deterministic TypeScript domain services; all dashboard navigation and key actions are interactive.
- JSON export for a demo report.
- FastAPI backend with prediction and simulation endpoints, Ed25519 demo signing/verification helpers, replay/freshness/range checks, and a SHA-256 audit chain.
- Twin and scenario JSON examples, backend unit tests and `.env.example`.

## Requirements

- Node.js 20+ and npm 10+
- Python 3.11+ recommended for the API (the included code uses modern typing and Pydantic v2)

## Start the frontend

```bash
npm install
npm run dev
```

Vite prints a local URL, normally `http://localhost:5173`. The frontend works without a backend or API key. The default interface explicitly labels data as demo/simulated.

Production build:

```bash
npm run build
npm run preview
```

## Start the API (optional)

In a second terminal:

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

Available endpoints:

- `GET /api/health`
- `POST /api/predict`
- `POST /api/simulate`
- `GET /api/trust/demo-public-key`
- `POST /api/trust/sign-demo` — local demo helper only; **disable before production**
- `POST /api/trust/verify`
- `GET /api/trust/audit`
- `POST /api/trust/audit/verify`

Example prediction request:

```json
{
  "rainfall_mm": 84,
  "temperature_c": 33,
  "outage_hours": 1.5,
  "transport_delay_min": 28
}
```

Example simulation request:

```json
{
  "rainfall_mm": 145,
  "temperature_c": 30,
  "outage_hours": 1.5,
  "transport_delay_min": 48,
  "intervention": "Extra shuttle buses"
}
```

The frontend currently uses its deterministic local adapter by design. The API is runnable and the request/response contracts are ready to wire through a client adapter; it is not automatically connected to the dashboard in this first version.

## Run backend tests

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Tests cover deterministic prediction output, disruption cascade behavior, intervention re-simulation, Ed25519 tamper detection and audit-chain integrity.

## Risk model

The prototype uses normalized severities and fixed weights:

| Factor | Weight | Reference threshold |
|---|---:|---:|
| Rainfall | 32% | 150 mm |
| Heat stress | 18% | 42 °C (severity starts at 20 °C) |
| Power outage | 28% | 6 hours |
| Transport delay | 22% | 90 minutes |

Categories: Low 0–29, Medium 30–59, High 60–79, Critical 80–100. These are illustrative policy thresholds and should be calibrated and reviewed before any real deployment.

The Learning Access Index uses `0.62 × modeled on-time access + 0.38 × modeled classroom functionality`. It represents an aggregated planning indicator, not observed attendance or an individual student score.

## Trust workflow and limitations

The backend demo generates an ephemeral Ed25519 key pair at process start. The private key is held in process memory only; the local demo signing endpoint exists for testing and must not be exposed in production. Events are schema/range/time/sequence checked, then signature-verified. Accepted events update the in-memory sequence registry; rejected events do not. Audit entries are chained with SHA-256 and can be verified. The in-memory registry and audit chain reset on restart.

A valid signature establishes integrity/authenticity relative to a key, not the physical truth of a measurement. Production needs secure key storage, identity provisioning, rotation/revocation, access control, persistent audit storage, robust replay handling, observability, threat modeling and independent review.

## Project layout

```text
pulsetwin-complete/
├── frontend/                 # React + TypeScript + Vite app
├── backend/app/               # FastAPI, schemas, simulator, signing, audit
├── backend/tests/             # pytest tests
├── configs/twins/             # Town, campus and additional twin examples
├── configs/scenarios/         # Heavy rain, heatwave and power-dip presets
├── .env.example
└── README.md
```

## Before real-world deployment

1. Validate the causal model with local education, transport, weather and facilities experts.
2. Replace synthetic adapters with documented, licensed, reliable feeds and clearly surface freshness/outages.
3. Calibrate the risk model and LAI against representative, privacy-preserving data; publish assumptions and validation results.
4. Implement persistent storage, role-based access control, protected keys, key rotation and audit retention policies.
5. Conduct accessibility, privacy, security, reliability and operational safety reviews.
6. Keep official emergency alerts and local authority decisions authoritative.
