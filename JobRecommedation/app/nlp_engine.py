import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "have", "has",
    "we", "you", "they", "he", "she", "it", "this", "that", "i",
    "by", "as", "from", "using", "needed", "required", "experience",
    "le", "la", "les", "un", "une", "des", "et", "ou", "en", "de",
}

def preprocess(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z0-9#+\-\.]+", text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def tf(tokens):
    count = Counter(tokens)
    total = len(tokens) or 1
    return {term: freq / total for term, freq in count.items()}

def build_tfidf_matrix(documents):
    n = len(documents)
    df = Counter()
    for doc in documents:
        for term in set(doc):
            df[term] += 1
    idf = {term: math.log(n / freq) + 1.0 for term, freq in df.items()}
    vectors = []
    for doc in documents:
        tf_scores = tf(doc)
        vec = {t: tf_scores[t] * idf.get(t, 1.0) for t in tf_scores}
        vectors.append(vec)
    return vectors, idf

def cosine_similarity(vec_a, vec_b):
    common = set(vec_a) & set(vec_b)
    if not common:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v**2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v**2 for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

class JobMatcher:
    def __init__(self, jobs):
        self.jobs = jobs
        self._build_index()

    def _build_index(self):
        docs = [f"{j.get('title','')} {j.get('description','')} {' '.join(j.get('skills_required',[]))}" for j in self.jobs]
        tokenized = [preprocess(d) for d in docs]
        self.job_vectors, self.idf = build_tfidf_matrix(tokenized)

    def match(self, profile, top_n=5, min_score=0.0):
        skills_text = " ".join(profile.get("skills", []))
        bio = profile.get("bio", "") or ""
        tokens = preprocess(f"{skills_text} {bio}")
        tf_scores = tf(tokens)
        candidate_vec = {t: tf_scores[t] * self.idf.get(t, 1.0) for t in tf_scores}
        candidate_skills = {s.lower() for s in profile.get("skills", [])}

        results = []
        for job, job_vec in zip(self.jobs, self.job_vectors):
            score = cosine_similarity(candidate_vec, job_vec)
            exp_bonus = 0.05 if profile.get("experience_years", 0) >= job.get("experience_years", 0) else 0.0
            final_score = min(score + exp_bonus, 1.0)
            if final_score >= min_score:
                results.append({
                    "job": job,
                    "score": round(final_score, 4),
                    "matching_skills": [s for s in job.get("skills_required", []) if s.lower() in candidate_skills],
                    "missing_skills": [s for s in job.get("skills_required", []) if s.lower() not in candidate_skills],
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]