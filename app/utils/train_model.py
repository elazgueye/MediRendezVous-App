import os
import json
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import pandas as pd

# French preprocessing: stopwords + Snowball stemmer via nltk
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
try:
    import spacy
except Exception:
    spacy = None


def ensure_nltk():
    try:
        stopwords.words('french')
    except Exception:
        nltk.download('stopwords')


def preprocess_text_fr(text: str, stemmer=None, stopset=None, nlp=None):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r"[^a-zàâäéèêëïîôöùûüçœæ0-9\s-]", ' ', text)
    # Prefer spaCy lemmatization if available
    if nlp is not None:
        doc = nlp(text)
        tokens = []
        for tok in doc:
            t = tok.lemma_.strip().lower()
            if not t or t in stopset:
                continue
            tokens.append(t)
        return ' '.join(tokens)

    tokens = [t.strip() for t in re.split(r"\s+", text) if t.strip()]
    if stopset:
        tokens = [t for t in tokens if t not in stopset]
    if stemmer:
        tokens = [stemmer.stem(t) for t in tokens]
    return ' '.join(tokens)


def ensure_spacy_model(model_name='fr_core_news_sm'):
    if spacy is None:
        return None
    try:
        return spacy.load(model_name)
    except Exception:
        try:
            from spacy.cli import download
            download(model_name)
            return spacy.load(model_name)
        except Exception:
            return None


def train(data_path='data/diagnostics.csv', model_dir='app/models_ia'):
    os.makedirs(model_dir, exist_ok=True)
    df = pd.read_csv(data_path)
    cols_lower = [c.lower() for c in df.columns]

    # Format 1: colonnes 'symptomes' et 'orientation'
    if 'symptomes' in cols_lower and 'orientation' in cols_lower:
        df = df.rename(columns={c: c.lower() for c in df.columns})
        df = df.dropna(subset=['symptomes', 'orientation'])
        X = df['symptomes'].astype(str).values
        y = df['orientation'].astype(str).values
    else:
        # Format 2: large table binaire où la première colonne est la maladie/étiquette
        # Construire un champ 'symptomes' en concaténant les noms de colonnes où la valeur est 1
        if df.shape[1] < 2:
            raise ValueError('CSV non reconnu : pas assez de colonnes.')
        label_col = df.columns[0]
        symptom_cols = list(df.columns[1:])
        def row_to_text(row):
            present = [sym for sym in symptom_cols if str(row[sym]) not in ('0', '0.0', 'False', 'false', 'nan', '')]
            return ', '.join(present) if present else ''

        df['symptomes'] = df.apply(row_to_text, axis=1)
        df['orientation'] = df[label_col].astype(str)
        df = df.dropna(subset=['symptomes', 'orientation'])
        X = df['symptomes'].astype(str).values
        y = df['orientation'].astype(str).values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # Prétraitement FR
    ensure_nltk()
    fr_stop = set(stopwords.words('french'))
    stemmer = FrenchStemmer()
    nlp = ensure_spacy_model()

    X_clean = [preprocess_text_fr(x, stemmer=stemmer, stopset=fr_stop, nlp=nlp) for x in X]

    X_train, X_test, y_train, y_test = train_test_split(X_clean, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

    vec = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_t = vec.fit_transform(X_train)
    X_test_t = vec.transform(X_test)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train_t, y_train)

    preds = clf.predict(X_test_t)
    acc = float(accuracy_score(y_test, preds))
    report = classification_report(y_test, preds, target_names=le.classes_, output_dict=True)

    joblib.dump(clf, os.path.join(model_dir, 'model.joblib'))
    joblib.dump(vec, os.path.join(model_dir, 'vectorizer.joblib'))
    joblib.dump(le, os.path.join(model_dir, 'label_encoder.joblib'))

    metrics = {'accuracy': acc, 'report': report}
    with open(os.path.join(model_dir, 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f'Model trained. Accuracy: {acc:.4f}. Artifacts saved in {model_dir}')


if __name__ == '__main__':
    train()
