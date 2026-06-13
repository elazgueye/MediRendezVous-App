MédiRendez-vous — instructions pour l'intégration et l'entraînement du modèle IA

Résumé

Ce dépôt contient une application Flask simple pour la prise de rendez-vous et un outil de triage IA.
Le projet peut utiliser un dataset CSV local pour entraîner un classifieur textuel (TF-IDF + LogisticRegression) afin d'orienter les symptômes.

Où placer votre CSV

- Placez votre fichier CSV à la racine du projet dans le dossier `data/`.
  Exemple : `data/diagnostics.csv`
- Format accepté :
  - Format 1 (simple) : colonnes `symptomes` et `orientation` (noms insensibles à la casse).
    - Chaque ligne : un texte libre de symptômes et l'orientation correspondante.
  - Format 2 (large tableau binaire) : la première colonne est la "maladie" ou l'étiquette, les colonnes suivantes sont des symptômes (0/1 ou 0.0/1.0).
    - Le script construit un champ texte `symptomes` en concaténant les noms des symptômes présents pour chaque ligne.

Sécurité des données

- Ne placez pas de données patients identifiables ici. Ajoutez tout fichier sensible à `.gitignore`.

Installer les dépendances

Sous Windows (PowerShell) :

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Exécuter l'application

```bash
python run.py
# puis ouvrez http://127.0.0.1:5000
```

Réentraîner le modèle (local)

- Script prévu : `retrain.py` (à la racine)
- Exemple :

```bash
# activez votre venv (voir ci-dessus)
python retrain.py
```

Le script utilise `data/diagnostics.csv` et sauvegarde les artefacts dans `app/models_ia/` :
- `model.joblib`, `vectorizer.joblib`, `label_encoder.joblib`, `metrics.json`.

Afficher la métrique sur la page d'accueil

- Si `app/models_ia/metrics.json` est présent, la précision (accuracy) sera affichée sur la page d'accueil.

Scripts utiles

- `app/utils/import_csv.py` : valider un CSV local.
- `app/utils/train_model.py` : code d'entraînement (TF-IDF + LogisticRegression).
- `app/services/diagnostic.py` : utilise le modèle enregistré s'il existe, sinon retombe sur la logique basée sur règles.

Prochaines améliorations possibles

- Nettoyage linguistique (lemmatisation/français), suppression des stopwords.
- Entraînement d'un modèle plus puissant (ex: fine-tuning transformers si vous disposez d'un dataset suffisamment grand).
- Interface d'administration pour lancer l'entraînement depuis l'UI et visualiser la matrice de confusion.

Contact

Si vous voulez, je peux :
- ajouter la lemmatisation/français et améliorer le prétraitement (recommandé pour de meilleurs résultats),
- créer une page admin pour réentraîner et afficher les métriques.

