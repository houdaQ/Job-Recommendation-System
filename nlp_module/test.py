from recommender import recommend
from candidat_profile import CandidatProfile

profil = CandidatProfile(
    titre_souhaite='Full Stack Software Engineer',
    competences=['React', 'Python', 'Node.js', 'AWS'],
    experience_annees=3,
    localisation='Remote',
    description_libre='web application REST API cloud deployment'
)

resultats = recommend(profil, top_k=5)
for r in resultats:
    print(f"{r['score']:.3f} — {r['position']} @ {r['company']}")