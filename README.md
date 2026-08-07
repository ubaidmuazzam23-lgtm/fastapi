# Fintech Advisor (FinanceBrews)

An AI-powered personal finance platform: a FastAPI + MongoDB backend paired with a React/TypeScript frontend that helps users track debt, plan repayment, evaluate loan options, and get financial guidance through a multilingual, voice-enabled LLM chat assistant.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [1. Clone the repo](#1-clone-the-repo)
  - [2. Backend](#2-backend)
  - [3. Frontend](#3-frontend)
  - [4. Docker (alternative)](#4-docker-alternative)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [API Overview](#api-overview)
- [Status](#status)
- [Author](#author)

## Features

- **Debt tracking** — record and manage multiple debts (credit cards, personal/home/car loans) with balances, APR, and payment history
- **Repayment planning** — generate repayment plans and compare payoff strategies (avalanche vs. snowball) against a user's actual debt data
- **What-if scenario analysis** — model the impact of extra payments, budget changes, or rate changes before committing to a plan
- **Loan recommendations** — compare loan options against a user's financial profile
- **Credit profile analysis** — track credit utilization, payment history, and score-improvement factors
- **Document analysis** — upload financial documents (PDF/CSV/XLSX) and get AI-generated summaries
- **Conversational financial assistant** — chat interface backed by an LLM (LangChain + Groq) for financial Q&A, grounded in the user's own data
- **Multilingual voice chat** — speak to the assistant and get spoken responses in 11 languages (Hindi, Marathi, Tamil, Telugu, Kannada, Gujarati, Bengali, Malayalam, Punjabi, Odia, English) via Sarvam AI speech-to-text/text-to-speech, with automatic language detection
- **Saved plans & notifications** — save generated repayment plans and receive reminders
- **Authentication** — user accounts and session handling via Clerk

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI, Uvicorn |
| Database | MongoDB, Beanie (ODM), Motor |
| AI / LLMs | LangChain, Groq (Llama 3.3 70B) |
| Voice | Sarvam AI (speech-to-text / text-to-speech, 11 languages) |
| Documents | pdfplumber, pdfminer.six, pandas |
| Auth | Clerk, JWT (PyJWT) |
| Frontend | React 18, TypeScript, Vite |
| UI | Material UI, Tailwind CSS |
| State / data | Zustand, TanStack React Query |
| Infra | Docker, docker-compose |

## Project Structure

```
backend/
  app/
    api/routes/       # auth, debt, plans, scenarios, loans, credit, documents, education, notifications, saved-plans
    core/              # business logic: optimization, recommendations, scenario/plan engines, LLM prompts
    services/          # service layer wrapping core logic + external integrations (LLM, voice, scraping)
    models/            # MongoDB document models (Beanie)
    schemas/           # Pydantic request/response schemas
    middleware/        # auth, CORS, error handling
    config/            # settings + database connection
  tests/               # pytest suite
frontend/
  src/
    pages/             # Dashboard, DebtManagement, RepaymentPlans, WhatIfScenarios, CreditScore, DocumentAnalysis, ...
    components/         # feature-organized UI (debt, plans, credit, scenarios, documents, charts, education)
    services/ hooks/ store/   # API clients, React hooks, Zustand stores
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB instance (local or Atlas)
- A [Groq](https://console.groq.com) API key
- A [Clerk](https://dashboard.clerk.com) application (for auth)
- (Optional) A [Sarvam AI](https://www.sarvam.ai/) API key, for voice chat

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/ubaidmuazzam23-lgtm/fastapi.git fintech-advisor
cd fintech-advisor
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # fill in MongoDB URI, Clerk keys, Groq key
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173` (Vite dev server).

### 4. Docker (alternative)

```bash
docker-compose up -d
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URL` | ✅ | MongoDB connection string |
| `DATABASE_NAME` | Optional | Default: `fintech_advisor` |
| `CLERK_PUBLISHABLE_KEY` | ✅ | Clerk publishable key |
| `CLERK_SECRET_KEY` | Optional | Clerk secret key (server-side verification) |
| `GROQ_API_KEY` | ✅ | Groq API key, powers the LLM chat assistant |
| `SARVAM_API_KEY` | Optional | Enables multilingual voice chat (disabled gracefully if absent) |
| `SARVAM_DEFAULT_LANGUAGE` | Optional | Default: `hi` |
| `SARVAM_TTS_SPEAKER` | Optional | Default: `meera` |
| `SECRET_KEY` | Optional | App-level secret; change in production |
| `CORS_ORIGINS` | Optional | JSON array of allowed frontend origins |
| `ENVIRONMENT` | Optional | `development` \| `production` |
| `DEBUG` | Optional | Default: `true` |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `FROM_EMAIL` | Optional | Enables email notifications |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | ✅ | Backend API base URL, e.g. `http://localhost:8000/api` |
| `VITE_CLERK_PUBLISHABLE_KEY` | ✅ | Clerk publishable key (same value as backend) |

## Running Tests

```bash
cd backend
pytest                     # full suite (auth, debts, plans, scenarios, db)
```

```bash
cd frontend
npm run test               # Vitest
npm run lint
```

## API Overview

All routes are mounted under `/api/v1`:

| Prefix | Purpose |
|---|---|
| `/auth` | Authentication |
| `/debt` | Debt CRUD and tracking |
| `/plans` | Repayment plan generation and strategy comparison |
| `/scenarios` | What-if scenario analysis |
| `/loans` | Loan recommendations |
| `/credit` | Credit profile and score analysis |
| `/documents` | Document upload and AI summarization |
| `/education` | Text & voice chat with the financial assistant |
| `/notifications` | User notifications |
| `/saved-plans` | Saving and retrieving generated plans |

Full interactive documentation (request/response schemas) is available at `/docs` when the backend is running.

## Status

Personal/learning full-stack project exploring LLM-assisted financial tooling — not a production or commercial product.

## Author

[Ubaid Muazzam](https://github.com/ubaidmuazzam23-lgtm)
