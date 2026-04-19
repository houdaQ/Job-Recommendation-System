import re
import pandas as pd

STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "have", "has",
    "we", "you", "they", "he", "she", "it", "this", "that", "i",
    "by", "as", "from", "using", "needed", "required", "experience",
    "le", "la", "les", "un", "une", "des", "et", "ou", "en", "de",
    "our", "your", "their", "will", "would", "could", "should",
}

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'\n|\r', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess(text: str) -> str:
    text = clean_text(text)
    tokens = text.split()
    tokens = [
        t for t in tokens
        if t not in STOPWORDS
        and len(t) > 2
        and t.isalpha()
    ]
    return " ".join(tokens)

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["Job_Description"]).copy()
    df["cleaned"] = df["Job_Description"].apply(preprocess)
    print(f"✅ {len(df)} offres prétraitées")
    return df