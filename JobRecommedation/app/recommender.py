import numpy as np 
from sklearn.metrics.pairwise import cosine_similarity 
from app.preprocessing import preprocess
from app.vectorizer import load_vectorizer
from app.candidat_profile import CandidatProfile 

vectorizer, job_vectors, jobs_df = load_vectorizer() 
def recommend(profil: CandidatProfile, top_k: int = 5) -> list:
     query_text = preprocess(profil.to_text())
     query_vec = vectorizer.transform([query_text])
     scores = cosine_similarity(query_vec, job_vectors).flatten()
     top_indices = np.argsort(scores)[::-1][:top_k] 
     results = [] 
     
     for idx in top_indices: 
         results.append({ "position": jobs_df.iloc[idx]["Position"], "company": jobs_df.iloc[idx]["Company"], "location": jobs_df.iloc[idx]["Location"], "url": jobs_df.iloc[idx]["URL"], "score": round(float(scores[idx]), 4) }) 
         return results