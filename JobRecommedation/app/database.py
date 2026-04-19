import json
import uuid
import logging
from pathlib import Path
from datetime import date
from app.nlp_adapter import JobMatcher

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent / "data" / "jobs.json"

_jobs: list[dict] = []
_matcher: JobMatcher | None = None


def load_jobs() -> None:
    global _jobs, _matcher
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    _jobs = raw
    _matcher = JobMatcher(_jobs)
    logger.info("Loaded %d jobs", len(_jobs))


def get_matcher() -> JobMatcher:
    if _matcher is None:
        raise RuntimeError("JobMatcher not initialised.")
    return _matcher


def list_jobs(
    location: str | None = None,
    job_type: str | None = None,
    min_experience: int | None = None,
    skill: str | None = None,
) -> list[dict]:
    results = _jobs
    if location:
        results = [j for j in results if location.lower() in j["location"].lower()]
    if job_type:
        results = [j for j in results if j["job_type"].lower() == job_type.lower()]
    if min_experience is not None:
        results = [j for j in results if j["experience_years"] <= min_experience]
    if skill:
        results = [j for j in results if any(skill.lower() in s.lower() for s in j["skills_required"])]
    return results


def get_job(job_id: str) -> dict | None:
    return next((j for j in _jobs if j["id"] == job_id), None)


def create_job(data: dict) -> dict:
    global _matcher
    new_job = {"id": f"j{uuid.uuid4().hex[:6]}", **data}
    if "posted_date" not in new_job or new_job["posted_date"] is None:
        new_job["posted_date"] = date.today().isoformat()
    elif hasattr(new_job["posted_date"], "isoformat"):
        new_job["posted_date"] = new_job["posted_date"].isoformat()
    _jobs.append(new_job)
    _matcher = JobMatcher(_jobs)
    return new_job


def delete_job(job_id: str) -> bool:
    global _jobs, _matcher
    before = len(_jobs)
    _jobs = [j for j in _jobs if j["id"] != job_id]
    if len(_jobs) < before:
        _matcher = JobMatcher(_jobs)
        return True
    return False