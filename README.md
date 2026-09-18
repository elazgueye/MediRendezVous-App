# MédiRendez-vous

MédiRendez-vous est une application web de gestion et de prise de rendez-vous médicaux.

Elle permet aux patients de rechercher des médecins, consulter leurs disponibilités et prendre rendez-vous. Les médecins peuvent gérer leur agenda, leurs disponibilités et leurs rendez-vous. Un espace administrateur permet également de gérer les utilisateurs, médecins, spécialités et rendez-vous.

L'application intègre également un système de **triage médical assisté par IA** permettant d'orienter l'utilisateur à partir des symptômes renseignés.

## Fonctionnalités

- 👤 Gestion des comptes patients et médecins
- 🔎 Recherche de médecins par nom ou spécialité
- 📅 Prise et gestion des rendez-vous
- 🕐 Gestion des disponibilités des médecins
- 👨‍⚕️ Gestion des agendas
- 🛠️ Administration des utilisateurs, médecins, spécialités et rendez-vous
- 🤖 Triage médical assisté par IA

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- MySQL / SQLite
- HTML / CSS
- Pandas
- Scikit-learn
- Ollama / Llama 3.2

## Installation

```bash
git clone https://github.com/elazgueye/MediRendezVous-App.git
cd MediRendezVous-App

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt