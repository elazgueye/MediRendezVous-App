from pathlib import Path

routes_content = '''from datetime import date
from functools import wraps
from flask import render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import Medecin, Patient, RendezVous, Disponibilite, User, Specialite


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@app.before_request
def load_current_user():
    g.user = current_user()


@app.context_processor
def inject_user():
    return dict(current_user=g.user)


def login_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = g.user
            if not user:
                return redirect(url_for('login'))
            if not user.actif:
                session.pop('user_id', None)
                return redirect(url_for('login'))
            if role is not None:
                allowed_roles = role if isinstance(role, (list, tuple)) else [role]
                if user.role not in allowed_roles:
                    return redirect(url_for('home'))
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if not user or not user.actif or not user.check_password(password):
            error = 'Email ou mot de passe invalide.'
        else:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
@app.route('/patients/new', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        telephone = request.form.get('telephone')
        preference_specialite = request.form.get('preference_specialite')
        preference_medecin = request.form.get('preference_medecin')
        horaires_preferes = request.form.get('horaires_preferes')
        historique_medical = request.form.get('historique_medical')

        if not nom or not email or not password:
            error = 'Veuillez saisir un nom, un email et un mot de passe.'
        elif User.query.filter_by(email=email).first():
            error = 'Cet email est déjà utilisé.'
        else:
            user = User(email=email, role='patient')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            patient = Patient(
                user_id=user.id,
                nom=nom,
                email=email,
                telephone=telephone,
                preference_specialite=preference_specialite,
                preference_medecin=preference_medecin,
                horaires_preferes=horaires_preferes,
                historique_medical=historique_medical,
            )
            db.session.add(patient)
            db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('patient_profile', id=patient.id))

    specialites = Specialite.query.order_by(Specialite.nom).all()
    return render_template('patient_new.html', error=error, specialites=specialites)


@app.route('/dashboard')
@login_required()
def dashboard():
    if g.user.role == 'patient' and g.user.patient:
        return redirect(url_for('patient_profile', id=g.user.patient.id))
    if g.user.role == 'medecin' and g.user.medecin:
        return redirect(url_for('medecin_agenda', id=g.user.medecin.id))
    if g.user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('home'))


@app.route('/patients/<int:id>')
@login_required(role=['patient', 'admin'])
def patient_profile(id):
    patient = Patient.query.get_or_404(id)
    if g.user.role == 'patient' and (not g.user.patient or g.user.patient.id != id):
        return redirect(url_for('patient_profile', id=g.user.patient.id))
    return render_template('patient_profile.html', patient=patient)


@app.route('/medecins')
def medecins():
    specialite = request.args.get('specialite', '').strip()
    query = Medecin.query
    if specialite:
        query = query.filter(Medecin.specialite.ilike(f'%{specialite}%'))
    medecins_list = query.order_by(Medecin.nom).all()
    specialites = Specialite.query.order_by(Specialite.nom).all()
    return render_template('medecins.html', medecins=medecins_list, specialites=specialites, selected_specialite=specialite)


@app.route('/medecin/<int:id>')
def medecin_detail(id):
    medecin = Medecin.query.get_or_404(id)
    disponibilites = Disponibilite.query.filter_by(medecin_id=id, est_disponible=True).order_by(Disponibilite.date).all()
    disponibilites_par_date = {}
    for dispo in disponibilites:
        disponibilites_par_date.setdefault(dispo.date, []).append(dispo)
    return render_template(
        'medecin_detail.html',
        medecin=medecin,
        disponibilites=disponibilites,
        disponibilites_par_date=disponibilites_par_date,
    )


@app.route('/medecin/<int:id>/agenda')
@login_required(role=['medecin', 'admin'])
def medecin_agenda(id):
    medecin = Medecin.query.get_or_404(id)
    if g.user.role == 'medecin' and (not g.user.medecin or g.user.medecin.id != id):
        return redirect(url_for('home'))
    rdvs = RendezVous.query.filter_by(medecin_id=id).order_by(RendezVous.date).all()
    today = date.today().isoformat()
    today_rdv = [rdv for rdv in rdvs if rdv.date == today]
    return render_template('medecin_agenda.html', medecin=medecin, rdvs=rdvs, today_rdv=today_rdv)


@app.route('/medecin/<int:id>/availability', methods=['GET', 'POST'])
@login_required(role=['medecin', 'admin'])
def medecin_availability(id):
    medecin = Medecin.query.get_or_404(id)
    if g.user.role == 'medecin' and (not g.user.medecin or g.user.medecin.id != id):
        return redirect(url_for('home'))
    message = None
    if request.method == 'POST':
        date_value = request.form.get('date')
        plage_horaire = request.form.get('plage_horaire')
        if date_value and plage_horaire:
            disponible = Disponibilite(medecin_id=id, date=date_value, plage_horaire=plage_horaire)
            db.session.add(disponible)
            db.session.commit()
            message = 'Créneau ajouté avec succès.'
    disponibilites = Disponibilite.query.filter_by(medecin_id=id).order_by(Disponibilite.date).all()
    return render_template('medecin_availability.html', medecin=medecin, disponibilites=disponibilites, message=message)


@app.route('/medecin/<int:medecin_id>/agenda/update/<int:rdv_id>', methods=['POST'])
@login_required(role=['medecin', 'admin'])
def medecin_agenda_update(medecin_id, rdv_id):
    rdv = RendezVous.query.get_or_404(rdv_id)
    if g.user.role == 'medecin' and (not g.user.medecin or g.user.medecin.id != medecin_id):
        return redirect(url_for('home'))
    statut = request.form.get('statut', 'Confirmé')
    rdv.statut = statut
    db.session.commit()
    return redirect(url_for('medecin_agenda', id=medecin_id))


@app.route('/confirmer_rdv/<int:id>', methods=['POST'])
def confirmer_rdv(id):
    nom = request.form.get('nom')
    email = request.form.get('email')
    telephone = request.form.get('telephone')
    motif = request.form.get('motif')
    slot = request.form.get('slot')
    date_value = ''
    horaire = request.form.get('horaire') or '09:00'

    if slot:
        try:
            date_value, horaire = slot.split('|')
        except ValueError:
            date_value = request.form.get('date')
    else:
        date_value = request.form.get('date')

    if not nom or not email or not date_value:
        return render_template(
            'succes.html',
            nom=nom,
            medecin='inconnu',
            date='invalide',
            erreur='Veuillez remplir tous les champs obligatoires.',
        )

    patient = Patient.query.filter_by(email=email).first()
    if not patient:
        patient = Patient(nom=nom, email=email, telephone=telephone)
        db.session.add(patient)
        db.session.flush()

    medecin = Medecin.query.get_or_404(id)
    nouveau_rdv = RendezVous(
        patient_id=patient.id,
        patient_nom=nom,
        patient_email=email,
        medecin_id=id,
        date=date_value,
        horaire=horaire,
        statut='Confirmé',
        motif=motif,
    )
    db.session.add(nouveau_rdv)

    if slot:
        disponibilite = Disponibilite.query.filter_by(
            medecin_id=id,
            date=date_value,
            plage_horaire=horaire,
            est_disponible=True,
        ).first()
        if disponibilite:
            disponibilite.est_disponible = False

    db.session.commit()
    return render_template(
        'succes.html',
        nom=nom,
        medecin=medecin.nom,
        date=f"{date_value} à {horaire}",
        motif=motif,
    )


@app.route('/rendezvous')
@login_required()
def voir_rendezvous():
    if g.user.role == 'patient' and g.user.patient:
        rdv_list = RendezVous.query.filter_by(patient_id=g.user.patient.id).order_by(RendezVous.date).all()
    elif g.user.role == 'medecin' and g.user.medecin:
        rdv_list = RendezVous.query.filter_by(medecin_id=g.user.medecin.id).order_by(RendezVous.date).all()
    else:
        rdv_list = RendezVous.query.order_by(RendezVous.date).all()
    return render_template('rendezvous.html', rdv=rdv_list)


@app.route('/rendezvous/<int:rdv_id>/cancel', methods=['POST'])
@login_required(role='patient')
def cancel_rdv(rdv_id):
    rdv = RendezVous.query.get_or_404(rdv_id)
    if not g.user.patient or rdv.patient_id != g.user.patient.id:
        return redirect(url_for('voir_rendezvous'))
    rdv.statut = 'Annulé'
    db.session.commit()
    return redirect(url_for('voir_rendezvous'))


@app.route('/triage', methods=['GET', 'POST'])
def triage():
    orientation = None
    if request.method == 'POST':
        symptomes = request.form.get('symptomes', '')
        orientation = orientation_par_symptomes(symptomes)
        return render_template('triage_result.html', symptomes=symptomes, orientation=orientation)
    return render_template('triage.html')


@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    total_patients = Patient.query.count()
    total_medecins = Medecin.query.count()
    total_rdv = RendezVous.query.count()
    today = date.today().isoformat()
    today_rdv = RendezVous.query.filter_by(date=today).count()
    blocked_users = User.query.filter_by(actif=False).count()
    return render_template(
        'admin_dashboard.html',
        total_patients=total_patients,
        total_medecins=total_medecins,
        total_rdv=total_rdv,
        today_rdv=today_rdv,
        blocked_users=blocked_users,
    )


@app.route('/admin/medecins', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_medecins():
    message = None
    specialites = Specialite.query.order_by(Specialite.nom).all()
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        specialite = request.form.get('specialite', '').strip()
        prix = request.form.get('prix', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if nom and specialite and prix:
            if email and password and not User.query.filter_by(email=email).first():
                user = User(email=email, role='medecin')
                user.set_password(password)
                db.session.add(user)
                db.session.flush()
                medecin = Medecin(nom=nom, specialite=specialite, prix=prix, email=email, user_id=user.id)
            else:
                medecin = Medecin(nom=nom, specialite=specialite, prix=prix, email=email)
            db.session.add(medecin)
            if specialite and not Specialite.query.filter_by(nom=specialite).first():
                db.session.add(Specialite(nom=specialite))
            db.session.commit()
            message = 'Médecin ajouté avec succès.'
    medecins = Medecin.query.order_by(Medecin.nom).all()
    return render_template('admin_medecins.html', medecins=medecins, specialites=specialites, message=message)


@app.route('/admin/medecins/<int:id>/delete', methods=['POST'])
@login_required(role='admin')
def admin_medecin_delete(id):
    medecin = Medecin.query.get_or_404(id)
    medecin.active = False if hasattr(medecin, 'active') else None
    db.session.delete(medecin)
    db.session.commit()
    return redirect(url_for('admin_medecins'))


@app.route('/admin/specialites', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_specialites():
    message = None
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        if nom and not Specialite.query.filter_by(nom=nom).first():
            db.session.add(Specialite(nom=nom))
            db.session.commit()
            message = 'Spécialité ajoutée.'
    specialites = Specialite.query.order_by(Specialite.nom).all()
    return render_template('admin_specialites.html', specialites=specialites, message=message)


@app.route('/admin/specialites/<int:id>/delete', methods=['POST'])
@login_required(role='admin')
def admin_specialite_delete(id):
    specialite = Specialite.query.get_or_404(id)
    db.session.delete(specialite)
    db.session.commit()
    return redirect(url_for('admin_specialites'))


@app.route('/admin/users')
@login_required(role='admin')
def admin_users():
    users = User.query.order_by(User.email).all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required(role='admin')
def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.actif = not user.actif
    db.session.commit()
    return redirect(url_for('admin_users'))


def orientation_par_symptomes(symptomes):
    texte = (symptomes or '').lower()
    urgence = ['sang', 'évanouissement', 'difficulté respiratoire', 'essoufflement', 'douleur aiguë', 'traumatisme', 'chute']
    specialist = ['douleur thoracique', 'douleur abdominale', 'allergie sévère', 'maux de tête intenses', 'perte de conscience', 'vision floue']
    generaliste = ['fièvre', 'toux', 'fatigue', 'nausée', 'mal de gorge', 'courbatures']

    if any(mot in texte for mot in urgence):
        return "Orientation : consultez les urgences immédiatement."
    if any(mot in texte for mot in specialist):
        return "Orientation : consultez un spécialiste rapidement."
    if any(mot in texte for mot in generaliste):
        return "Orientation : commencez par consulter un médecin généraliste."
    return "Orientation : un médecin généraliste reste le meilleur premier interlocuteur."
'''

Path(r'c:\Users\DELL\Desktop\medi_rendez_vous\app\routes.py').write_text(routes_content, encoding='utf-8')
print('routes written')
