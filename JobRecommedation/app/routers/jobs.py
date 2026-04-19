from fastapi import APIRouter, HTTPException, Query, status
from app import database as db
from app.schemas import JobCreate, JobResponse, MessageResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    location: str | None = Query(None),
    job_type: str | None = Query(None),
    min_experience: int | None = Query(None),
    skill: str | None = Query(None),
):
    return db.list_jobs(location=location, job_type=job_type,
                        min_experience=min_experience, skill=skill)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreate):
    return db.create_job(payload.model_dump())

@router.delete("/{job_id}", response_model=MessageResponse)
async def delete_job(job_id: str):
    if not db.delete_job(job_id):
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return {"message": f"Job '{job_id}' deleted."}