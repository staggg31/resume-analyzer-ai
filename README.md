# ResumeLens AI 🔍

A full-stack GenAI career optimization platform built with **FastAPI**, **React (Vite)**, and **Groq Cloud LLMs**.

ResumeLens AI enables candidates to upload a resume PDF and compare it directly against any target job description. The system deterministic-extracts candidate credentials, analyzes skill gaps and semantic alignment, computes an objective match rating, and delivers actionable recruiter-grade feedback.

---

## 🏗️ Architecture

```
                  ┌──────────────────────────────────────┐
                  │          React + Vite Frontend        │
                  │        (http://localhost:5173)       │
                  └──────────────────┬───────────────────┘
                                     │
                     REST API Calls  │  (No API keys exposed)
                                     ▼
                  ┌──────────────────────────────────────┐
                  │          FastAPI Backend             │
                  │        (http://localhost:8000)       │
                  └─────────┬──────────────────┬─────────┘
                            │                  │
                pypdf text  │                  │  groq Python SDK
                extraction  ▼                  ▼  (Bounded retries & rate-limit handling)
                  ┌──────────────────┐   ┌───────────────────────────┐
                  │  Resume PDF File │   │         Groq API          │
                  │   (In-Memory)    │   │   (openai/gpt-oss-120b)   │
                  └──────────────────┘   └───────────────────────────┘
```

* **Frontend**: React 18, Vite, Vanilla Modern CSS (Dark SaaS theme), Lucide Icons.
* **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic.
* **GenAI Engine**: Groq API via official `groq` Python SDK.
* **PDF Extraction**: `pypdf` (in-memory extraction with safe truncation).
* **Security**: API keys are isolated exclusively to the Python backend `.env` file; zero secrets are exposed to the browser client or build assets.

---

## ✨ Features

1. **Resume & Job Match Analysis**:
   - Drag & drop PDF resume upload.
   - Comprehensive job description input with character counter and quick-fill sample.
   - Overall match score with animated SVG progress ring.
   - Categorized badges for **Matching Skills** and **Missing/Gap Skills**.
   - Actionable **Strengths** and **Areas for Improvement**.
   - Collapsible **Relevant Experience Alignment** breakdown.
   - ATS **Suggested Keywords** tags.
   - Targeted **Interview Preparation Topics**.
   - Executive evaluation summary.

2. **AI Resume Bullet Improver**:
   - Transform weak or passive resume bullets into strong, action-oriented achievements.
   - Optional context input (role, technologies, impact).
   - Instant one-click copy to clipboard.
   - **Truthfulness Guardrails**: Derives suggestions strictly from candidate input without hallucinating fake metrics or credentials.

3. **Production Reliability & Error Handling**:
   - **HTTP 503 Capacity Spikes**: Automatic bounded retry loop with exponential backoff (2s, 5s, 10s).
   - **HTTP 429 Rate Limit / Quota**: Immediate, human-readable user guidance without wasteful retries.
   - **Model Fallback / Override**: Configurable via `GROQ_MODEL` environment variable.

---

## 📁 Project Structure

```
resume_ai/
│
├── backend/
│   ├── __init__.py
│   └── main.py              # FastAPI app, CORS, routes & validation
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js       # Vite configuration with /api backend proxy
│   ├── index.html           # HTML5 entry with Plus Jakarta Sans typography
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── ResumeUploader.jsx
│       │   ├── JobDescriptionInput.jsx
│       │   ├── LoadingAnalysis.jsx
│       │   ├── ScoreVisualizer.jsx
│       │   ├── ResultsDashboard.jsx
│       │   └── AboutModal.jsx
│       ├── pages/
│       │   ├── AnalyzerPage.jsx
│       │   └── BulletImproverPage.jsx
│       ├── services/
│       │   └── api.js        # API service layer (FastAPI communication)
│       ├── styles/
│       │   ├── index.css     # Design tokens & dark SaaS theme
│       │   └── App.css       # Layouts, cards, animations & responsiveness
│       ├── App.jsx
│       └── main.jsx
│
├── analyzer.py              # Groq API client, bounded retries & structured JSON parsing
├── pdf_reader.py            # PDF text extraction & length truncation
├── prompts.py               # Prompt templates with truthfulness constraints
├── run_tests.py             # Complete test suite (100% mocked, 0 API quota used)
├── requirements.txt         # Python dependencies (FastAPI, uvicorn, pypdf, groq)
├── .env                     # Local environment secrets (excluded from Git)
├── .env.example             # Example environment configuration
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Prerequisites
* Python 3.12+
* Node.js 18+ and npm

### 2. Backend Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```

---

## 🏃 Running the Application

### 1. Run the FastAPI Backend
From the project root (`resume_ai/`):
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
* API Health check: `http://localhost:8000/api/health`
* Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

### 2. Run the React Frontend
In a separate terminal, from `resume_ai/frontend/`:
```bash
npm run dev
```
Open your browser at `http://localhost:5173/`.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Returns backend status and configured Groq model name. |
| `POST` | `/api/analyze-resume` | Accepts `multipart/form-data` with `resume` (PDF) and `job_description`. Returns structured match JSON. |
| `POST` | `/api/improve-bullet` | Accepts JSON `{"bullet": "...", "context": "..."}`. Returns enhanced phrasing. |

---

## 🧪 Testing

Execute the automated test suite covering syntax, parser validation, retry backoff, quota exhaustion, and FastAPI endpoints:

```bash
python run_tests.py
```
* **Test Count**: 100% passing tests.
* Tests run with safe mocks to avoid consuming live Groq free-tier quota during automated verification.

---

## 🔮 Future Improvements

* Multi-resume comparison against a single job description.
* PDF export of the generated analysis report.
* Integration with LinkedIn job posting URLs for automatic JD extraction.
* Custom prompt profile templates (e.g., Executive, Entry-Level, Career Pivot).
