import os
import json
from datetime import datetime
import joblib

SYMPTOM_KEYWORDS = {
    'fièvre': ['fièvre', 'temperature', 'température', 'febre', 'chaud'],
    'toux': ['toux', 'tousse', 'tousser'],
    'fatigue': ['fatigue', 'fatigué', 'épuisé', 'lassitude'],
    'mal de tête': ['mal de tête', 'céphalée', 'maux de tête'],
    'douleurs abdominales': ['douleur abdominale', 'douleurs abdominales', 'césarienne', 'ventre'],
    'difficultés respiratoires': ['difficulté respiratoire', 'essoufflement', 'respiration difficile', 'respirer'],
    'nausées': ['nausée', 'nausées', 'malaise', 'haut-le-cœur'],
    'vomissements': ['vomissement', 'vomissements', 'vomir'],
}
EMERGENCY_SIGNS = ['douleur thoracique', 'difficulté respiratoire sévère', 'saignement', 'perte de conscience']
SPECIALTY_PATTERNS = {
    'fièvre': 'Consulter un médecin généraliste.',
    'toux': 'Consulter un médecin généraliste.',
    'fatigue': 'Consulter un médecin généraliste.',
    'mal de tête': 'Consulter un médecin généraliste.',
    'douleurs abdominales': 'Consulter un gastro-entérologue.',
    'difficultés respiratoires': 'Consulter un pneumologue.',
    'nausées': 'Consulter un médecin généraliste.',
    'vomissements': 'Consulter un médecin généraliste.',
}


def analyze_symptoms(symptomes: str) -> str:
    # Si un modèle est présent, l'utiliser d'abord
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_dir = os.path.join(base_dir, 'models_ia')
    model_path = os.path.join(model_dir, 'model.joblib')
    vec_path = os.path.join(model_dir, 'vectorizer.joblib')
    le_path = os.path.join(model_dir, 'label_encoder.joblib')

    texte = (symptomes or '').strip()
    if os.path.exists(model_path) and os.path.exists(vec_path) and os.path.exists(le_path):
        try:
            clf = joblib.load(model_path)
            vec = joblib.load(vec_path)
            le = joblib.load(le_path)
            X_t = vec.transform([texte])
            pred = clf.predict(X_t)
            label = le.inverse_transform(pred)[0]
            return f'Orientation (IA) : {label}'
        except Exception:
            pass

    # Fallback rule-based
    texte_low = texte.lower()
    if any(term in texte_low for term in EMERGENCY_SIGNS):
        return 'Orientation : consultez les urgences immédiatement.'

    detected = []
    for label, keywords in SYMPTOM_KEYWORDS.items():
        if any(keyword in texte_low for keyword in keywords):
            detected.append(label)

    if 'fièvre' in detected and 'toux' in detected:
        return 'Orientation : consultez un médecin généraliste.'
    if 'difficultés respiratoires' in detected:
        return 'Orientation : consultez un pneumologue ou les urgences selon votre état.'
    if 'douleurs abdominales' in detected:
        return 'Orientation : consultez un gastro-entérologue.'
    if detected:
        return 'Orientation : consultez un médecin généraliste pour une évaluation plus approfondie.'
    return 'Orientation : la situation semble légère, mais prenez rendez-vous avec un médecin si les symptômes persistent.'
