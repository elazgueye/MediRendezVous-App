from pathlib import Path

files = {
    Path(r"c:\Users\DELL\Desktop\medi_rendez_vous\app\__init__.py"): '''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import des modèles pour que SQLAlchemy les connaisse
from app import models
from app.models import Medecin, Disponibilite, Specialite

# Création automatique des tables au démarrage si elles n'existent pas
with app.app_context():
    def ensure_column(table_name, column_name, column_type):
        existing = db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        if not any(row[1] == column_name for row in existing):
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            db.session.commit()

    db.create_all()
    ensure_column('medecin', 'email', 'VARCHAR(120)')
    ensure_column('medecin', 'user_id', 'INTEGER')
    ensure_column('patient', 'user_id', 'INTEGER')
    ensure_column('rendez_vous', 'patient_id', 'INTEGER')
    ensure_column('rendez_vous', 'patient_email', 'VARCHAR(120)')
    ensure_column('rendez_vous', 'horaire', 'VARCHAR(50)')
    ensure_column('rendez_vous', 'statut', 'VARCHAR(30)')
    ensure_column('rendez_vous', 'motif', 'VARCHAR(255)')
    db.create_all()

    # Données initiales pour démonstration
    if Medecin.query.count() == 0:
        medecins = [
            Medecin(nom='Dr. Léa Dubois', specialite='Généraliste', prix='60€', email='lea.dubois@mediris.fr'),
            Medecin(nom='Dr. Karim El Hadi', specialite='Cardiologue', prix='90€', email='karim.elhadi@mediris.fr'),
            Medecin(nom='Dr. Emma Lavergne', specialite='Dermatologue', prix='80€', email='emma.lavergne@mediris.fr'),
        ]
        db.session.add_all(medecins)
        db.session.commit()

    if Disponibilite.query.count() == 0:
        medecins = Medecin.query.all()
        disponibilites = []
        if len(medecins) > 0:
            disponibilites.extend([
                Disponibilite(medecin_id=medecins[0].id, date='2026-06-15', plage_horaire='09:00 - 10:00'),
                Disponibilite(medecin_id=medecins[0].id, date='2026-06-15', plage_horaire='14:00 - 15:00'),
            ])
        if len(medecins) > 1:
            disponibilites.append(Disponibilite(medecin_id=medecins[1].id, date='2026-06-16', plage_horaire='10:30 - 11:30'))
        if len(medecins) > 2:
            disponibilites.append(Disponibilite(medecin_id=medecins[2].id, date='2026-06-17', plage_horaire='13:00 - 14:00'))
        if disponibilites:
            db.session.add_all(disponibilites)
            db.session.commit()

    if Specialite.query.count() == 0:
        specialites = [
            Specialite(nom='Généraliste'),
            Specialite(nom='Cardiologie'),
            Specialite(nom='Dermatologie'),
            Specialite(nom='Pédiatrie'),
            Specialite(nom='Gynécologie'),
        ]
        db.session.add_all(specialites)
        db.session.commit()

from app import routes
''',
}

for path, content in files.items():
    path.write_text(content, encoding='utf-8')
print('patched files')
