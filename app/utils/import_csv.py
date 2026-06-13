import os
import pandas as pd


def validate_csv(path: str):
    """Charge et valide un CSV de diagnostics attendus.

    Attendu: colonnes 'symptomes' et 'orientation' (insensibles à la casse).
    Retourne un DataFrame pandas prêt pour le traitement.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable: {path}")

    df = pd.read_csv(path)
    cols = [c.lower() for c in df.columns]
    if 'symptomes' not in cols or 'orientation' not in cols:
        raise ValueError("Le CSV doit contenir au moins les colonnes 'symptomes' et 'orientation'.")

    # Normaliser noms de colonnes
    mapping = {orig: orig.lower() for orig in df.columns}
    df = df.rename(columns=mapping)

    # Supprimer lignes vides
    df = df.dropna(subset=['symptomes', 'orientation']).reset_index(drop=True)
    return df


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Valide un CSV de diagnostics.')
    parser.add_argument('csv', help='Chemin vers le CSV (ex: data/diagnostics.csv)')
    args = parser.parse_args()
    df = validate_csv(args.csv)
    print(f'Chargé {len(df)} entrées. Colonnes: {list(df.columns)}')
    print(df.head(5).to_string(index=False))
