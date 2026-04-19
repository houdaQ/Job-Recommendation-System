from fastapi import APIRouter, Query
from app import database as db
from app.schemas import CandidateProfile, RecommendationResponse, RecommendationItem, JobResponse

router = APIRouter(prefix="/recommend", tags=["Recommendations"])

@router.post("/", response_model=RecommendationResponse)
async def recommend(
    profile: CandidateProfile,
    top_n: int = Query(5, ge=1, le=20),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
):
    matcher = db.get_matcher()
    raw_results = matcher.match(profile.model_dump(), top_n=top_n, min_score=min_score)

    recommendations = [
        RecommendationItem(
            job=JobResponse(**r["job"]),
            score=r["score"],
            matching_skills=r["matching_skills"],
            missing_skills=r["missing_skills"],
        )
        for r in raw_results
    ]

    return RecommendationResponse(
        candidate_name=profile.name,
        total_jobs_analyzed=len(db.list_jobs()),
        recommendations=recommendations,
    )