import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import os

if not os.path.exists('modele'):
    os.makedirs('modele')

def train():
    # 1. Chargement du fichier
    df = pd.read_csv('data/diagnostics.csv')
    
    # La première colonne est 'Maladie', les autres sont les symptômes
    label_col = df.columns[0]
    symptom_cols = df.columns[1:]
    
    # Transformer les colonnes binaires en une liste de symptômes textuels
    def row_to_text(row):
        return ', '.join([col for col in symptom_cols if row[col] == 1.0])

    X = df.apply(row_to_text, axis=1)
    y = df[label_col]

    # 2. Préparation
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer()
    X_vec = vec.fit_transform(X)

    # 3. Entraînement
    model = XGBClassifier()
    model.fit(X_vec, y_enc)

    # 4. Sauvegarde
    joblib.dump(model, 'modele/model.pkl')
    joblib.dump(vec, 'modele/vectorizer.pkl')
    joblib.dump(le, 'modele/encoder.pkl')
    
    print("Succès : Le nouveau cerveau est prêt !")

if __name__ == '__main__':
    train()