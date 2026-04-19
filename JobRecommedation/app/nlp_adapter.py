import logging
from app.candidat_profile import CandidatProfile
from app.recommender import recommend

logger = logging.getLogger(__name__)


class JobMatcher:

    def __init__(self, jobs: list[dict]) -> None:
        logger.info("NLP module Étudiant 2 chargé.")

    def match(
        self,
        profile: dict,
        top_n: int = 5,
        min_score: float = 0.0,
    ) -> list[dict]:

        # Construire le profil avec ses champs exacts
        candidat = CandidatProfile(
            titre_souhaite=" ".join(profile.get("skills", [])),
            competences=profile.get("skills", []),
            experience_annees=profile.get("experience_years", 0),
            localisation=profile.get("desired_location", None),
            description_libre=profile.get("bio", ""),
        )

        # Appeler sa fonction
        raw_results = recommend(candidat, top_k=top_n)

        # Convertir vers le format de ton API
        results = []
        for i, item in enumerate(raw_results):
            if item["score"] >= min_score:
                results.append({
                    "job": {
                        "id": f"j{i+1:03d}",
                        "title": item.get("position", ""),
                        "company": item.get("company", ""),
                        "location": item.get("location", ""),
                        "description": "",
                        "skills_required": [],
                        "experience_years": 0,
                        "salary_range": "",
                        "job_type": "full-time",
                        "posted_date": None,
                    },
                    "score": item["score"],
                    "matching_skills": profile.get("skills", []),
                    "missing_skills": [],
                })
        return results