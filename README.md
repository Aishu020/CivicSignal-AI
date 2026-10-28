# CivicSignal AI — Urban Infrastructure Early Warning

A local-first AI portfolio project for organizing civic infrastructure reports, detecting potentially duplicated complaints, prioritizing incidents with transparent scoring, and visualizing issues on an interactive map.

**Status:** Working portfolio MVP · Synthetic demonstration data · Heuristic-based AI

## Overview

Civic infrastructure reports can be repetitive, inconsistently described, and difficult to prioritize. CivicSignal AI explores how lightweight natural language processing and geographic proximity can support more organized incident triage.

### Features

- **Incident classification:** TF-IDF text similarity with keyword-based fallback rules.
- **Duplicate detection:** Text similarity and geographic proximity identify potentially related reports.
- **Explainable prioritization:** Rule-based scores use severity, public impact, category, and duplicate status.
- **Interactive map:** Leaflet and OpenStreetMap display incident locations.
- **Dashboard and analytics:** Summaries of incidents, categories, neighbourhoods, and priorities.
- **Incident management:** Report submission, search, filtering, and status updates.
- **CSV export:** Export incident records for analysis.
- **Theme support:** Dark and light interfaces.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| Text processing | scikit-learn, TF-IDF, keyword rules |
| Mapping | Leaflet, OpenStreetMap |
| Validation | Pydantic |
| Testing | Python evaluation and API scripts |

## Architecture

1. A user submits a civic incident through the React interface.
2. FastAPI validates the report.
3. The classification component predicts an incident category.
4. Duplicate detection compares report text and geographic proximity.
5. A rule-based scoring function assigns a priority and explanation.
6. SQLite stores the incident for use by the dashboard, map, filters, and CSV export.

## Getting Started

### Requirements

- Python 3.10+
- Node.js 18+
- npm
- Internet access for package installation and map tiles

### Backend

From the project root, open PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks virtual environment activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

- Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Frontend

Open a second PowerShell terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually [http://localhost:5173](http://localhost:5173).

## Evaluation and Testing

Initial hand-authored component tests and API integration checks have been completed.

| Check | Result |
|---|---|
| Classification robustness tests | 16/16 passed |
| Duplicate detection robustness tests | 12/12 passed |
| Duplicate test breakdown | TP: 6 · FP: 0 · FN: 0 · TN: 6 |
| Priority scoring sanity check | Higher severity and impact produced a higher score |
| API integration checks | Passed |

API checks covered health, incident listing and creation, classification and priority responses, duplicate handling, search and filtering, status updates, dashboard summary consistency, CSV export, invalid payload rejection, and test-record cleanup.

One duplicate integration example returned a similarity score of `0.931` at a reported distance of 16 metres. This is an illustrative output, not a validated performance metric.

### Reproduce the tests

Run from the `backend` directory with the backend server running:

```powershell
python evaluate_baseline.py
python evaluate_robustness.py
python test_api.py
```

The API test creates temporary records and removes the records it creates afterward.

**Evaluation note:** These results describe the supplied test cases only. They are not estimates of real-world accuracy or independent validation.

## Research Direction

**Proposed research question:** Does combining textual similarity with geographic proximity improve duplicate detection for civic infrastructure reports compared with textual similarity alone?

### Proposed methodology

1. Identify an appropriately licensed public civic-complaint dataset.
2. Create labelled duplicate and non-duplicate report pairs.
3. Separate development and held-out evaluation data to reduce leakage.
4. Compare text-only and text-plus-location approaches.
5. Evaluate precision, recall, F1-score, and false-positive behaviour.
6. Analyze paraphrases, spelling errors, and similar reports from different locations.
7. Document limitations and reproducibility details.

This is a proposed research direction, not a completed experimental finding.

## Limitations and Responsible Use

- Demonstration data contains synthetic, illustrative Coimbatore reports, not verified municipal complaints.
- Classification relies on a small, hand-authored training set and keyword fallback rules.
- Duplicate thresholds are heuristic and require calibration against labelled data.
- Priority scores are not calibrated emergency-risk predictions.
- Geographic proximity alone does not establish that reports describe the same incident.
- Human review is necessary before merging reports or taking action.
- The application is a portfolio prototype, not a production-ready civic service.

## Screenshot

<img width="949" height="437" alt="image" src="https://github.com/user-attachments/assets/ba916c50-6c60-442f-ba7a-aa25f8c3ae6a" />

<img width="945" height="434" alt="image" src="https://github.com/user-attachments/assets/60cde30d-a463-4b5a-b0f0-d301564e8ca1" />

<img width="959" height="442" alt="image" src="https://github.com/user-attachments/assets/e8043854-6398-4179-bb01-eeb0fb32fa6f" />

<img width="941" height="438" alt="image" src="https://github.com/user-attachments/assets/09560f59-cdd1-411c-af2b-c36f0fd0f7a3" />

<img width="946" height="434" alt="image" src="https://github.com/user-attachments/assets/ceb7f137-e871-47a7-9cd7-26b277dd9d5a" />

<img width="950" height="435" alt="image" src="https://github.com/user-attachments/assets/4b97dfd3-7e2b-443c-9d28-8b907e4d1545" />

<img width="948" height="434" alt="image" src="https://github.com/user-attachments/assets/f3e7b20b-e55e-42cd-b984-090fbd633bcd" />


## Future Work

- Evaluate using a licensed public complaint dataset.
- Measure per-category classification performance.
- Compare text-only and text-plus-geography duplicate detection.
- Study threshold sensitivity and confidence calibration.
- Improve explainability and error analysis.
- Strengthen validation, privacy safeguards, and deployment testing.
