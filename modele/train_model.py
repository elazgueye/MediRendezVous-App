import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import os

# Création du dossier si besoin
if not os.path.exists('modele'):
    os.makedirs('modele')

def train():
    # 1. Chargement
    # Remplace 'data/diagnostics.csv' par le chemin exact de ton fichier
    df = pd.read_csv('data/diagnostics.csv')
    X = df['symptomes'].astype(str)
    y = df['orientation'].astype(str)

    # 2. Préparation
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    
    vec = TfidfVectorizer(max_features=2000)
    X_vec = vec.fit_transform(X)

    # 3. Entraînement avec XGBoost (plus efficace que la régression logistique)
    model = XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=6)
    model.fit(X_vec, y_enc)

    # 4. Sauvegarde
    joblib.dump(model, 'modele/model.pkl')
    joblib.dump(vec, 'modele/vectorizer.pkl')
    joblib.dump(le, 'modele/encoder.pkl')
    
    print("Modèle entraîné et sauvegardé dans le dossier 'modele/'.")

if __name__ == '__main__':
    train()