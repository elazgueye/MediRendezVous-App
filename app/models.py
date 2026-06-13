from datetime import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')
    actif = db.Column(db.Boolean, default=True)
    patient = db.relationship('Patient', backref='user', uselist=False)
    medecin = db.relationship('Medecin', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Specialite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    medecins = db.relationship('Medecin', backref='specialite_rel', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    prenom = db.Column(db.String(80))
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(30))
    preference_specialite = db.Column(db.String(100))
    preference_medecin = db.Column(db.String(100))
    horaires_preferes = db.Column(db.String(120))
    historique_medical = db.Column(db.Text)
    rendezvous = db.relationship('RendezVous', backref='patient', lazy=True)
    consultations = db.relationship('Consultation', backref='patient', lazy=True)
    diagnostics = db.relationship('DiagnosticIA', backref='patient', lazy=True)

class Medecin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    prenom = db.Column(db.String(80))
    nom = db.Column(db.String(100), nullable=False)
    specialite = db.Column(db.String(100), nullable=False)
    specialite_id = db.Column(db.Integer, db.ForeignKey('specialite.id'), nullable=True)
    prix = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(30))
    numero_ordre = db.Column(db.String(80))
    experience = db.Column(db.String(80))
    disponibilites = db.relationship('Disponibilite', backref='medecin', lazy=True)
    rendezvous = db.relationship('RendezVous', backref='medecin', lazy=True)
    consultations = db.relationship('Consultation', backref='medecin', lazy=True)

class Disponibilite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecin.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    plage_horaire = db.Column(db.String(50), nullable=False)
    est_disponible = db.Column(db.Boolean, default=True)

class RendezVous(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    patient_nom = db.Column(db.String(100), nullable=False)
    patient_email = db.Column(db.String(120))
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecin.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    horaire = db.Column(db.String(50))
    statut = db.Column(db.String(30), default='En attente')
    motif = db.Column(db.String(255))
    consultation = db.relationship('Consultation', backref='rendezvous', uselist=False)

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rendezvous_id = db.Column(db.Integer, db.ForeignKey('rendez_vous.id'), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecin.id'), nullable=False)
    compte_rendu = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.relationship('NoteMedicale', backref='consultation', lazy=True)

class NoteMedicale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecin.id'), nullable=False)
    texte = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DiagnosticIA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    symptomes = db.Column(db.Text, nullable=False)
    orientation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
