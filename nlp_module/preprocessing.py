import spacy, re, pandas as pd

nlp = spacy.load("en_core_web_sm") 

def clean_text(text: str) -> str: 
    text = text.lower()
    text = re.sub(r'\\n', ' ', text) 
    text = re.sub(r'\n|\r', ' ', text) 
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip() 
    return text 

def preprocess(text: str) -> str:
     text = clean_text(text)
     doc = nlp(text) 
     tokens = [ token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.is_alpha and len(token.text) > 2 ] 
     return " ".join(tokens)

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
     df = df.dropna(subset=["Job_Description"]).copy()
     df["cleaned"] = df["Job_Description"].apply(preprocess) 
     print(f"✅ {len(df)} offres prétraitées")
     return df