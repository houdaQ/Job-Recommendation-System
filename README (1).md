# Job Recommendation System 🎯

A full-stack NLP-powered job recommendation engine that scrapes job listings from Jooble, matches them against candidate profiles using TF-IDF + cosine similarity, and serves results through a FastAPI backend with a Streamlit frontend.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                        │
│         (Profile Form / Results / Browse Jobs)          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (POST /recommend/, GET /jobs/)
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│     /recommend/   /jobs/   /health   /jobs/{id}         │
│            Pydantic schema validation                    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   NLP Engine                             │
│   TF-IDF Vectorizer  →  Cosine Similarity  →  Ranking   │
│        vectorizer.pkl          job_vectors.pkl           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Data Layer                              │
│     jobs.json (22 Jooble listings)   jobs_index.csv     │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Scraping | Python · Selenium · ChromeDriver |
| NLP Engine | scikit-learn · TF-IDF · Cosine Similarity |
| Backend API | FastAPI · Uvicorn · Pydantic v2 |
| Frontend | Streamlit |
| Data | JSON · CSV (22 Full Stack listings from Jooble) |
| Testing | pytest · pytest-cov · unittest.mock |

---

## Project Structure

```
Job-Recommendation-System/
├── JobRecommedation/
│   ├── app/
│   │   ├── main.py               # FastAPI app entrypoint
│   │   ├── schemas.py            # Pydantic models (request/response)
│   │   ├── database.py           # In-memory job store + loader
│   │   ├── nlp_adapter.py        # Bridge: API ↔ NLP engine
│   │   ├── recommender.py        # TF-IDF cosine similarity logic
│   │   ├── vectorizer.py         # Vectorizer loader (pkl files)
│   │   ├── preprocessing.py      # Text cleaning & stopword removal
│   │   ├── candidat_profile.py   # Candidate profile data class
│   │   ├── vectorizer.pkl        # Pre-trained TF-IDF vectorizer
│   │   ├── job_vectors.pkl       # Pre-computed job vectors
│   │   └── routers/
│   │       ├── jobs.py           # /jobs/ endpoints
│   │       └── recommend.py      # /recommend/ endpoint
│   ├── data/
│   │   ├── jobs.json             # 22 job listings with URLs
│   │   └── jobs.csv              # Raw scraped data
│   └── requirements.txt
├── nlp_module/                   # Standalone NLP prototype
├── Jobs-Screaping.ipynb          # Selenium scraper notebook
├── streamlit_app.py              # Frontend UI
└── tests/
    ├── test_scraper.py
    ├── test_nlp.py
    └── test_api.py
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js (optional, for dev tooling)
- Google Chrome + ChromeDriver (for scraper)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Job-Recommendation-System.git
cd Job-Recommendation-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r JobRecommedation/requirements.txt
pip install streamlit requests pytest pytest-cov
```

### 4. Environment variables

Create a `.env` file at the project root (optional — only needed if re-scraping):

```env
# Jooble API key (only for re-scraping via the API)
JOOBLE_API_KEY=your_jooble_api_key_here

# ChromeDriver path (if not on PATH)
CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
```

> **Note:** The project ships with `jobs.json` already populated — you do **not** need a Jooble API key to run the recommendation engine.

---

## Running the Project

### Step 1 — Start the FastAPI backend

```bash
cd JobRecommedation
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
Interactive Swagger docs: `http://localhost:8000/docs`

### Step 2 — Start the Streamlit frontend

Open a second terminal:

```bash
# from the project root
streamlit run streamlit_app.py
```

The UI will open at `http://localhost:8501`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | API status and job count |
| `POST` | `/recommend/` | Get job recommendations |
| `GET` | `/jobs/` | List / filter all jobs |
| `GET` | `/jobs/{id}` | Get a single job by ID |
| `POST` | `/jobs/` | Add a new job listing |
| `DELETE` | `/jobs/{id}` | Remove a job listing |

---

## Example API Calls (curl)

### Health check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "jobs_indexed": 22,
  "version": "1.0.0"
}
```

### Get recommendations

```bash
curl -X POST "http://localhost:8000/recommend/?top_n=3&min_score=0.1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Martin",
    "skills": ["Python", "React", "FastAPI", "Docker", "AWS"],
    "experience_years": 3,
    "desired_location": "Remote",
    "bio": "Full Stack developer with 3 years experience in Python and React. Built REST APIs and deployed on AWS with Docker."
  }'
```

```json
{
  "candidate_name": "Alice Martin",
  "total_jobs_analyzed": 22,
  "recommendations": [
    {
      "job": {
        "id": "j008",
        "title": "Full stack software engineer",
        "company": "MORSE Corp",
        "location": "Cambridge, MA",
        "job_url": "https://jooble.org/desc/6711212706694077316",
        "job_type": "full-time"
      },
      "score": 0.42,
      "matching_skills": ["Python", "React", "Docker"],
      "missing_skills": []
    }
  ]
}
```

### List jobs filtered by location

```bash
curl "http://localhost:8000/jobs/?location=Remote"
```

### Pydantic validation error example (bad input)

```bash
curl -X POST "http://localhost:8000/recommend/" \
  -H "Content-Type: application/json" \
  -d '{"name": "", "skills": [], "experience_years": 2}'
```

```json
{
  "detail": [
    { "loc": ["body", "skills"], "msg": "skills list must not be empty" }
  ]
}
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Target: ≥ 80% code coverage
```

### Test modules

| File | What it tests |
|------|--------------|
| `tests/test_scraper.py` | HTML parsing, CSV export, error handling |
| `tests/test_nlp.py` | TF-IDF vectorizer, cosine similarity, preprocessing |
| `tests/test_api.py` | POST /recommend/ with mock profiles, Pydantic schema validation, all endpoints |

---

## How the NLP Matching Works

1. **Text extraction** — candidate skills + bio are concatenated into a single text string
2. **Preprocessing** — lowercasing, punctuation removal, English stopword filtering
3. **TF-IDF vectorization** — the text is transformed into a numerical vector using the pre-trained `vectorizer.pkl`
4. **Cosine similarity** — the candidate vector is compared against all 22 pre-computed job vectors (`job_vectors.pkl`)
5. **Ranking** — jobs are sorted by descending score; only those above `min_score` are returned

> **Why TF-IDF + Cosine?** Lightweight, interpretable, and highly effective on small corpora. No GPU required.

---

## Data Collection

Jobs were scraped from **Jooble** using Selenium (see `Jobs-Screaping.ipynb`). The scraper navigates to each listing, extracts the full job description, company, location, and original URL, and saves everything to `data/jobs.json` and `data/jobs.csv`.

---

## Known Limitations

- Dataset is small (22 jobs) — scores are generally low due to vocabulary sparsity
- `skills_required` and `experience_years` fields are empty in the scraped data — matching is description-only
- TF-IDF does not capture semantic meaning (e.g., "developer" ≠ "engineer")

## Future Improvements

- Replace TF-IDF with sentence embeddings (e.g., `sentence-transformers`)
- Expand dataset with periodic re-scraping
- Add user authentication and saved profiles
- Deploy on cloud (Railway, Render, or AWS EC2)

---

## Author

Developed as part of a university NLP & software engineering project.
