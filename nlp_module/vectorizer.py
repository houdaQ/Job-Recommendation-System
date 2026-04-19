import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from preprocessing import preprocess_dataframe

def build_and_save_vectors(csv_path: str):
    df = pd.read_csv(csv_path)
    df = preprocess_dataframe(df)

    vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
    job_vectors = vectorizer.fit_transform(df["cleaned"])

    joblib.dump(vectorizer, "vectorizer.pkl")
    joblib.dump(job_vectors, "job_vectors.pkl")

    df[["Position", "Company", "Location", "URL"]].to_csv("jobs_index.csv", index=False)
    print(f"✅ {job_vectors.shape[0]} offres vectorisées")

def load_vectorizer():
    vectorizer = joblib.load("vectorizer.pkl")
    job_vectors = joblib.load("job_vectors.pkl")
    jobs_df = pd.read_csv("jobs_index.csv")
    return vectorizer, job_vectors, jobs_df

if __name__ == "__main__":
    build_and_save_vectors("../data/jobs.csv")