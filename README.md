# AIPathFinder

> An end-to-end multi-agent platform guiding international students from program discovery to career outlook for US graduate programs.

**Columbia University · Generative AI using LLM · Spring 2026**
Joaquin Siebert · Meghna Choudhury · Benjamin Fuentes

---

## Overview

AIPathFinder replaces 5+ disconnected tools and $3,000–$8,000 consulting fees with a single AI-powered platform. Students fill out a short onboarding form and instantly receive personalized recommendations across 6 dimensions: program matching, visa guidance, career outlook, test preparation, and a week-by-week application roadmap.

---

## Features

- **Profile Agent** — Normalizes raw student input into a structured profile using LLM + Pydantic validation
- **Match Agent** — Queries a SQLite programs database and ranks US master's programs by fit score
- **Visa Agent** — RAG-grounded over official USCIS/ICE PDFs with nationality-specific guidance and embassy links
- **Career Agent** — Prompt-based subjective analysis of job market outlook, salaries, and H-1B sponsorship likelihood
- **Test Prep Agent** — Gap analysis across TOEFL, IELTS, GRE, GMAT with prioritized study plans and resources
- **Roadmap Agent** — Week-by-week application roadmap with Gantt chart data and deterministic urgency calculation
- **Fault tolerant** — All agents fall back to prompt-based generation if primary data sources fail

---

## System Architecture

```
Frontend (React + Vite)
    ↓ POST /api/dashboard
Backend API (FastAPI + Pydantic)
    ↓ invokes graph
LangGraph Orchestrator
    Profile → Match → [Visa + Career + TestPrep + Roadmap] → Response Formatter
    ↓ RAG retrieval
Data Sources (SQLite · ChromaDB · OpenAI/Gemini)
```

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | Python 3.12, FastAPI, Pydantic |
| AI & Orchestration | LangGraph, LangChain, GPT-4o, Gemini 2.5 Flash |
| RAG & Embeddings | ChromaDB, OpenAI Embeddings, PDF chunker |
| Data Sources | US College Scorecard API, O*NET, BLS, USCIS/ICE PDFs |
| Database | SQLite + SQLAlchemy |

---

## Installation

### Prerequisites
- Python 3.12
- Node.js 18+
- Conda
- OpenAI or Gemini API key

### 1. Clone the repository
```bash
git clone https://github.com/your-org/gen_ai-project.git
cd gen_ai-project
```

### 2. Set up the environment
```bash
make setup
conda activate myenv
```

### 3. Configure environment variables
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and fill in your API keys:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o
```

### 4. Run the backend
```bash
cd backend
uvicorn main:app --reload
```

### 5. Run the frontend
```bash
# In a new terminal from project root
npm install
npm run dev
```

The app will be available at `http://localhost:5173` and the API docs at `http://localhost:8000/docs`.

---

## Project Structure

```
gen_ai-project/
├── backend/
│   ├── agents/
│   │   ├── profile_agent.py      # Normalizes student input
│   │   ├── match_agent.py        # Program matching with SQLite + LLM
│   │   ├── visa_agent.py         # RAG-grounded visa guidance
│   │   ├── career_agent.py       # Job market outlook
│   │   ├── testprep_agent.py     # Test prep gap analysis
│   │   ├── roadmap_agent.py      # Week-by-week application roadmap
│   │   ├── llm_client.py         # Unified OpenAI/Gemini client
│   │   ├── graph.py              # LangGraph pipeline
│   │   └── state.py              # Shared graph state
│   ├── routes/
│   │   ├── dashboard.py          # Main pipeline endpoint
│   │   ├── health.py             # Health check
│   │   └── ...                   # Individual agent endpoints
│   ├── services/
│   │   └── rag_service.py        # Shared RAG retrieval service
│   ├── data/                     # SQLite DB + visa docs
│   ├── formatters.py             # Response assembly
│   ├── config.py                 # Settings + env loading
│   └── main.py                   # FastAPI entry point
├── src/
│   ├── pages/                    # React pages (onboarding + dashboard)
│   ├── components/               # UI components
│   ├── contexts/                 # App state management
│   └── types/                    # TypeScript interfaces
├── Makefile                      # Dev commands
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root health check |
| `GET` | `/api/health` | Detailed health check |
| `POST` | `/api/dashboard` | Full pipeline — returns complete dashboard |
| `POST` | `/api/profile` | Profile agent only |
| `POST` | `/api/match` | Match agent only |
| `POST` | `/api/visa` | Visa agent only |
| `POST` | `/api/career` | Career agent only |

---

## Data Strategy

### Program Data
- **Source:** US College Scorecard API (DOE) — ~3,000 graduate institutions
- **Enrichment:** Claude API used to generate ~200 realistic program records using Scorecard as factual anchor
- **Storage:** SQLite `masters_programs` + `program_requirements` tables

### Visa & Career Data
- **Visa:** Official PDFs from uscis.gov, ice.gov/sevis, travel.state.gov — chunked and embedded into ChromaDB
- **Career:** O*NET Online + BLS Occupational Outlook Handbook

---

## LangGraph Pipeline

The pipeline uses a stateful directed graph with parallel execution:

```
START
  └─► profile_agent       # Standardizes raw input
        └─► match_agent   # SQL + RAG + LLM ranking
              ├─► visa_agent      ┐
              ├─► career_agent    ├── parallel superstep
              ├─► testprep_agent  ┘
              └─► roadmap_agent   # Reads matches + calculates urgency
                    └─► Response Formatter → END
```

**Key design decisions:**
- Profile → Match run sequentially (each depends on the previous)
- Visa, Career, TestPrep, Roadmap run in parallel (~3x faster than sequential)
- Urgency calculation is deterministic Python — no LLM involved
- All agents are fault tolerant with prompt-based fallbacks

---

## Error Handling

- All agent endpoints return `HTTP 500` with descriptive error messages on failure
- Every agent has a prompt-based fallback if primary data sources (SQLite, ChromaDB) are unavailable
- Pydantic schema validation on all incoming requests returns `HTTP 422` with field-level errors
- LangGraph pipeline logs failures per node without crashing the entire graph

---

## Reproducibility

To reproduce the program database:
```bash
python generate_programs_data.py
```

To re-index the RAG corpus:
```bash
python scripts/ingest.py
```

---

## Known Limitations

- Program data is LLM-generated — real-time scraping would improve accuracy
- Career agent relies on LLM knowledge — not yet linked to live salary APIs
- RAG corpus limited to ~10 visa PDFs — production needs broader coverage
- No user authentication or persistent profiles in current demo
- GPA conversion for non-US systems not yet implemented

---

## Development Commands

```bash
make setup           # Create conda env + install all dependencies
make install         # Install frontend dependencies
make install-backend # Install backend dependencies
make lint            # Run ruff check and format
```