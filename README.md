# Opportunity Tracker

A personal automation project that helps evaluate job openings against a candidate profile and drafts tailored application material — built to learn real-world Python, API integration, and LLM orchestration patterns.

**Important:** this tool only produces a **draft PDF for the candidate to review**. This tool can never submit any application automatically.

## What it does

1. **Fetches** open positions from a company's public Applicant Tracking System (ATS) API.
2. **Screens** postings by title (filters out roles that don't match the candidate's profile, e.g. advanced-degree-only positions) and de-duplicates re-posted or multi-language listings.
3. **Classifies** each posting's required language level and scores candidate/role affinity using an LLM, with a cost-aware screening cascade — later, more expensive stages only run for postings that already passed cheaper checks.
4. **Extracts** key skills/requirements per posting.
5. **Drafts** a personalized cover letter and compiles it to a PDF via LaTeX.

## Notes

- LLM orchestration: retry with parsed backoff and per-stage model fallback across two providers (Gemini, Claude), each stage using its own API key to isolate quota usage.
- Cost control: multi-stage filtering cascade — cheap checks run before any LLM call, and a config-driven hard cap limits the most expensive stage (cover letter generation).
- Persistence-aware scraping: a dedicated SQLite table tracks postings already screened out, so re-running the fetch skips work it's already done.
- Config-driven: company/ATS-specific values live in a gitignored config file, with a committed example template documenting the schema.
- Structured logging: dual-handler setup (console + persistent file) at different verbosity levels, with per-stage error isolation so one failure doesn't kill the run.

## Setup

1. Copy .env.example to .env and fill in your API keys.
2. Copy company.example.json to company.json and fill in the target company's ATS details.
3. pip install -r requirements.txt
4. python3 src/run_pipeline.py
