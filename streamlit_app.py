import streamlit as st
import requests
import json

# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Job Recommendation System",
    layout="wide",
)

# ──────────────────────────────────────────────
#  STYLE
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .header {
        background: #1a2e4a;
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.8rem;
    }
    .header h1 { margin: 0; font-size: 1.8rem; font-weight: 600; }
    .header p  { margin: 0.4rem 0 0; color: #94b4d1; font-size: 0.95rem; }

    .job-card {
        background: #ffffff;
        border: 1px solid #dde3ec;
        border-left: 4px solid #1a2e4a;
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.9rem;
    }
    .job-card h3 {
        margin: 0 0 0.3rem;
        font-size: 1rem;
        font-weight: 600;
        color: #1a2e4a;
    }
    .job-card .meta {
        font-size: 0.82rem;
        color: #5a6a7a;
        margin-bottom: 0.5rem;
    }
    .job-card .desc {
        font-size: 0.83rem;
        color: #3d4a5a;
        line-height: 1.5;
        border-top: 1px solid #edf0f5;
        padding-top: 0.6rem;
        margin-top: 0.5rem;
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        color: white;
    }
    .badge-high { background: #1d7a4a; }
    .badge-mid  { background: #b06000; }
    .badge-low  { background: #9b1c1c; }

    .stat-box {
        border: 1px solid #dde3ec;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
        background: #f8fafc;
    }
    .stat-box .num { font-size: 2rem; font-weight: 700; color: #1a2e4a; }
    .stat-box .lbl { font-size: 0.8rem; color: #5a6a7a; }

    .status-ok  { color: #1d7a4a; font-weight: 600; font-size: 0.85rem; }
    .status-err { color: #9b1c1c; font-weight: 600; font-size: 0.85rem; }

    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a2e4a;
        border-bottom: 2px solid #1a2e4a;
        padding-bottom: 0.3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  API HELPERS
# ──────────────────────────────────────────────
def api_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.json() if r.ok else None
    except Exception:
        return None


def api_recommend(payload: dict, top_n: int, min_score: float):
    try:
        r = requests.post(
            f"{API_BASE}/recommend/",
            json=payload,
            params={"top_n": top_n, "min_score": min_score},
            timeout=10,
        )
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Impossible de se connecter a l'API. Verifiez que FastAPI tourne sur le port 8000."
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, f"Erreur API : {detail}"
    except Exception as e:
        return None, f"Erreur : {e}"


def api_list_jobs(location=None, min_exp=None):
    params = {}
    if location:
        params["location"] = location
    if min_exp is not None:
        params["min_experience"] = min_exp
    try:
        r = requests.get(f"{API_BASE}/jobs/", params=params, timeout=5)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "API non disponible."
    except Exception as e:
        return None, str(e)


# ──────────────────────────────────────────────
#  UTILS
# ──────────────────────────────────────────────
def badge_class(score: float) -> str:
    if score >= 0.35:
        return "badge-high"
    if score >= 0.15:
        return "badge-mid"
    return "badge-low"


def render_recommendation(rec: dict, rank: int):
    job   = rec["job"]
    score = rec["score"]
    bc    = badge_class(score)
    desc  = (job.get("description") or "")[:400].strip()
    if len(job.get("description") or "") > 400:
        desc += "..."

    st.markdown(f"""
    <div class="job-card">
        <h3>#{rank} &nbsp; {job.get('title', '—')}</h3>
        <div class="meta">
            Entreprise : <strong>{job.get('company', '—')}</strong>
            &nbsp;|&nbsp;
            Localisation : <strong>{job.get('location', '—')}</strong>
            &nbsp;|&nbsp;
            Contrat : <strong>{job.get('job_type', '—')}</strong>
        </div>
        <span class="badge {bc}">Score de correspondance : {score:.0%}</span>
        <div class="desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def render_job_card(job: dict):
    desc = (job.get("description") or "")[:350].strip()
    if len(job.get("description") or "") > 350:
        desc += "..."

    st.markdown(f"""
    <div class="job-card">
        <h3>{job.get('title', '—')}</h3>
        <div class="meta">
            Entreprise : <strong>{job.get('company', '—')}</strong>
            &nbsp;|&nbsp;
            Localisation : <strong>{job.get('location', '—')}</strong>
            &nbsp;|&nbsp;
            Contrat : <strong>{job.get('job_type', '—')}</strong>
            &nbsp;|&nbsp;
            ID : <code>{job.get('id', '—')}</code>
        </div>
        <div class="desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Page",
        ["Recommandations", "Parcourir les offres", "Documentation"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Statut de l'API")
    health = api_health()
    if health:
        st.markdown('<p class="status-ok">Connectee</p>', unsafe_allow_html=True)
        st.caption(f"Offres indexees : **{health.get('jobs_indexed', '?')}**")
        st.caption(f"Version : {health.get('version', '?')}")
    else:
        st.markdown('<p class="status-err">Non disponible</p>', unsafe_allow_html=True)
        st.caption("Lancez d'abord le serveur FastAPI.")

    st.markdown("---")
    st.caption(
        "Base de donnees : 22 offres Full Stack Software Engineer "
        "scrappees depuis Jooble. Matching par similarite cosinus sur la description textuelle."
    )


# ──────────────────────────────────────────────
#  HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="header">
    <h1>Systeme de Recommandation d'Emploi</h1>
    <p>Analyse de profil par NLP — TF-IDF + similarite cosinus — FastAPI + Streamlit</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE 1 — RECOMMANDATIONS
# ══════════════════════════════════════════════
if page == "Recommandations":

    st.markdown('<div class="section-title">Profil du candidat</div>', unsafe_allow_html=True)
    st.caption(
        "Le moteur NLP construit un vecteur textuel a partir de vos competences et description, "
        "puis le compare aux descriptions des offres via la similarite cosinus (TF-IDF)."
    )

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Nom complet *",
                placeholder="Ex : Alice Martin",
            )
            skills_raw = st.text_area(
                "Competences * — une par ligne",
                placeholder="Python\nReact\nSQL\nFastAPI\nDocker",
                height=160,
                help="Chaque ligne correspond a une competence. Ce champ est obligatoire.",
            )
            experience = st.number_input(
                "Annees d'experience *",
                min_value=0, max_value=30, value=2, step=1,
            )

        with col2:
            location = st.text_input(
                "Localisation souhaitee",
                placeholder="Ex : Remote, California, Maryland...",
                help="Optionnel. Localisations disponibles : Remote, California, Maryland, Michigan...",
            )
            bio = st.text_area(
                "Description du profil",
                placeholder=(
                    "Ex : Developpeur Full Stack avec 2 ans d'experience en Python et React. "
                    "J'ai travaille sur des APIs REST, des bases de donnees PostgreSQL et "
                    "des applications cloud. Interesse par les systemes distribues."
                ),
                height=160,
                help=(
                    "C'est le champ le plus important pour le matching NLP. "
                    "Decrivez vos experiences, projets et technologies utilisees."
                ),
            )
            top_n = st.slider(
                "Nombre de resultats",
                min_value=1, max_value=22, value=5,
            )
            min_score = st.slider(
                "Score minimum de correspondance",
                min_value=0.0, max_value=1.0,
                value=0.0, step=0.05, format="%.2f",
            )

        submitted = st.form_submit_button(
            "Lancer la recommandation", use_container_width=True
        )

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Le nom est obligatoire.")
        skills = [s.strip() for s in skills_raw.strip().splitlines() if s.strip()]
        if not skills:
            errors.append("Ajoutez au moins une competence.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            payload = {
                "name": name.strip(),
                "skills": skills,
                "experience_years": int(experience),
                "desired_location": location.strip() or None,
                "desired_job_type": None,
                "bio": bio.strip() or None,
            }

            with st.spinner("Analyse en cours..."):
                data, err = api_recommend(payload, top_n, min_score)

            if err:
                st.error(err)
            else:
                recs  = data.get("recommendations", [])
                total = data.get("total_jobs_analyzed", 0)

                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="num">{len(recs)}</div>
                        <div class="lbl">Offres recommandees</div>
                    </div>""", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="num">{total}</div>
                        <div class="lbl">Offres analysees</div>
                    </div>""", unsafe_allow_html=True)
                with m3:
                    best = f"{recs[0]['score']:.0%}" if recs else "—"
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="num">{best}</div>
                        <div class="lbl">Meilleur score</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if recs:
                    st.success(
                        f"{len(recs)} offre(s) trouvee(s) pour {name} sur {total} analysees."
                    )
                    st.markdown(
                        '<div class="section-title">Resultats</div>',
                        unsafe_allow_html=True,
                    )
                    for i, rec in enumerate(recs, 1):
                        render_recommendation(rec, i)

                    with st.expander("Exporter les resultats en JSON"):
                        st.download_button(
                            label="Telecharger recommandations.json",
                            data=json.dumps(data, ensure_ascii=False, indent=2),
                            file_name="recommandations.json",
                            mime="application/json",
                        )
                else:
                    st.warning(
                        "Aucune offre ne correspond avec ces criteres. "
                        "Essayez de baisser le score minimum ou d'enrichir la description."
                    )


# ══════════════════════════════════════════════
#  PAGE 2 — PARCOURIR LES OFFRES
# ══════════════════════════════════════════════
elif page == "Parcourir les offres":

    st.markdown(
        '<div class="section-title">Toutes les offres disponibles</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        f_location = st.text_input(
            "Filtrer par localisation",
            placeholder="Ex : Remote, California, Maryland...",
        )
    with col2:
        f_exp = st.number_input(
            "Experience maximum (annees)",
            min_value=0, max_value=30, value=30, step=1,
        )

    jobs, err = api_list_jobs(
        location=f_location or None,
        min_exp=f_exp,
    )

    if err:
        st.error(err)
    elif jobs is not None:
        st.info(f"{len(jobs)} offre(s) trouvee(s)")

        if jobs:
            st.markdown(
                '<div class="section-title">Liste des offres</div>',
                unsafe_allow_html=True,
            )
            for job in jobs:
                render_job_card(job)
        else:
            st.warning("Aucune offre ne correspond aux filtres appliques.")

        with st.expander("Voir toutes les localisations disponibles"):
            all_jobs, _ = api_list_jobs()
            if all_jobs:
                locs = sorted(set(j["location"] for j in all_jobs if j.get("location")))
                st.write(", ".join(locs))


# ══════════════════════════════════════════════
#  PAGE 3 — DOCUMENTATION
# ══════════════════════════════════════════════
elif page == "Documentation":

    st.markdown(
        '<div class="section-title">Documentation du projet</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Architecture technique")
        st.markdown("""
        | Composant | Technologie |
        |-----------|-------------|
        | Backend API | FastAPI + Uvicorn |
        | Moteur NLP | TF-IDF (scikit-learn) |
        | Mesure de similarite | Cosinus |
        | Donnees | JSON — 22 offres Jooble |
        | Interface | Streamlit |
        """)

        st.markdown("#### Structure d'une offre (jobs.json)")
        st.markdown("""
        | Champ | Type | Remarque |
        |-------|------|----------|
        | `id` | string | j001, j002... |
        | `title` | string | Intitule du poste |
        | `company` | string | Nom de l'entreprise |
        | `location` | string | Ville / Pays |
        | `description` | string | Base du matching NLP |
        | `job_type` | string | Toujours full-time |
        | `experience_years` | int | Toujours 0 dans la base |
        | `skills_required` | list | Vide dans la base |
        """)

    with col2:
        st.markdown("#### Endpoints de l'API")
        st.markdown("""
        | Methode | Endpoint | Description |
        |---------|----------|-------------|
        | GET | `/health` | Statut et nombre d'offres |
        | POST | `/recommend/` | Obtenir des recommandations |
        | GET | `/jobs/` | Lister / filtrer les offres |
        | GET | `/jobs/{id}` | Detail d'une offre |
        | POST | `/jobs/` | Ajouter une offre |
        | DELETE | `/jobs/{id}` | Supprimer une offre |
        """)

        st.markdown("#### Fonctionnement du matching NLP")
        st.markdown("""
        1. Le profil est converti en texte : `competences + description`
        2. Nettoyage : minuscules, suppression des stopwords
        3. Vectorisation TF-IDF via le modele pre-entraine (`vectorizer.pkl`)
        4. Calcul de la similarite cosinus avec chaque offre (`job_vectors.pkl`)
        5. Classement des offres par score decroissant
        """)

        st.info(
            "Le matching repose uniquement sur la description textuelle car "
            "les champs 'skills_required' et 'experience_years' sont vides "
            "dans la base de donnees actuelle."
        )

    st.markdown("---")
    health = api_health()
    if health:
        st.success(
            f"API operationnelle — {health.get('jobs_indexed')} offres indexees — "
            f"version {health.get('version')}"
        )
        st.markdown(
            "Documentation Swagger interactive disponible sur "
            "[http://localhost:8000/docs](http://localhost:8000/docs)"
        )
    else:
        st.error(
            "API non disponible. "
            "Lancez : uvicorn app.main:app --reload --port 8000 "
            "depuis le dossier JobRecommedation/"
        )