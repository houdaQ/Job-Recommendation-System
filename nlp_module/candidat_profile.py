from pydantic import BaseModel
from typing import List, Optional

class CandidatProfile(BaseModel):
    titre_souhaite: str
    competences: List[str]
    experience_annees: int
    localisation: Optional[str] = None
    description_libre: str

    def to_text(self) -> str:
        skills_text = " ".join(self.competences)
        return f"{self.titre_souhaite} {skills_text} {self.description_libre}"