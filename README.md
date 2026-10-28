# \# CivicSignal AI — Urban Infrastructure Early Warning

# 

# CivicSignal AI is a local-first AI portfolio project that helps organize urban infrastructure reports, identify potentially duplicated complaints, prioritize incidents using transparent scoring, and visualize civic issues on an interactive map.

# 

# The project explores how lightweight natural language processing and geographic proximity can support more efficient civic issue triage.

# 

# > \*\*Project status:\*\* Working portfolio MVP. Uses synthetic demonstration data and heuristic-based AI components. It is not a production municipal service.

# 

# \## Problem Statement

# 

# Civic infrastructure complaints can be repetitive, inconsistently described, and difficult to prioritize when many reports arrive from different locations. A useful triage system should help organize reports, surface possible duplicates, and explain why an incident receives a particular priority.

# 

# CivicSignal AI implements a prototype workflow for exploring these challenges.

# 

# \## Features

# 

# \- \*\*Incident classification:\*\* Predicts an infrastructure category from report text using TF-IDF-based text similarity and keyword fallback rules.

# \- \*\*Duplicate detection:\*\* Identifies potentially related reports using text similarity and geographic distance.

# \- \*\*Explainable prioritization:\*\* Assigns priority scores using severity, public impact, category, and duplicate status.

# \- \*\*Interactive map:\*\* Displays reported incidents geographically using Leaflet and OpenStreetMap.

# \- \*\*Dashboard and analytics:\*\* Summarizes incidents, categories, neighborhoods, and priority levels.

# \- \*\*Incident management:\*\* Supports report submission, search, filtering, and status updates.

# \- \*\*CSV export:\*\* Exports incident records for further analysis.

# \- \*\*Dark and light themes:\*\* Provides two interface themes.

# 

# \## Technology Stack

# 

# | Component | Technology |

# |---|---|

# | Frontend | React, Vite, JavaScript |

# | Backend | Python, FastAPI |

# | Database | SQLite |

# | Text processing | scikit-learn, TF-IDF, keyword rules |

# | Mapping | Leaflet, OpenStreetMap |

# | API validation | Pydantic |

# | Testing | Python evaluation and API test scripts |

# 

# \## System Architecture

# 

# 1\. A user submits a civic incident through the React interface.

# 2\. The FastAPI backend validates the report.

# 3\. The classification component predicts an incident category.

# 4\. The duplicate detector compares report text and geographic proximity with existing incidents.

# 5\. A priority-scoring function generates a score, priority level, and explanation.

# 6\. The incident is stored in SQLite and made available to the dashboard, map, filters, and CSV export.

# 

# \## Local Setup

# 

# \### Requirements

# 

# \- Python 3.10 or later

# \- Node.js 18 or later

# \- npm

# \- Internet access for package installation and OpenStreetMap tiles

# 

# \### 1. Start the backend

# 

# Open PowerShell in the project root:

# 

# ```powershell

# cd backend

# py -m venv .venv

# .\\.venv\\Scripts\\Activate.ps1

# python -m pip install --upgrade pip

# pip install -r requirements.txt

# python -m uvicorn app.main:app --reload --port 8000

# ```

# 

# If PowerShell blocks virtual environment activation, run:

# 

# ```powershell

# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# .\\.venv\\Scripts\\Activate.ps1

# ```

# 

# Backend health check: http://127.0.0.1:8000/api/health

# 

# Interactive API documentation: http://127.0.0.1:8000/docs

# 

# \### 2. Start the frontend

# 

# Open a second PowerShell terminal in the project root:

# 

# ```powershell

# cd frontend

# npm install

# npm run dev

# ```

# 

# Open the local URL printed by Vite, usually http://localhost:5173.

# 

# \## Evaluation and Testing

# 

# The project has undergone initial hand-authored component tests and API integration checks.

# 

# \### Initial component tests

# 

# \- Classification: \*\*16/16\*\* hand-authored test cases passed.

# \- Duplicate detection: \*\*12/12\*\* hand-authored test cases passed.

# \- Duplicate test breakdown: TP = 6, FP = 0, FN = 0, TN = 6.

# \- Priority scoring sanity check: a higher-severity, higher-impact example received a higher score than a low-severity example.

# 

# These results describe the supplied test cases only. They are not estimates of real-world accuracy or independent validation.

# 

# \### API integration checks

# 

# The following checks passed:

# 

# \- Health endpoint and incident listing

# \- Incident creation and category/priority response

# \- Duplicate candidate response and linking

# \- Search/filter endpoint

# \- Incident status update

# \- Dashboard summary consistency

# \- CSV export

# \- Rejection of an invalid request payload

# \- Cleanup of test-created records

# 

# The duplicate integration example returned a similarity score of 0.931 at a reported distance of 16 metres. This is an example output, not a validated performance metric.

# 

# \### Reproducing the tests

# 

# Run the backend evaluation scripts from the `backend` directory:

# 

# ```powershell

# python evaluate\_baseline.py

# python evaluate\_robustness.py

# python test\_api.py

# ```

# 

# Keep the backend server running while executing `test\_api.py`. The API test creates temporary records and removes the records it created afterward.

# 

# \## Research Motivation

# 

# \*\*Proposed research question:\*\*

# 

# Does combining textual similarity with geographic proximity improve duplicate detection for civic infrastructure reports compared with using textual similarity alone?

# 

# \### Proposed methodology

# 

# 1\. Identify an appropriately licensed public civic-complaint dataset.

# 2\. Define and document a labelled set of duplicate and non-duplicate report pairs.

# 3\. Split data into development and held-out evaluation sets to reduce leakage.

# 4\. Compare a text-only baseline with a text-plus-location approach.

# 5\. Evaluate precision, recall, F1-score, and false-positive behavior.

# 6\. Analyze failure cases such as paraphrases, spelling errors, and similar reports from different locations.

# 7\. Document limitations, reproducibility details, and possible improvements.

# 

# This is a proposed research direction, not a completed experimental finding.

# 

# \## Limitations and Responsible Use

# 

# \- The demonstration dataset contains synthetic, illustrative Coimbatore reports; it does not represent verified municipal complaints.

# \- Classification uses a small, hand-authored training set and keyword fallback rules. It has not been validated across a representative real-world dataset.

# \- Duplicate scores and thresholds are heuristic and need calibration against labelled data.

# \- Priority scores are rule-based and are not calibrated emergency-risk predictions.

# \- Geographic proximity alone does not establish that two reports describe the same incident.

# \- Human review is necessary before merging reports or taking action.

# \- The application is a portfolio prototype, not a production-ready civic service.

# 

# \## Future Work

# 

# \- Evaluate against a licensed public complaint dataset.

# \- Improve category coverage and evaluate per-category performance.

# \- Compare text-only and text-plus-geography duplicate detection.

# \- Add confidence calibration and threshold sensitivity analysis.

# \- Improve explainability and error analysis.

# \- Add stronger validation, privacy safeguards, and deployment testing.



