import joblib
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from app.preprocessing import preprocess_dataframe

BASE = Path(__file__).parent

def build_and_save_vectors(csv_path: str):
    df = pd.read_csv(csv_path)
    df = preprocess_dataframe(df)

    vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
    job_vectors = vectorizer.fit_transform(df["cleaned"])

    joblib.dump(vectorizer, BASE / "vectorizer.pkl")
    joblib.dump(job_vectors, BASE / "job_vectors.pkl")

    df[["Position", "Company", "Location", "URL"]].to_csv(BASE / "jobs_index.csv", index=False)
    print(f"✅ {job_vectors.shape[0]} offres vectorisées")

def load_vectorizer():
    vectorizer = joblib.load(BASE / "vectorizer.pkl")
    job_vectors = joblib.load(BASE / "job_vectors.pkl")
    jobs_df = pd.read_csv(BASE / "jobs_index.csv")
    return vectorizer, job_vectors, jobs_df