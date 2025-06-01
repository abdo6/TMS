# app/routes/main_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.chauffeur import Chauffeur
from app.models.vehicule import Vehicule
from app.models.mission import Mission
from app.models.ville import Ville
from app.models.province import Province
from app.models.destination import Destination
from app.models.user import User, ROLES
from app.models.client_initial import ClientInitial
from datetime import date, time, datetime, timedelta  # Ensure datetime is imported for combine()
from functools import wraps
from app.models.service_client import ServiceClient
from app.models.type_vehicule import TypeVehicule
from app.models.entete_commande import EnteteCommande
from app.models.client_final import ClientFinal
from app.models.detail_commande import DetailCommande
from app.models.trajet import Trajet
from app.models.sous_traitant import SousTraitant
from app.models.type_indispo_chauffeur import TypeIndispoChauffeur
from app.models.type_indispo_vehicule import TypeIndispoVehicule
from app.models.indispo_chauffeur import IndisponibiliteChauffeur
from app.models.indispo_vehicule import IndisponibiliteVehicule
from app.models.vehicule_externe import VehiculeExterne
from app.models.chauffeur_externe import ChauffeurExterne
from app.models.mission_detail import MissionDetail
from sqlalchemy.orm import joinedload, selectinload
from app.models.date_cv import DateCV
from app.models.date_tr import DateTR
from app.models.affretement import Affretement
from app.models.feuille_de_route import FeuilleDeRoute
from app.models.localisation import Localisation # Re-confirmer cet import
from sqlalchemy import distinct, func # Re-confirmer cet import





# --- Fonctions utilitaires pour la gestion des rôles ---
def role_required(required_role_key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Veuillez vous connecter pour accéder à cette page.', 'info')
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role != required_role_key and current_user.role != 'ADMIN':
                flash('Vous n\'avez pas les permissions nécessaires pour accéder à cette page.', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# app/routes/main_routes.py (Ajoutez cette nouvelle fonction utilitaire)

def get_validity_alerts(days_threshold=30):
    """
    Récupère les alertes pour les dates de validité des chauffeurs et véhicules.
    days_threshold: Nombre de jours avant l'expiration pour déclencher une alerte.
    """
    today = date.today()
    alerts = {
        'chauffeur_cv': [], # Alertes pour les documents des chauffeurs (permis, visite médicale)
        'vehicule_tr': []   # Alertes pour les contrôles techniques des véhicules
    }

    # --- Alertes pour les chauffeurs (DateCV) ---
    # Documents expirés
    expired_cv = db.session.execute(
        db.select(DateCV)
        .filter(DateCV.date_fin < today)
        .options(joinedload(DateCV.chauffeur))
    ).scalars().all()
    for doc in expired_cv:
        alerts['chauffeur_cv'].append({
            'type': 'expiré',
            'description': doc.description,
            'chauffeur_nom': doc.chauffeur.nom_complet if doc.chauffeur else 'N/A',
            'date_fin': doc.date_fin,
            'days_left': (doc.date_fin - today).days # Sera négatif
        })

    # Documents expirant bientôt
    expiring_soon_cv = db.session.execute(
        db.select(DateCV)
        .filter(DateCV.date_fin >= today, DateCV.date_fin <= today + timedelta(days=days_threshold))
        .options(joinedload(DateCV.chauffeur))
    ).scalars().all()
    for doc in expiring_soon_cv:
        alerts['chauffeur_cv'].append({
            'type': 'expire_bientot',
            'description': doc.description,
            'chauffeur_nom': doc.chauffeur.nom_complet if doc.chauffeur else 'N/A',
            'date_fin': doc.date_fin,
            'days_left': (doc.date_fin - today).days
        })

    # --- Alertes pour les véhicules (DateTR) ---
    # Documents expirés
    expired_tr = db.session.execute(
        db.select(DateTR)
        .filter(DateTR.date_fin < today)
        .options(joinedload(DateTR.vehicule))
    ).scalars().all()
    for doc in expired_tr:
        alerts['vehicule_tr'].append({
            'type': 'expiré',
            'description': doc.description,
            'vehicule_immat': doc.vehicule.immatriculation_ve if doc.vehicule else 'N/A',
            'date_fin': doc.date_fin,
            'days_left': (doc.date_fin - today).days
        })

    # Documents expirant bientôt
    expiring_soon_tr = db.session.execute(
        db.select(DateTR)
        .filter(DateTR.date_fin >= today, DateTR.date_fin <= today + timedelta(days=days_threshold))
        .options(joinedload(DateTR.vehicule))
    ).scalars().all()
    for doc in expiring_soon_tr:
        alerts['vehicule_tr'].append({
            'type': 'expire_bientot',
            'description': doc.description,
            'vehicule_immat': doc.vehicule.immatriculation_ve if doc.vehicule else 'N/A',
            'date_fin': doc.date_fin,
            'days_left': (doc.date_fin - today).days
        })

    return alerts

# --- Fonction de vérification de la disponibilité des Missions ---
def check_availability(chauffeur_id_str, vehicule_id_str, new_date_debut, new_heure_debut, new_date_fin, new_heure_fin, mission_id=None):
	# Convertir les IDs de string (form) en int (DB)
	chauffeur_id = int(chauffeur_id_str)
	vehicule_id = int(vehicule_id_str)

	# Combiner la nouvelle date et heure pour faciliter la comparaison
	new_start_dt = datetime.combine(new_date_debut, new_heure_debut)
	new_end_dt = datetime.combine(new_date_fin, new_heure_fin)

	# Vérifier si la date/heure de fin est antérieure à la date/heure de début
	if new_end_dt < new_start_dt:
		return "La date et l'heure de fin doivent être postérieures à la date et l'heure de début."
	
	# Récupérer toutes les missions qui impliquent ce chauffeur OU ce véhicule
	# et qui pourraient chevaucher la nouvelle période
	# Nous chargeons l'objet Mission pour pouvoir accéder à ses attributs de date/heure
	potentially_overlapping_missions_query = db.session.execute(
		db.select(Mission).filter(
			(Mission.id_chauffeur == chauffeur_id) | (Mission.id_vehicule == vehicule_id),
			# Exclure la mission actuelle si nous sommes en mode édition
			Mission.id_mission != mission_id if mission_id else True
		)
	)
	potential_overlapping_missions = potentially_overlapping_missions_query.scalars().all()

	# Itérer sur les missions potentiellement en conflit et vérifier le chevauchement précis
	for mission in potential_overlapping_missions:
		existing_start_dt = datetime.combine(mission.date_debut, mission.heure_debut)
		existing_end_dt = datetime.combine(mission.date_fin, mission.heure_fin)

		# Condition de chevauchement:
		# La nouvelle mission chevauche si: (début nouvelle < fin existante) ET (fin nouvelle > début existante)
		if (new_start_dt < existing_end_dt and new_end_dt > existing_start_dt):
			if mission.id_chauffeur == chauffeur_id:
				return f"Le chauffeur est déjà occupé par la mission ID: {mission.id_mission} ({mission.date_debut.strftime('%d/%m/%Y')} {mission.heure_debut.strftime('%H:%M')} - {mission.date_fin.strftime('%d/%m/%Y')} {mission.heure_fin.strftime('%H:%M')})."
			if mission.id_vehicule == vehicule_id:
				return f"Le véhicule est déjà occupé par la mission ID: {mission.id_mission} ({mission.date_debut.strftime('%d/%m/%Y')} {mission.heure_debut.strftime('%H:%M')} - {mission.date_fin.strftime('%d/%m/%Y')} {mission.heure_fin.strftime('%H:%M')})."

	return None # Aucun problème de disponibilité détecté

# --- Définition du Blueprint principal ---
main = Blueprint('main', __name__)

# --- Route d'accueil ---
# app/routes/main_routes.py (Modifiez la fonction index)

@main.route('/')
def index():
    stats = {}
    alerts = {'chauffeur_cv': [], 'vehicule_tr': []} # Initialiser par défaut

    if current_user.is_authenticated:
        today = date.today()

        # Stats existantes (à afficher pour les rôles de gestion)
        stats['total_chauffeurs'] = db.session.scalar(db.select(db.func.count(Chauffeur.id_chauffeur)))
        stats['total_vehicules'] = db.session.scalar(db.select(db.func.count(Vehicule.id_vehicule)))
        stats['missions_actives'] = db.session.scalar(
            db.select(db.func.count(Mission.id_mission))
            .filter(
                Mission.date_debut <= today,
                Mission.date_fin >= today
            )
        )
        stats['commandes_non_planifiees_count'] = db.session.scalar(
            db.select(db.func.count(DetailCommande.id_detail_commande))
            .filter(db.not_(DetailCommande.missions.any()))
        )
        stats['vehicules_indisponibles_count'] = db.session.scalar(
            db.select(db.func.count(IndisponibiliteVehicule.id_indispo_vehicule))
            .filter(
                IndisponibiliteVehicule.date_debut <= today,
                IndisponibiliteVehicule.date_fin >= today
            )
        )
        stats['chauffeurs_indisponibles_count'] = db.session.scalar(
            db.select(db.func.count(IndisponibiliteChauffeur.id_indispo_chauffeur))
            .filter(
                IndisponibiliteChauffeur.date_debut <= today,
                IndisponibiliteChauffeur.date_fin >= today
            )
        )
        
        # Récupération des alertes de validité
        alerts = get_validity_alerts() # Appelle la fonction que vous avez créée

    return render_template('index.html', stats=stats, alerts=alerts)

# --- Route de test ---
@main.route('/test')
def test_page():
	return "Ceci est une page de test Flask !"

# --- Routes pour la gestion des Chauffeurs ---
@main.route('/chauffeurs')
@login_required
@role_required('RH')
def liste_chauffeurs():
	search_query = request.args.get('search', '').strip() 
	
	query = db.select(Chauffeur).order_by(Chauffeur.nom)

	if search_query:
		query = query.filter(
			db.or_(
				Chauffeur.nom.ilike(f'%{search_query}%'),
				Chauffeur.prenom.ilike(f'%{search_query}%'),
				Chauffeur.email.ilike(f'%{search_query}%')
			)
		)

	chauffeurs = db.session.execute(query).scalars().all()
	
	return render_template('chauffeurs.html', chauffeurs=chauffeurs, search_query=search_query)

@main.route('/chauffeurs/add', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def add_chauffeur():
	if request.method == 'POST':
		nom = request.form['nom']
		prenom = request.form['prenom']
		email = request.form['email']
		numero_telephone = request.form.get('numero_telephone')
		adresse = request.form.get('adresse')
		categorie_ch = request.form.get('categorie_ch')

		existing_chauffeur = db.session.execute(db.select(Chauffeur).filter_by(email=email)).scalar_one_or_none()
		if existing_chauffeur:
			flash("Un chauffeur avec cet email existe déjà.", 'danger')
			return render_template('add_chauffeur.html')

		new_chauffeur = Chauffeur(
			nom=nom, prenom=prenom, email=email,
			numero_telephone=numero_telephone, adresse=adresse, categorie_ch=categorie_ch
		)
		db.session.add(new_chauffeur)
		db.session.commit()
		flash('Chauffeur ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_chauffeurs'))
	return render_template('add_chauffeur.html')

@main.route('/chauffeurs/edit/<int:chauffeur_id>', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def edit_chauffeur(chauffeur_id):
	chauffeur = db.session.execute(db.select(Chauffeur).filter_by(id_chauffeur=chauffeur_id)).scalar_one_or_none()
	if chauffeur is None:
		flash('Chauffeur non trouvé.', 'danger')
		return redirect(url_for('main.liste_chauffeurs'))

	if request.method == 'POST':
		chauffeur.nom = request.form['nom']
		chauffeur.prenom = request.form['prenom']
		chauffeur.email = request.form['email']
		chauffeur.numero_telephone = request.form.get('numero_telephone')
		chauffeur.adresse = request.form.get('adresse')
		chauffeur.categorie_ch = request.form.get('categorie_ch')

		existing_chauffeur_with_email = db.session.execute(
			db.select(Chauffeur).filter(Chauffeur.email == chauffeur.email, Chauffeur.id_chauffeur != chauffeur_id)
		).scalar_one_or_none()

		if existing_chauffeur_with_email:
			flash("Un autre chauffeur avec cet email existe déjà.", 'danger')
			return render_template('edit_chauffeur.html', chauffeur=chauffeur)

		db.session.commit()
		flash('Chauffeur modifié avec succès !', 'success')
		return redirect(url_for('main.liste_chauffeurs'))
	return render_template('edit_chauffeur.html', chauffeur=chauffeur)

@main.route('/chauffeurs/delete/<int:chauffeur_id>')
@login_required
@role_required('RH')
def delete_chauffeur(chauffeur_id):
	chauffeur = db.session.execute(db.select(Chauffeur).filter_by(id_chauffeur=chauffeur_id)).scalar_one_or_none()
	if chauffeur:
		db.session.delete(chauffeur)
		db.session.commit()
		flash('Chauffeur supprimé avec succès !', 'success')
	else:
		flash('Chauffeur non trouvé.', 'danger')
	return redirect(url_for('main.liste_chauffeurs'))

# --- Routes pour la gestion des Véhicules ---
@main.route('/vehicules')
@login_required
@role_required('CHARGE_EXPLOITATION')
def liste_vehicules():
	search_query = request.args.get('search', '').strip() 
	
	query = db.select(Vehicule).order_by(Vehicule.immatriculation_ve)

	if search_query:
		query = query.filter(
			db.or_(
				Vehicule.immatriculation_ve.ilike(f'%{search_query}%'),
				Vehicule.categorie.ilike(f'%{search_query}%')
			)
		)

	vehicules = db.session.execute(query).scalars().all()
	
	return render_template('list_vehicules.html', vehicules=vehicules, search_query=search_query)

@main.route('/vehicules/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def add_vehicule():
	if request.method == 'POST':
		immatriculation_ve = request.form['immatriculation_ve']
		categorie = request.form.get('categorie')

		existing_vehicule = db.session.execute(db.select(Vehicule).filter_by(immatriculation_ve=immatriculation_ve)).scalar_one_or_none()
		if existing_vehicule:
			flash("Un véhicule avec cette immatriculation existe déjà.", 'danger')
			return render_template('add_vehicule.html', immatriculation_ve=immatriculation_ve, categorie=categorie)

		new_vehicule = Vehicule(immatriculation_ve=immatriculation_ve, categorie=categorie)
		db.session.add(new_vehicule)
		db.session.commit()
		flash('Véhicule ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_vehicules'))
	return render_template('add_vehicule.html')

@main.route('/vehicules/edit/<int:vehicule_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def edit_vehicule(vehicule_id):
	vehicule = db.session.execute(db.select(Vehicule).filter_by(id_vehicule=vehicule_id)).scalar_one_or_none()
	if vehicule is None:
		flash('Véhicule non trouvé.', 'danger')
		return redirect(url_for('main.liste_vehicules'))

	if request.method == 'POST':
		new_immatriculation = request.form['immatriculation_ve']
		categorie = request.form.get('categorie')

		existing_vehicule_with_immat = db.session.execute(
			db.select(Vehicule).filter(
				Vehicule.immatriculation_ve == new_immatriculation,
				Vehicule.id_vehicule != vehicule_id
			)
		).scalar_one_or_none()

		if existing_vehicule_with_immat:
			flash("Un autre véhicule avec cette immatriculation existe déjà.", 'danger')
			return render_template('edit_vehicule.html', vehicule=vehicule)

		vehicule.immatriculation_ve = new_immatriculation
		vehicule.categorie = categorie
		db.session.commit()
		flash('Véhicule modifié avec succès !', 'success')
		return redirect(url_for('main.liste_vehicules'))
	return render_template('edit_vehicule.html', vehicule=vehicule)

@main.route('/vehicules/delete/<int:vehicule_id>')
@login_required
@role_required('CHARGE_EXPLOITATION')
def delete_vehicule(vehicule_id):
	vehicule = db.session.execute(db.select(Vehicule).filter_by(id_vehicule=vehicule_id)).scalar_one_or_none()
	if vehicule:
		db.session.delete(vehicule)
		db.session.commit()
		flash('Véhicule supprimé avec succès !', 'success')
	else:
		flash('Véhicule non trouvé.', 'danger')
	return redirect(url_for('main.liste_vehicules'))

# --- Routes pour la gestion des Missions ---
@main.route('/missions')
@login_required
@role_required('PLANIFIER')
def liste_missions():
	search_chauffeur = request.args.get('chauffeur', '').strip()
	search_vehicule = request.args.get('vehicule', '').strip()
	search_date_from_str = request.args.get('date_from', '').strip()
	search_date_to_str = request.args.get('date_to', '').strip()

	query = db.select(Mission) \
			.options(joinedload(Mission.chauffeur)) \
			.options(joinedload(Mission.vehicule)) \
			.options(joinedload(Mission.destination)) \
			.options(joinedload(Mission.feuille_de_route)) \
			.options(selectinload(Mission.details_commandes).joinedload(DetailCommande.entete_commande)) \
			.order_by(Mission.date_debut)

	if search_chauffeur:
		query = query.filter(
			db.or_(
				Mission.chauffeur.has(Chauffeur.nom.ilike(f'%{search_chauffeur}%')),
				Mission.chauffeur.has(Chauffeur.prenom.ilike(f'%{search_chauffeur}%'))
			)
		)
	
	if search_vehicule:
		query = query.filter(Mission.vehicule.has(Vehicule.immatriculation_ve.ilike(f'%{search_vehicule}%')))

	if search_date_from_str:
		try:
			search_date_from = date.fromisoformat(search_date_from_str)
			query = query.filter(Mission.date_fin >= search_date_from)
		except ValueError:
			flash("Format de date de début invalide pour la recherche.", 'danger')

	if search_date_to_str:
		try:
			search_date_to = date.fromisoformat(search_date_to_str)
			query = query.filter(Mission.date_debut <= search_date_to)
		except ValueError:
			flash("Format de date de fin invalide pour la recherche.", 'danger')

	missions = db.session.execute(query).scalars().all()
	
	return render_template('list_missions.html', 
						missions=missions,
						search_chauffeur=search_chauffeur,
						search_vehicule=search_vehicule,
						search_date_from=search_date_from_str,
						search_date_to=search_date_to_str)


@main.route('/missions/add', methods=['GET', 'POST'])
@login_required
@role_required('PLANIFIER')
def add_mission():
	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()
	destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()
	feuilles_de_route = db.session.execute(db.select(FeuilleDeRoute).order_by(FeuilleDeRoute.date_depart_prevu.desc())).scalars().all()

	if request.method == 'POST':
		id_chauffeur = request.form['id_chauffeur']
		id_vehicule = request.form['id_vehicule']
		id_destination = request.form.get('id_destination')
		id_destination = id_destination if id_destination else None
		id_feuille_de_route = request.form.get('id_feuille_de_route')
		id_feuille_de_route = id_feuille_de_route if id_feuille_de_route else None

		date_debut_str = request.form['date_debut']
		heure_debut_str = request.form['heure_debut']
		date_fin_str = request.form['date_fin']
		heure_fin_str = request.form['heure_fin']

		try:
			new_date_debut = date.fromisoformat(date_debut_str)
			new_heure_debut = time.fromisoformat(heure_debut_str)
			new_date_fin = date.fromisoformat(date_fin_str)
			new_heure_fin = time.fromisoformat(heure_fin_str)
		except ValueError:
			return render_template('add_mission.html', 
								chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations, 
								feuilles_de_route=feuilles_de_route,
								form_error="Format de date ou d'heure invalide.")

		availability_error = check_availability(id_chauffeur, id_vehicule, new_date_debut, new_heure_debut, new_date_fin, new_heure_fin)
		
		if availability_error:
			return render_template('add_mission.html', 
								chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations, 
								feuilles_de_route=feuilles_de_route,
								form_error=availability_error)
		# NOUVELLE VÉRIFICATION : Capacité du véhicule
    	

		new_mission = Mission(
			id_chauffeur=id_chauffeur, id_vehicule=id_vehicule, id_destination=id_destination,
			date_debut=new_date_debut, heure_debut=new_heure_debut, date_fin=new_date_fin, heure_fin=new_heure_fin,
			id_feuille_de_route=id_feuille_de_route,
			statut='Planifiée' # Statut par défaut
		)
		db.session.add(new_mission)
		db.session.commit()
		flash('Mission planifiée avec succès !', 'success')
		return redirect(url_for('main.liste_missions'))
	
	return render_template('add_mission.html', chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations, 
						feuilles_de_route=feuilles_de_route,
						form_error=None)


# app/routes/main_routes.py (Remplacez TOUTE la fonction edit_mission par celle-ci)

@main.route('/missions/edit/<int:mission_id>', methods=['GET', 'POST'])
@login_required
@role_required('PLANIFIER')
def edit_mission(mission_id):
    print(f"DEBUG: Requête reçue pour éditer mission ID {mission_id}")
    print(f"DEBUG: Méthode de la requête: {request.method}")

    mission = db.session.execute(db.select(Mission).filter_by(id_mission=mission_id)).scalar_one_or_none()
    if mission is None:
        flash('Mission non trouvée.', 'danger')
        return redirect(url_for('main.liste_missions'))

    # Charger les listes pour les selects, quelle que soit la méthode
    chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
    vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()
    destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()
    feuilles_de_route = db.session.execute(db.select(FeuilleDeRoute).order_by(FeuilleDeRoute.date_depart_prevu.desc())).scalars().all()

    # Charger les détails associés et disponibles
    associated_details = mission.details_commandes # Les détails DÉJÀ liés à cette mission
    available_details_commandes = db.session.execute(
        db.select(DetailCommande)
        .filter(db.not_(DetailCommande.missions.any())) # Détails non encore liés à UNE mission
        .options(joinedload(DetailCommande.entete_commande))
        .options(joinedload(DetailCommande.destination))
        .options(joinedload(DetailCommande.type_vehicule))
        .order_by(DetailCommande.id_entete_commande)
    ).scalars().all()

    # Combiner les détails associés et les détails disponibles pour la liste 'available_details'
    # afin de toujours montrer les détails liés à la mission actuelle comme "disponibles" pour l'édition
    # mais sans les compter comme "non encore affectés" s'ils sont déjà liés à cette mission.
    # On fait cette manipulation pour éviter les doublons et les conflits d'affichage.
    combined_available_details = []
    # Ajouter les détails qui sont déjà associés à la mission actuelle
    for detail in associated_details:
        combined_available_details.append(detail)
    # Ajouter les détails non affectés ailleurs
    for detail in available_details_commandes:
        # S'assurer qu'il n'est pas déjà dans les associés_details
        if detail not in combined_available_details:
            combined_available_details.append(detail)
    # Sortir la liste pour l'affichage
    combined_available_details.sort(key=lambda x: x.id_detail_commande) # Tri par ID pour la cohérence


    form_error_message = None # Variable pour stocker les messages d'erreur du formulaire

    if request.method == 'POST':
        print(f"DEBUG: Traitement de la requête POST pour mission ID {mission_id}")
        
        # Récupération des données du formulaire
        id_chauffeur = request.form['id_chauffeur']
        id_vehicule = request.form['id_vehicule']
        id_destination = request.form.get('id_destination')
        id_destination = id_destination if id_destination else None
        id_feuille_de_route = request.form.get('id_feuille_de_route')
        id_feuille_de_route = id_feuille_de_route if id_feuille_de_route else None

        date_debut_str = request.form['date_debut']
        heure_debut_str = request.form['heure_debut']
        date_fin_str = request.form['date_fin']
        heure_fin_str = request.form['heure_fin']

        try:
            new_date_debut = date.fromisoformat(date_debut_str)
            new_heure_debut = time.fromisoformat(heure_debut_str)
            new_date_fin = date.fromisoformat(date_fin_str)
            new_heure_fin = time.fromisoformat(heure_fin_str)
        except ValueError:
            form_error_message = "Format de date ou d'heure invalide."
            # Rendu du template en cas d'erreur de format, avec le message
            return render_template('edit_mission.html',
                                mission=mission, chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations,
                                feuilles_de_route=feuilles_de_route,
                                associated_details=associated_details,
                                available_details=combined_available_details, # Utiliser la liste combinée
                                form_error=form_error_message)

        # Vérification de la disponibilité du chauffeur/véhicule
        availability_error = check_availability(id_chauffeur, id_vehicule, new_date_debut, new_heure_debut, new_date_fin, new_heure_fin, mission_id=mission.id_mission)
        if availability_error:
            form_error_message = availability_error
            # Rendu du template en cas d'erreur de disponibilité
            return render_template('edit_mission.html',
                                mission=mission, chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations,
                                feuilles_de_route=feuilles_de_route,
                                associated_details=associated_details,
                                available_details=combined_available_details, # Utiliser la liste combinée
                                form_error=form_error_message)

        # NOUVELLE VÉRIFICATION : Capacité du véhicule
        # Pour check_vehicle_capacity, nous devons passer l'ID du véhicule et l'ID de la mission.
        # La fonction va récupérer les détails associés à cette mission pour faire le calcul.
        capacity_error = check_vehicle_capacity(vehicule_id=id_vehicule, mission_id=mission.id_mission)
        if capacity_error:
            form_error_message = capacity_error
            # Rendu du template en cas d'erreur de capacité
            return render_template('edit_mission.html',
                                mission=mission, chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations,
                                feuilles_de_route=feuilles_de_route,
                                associated_details=associated_details,
                                available_details=combined_available_details, # Utiliser la liste combinée
                                form_error=form_error_message)


        # Mise à jour des attributs de la mission
        mission.id_chauffeur = id_chauffeur
        mission.id_vehicule = id_vehicule
        mission.id_destination = id_destination
        mission.id_feuille_de_route = id_feuille_de_route
        mission.date_debut = new_date_debut
        mission.heure_debut = new_heure_debut
        mission.date_fin = new_date_fin
        mission.heure_fin = new_heure_fin
        
        # Traitement des ordres de livraison des détails de commande associés
        # On parcourt les détails de commande déjà associés à cette mission via la table de liaison
        for mission_detail_entry in mission.mission_details_link:
            form_field_name = f"ordre_livraison_{mission_detail_entry.id_detail_commande}"
            ordre_str = request.form.get(form_field_name)
            
            if ordre_str:
                try:
                    mission_detail_entry.ordre_livraison = int(ordre_str)
                except ValueError:
                    flash(f"L'ordre de livraison pour le détail {mission_detail_entry.id_detail_commande} n'est pas un nombre valide. Il n'a pas été mis à jour.", 'warning')
                    mission_detail_entry.ordre_livraison = None
            else:
                mission_detail_entry.ordre_livraison = None

        db.session.commit()
        flash('Mission modifiée avec succès !', 'success')
        return redirect(url_for('main.liste_missions'))   

    # Si la méthode est GET (ou si la logique POST n'a pas déclenché de redirect)
    # Rendu initial du template pour afficher le formulaire
    print(f"DEBUG: Rendu du template edit_mission.html pour mission ID {mission_id} (Méthode GET / Erreur)")
    return render_template('edit_mission.html',
                        mission=mission, chauffeurs=chauffeurs, vehicules=vehicules, destinations=destinations,
                        feuilles_de_route=feuilles_de_route,
                        associated_details=associated_details,
                        available_details=combined_available_details, # Utiliser la liste combinée
                        form_error=form_error_message) # Passe l'erreur si elle a été définie plus tôt et qu'on rerend le template


# Nouvelle route pour associer un DetailCommande à une Mission
@main.route('/missions/<int:mission_id>/add_detail', methods=['POST'])
@login_required
@role_required('PLANIFIER')
def add_detail_to_mission(mission_id):
	mission = db.session.execute(db.select(Mission).filter_by(id_mission=mission_id)).scalar_one_or_none()
	detail_id = request.form.get('detail_id')

	if not mission:
		flash("Mission non trouvée.", 'danger')
		return redirect(url_for('main.liste_missions'))
	if not detail_id:
		flash("Aucun détail de commande sélectionné.", 'danger')
		return redirect(url_for('main.edit_mission', mission_id=mission_id))

	detail_commande = db.session.execute(db.select(DetailCommande).filter_by(id_detail_commande=detail_id)).scalar_one_or_none()
	if not detail_commande:
		flash("Détail de commande non trouvé.", 'danger')
		return redirect(url_for('main.edit_mission', mission_id=mission_id))
	
	# CORRECTION DE LA LOGIQUE DE VÉRIFICATION
	# Vérifier si ce détail de commande est déjà associé à cette mission
	if detail_commande in mission.details_commandes:
		flash('Ce détail de commande est déjà associé à cette mission.', 'info')
		return redirect(url_for('main.edit_mission', mission_id=mission_id))

	# Vérifier si ce détail de commande est déjà associé à UNE AUTRE mission
	# On itère sur la collection 'missions' de detail_commande
	for existing_mission_for_detail in detail_commande.missions:
		if existing_mission_for_detail.id_mission != mission_id:
			flash(f"Ce détail de commande est déjà associé à la mission ID: {existing_mission_for_detail.id_mission}.", 'danger')
			return redirect(url_for('main.edit_mission', mission_id=mission_id))

	# Si le détail n'est ni associé à cette mission, ni à une autre, alors on l'ajoute
	mission.details_commandes.append(detail_commande)
	db.session.commit()
	flash('Détail de commande associé avec succès à la mission !', 'success')
	
	return redirect(url_for('main.edit_mission', mission_id=mission_id))

# Nouvelle route pour dissocier un DetailCommande d'une Mission
@main.route('/missions/<int:mission_id>/remove_detail/<int:detail_id>', methods=['POST'])
@login_required
@role_required('PLANIFIER')
def remove_detail_from_mission(mission_id, detail_id):
	mission = db.session.execute(db.select(Mission).filter_by(id_mission=mission_id)).scalar_one_or_none()
	detail_commande = db.session.execute(db.select(DetailCommande).filter_by(id_detail_commande=detail_id)).scalar_one_or_none()

	if not mission:
		flash("Mission non trouvée.", 'danger')
		return redirect(url_for('main.liste_missions'))
	if not detail_commande:
		flash("Détail de commande non trouvé.", 'danger')
		return redirect(url_for('main.edit_mission', mission_id=mission_id))

	if detail_commande in mission.details_commandes:
		mission.details_commandes.remove(detail_commande)
		db.session.commit()
		flash('Détail de commande dissocié avec succès de la mission !', 'success')
	else:
		flash('Ce détail de commande n\'est pas associé à cette mission.', 'info')
	
	return redirect(url_for('main.edit_mission', mission_id=mission_id))


@main.route('/missions/delete/<int:mission_id>')
@login_required
@role_required('PLANIFIER')
def delete_mission(mission_id):
	mission = db.session.execute(db.select(Mission).filter_by(id_mission=mission_id)).scalar_one_or_none()
	if mission:
		db.session.delete(mission)
		db.session.commit()
		flash('Mission supprimée avec succès !', 'success')
	else:
		flash('Mission non trouvée.', 'danger')
	return redirect(url_for('main.liste_missions'))

# --- Routes pour la gestion des Villes ---
@main.route('/villes')
@login_required
@role_required('CHARGE_EXPLOITATION')
def liste_villes():
	villes = db.session.execute(db.select(Ville).order_by(Ville.nom_ville)).scalars().all()
	return render_template('list_villes.html', villes=villes)

@main.route('/villes/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def add_ville():
	if request.method == 'POST':
		code_ville = request.form['code_ville']
		nom_ville = request.form['nom_ville']

		existing_ville = db.session.execute(db.select(Ville).filter_by(code_ville=code_ville)).scalar_one_or_none()
		if existing_ville:
			flash("Une ville avec ce code existe déjà.", 'danger')
			return render_template('add_ville.html', code_ville=code_ville, nom_ville=nom_ville)

		new_ville = Ville(code_ville=code_ville, nom_ville=nom_ville)
		db.session.add(new_ville)
		db.session.commit()
		flash('Ville ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_villes'))
	return render_template('add_ville.html')

@main.route('/villes/edit/<int:ville_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def edit_ville(ville_id):
	ville = db.session.execute(db.select(Ville).filter_by(id_ville=ville_id)).scalar_one_or_none()
	if ville is None:
		flash('Ville non trouvée.', 'danger')
		return redirect(url_for('main.liste_villes'))

	if request.method == 'POST':
		new_code_ville = request.form['code_ville']
		new_nom_ville = request.form['nom_ville']

		existing_ville_with_code = db.session.execute(
			db.select(Ville).filter(Ville.code_ville == new_code_ville, Ville.id_ville != ville_id)
		).scalar_one_or_none()

		if existing_ville_with_code:
			flash("Une autre ville avec ce code existe déjà.", 'danger')
			return render_template('edit_ville.html', ville=ville)

		ville.code_ville = new_code_ville
		ville.nom_ville = new_nom_ville
		db.session.commit()
		flash('Ville modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_villes'))
	return render_template('edit_ville.html', ville=ville)

@main.route('/villes/delete/<int:ville_id>')
@login_required
@role_required('CHARGE_EXPLOITATION')
def delete_ville(ville_id):
	ville = db.session.execute(db.select(Ville).filter_by(id_ville=ville_id)).scalar_one_or_none()
	if ville:
		db.session.delete(ville)
		db.session.commit()
		flash('Ville supprimée avec succès !', 'success')
	else:
		flash('Ville non trouvée.', 'danger')
	return redirect(url_for('main.liste_villes'))

# --- Routes pour la gestion des Provinces ---
@main.route('/provinces')
@login_required
@role_required('CHARGE_EXPLOITATION')
def liste_provinces():
	provinces = db.session.execute(db.select(Province).order_by(Province.nom_province)).scalars().all()
	return render_template('list_provinces.html', provinces=provinces)

@main.route('/provinces/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def add_province():
	villes = db.session.execute(db.select(Ville).order_by(Ville.nom_ville)).scalars().all()
	if request.method == 'POST':
		nom_province = request.form['nom_province']
		id_ville = request.form['id_ville']

		new_province = Province(nom_province=nom_province, id_ville=id_ville)
		db.session.add(new_province)
		db.session.commit()
		flash('Province ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_provinces'))
	return render_template('add_province.html', villes=villes)

@main.route('/provinces/edit/<int:province_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def edit_province(province_id):
	province = db.session.execute(db.select(Province).filter_by(id_province=province_id)).scalar_one_or_none()
	if province is None:
		flash('Province non trouvée.', 'danger')
		return redirect(url_for('main.liste_provinces'))

	villes = db.session.execute(db.select(Ville).order_by(Ville.nom_ville)).scalars().all()
	if request.method == 'POST':
		province.nom_province = request.form['nom_province']
		province.id_ville = request.form['id_ville']
		db.session.commit()
		flash('Province modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_provinces'))
	return render_template('edit_province.html', province=province, villes=villes)

@main.route('/provinces/delete/<int:province_id>')
@login_required
@role_required('CHARGE_EXPLOITATION')
def delete_province(province_id):
	province = db.session.execute(db.select(Province).filter_by(id_province=province_id)).scalar_one_or_none()
	if province:
		db.session.delete(province)
		db.session.commit()
		flash('Province supprimée avec succès !', 'success')
	else:
		flash('Province non trouvée.', 'danger')
	return redirect(url_for('main.liste_provinces'))

# --- Routes pour la gestion des Destinations ---
@main.route('/destinations')
@login_required
@role_required('CHARGE_EXPLOITATION')
def liste_destinations():
	destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()
	return render_template('list_destinations.html', destinations=destinations)

@main.route('/destinations/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def add_destination():
	villes = db.session.execute(db.select(Ville).order_by(Ville.nom_ville)).scalars().all()
	provinces = db.session.execute(db.select(Province).order_by(Province.nom_province)).scalars().all()
	if request.method == 'POST':
		description = request.form['description']
		latitude = request.form['latitude']
		longitude = request.form['longitude']
		id_ville = request.form.get('id_ville')
		id_province = request.form.get('id_province')

		new_destination = Destination(
			description=description, latitude=latitude, longitude=longitude,
			id_ville=id_ville if id_ville else None, id_province=id_province if id_province else None
		)
		db.session.add(new_destination)
		db.session.commit()
		flash('Destination ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_destinations'))
	return render_template('add_destination.html', villes=villes, provinces=provinces)

@main.route('/destinations/edit/<int:destination_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def edit_destination(destination_id):
	destination = db.session.execute(db.select(Destination).filter_by(id_destination=destination_id)).scalar_one_or_none()
	if destination is None:
		flash('Destination non trouvée.', 'danger')
		return redirect(url_for('main.liste_destinations'))

	villes = db.session.execute(db.select(Ville).order_by(Ville.nom_ville)).scalars().all()
	provinces = db.session.execute(db.select(Province).order_by(Province.nom_province)).scalars().all()
	if request.method == 'POST':
		destination.description = request.form['description']
		destination.latitude = request.form['latitude']
		destination.longitude = request.form['longitude']
		destination.id_ville = request.form.get('id_ville') if request.form.get('id_ville') else None
		destination.id_province = request.form.get('id_province') if request.form.get('id_province') else None
		db.session.commit()
		flash('Destination modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_destinations'))
	return render_template('edit_destination.html', destination=destination, villes=villes, provinces=provinces)

@main.route('/destinations/delete/<int:destination_id>')
@login_required
@role_required('CHARGE_EXPLOITATION')
def delete_destination(destination_id):
	destination = db.session.execute(db.select(Destination).filter_by(id_destination=destination_id)).scalar_one_or_none()
	if destination:
		db.session.delete(destination)
		db.session.commit()
		flash('Destination supprimée avec succès !', 'success')
	else:
		flash('Destination non trouvée.', 'danger')
	return redirect(url_for('main.liste_destinations'))

# --- Routes pour la gestion des Utilisateurs ---
@main.route('/users')
@login_required
@role_required('ADMIN')
def liste_users():
	search_query = request.args.get('search', '').strip() 
	
	query = db.select(User).order_by(User.username)

	if search_query:
		query = query.filter(
			db.or_(
				User.username.ilike(f'%{search_query}%'),
				User.email.ilike(f'%{search_query}%'),
				User.role.ilike(f'%{search_query}%')
			)
		)

	users = db.session.execute(query).scalars().all()
	
	return render_template('list_users.html', users=users, roles=ROLES, search_query=search_query)

@main.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def add_user():
	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()
	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()

	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		role = request.form['role']

		user_id_client_initial = None
		user_id_chauffeur = None

		if role == 'CLIENT':
			id_client_initial_form = request.form.get('id_client_initial')
			if id_client_initial_form:
				try:
					user_id_client_initial = int(id_client_initial_form)
				except ValueError:
					flash("ID Client Initial invalide.", "danger")
					return render_template('add_user.html', roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs, username=username, email=email, role=role)
		elif role == 'CHAUFFEUR':
			id_chauffeur_form = request.form.get('id_chauffeur')
			if id_chauffeur_form:
				try:
					user_id_chauffeur = int(id_chauffeur_form)
				except ValueError:
					flash("ID Chauffeur invalide.", "danger")
					return render_template('add_user.html', roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs, username=username, email=email, role=role)
		
		existing_user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
		if existing_user:
			flash("Un utilisateur avec ce nom d'utilisateur existe déjà.", 'danger')
			return render_template('add_user.html', roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs, username=username, email=email, role=role)
		
		existing_email = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
		if existing_email:
			flash("Un utilisateur avec cet email existe déjà.", 'danger')
			return render_template('add_user.html', roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs, username=username, email=email, role=role)

		new_user = User(username=username, email=email, role=role)
		if user_id_client_initial:
			new_user.id_client_initial = user_id_client_initial
		if user_id_chauffeur:
			new_user.id_chauffeur = user_id_chauffeur
		
		new_user.set_password(password)
		db.session.add(new_user)
		db.session.commit()
		flash('Utilisateur ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_users'))
	
	return render_template('add_user.html', roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs)


@main.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def edit_user(user_id):
	user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
	if user is None:
		flash('Utilisateur non trouvé.', 'danger')
		return redirect(url_for('main.liste_users'))

	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()
	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()

	if request.method == 'POST':
		user.username = request.form['username']
		user.email = request.form['email']
		new_role = request.form['role']
		new_password = request.form.get('password')

		user_id_client_initial = None
		user_id_chauffeur = None

		if new_role == 'CLIENT':
			id_client_initial_form = request.form.get('id_client_initial')
			if id_client_initial_form:
				try:
					user_id_client_initial = int(id_client_initial_form)
				except ValueError:
					flash("ID Client Initial invalide.", "danger")
					return render_template('edit_user.html', user=user, roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs)
			user.id_client_initial = user_id_client_initial
			user.id_chauffeur = None
		elif new_role == 'CHAUFFEUR':
			id_chauffeur_form = request.form.get('id_chauffeur')
			if id_chauffeur_form:
				try:
					user_id_chauffeur = int(id_chauffeur_form)
				except ValueError:
					flash("ID Chauffeur invalide.", "danger")
					return render_template('edit_user.html', user=user, roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs)
			user.id_chauffeur = user_id_chauffeur
			user.id_client_initial = None
		else:
			user.id_client_initial = None
			user.id_chauffeur = None
		
		user.role = new_role
		
		if new_password:
			user.set_password(new_password)

		existing_username_check = db.session.execute(
			db.select(User).filter(User.username == user.username, User.id != user_id)
		).scalar_one_or_none()
		if existing_username_check:
			flash("Ce nom d'utilisateur est déjà utilisé par un autre compte.", 'danger')
			return render_template('edit_user.html', user=user, roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs)

		existing_email_check = db.session.execute(
			db.select(User).filter(User.email == user.email, User.id != user_id)
		).scalar_one_or_none()
		if existing_email_check:
			flash("Cet email est déjà utilisé par un autre compte.", 'danger')
			return render_template('edit_user.html', user=user, roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs)

		db.session.commit()
		flash('Utilisateur modifié avec succès !', 'success')
		return redirect(url_for('main.liste_users'))
	
	return render_template('edit_user.html', user=user, roles=ROLES, clients_initial=clients_initial, chauffeurs=chauffeurs)

@main.route('/users/delete/<int:user_id>')
@login_required
@role_required('ADMIN')
def delete_user(user_id):
	user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
	if user:
		if user.role == 'ADMIN' and user.id == current_user.id:
			admin_count = db.session.execute(db.select(db.func.count(User.id)).filter_by(role='ADMIN')).scalar()
			if admin_count == 1:
				flash('Vous ne pouvez pas supprimer le seul administrateur du système.', 'danger')
				return redirect(url_for('main.liste_users'))

		db.session.delete(user)
		db.session.commit()
		flash('Utilisateur supprimé avec succès !', 'success')
	else:
		flash('Utilisateur non trouvé.', 'danger')
	return redirect(url_for('main.liste_users'))

# --- Route pour la carte ---
@main.route('/map')
@login_required
@role_required('PLANIFIER')
def map_view():
	missions = db.session.execute(
		db.select(Mission)
		.options(joinedload(Mission.chauffeur))
		.options(joinedload(Mission.vehicule))
		.options(joinedload(Mission.destination))
		.options(selectinload(Mission.details_commandes).joinedload(DetailCommande.destination))
		.options(selectinload(Mission.details_commandes).joinedload(DetailCommande.entete_commande))
		.options(selectinload(Mission.details_commandes).joinedload(DetailCommande.type_vehicule))
		.order_by(Mission.date_debut)
	).scalars().all()
	
	missions_data = []
	for mission in missions:
		mission_dict = mission.to_dict()
		mission_dict['detail_destinations'] = []
		for detail in mission.details_commandes:
			if detail.destination:
				mission_dict['detail_destinations'].append({
					'detail_id': detail.id_detail_commande,
					'description': detail.destination.description,
					'latitude': float(detail.destination.latitude) if detail.destination.latitude else None,
					'longitude': float(detail.destination.longitude) if detail.destination.longitude else None,
					'entete_reference': detail.entete_commande.reference if detail.entete_commande else 'N/A',
					'quantite': detail.quantite,
					'type_vehicule_requis': detail.type_vehicule.nom_type if detail.type_vehicule else 'N/A'
				})
		missions_data.append(mission_dict)

	latest_locations_subquery = db.session.query(
		Localisation.id_chauffeur,
		func.max(Localisation.timestamp).label('max_timestamp')
	).group_by(Localisation.id_chauffeur).subquery()

	chauffeur_locations = db.session.execute(
		db.select(Localisation)
		.join(latest_locations_subquery,
				(Localisation.id_chauffeur == latest_locations_subquery.c.id_chauffeur) &
				(Localisation.timestamp == latest_locations_subquery.c.max_timestamp))
		.options(joinedload(Localisation.chauffeur))
	).scalars().all()

	chauffeur_locations_data = []
	for loc in chauffeur_locations:
		chauffeur_locations_data.append(loc.to_dict())

	return render_template('map_view.html', 
							missions_data=missions_data,
							chauffeur_locations_data=chauffeur_locations_data)

# --- Routes pour la gestion des Clients Initiaux ---
@main.route('/clients_initial')
@login_required
@role_required('COMMERCIAL')
def liste_clients_initial():
	search_query = request.args.get('search', '').strip() 
	
	query = db.select(ClientInitial).order_by(ClientInitial.nom)

	if search_query:
		query = query.filter(
			db.or_(
				ClientInitial.nom.ilike(f'%{search_query}%'),
				ClientInitial.prenom.ilike(f'%{search_query}%'),
				ClientInitial.email.ilike(f'%{search_query}%')
			)
		)

	clients = db.session.execute(query).scalars().all()
	
	return render_template('list_clients_initial.html', clients=clients, search_query=search_query)

@main.route('/clients_initial/add', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def add_client_initial():
	if request.method == 'POST':
		nom = request.form['nom']
		prenom = request.form.get('prenom')
		adresse = request.form.get('adresse')
		numero_telephone = request.form.get('numero_telephone')
		email = request.form.get('email')

		if not nom:
			return render_template('add_client_initial.html', form_error="Le nom est obligatoire.",
								nom=nom, prenom=prenom, adresse=adresse, numero_telephone=numero_telephone, email=email)

		if email:
			existing_client = db.session.execute(db.select(ClientInitial).filter_by(email=email)).scalar_one_or_none()
			if existing_client:
				return render_template('add_client_initial.html', form_error="Un client avec cet email existe déjà.",
									nom=nom, prenom=prenom, adresse=adresse, numero_telephone=numero_telephone, email=email)

		new_client = ClientInitial(
			nom=nom, prenom=prenom, adresse=adresse,
			numero_telephone=numero_telephone, email=email
		)
		db.session.add(new_client)
		db.session.commit()
		flash('Client initial ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_clients_initial'))
	
	return render_template('add_client_initial.html', form_error=None)

@main.route('/clients_initial/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def edit_client_initial(client_id):
	client = db.session.execute(db.select(ClientInitial).filter_by(id_client_initial=client_id)).scalar_one_or_none()
	if client is None:
		flash('Client initial non trouvé.', 'danger')
		return redirect(url_for('main.liste_clients_initial'))

	if request.method == 'POST':
		client.nom = request.form['nom']
		client.prenom = request.form.get('prenom')
		client.adresse = request.form.get('adresse')
		client.numero_telephone = request.form.get('numero_telephone')
		client.email = request.form.get('email')

		if not client.nom:
			return render_template('edit_client_initial.html', client=client, form_error="Le nom est obligatoire.")

		if client.email:
			existing_client_with_email = db.session.execute(
				db.select(ClientInitial).filter(
					ClientInitial.email == client.email, 
					ClientInitial.id_client_initial != client_id
				)
			).scalar_one_or_none()
			if existing_client_with_email:
				return render_template('edit_client_initial.html', client=client, form_error="Un autre client avec cet email existe déjà.")

		db.session.commit()
		flash('Client initial modifié avec succès !', 'success')
		return redirect(url_for('main.liste_clients_initial'))
	
	return render_template('edit_client_initial.html', client=client, form_error=None)

@main.route('/clients_initial/delete/<int:client_id>')
@login_required
@role_required('COMMERCIAL')
def delete_client_initial(client_id):
	client = db.session.execute(db.select(ClientInitial).filter_by(id_client_initial=client_id)).scalar_one_or_none()
	if client:
		db.session.delete(client)
		db.session.commit()
		flash('Client initial supprimé avec succès !', 'success')
	else:
		flash('Client initial non trouvé.', 'danger')
	return redirect(url_for('main.liste_clients_initial'))

@main.route('/service_clients')
@login_required
@role_required('COMMERCIAL')
def liste_service_clients():
	service_clients = db.session.execute(
		db.select(ServiceClient)
		.options(db.joinedload(ServiceClient.client_initial))
		.order_by(ServiceClient.nom_service)
	).scalars().all()
	return render_template('list_service_clients.html', service_clients=service_clients)

@main.route('/service_clients/add', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def add_service_client():
	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()

	if request.method == 'POST':
		nom_service = request.form['nom_service']
		id_client_initial = request.form['id_client_initial']

		if not nom_service or not id_client_initial:
			return render_template('add_service_client.html', 
								clients_initial=clients_initial, 
								form_error="Le nom du service et le client initial sont obligatoires.",
								nom_service=nom_service, id_client_initial=id_client_initial)

		existing_service = db.session.execute(db.select(ServiceClient).filter_by(
			nom_service=nom_service, 
			id_client_initial=id_client_initial
		)).scalar_one_or_none()
		
		if existing_service:
			return render_template('add_service_client.html', 
								clients_initial=clients_initial, 
								form_error="Un service avec ce nom existe déjà pour ce client initial.",
								nom_service=nom_service, id_client_initial=id_client_initial)

		new_service_client = ServiceClient(
			nom_service=nom_service, 
			id_client_initial=id_client_initial
		)
		db.session.add(new_service_client)
		db.session.commit()
		flash('Service client ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_service_clients'))
	
	return render_template('add_service_client.html', clients_initial=clients_initial, form_error=None)

@main.route('/service_clients/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def edit_service_client(service_id):
	service_client = db.session.execute(db.select(ServiceClient).filter_by(id_service=service_id)).scalar_one_or_none()
	if service_client is None:
		flash('Service client non trouvé.', 'danger')
		return redirect(url_for('main.liste_service_clients'))

	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()

	if request.method == 'POST':
		new_nom_service = request.form['nom_service']
		new_id_client_initial = request.form['id_client_initial']

		if not new_nom_service or not new_id_client_initial:
			return render_template('edit_service_client.html', 
								service_client=service_client, 
								clients_initial=clients_initial, 
								form_error="Le nom du service et le client initial sont obligatoires.")

		existing_service_check = db.session.execute(
			db.select(ServiceClient).filter(
				ServiceClient.nom_service == new_nom_service,
				ServiceClient.id_client_initial == new_id_client_initial,
				ServiceClient.id_service != service_id
			)
		).scalar_one_or_none()

		if existing_service_check:
			return render_template('edit_service_client.html', 
								service_client=service_client, 
								clients_initial=clients_initial, 
								form_error="Un autre service avec ce nom existe déjà pour ce client initial.")

		service_client.nom_service = new_nom_service
		service_client.id_client_initial = new_id_client_initial
		db.session.commit()
		flash('Service client modifié avec succès !', 'success')
		return redirect(url_for('main.liste_service_clients'))
	
	return render_template('edit_service_client.html', service_client=service_client, clients_initial=clients_initial, form_error=None)

@main.route('/service_clients/delete/<int:service_id>')
@login_required
@role_required('COMMERCIAL')
def delete_service_client(service_id):
	service_client = db.session.execute(db.select(ServiceClient).filter_by(id_service=service_id)).scalar_one_or_none()
	if service_client:
		db.session.delete(service_client)
		db.session.commit()
		flash('Service client supprimé avec succès !', 'success')
	else:
		flash('Service client non trouvé.', 'danger')
	return redirect(url_for('main.liste_service_clients'))

@main.route('/types_vehicule')
@login_required
@role_required('CHARGE_EXPLOITATION')
def liste_types_vehicule():
	types = db.session.execute(db.select(TypeVehicule).order_by(TypeVehicule.nom_type)).scalars().all()
	return render_template('list_types_vehicule.html', types=types)

@main.route('/types_vehicule/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def add_type_vehicule():
	if request.method == 'POST':
		nom_type = request.form['nom_type']

		if not nom_type:
			return render_template('add_type_vehicule.html', form_error="Le nom du type de véhicule est obligatoire.", nom_type=nom_type)

		existing_type = db.session.execute(db.select(TypeVehicule).filter_by(nom_type=nom_type)).scalar_one_or_none()
		if existing_type:
			return render_template('add_type_vehicule.html', form_error="Un type de véhicule avec ce nom existe déjà.", nom_type=nom_type)

		new_type = TypeVehicule(nom_type=nom_type)
		db.session.add(new_type)
		db.session.commit()
		flash('Type de véhicule ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_types_vehicule'))
	
	return render_template('add_type_vehicule.html', form_error=None)

@main.route('/types_vehicule/edit/<int:type_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def edit_type_vehicule(type_id):
	type_vehicule = db.session.execute(db.select(TypeVehicule).filter_by(id_type_vehicule=type_id)).scalar_one_or_none()
	if type_vehicule is None:
		flash('Type de véhicule non trouvé.', 'danger')
		return redirect(url_for('main.liste_types_vehicule'))

	if request.method == 'POST':
		new_nom_type = request.form['nom_type']

		if not new_nom_type:
			return render_template('edit_type_vehicule.html', type_vehicule=type_vehicule, form_error="Le nom du type de véhicule est obligatoire.")

		existing_type_check = db.session.execute(
			db.select(TypeVehicule).filter(
				TypeVehicule.nom_type == new_nom_type,
				TypeVehicule.id_type_vehicule != type_id
			)
		).scalar_one_or_none()

		if existing_type_check:
			return render_template('edit_type_vehicule.html', type_vehicule=type_vehicule, form_error="Un autre type de véhicule avec ce nom existe déjà.")

		type_vehicule.nom_type = new_nom_type
		db.session.commit()
		flash('Type de véhicule modifié avec succès !', 'success')
		return redirect(url_for('main.liste_types_vehicule'))
	
	return render_template('edit_type_vehicule.html', type_vehicule=type_vehicule, form_error=None)

@main.route('/types_vehicule/delete/<int:type_id>')
@login_required
@role_required('CHARGE_EXPLOITATION')
def delete_type_vehicule(type_id):
	type_vehicule = db.session.execute(db.select(TypeVehicule).filter_by(id_type_vehicule=type_id)).scalar_one_or_none()
	if type_vehicule:
		db.session.delete(type_vehicule)
		db.session.commit()
		flash('Type de véhicule supprimé avec succès !', 'success')
	else:
		flash('Type de véhicule non trouvé.', 'danger')
	return redirect(url_for('main.liste_types_vehicule'))

@main.route('/entetes_commande')
@login_required
@role_required('COMMERCIAL')
def liste_entetes_commande():
	search_reference = request.args.get('reference', '').strip()
	search_client = request.args.get('client', '').strip()
	search_service = request.args.get('service', '').strip()

	query = db.select(EnteteCommande) \
			.options(joinedload(EnteteCommande.client_initial)) \
			.options(joinedload(EnteteCommande.service_client)) \
			.order_by(EnteteCommande.date_commande.desc())

	if search_reference:
		query = query.filter(EnteteCommande.reference.ilike(f'%{search_reference}%'))
	
	if search_client:
		query = query.filter(EnteteCommande.client_initial.has(ClientInitial.nom.ilike(f'%{search_client}%')))

	if search_service:
		query = query.filter(EnteteCommande.service_client.has(ServiceClient.nom_service.ilike(f'%{search_service}%')))

	entetes = db.session.execute(query).scalars().all()
	
	return render_template('list_entetes_commande.html', 
						entetes=entetes,
						search_reference=search_reference,
						search_client=search_client,
						search_service=search_service)

@main.route('/entetes_commande/add', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def add_entete_commande():
	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()
	services_clients = db.session.execute(db.select(ServiceClient).order_by(ServiceClient.nom_service)).scalars().all()

	if request.method == 'POST':
		reference = request.form['reference']
		id_client_initial = request.form['id_client_initial']
		id_service = request.form['id_service']

		if not reference or not id_client_initial or not id_service:
			return render_template('add_entete_commande.html', 
								clients_initial=clients_initial, 
								services_clients=services_clients, 
								form_error="Tous les champs obligatoires doivent être remplis.",
								reference=reference, id_client_initial=id_client_initial, id_service=id_service)

		existing_entete = db.session.execute(db.select(EnteteCommande).filter_by(reference=reference)).scalar_one_or_none()
		if existing_entete:
			return render_template('add_entete_commande.html', 
								clients_initial=clients_initial, 
								services_clients=services_clients, 
								form_error="Une entête de commande avec cette référence existe déjà.",
								reference=reference, id_client_initial=id_client_initial, id_service=id_service)

		new_entete = EnteteCommande(
			reference=reference, 
			id_client_initial=id_client_initial, 
			id_service=id_service,
			date_commande=date.today()
		)
		db.session.add(new_entete)
		db.session.commit()
		flash('Entête de commande ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_entetes_commande'))
	
	return render_template('add_entete_commande.html', 
						clients_initial=clients_initial, 
						services_clients=services_clients, 
						form_error=None)

@main.route('/entetes_commande/edit/<int:entete_id>', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def edit_entete_commande(entete_id):
	entete = db.session.execute(db.select(EnteteCommande).filter_by(id_entete_commande=entete_id)).scalar_one_or_none()
	if entete is None:
		flash('Entête de commande non trouvée.', 'danger')
		return redirect(url_for('main.liste_entetes_commande'))

	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()
	services_clients = db.session.execute(db.select(ServiceClient).order_by(ServiceClient.nom_service)).scalars().all()

	if request.method == 'POST':
		new_reference = request.form['reference']
		new_id_client_initial = request.form['id_client_initial']
		new_id_service = request.form['id_service']

		if not new_reference or not new_id_client_initial or not new_id_service:
			return render_template('edit_entete_commande.html', 
								entete=entete, 
								clients_initial=clients_initial, 
								services_clients=services_clients, 
								form_error="Tous les champs obligatoires doivent être remplis.")

		existing_entete_check = db.session.execute(
			db.select(EnteteCommande).filter(
				EnteteCommande.reference == new_reference,
				EnteteCommande.id_entete_commande != entete_id
			)
		).scalar_one_or_none()

		if existing_entete_check:
			return render_template('edit_entete_commande.html', 
								entete=entete, 
								clients_initial=clients_initial, 
								services_clients=services_clients, 
								form_error="Une autre entête de commande avec cette référence existe déjà.")

		entete.reference = new_reference
		entete.id_client_initial = new_id_client_initial
		entete.id_service = new_id_service
		
		db.session.commit()
		flash('Entête de commande modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_entetes_commande'))
	
	return render_template('edit_entete_commande.html', 
						entete=entete, 
						clients_initial=clients_initial, 
						services_clients=services_clients, 
						form_error=None)

@main.route('/entetes_commande/delete/<int:entete_id>')
@login_required
@role_required('COMMERCIAL')
def delete_entete_commande(entete_id):
	entete = db.session.execute(db.select(EnteteCommande).filter_by(id_entete_commande=entete_id)).scalar_one_or_none()
	if entete:
		db.session.delete(entete)
		db.session.commit()
		flash('Entête de commande supprimée avec succès !', 'success')
	else:
		flash('Entête de commande non trouvée.', 'danger')
	return redirect(url_for('main.liste_entetes_commande'))


@main.route('/clients_final')
@login_required
@role_required('COMMERCIAL')
def liste_clients_final():
	clients = db.session.execute(
		db.select(ClientFinal)
		.options(db.joinedload(ClientFinal.client_initial))
		.order_by(ClientFinal.nom)
	).scalars().all()
	return render_template('list_clients_final.html', clients=clients)

@main.route('/clients_final/add', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def add_client_final():
	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()

	if request.method == 'POST':
		nom = request.form['nom']
		prenom = request.form.get('prenom')
		adresse = request.form.get('adresse')
		numero_telephone = request.form.get('numero_telephone')
		email = request.form.get('email')
		id_client_initial = request.form['id_client_initial']

		if not nom or not id_client_initial:
			return render_template('add_client_final.html',
								clients_initial=clients_initial,
								form_error="Le nom et le client initial sont obligatoires.",
								nom=nom, prenom=prenom, adresse=adresse, numero_telephone=numero_telephone, email=email, id_client_initial=id_client_initial)

		new_client = ClientFinal(
			nom=nom, prenom=prenom, adresse=adresse,
			numero_telephone=numero_telephone, email=email,
			id_client_initial=id_client_initial
		)
		db.session.add(new_client)
		db.session.commit()
		flash('Client final ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_clients_final'))

	return render_template('add_client_final.html', clients_initial=clients_initial, form_error=None)

@main.route('/clients_final/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def edit_client_final(client_id):
	client = db.session.execute(db.select(ClientFinal).filter_by(id_client_final=client_id)).scalar_one_or_none()
	if client is None:
		flash('Client final non trouvé.', 'danger')
		return redirect(url_for('main.liste_clients_final'))

	clients_initial = db.session.execute(db.select(ClientInitial).order_by(ClientInitial.nom)).scalars().all()

	if request.method == 'POST':
		client.nom = request.form['nom']
		client.prenom = request.form.get('prenom')
		client.adresse = request.form.get('adresse')
		client.numero_telephone = request.form.get('numero_telephone')
		client.email = request.form.get('email')
		client.id_client_initial = request.form['id_client_initial']

		if not client.nom or not client.id_client_initial:
			return render_template('edit_client_final.html', client=client, clients_initial=clients_initial, form_error="Le nom et le client initial sont obligatoires.")

		db.session.commit()
		flash('Client final modifié avec succès !', 'success')
		return redirect(url_for('main.liste_clients_final'))

	return render_template('edit_client_final.html', client=client, clients_initial=clients_initial, form_error=None)

@main.route('/clients_final/delete/<int:client_id>')
@login_required
@role_required('COMMERCIAL')
def delete_client_final(client_id):
	client = db.session.execute(db.select(ClientFinal).filter_by(id_client_final=client_id)).scalar_one_or_none()
	if client:
		db.session.delete(client)
		db.session.commit()
		flash('Client final supprimé avec succès !', 'success')
	else:
		flash('Client final non trouvé.', 'danger')
	return redirect(url_for('main.liste_clients_final'))

@main.route('/entetes_commande/<int:entete_id>/details')
@login_required
@role_required('COMMERCIAL')
def liste_details_commande(entete_id):
	entete = db.session.execute(db.select(EnteteCommande).filter_by(id_entete_commande=entete_id)).scalar_one_or_none()
	if entete is None:
		flash('Entête de commande non trouvée.', 'danger')
		return redirect(url_for('main.liste_entetes_commande'))
	
	details = db.session.execute(
		db.select(DetailCommande)
		.filter_by(id_entete_commande=entete_id)
		.options(db.joinedload(DetailCommande.type_vehicule))
		.options(db.joinedload(DetailCommande.client_final))
		.options(db.joinedload(DetailCommande.destination))
		.order_by(DetailCommande.id_detail_commande)
	).scalars().all()
	
	return render_template('list_details_commande.html', entete=entete, details=details)


@main.route('/entetes_commande/<int:entete_id>/details/add', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def add_detail_commande(entete_id):
	entete = db.session.execute(db.select(EnteteCommande).filter_by(id_entete_commande=entete_id)).scalar_one_or_none()
	if entete is None:
		flash('Entête de commande non trouvée.', 'danger')
		return redirect(url_for('main.liste_entetes_commande'))
	
	types_vehicule = db.session.execute(db.select(TypeVehicule).order_by(TypeVehicule.nom_type)).scalars().all()
	clients_final = db.session.execute(db.select(ClientFinal).order_by(ClientFinal.nom)).scalars().all()
	destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()

	if request.method == 'POST':
		try:
			quantite = int(request.form['quantite'])
			volume = float(request.form['volume']) if request.form['volume'] else None
			poids = float(request.form['poids']) if request.form['poids'] else None
		except ValueError:
			return render_template('add_detail_commande.html', 
								entete=entete, 
								types_vehicule=types_vehicule, 
								clients_final=clients_final, 
								destinations=destinations, 
								form_error="Quantité, volume ou poids doivent être des nombres valides.")

		description_colis = request.form.get('description_colis')
		id_type_vehicule = request.form['id_type_vehicule']
		id_client_final = request.form['id_client_final']
		id_destination = request.form['id_destination']

		if not quantite or not id_type_vehicule or not id_client_final or not id_destination:
			return render_template('add_detail_commande.html', 
								entete=entete, 
								types_vehicule=types_vehicule, 
								clients_final=clients_final, 
								destinations=destinations, 
								form_error="Tous les champs obligatoires (quantité, type véhicule, client final, destination) doivent être remplis.")
		
		if quantite <= 0:
			return render_template('add_detail_commande.html',
								entete=entete,
								types_vehicule=types_vehicule,
								clients_final=clients_final,
								destinations=destinations,
								form_error="La quantité doit être supérieure à zéro.")


		new_detail = DetailCommande(
			id_entete_commande=entete_id,
			quantite=quantite,
			description_colis=description_colis,
			volume=volume,
			poids=poids,
			id_type_vehicule=id_type_vehicule,
			id_client_final=id_client_final,
			id_destination=id_destination
		)
		db.session.add(new_detail)
		db.session.commit()
		flash('Détail de commande ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_details_commande', entete_id=entete_id))
	
	return render_template('add_detail_commande.html', 
						entete=entete, 
						types_vehicule=types_vehicule, 
						clients_final=clients_final, 
						destinations=destinations, 
						form_error=None)


@main.route('/entetes_commande/<int:entete_id>/details/edit/<int:detail_id>', methods=['GET', 'POST'])
@login_required
@role_required('COMMERCIAL')
def edit_detail_commande(entete_id, detail_id):
	entete = db.session.execute(db.select(EnteteCommande).filter_by(id_entete_commande=entete_id)).scalar_one_or_none()
	detail = db.session.execute(db.select(DetailCommande).filter_by(id_detail_commande=detail_id, id_entete_commande=entete_id)).scalar_one_or_none()

	if entete is None:
		flash('Entête de commande non trouvée.', 'danger')
		return redirect(url_for('main.liste_entetes_commande'))
	if detail is None:
		flash('Détail de commande non trouvé pour cette entête.', 'danger')
		return redirect(url_for('main.liste_details_commande', entete_id=entete_id))

	types_vehicule = db.session.execute(db.select(TypeVehicule).order_by(TypeVehicule.nom_type)).scalars().all()
	clients_final = db.session.execute(db.select(ClientFinal).order_by(ClientFinal.nom)).scalars().all()
	destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()

	if request.method == 'POST':
		try:
			detail.quantite = int(request.form['quantite'])
			detail.volume = float(request.form['volume']) if request.form['volume'] else None
			detail.poids = float(request.form['poids']) if request.form['poids'] else None
		except ValueError:
			return render_template('edit_detail_commande.html', 
								entete=entete, detail=detail, 
								types_vehicule=types_vehicule, 
								clients_final=clients_final, 
								destinations=destinations, 
								form_error="Quantité, volume ou poids doivent être des nombres valides.")

		detail.description_colis = request.form.get('description_colis')
		detail.id_type_vehicule = request.form['id_type_vehicule']
		detail.id_client_final = request.form['id_client_final']
		detail.id_destination = request.form['id_destination']

		if not detail.quantite or not detail.id_type_vehicule or not detail.id_client_final or not detail.id_destination:
			return render_template('edit_detail_commande.html', 
								entete=entete, detail=detail, 
								types_vehicule=types_vehicule, 
								clients_final=clients_final, 
								destinations=destinations, 
								form_error="Tous les champs obligatoires (quantité, type véhicule, client final, destination) doivent être remplis.")
		
		if detail.quantite <= 0:
			return render_template('edit_detail_commande.html',
								entete=entete, detail=detail,
								types_vehicule=types_vehicule,
								clients_final=clients_final,
								destinations=destinations,
								form_error="La quantité doit être supérieure à zéro.")

		db.session.commit()
		flash('Détail de commande modifié avec succès !', 'success')
		return redirect(url_for('main.liste_details_commande', entete_id=entete_id))
	
	return render_template('edit_detail_commande.html', 
						entete=entete, detail=detail, 
						types_vehicule=types_vehicule, 
						clients_final=clients_final, 
						destinations=destinations, 
						form_error=None)

@main.route('/entetes_commande/<int:entete_id>/details/delete/<int:detail_id>')
@login_required
@role_required('COMMERCIAL')
def delete_detail_commande(entete_id, detail_id):
	entete = db.session.execute(db.select(EnteteCommande).filter_by(id_entete_commande=entete_id)).scalar_one_or_none()
	detail = db.session.execute(db.select(DetailCommande).filter_by(id_detail_commande=detail_id, id_entete_commande=entete_id)).scalar_one_or_none()
	
	if entete is None:
		flash('Entête de commande non trouvée.', 'danger')
		return redirect(url_for('main.liste_entetes_commande'))
	if detail:
		db.session.delete(detail)
		db.session.commit()
		flash('Détail de commande supprimé avec succès !', 'success')
	else:
		flash('Détail de commande non trouvé.', 'danger')
	return redirect(url_for('main.liste_details_commande', entete_id=entete_id))

@main.route('/trajets')
@login_required
@role_required('CHARGE_EXPLOITATION')
def liste_trajets():
	trajets = db.session.execute(
		db.select(Trajet)
		.options(db.joinedload(Trajet.destination))
		.order_by(Trajet.id_trajet)
	).scalars().all()
	return render_template('list_trajets.html', trajets=trajets)

@main.route('/trajets/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def add_trajet():
	destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()

	if request.method == 'POST':
		description = request.form.get('description')
		id_destination = request.form['id_destination']
		
		try:
			distance_km = float(request.form['distance_km']) if request.form['distance_km'] else None
			duree_heures = float(request.form['duree_heures']) if request.form['duree_heures'] else None
		except ValueError:
			return render_template('add_trajet.html', 
								destinations=destinations, 
								form_error="Distance et durée doivent être des nombres valides.",
								description=description, id_destination=id_destination)

		if not id_destination:
			return render_template('add_trajet.html', 
								destinations=destinations, 
								form_error="La destination est obligatoire.",
								description=description, id_destination=id_destination)

		new_trajet = Trajet(
			description=description, 
			distance_km=distance_km, 
			duree_heures=duree_heures,
			id_destination=id_destination
		)
		db.session.add(new_trajet)
		db.session.commit()
		flash('Trajet ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_trajets'))
	
	return render_template('add_trajet.html', destinations=destinations, form_error=None)

@main.route('/trajets/edit/<int:trajet_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_EXPLOITATION')
def edit_trajet(trajet_id):
	trajet = db.session.execute(db.select(Trajet).filter_by(id_trajet=trajet_id)).scalar_one_or_none()
	if trajet is None:
		flash('Trajet non trouvé.', 'danger')
		return redirect(url_for('main.liste_trajets'))

	destinations = db.session.execute(db.select(Destination).order_by(Destination.description)).scalars().all()

	if request.method == 'POST':
		trajet.description = request.form.get('description')
		trajet.id_destination = request.form['id_destination']
		
		try:
			trajet.distance_km = float(request.form['distance_km']) if request.form['distance_km'] else None
			trajet.duree_heures = float(request.form['duree_heures']) if request.form['duree_heures'] else None
		except ValueError:
			return render_template('edit_trajet.html', 
								trajet=trajet, 
								destinations=destinations, 
								form_error="Distance et durée doivent être des nombres valides.")

		if not trajet.id_destination:
			return render_template('edit_trajet.html', 
								trajet=trajet, 
								destinations=destinations, 
								form_error="La destination est obligatoire.")

		db.session.commit()
		flash('Trajet modifié avec succès !', 'success')
		return redirect(url_for('main.liste_trajets'))
	
	return render_template('edit_trajet.html', trajet=trajet, destinations=destinations, form_error=None)

@main.route('/trajets/delete/<int:trajet_id>')
@login_required
@role_required('CHARGE_EXPLOITATION')
def delete_trajet(trajet_id):
	trajet = db.session.execute(db.select(Trajet).filter_by(id_trajet=trajet_id)).scalar_one_or_none()
	if trajet:
		db.session.delete(trajet)
		db.session.commit()
		flash('Trajet supprimé avec succès !', 'success')
	else:
		flash('Trajet non trouvé.', 'danger')
	return redirect(url_for('main.liste_trajets'))

@main.route('/sous_traitants')
@login_required
@role_required('APPROVISIONNEUR')
def liste_sous_traitants():
	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()
	return render_template('list_sous_traitants.html', sous_traitants=sous_traitants)

@main.route('/sous_traitants/add', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def add_sous_traitant():
	if request.method == 'POST':
		nom_entreprise = request.form['nom_entreprise']
		contact_personne = request.form.get('contact_personne')
		numero_telephone = request.form.get('numero_telephone')
		email = request.form.get('email')
		adresse = request.form.get('adresse')

		if not nom_entreprise:
			return render_template('add_sous_traitant.html', 
								form_error="Le nom de l'entreprise est obligatoire.",
								nom_entreprise=nom_entreprise, contact_personne=contact_personne, 
								numero_telephone=numero_telephone, email=email, adresse=adresse)

		existing_by_name = db.session.execute(db.select(SousTraitant).filter_by(nom_entreprise=nom_entreprise)).scalar_one_or_none()
		if existing_by_name:
			return render_template('add_sous_traitant.html', 
								form_error="Une entreprise avec ce nom existe déjà.",
								nom_entreprise=nom_entreprise, contact_personne=contact_personne, 
								numero_telephone=numero_telephone, email=email, adresse=adresse)
		
		if email:
			existing_by_email = db.session.execute(db.select(SousTraitant).filter_by(email=email)).scalar_one_or_none()
			if existing_by_email:
				return render_template('add_sous_traitant.html', 
									form_error="Un sous-traitant avec cet email existe déjà.",
									nom_entreprise=nom_entreprise, contact_personne=contact_personne, 
									numero_telephone=numero_telephone, email=email, adresse=adresse)

		new_sous_traitant = SousTraitant(
			nom_entreprise=nom_entreprise,
			contact_personne=contact_personne,
			numero_telephone=numero_telephone,
			email=email,
			adresse=adresse
		)
		db.session.add(new_sous_traitant)
		db.session.commit()
		flash('Sous-traitant ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_sous_traitants'))
	
	return render_template('add_sous_traitant.html', form_error=None)

@main.route('/sous_traitants/edit/<int:st_id>', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def edit_sous_traitant(st_id):
	sous_traitant = db.session.execute(db.select(SousTraitant).filter_by(id_sous_traitant=st_id)).scalar_one_or_none()
	if sous_traitant is None:
		flash('Sous-traitant non trouvé.', 'danger')
		return redirect(url_for('main.liste_sous_traitants'))

	if request.method == 'POST':
		new_nom_entreprise = request.form['nom_entreprise']
		new_contact_personne = request.form.get('contact_personne')
		new_numero_telephone = request.form.get('numero_telephone')
		new_email = request.form.get('email')
		new_adresse = request.form.get('adresse')

		if not new_nom_entreprise:
			return render_template('edit_sous_traitant.html', 
								sous_traitant=sous_traitant, 
								form_error="Le nom de l'entreprise est obligatoire.")

		existing_by_name_check = db.session.execute(
			db.select(SousTraitant).filter(
				SousTraitant.nom_entreprise == new_nom_entreprise,
				SousTraitant.id_sous_traitant != st_id
			)
		).scalar_one_or_none()
		if existing_by_name_check:
			return render_template('edit_sous_traitant.html', 
								sous_traitant=sous_traitant, 
								form_error="Une autre entreprise avec ce nom existe déjà.")

		if new_email:
			existing_by_email_check = db.session.execute(
				db.select(SousTraitant).filter(
					SousTraitant.email == new_email,
					SousTraitant.id_sous_traitant != st_id
				)
			).scalar_one_or_none()
			if existing_by_email_check:
				return render_template('edit_sous_traitant.html', 
									sous_traitant=sous_traitant, 
									form_error="Un autre sous-traitant avec cet email existe déjà.")

		sous_traitant.nom_entreprise = new_nom_entreprise
		sous_traitant.contact_personne = new_contact_personne
		sous_traitant.numero_telephone = new_numero_telephone
		sous_traitant.email = new_email
		sous_traitant.adresse = new_adresse
		
		db.session.commit()
		flash('Sous-traitant modifié avec succès !', 'success')
		return redirect(url_for('main.liste_sous_traitants'))
	
	return render_template('edit_sous_traitant.html', sous_traitant=sous_traitant, form_error=None)

@main.route('/sous_traitants/delete/<int:st_id>')
@login_required
@role_required('APPROVISIONNEUR')
def delete_sous_traitant(st_id):
	sous_traitant = db.session.execute(db.select(SousTraitant).filter_by(id_sous_traitant=st_id)).scalar_one_or_none()
	if sous_traitant:
		db.session.delete(sous_traitant)
		db.session.commit()
		flash('Sous-traitant supprimé avec succès !', 'success')
	else:
		flash('Sous-traitant non trouvé.', 'danger')
	return redirect(url_for('main.liste_sous_traitants'))

@main.route('/types_indispo_chauffeur')
@login_required
@role_required('RH')
def liste_types_indispo_chauffeur():
	types = db.session.execute(db.select(TypeIndispoChauffeur).order_by(TypeIndispoChauffeur.nom_type)).scalars().all()
	return render_template('list_types_indispo_chauffeur.html', types=types)

@main.route('/types_indispo_chauffeur/add', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def add_type_indispo_chauffeur():
	if request.method == 'POST':
		nom_type = request.form['nom_type']

		if not nom_type:
			return render_template('add_type_indispo_chauffeur.html', form_error="Le nom du type d'indisponibilité est obligatoire.", nom_type=nom_type)

		existing_type = db.session.execute(db.select(TypeIndispoChauffeur).filter_by(nom_type=nom_type)).scalar_one_or_none()
		if existing_type:
			return render_template('add_type_indispo_chauffeur.html', form_error="Un type d'indisponibilité avec ce nom existe déjà.", nom_type=nom_type)

		new_type = TypeIndispoChauffeur(nom_type=nom_type)
		db.session.add(new_type)
		db.session.commit()
		flash("Type d'indisponibilité chauffeur ajouté avec succès !", 'success')
		return redirect(url_for('main.liste_types_indispo_chauffeur'))
	
	return render_template('add_type_indispo_chauffeur.html', form_error=None)

@main.route('/types_indispo_chauffeur/edit/<int:type_id>', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def edit_type_indispo_chauffeur(type_id):
	type_indispo = db.session.execute(db.select(TypeIndispoChauffeur).filter_by(id_type_indispo_chauffeur=type_id)).scalar_one_or_none()
	if type_indispo is None:
		flash("Type d'indisponibilité chauffeur non trouvé.", 'danger')
		return redirect(url_for('main.liste_types_indispo_chauffeur'))

	if request.method == 'POST':
		new_nom_type = request.form['nom_type']

		if not new_nom_type:
			return render_template('edit_type_indispo_chauffeur.html', type_indispo=type_indispo, form_error="Le nom du type d'indisponibilité est obligatoire.")

		existing_type_check = db.session.execute(
			db.select(TypeIndispoChauffeur).filter(
				TypeIndispoChauffeur.nom_type == new_nom_type,
				TypeIndispoChauffeur.id_type_indispo_chauffeur != type_id
			)
		).scalar_one_or_none()

		if existing_type_check:
			return render_template('edit_type_indispo_chauffeur.html', type_indispo=type_indispo, form_error="Un autre type d'indisponibilité avec ce nom existe déjà.")

		type_indispo.nom_type = new_nom_type
		db.session.commit()
		flash("Type d'indisponibilité chauffeur modifié avec succès !", 'success')
		return redirect(url_for('main.liste_types_indispo_chauffeur'))
	
	return render_template('edit_type_indispo_chauffeur.html', type_indispo=type_indispo, form_error=None)

@main.route('/types_indispo_chauffeur/delete/<int:type_id>')
@login_required
@role_required('RH')
def delete_type_indispo_chauffeur(type_id):
	type_indispo = db.session.execute(db.select(TypeIndispoChauffeur).filter_by(id_type_indispo_chauffeur=type_id)).scalar_one_or_none()
	if type_indispo:
		db.session.delete(type_indispo)
		db.session.commit()
		flash("Type d'indisponibilité chauffeur supprimé avec succès !", 'success')
	else:
		flash("Type d'indisponibilité chauffeur non trouvé.", 'danger')
	return redirect(url_for('main.liste_types_indispo_chauffeur'))


# --- Routes pour la gestion des Types d'Indisponibilité Véhicule ---
@main.route('/types_indispo_vehicule')
@login_required
@role_required('CHARGE_MAINTENANCE')
def liste_types_indispo_vehicule():
	types = db.session.execute(db.select(TypeIndispoVehicule).order_by(TypeIndispoVehicule.nom_type)).scalars().all()
	return render_template('list_types_indispo_vehicule.html', types=types)

@main.route('/types_indispo_vehicule/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_MAINTENANCE')
def add_type_indispo_vehicule():
	if request.method == 'POST':
		nom_type = request.form['nom_type']

		if not nom_type:
			return render_template('add_type_indispo_vehicule.html', form_error="Le nom du type d'indisponibilité est obligatoire.", nom_type=nom_type)

		existing_type = db.session.execute(db.select(TypeIndispoVehicule).filter_by(nom_type=nom_type)).scalar_one_or_none()
		if existing_type:
			return render_template('add_type_indispo_vehicule.html', form_error="Un type d'indisponibilité avec ce nom existe déjà.", nom_type=nom_type)

		new_type = TypeIndispoVehicule(nom_type=nom_type)
		db.session.add(new_type)
		db.session.commit()
		flash("Type d'indisponibilité véhicule ajouté avec succès !", 'success')
		return redirect(url_for('main.liste_types_indispo_vehicule'))
	
	return render_template('add_type_indispo_vehicule.html', form_error=None)

@main.route('/types_indispo_vehicule/edit/<int:type_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_MAINTENANCE')
def edit_type_indispo_vehicule(type_id):
	type_indispo = db.session.execute(db.select(TypeIndispoVehicule).filter_by(id_type_indispo_vehicule=type_id)).scalar_one_or_none()
	if type_indispo is None:
		flash("Type d'indisponibilité véhicule non trouvé.", 'danger')
		return redirect(url_for('main.liste_types_indispo_vehicule'))

	if request.method == 'POST':
		new_nom_type = request.form['nom_type']

		if not new_nom_type:
			return render_template('edit_type_indispo_vehicule.html', type_indispo=type_indispo, form_error="Le nom du type d'indisponibilité est obligatoire.")

		existing_type_check = db.session.execute(
			db.select(TypeIndispoVehicule).filter(
				TypeIndispoVehicule.nom_type == new_nom_type,
				TypeIndispoVehicule.id_type_indispo_vehicule != type_id
			)
		).scalar_one_or_none()

		if existing_type_check:
			return render_template('edit_type_indispo_vehicule.html', type_indispo=type_indispo, form_error="Un autre type d'indisponibilité avec ce nom existe déjà.")

		type_indispo.nom_type = new_nom_type
		db.session.commit()
		flash("Type d'indisponibilité véhicule modifié avec succès !", 'success')
		return redirect(url_for('main.liste_types_indispo_vehicule'))
	
	return render_template('edit_type_indispo_vehicule.html', type_indispo=type_indispo, form_error=None)

@main.route('/types_indispo_vehicule/delete/<int:type_id>')
@login_required
@role_required('CHARGE_MAINTENANCE')
def delete_type_indispo_vehicule(type_id):
	type_indispo = db.session.execute(db.select(TypeIndispoVehicule).filter_by(id_type_indispo_vehicule=type_id)).scalar_one_or_none()
	if type_indispo:
		db.session.delete(type_indispo)
		db.session.commit()
		flash("Type d'indisponibilité véhicule supprimé avec succès !", 'success')
	else:
		flash("Type d'indisponibilité véhicule non trouvé.", 'danger')
	return redirect(url_for('main.liste_types_indispo_vehicule'))

@main.route('/indispo_chauffeur')
@login_required
@role_required('RH')
def liste_indispo_chauffeur():
	indispos = db.session.execute(
		db.select(IndisponibiliteChauffeur)
		.options(db.joinedload(IndisponibiliteChauffeur.chauffeur))
		.options(db.joinedload(IndisponibiliteChauffeur.type_indispo_chauffeur))
		.order_by(IndisponibiliteChauffeur.date_debut.desc())
	).scalars().all()
	return render_template('list_indispo_chauffeur.html', indispos=indispos)

@main.route('/indispo_chauffeur/add', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def add_indispo_chauffeur():
	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
	types_indispo = db.session.execute(db.select(TypeIndispoChauffeur).order_by(TypeIndispoChauffeur.nom_type)).scalars().all()

	if request.method == 'POST':
		id_chauffeur = request.form['id_chauffeur']
		id_type_indispo_chauffeur = request.form['id_type_indispo_chauffeur']
		date_debut_str = request.form['date_debut']
		date_fin_str = request.form['date_fin']
		description = request.form.get('description')

		try:
			date_debut = date.fromisoformat(date_debut_str)
			date_fin = date.fromisoformat(date_fin_str)
		except ValueError:
			return render_template('add_indispo_chauffeur.html',
								chauffeurs=chauffeurs, types_indispo=types_indispo,
								form_error="Format de date invalide.")

		if date_fin < date_debut:
			return render_template('add_indispo_chauffeur.html',
								chauffeurs=chauffeurs, types_indispo=types_indispo,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		existing_indispos = db.session.execute(
			db.select(IndisponibiliteChauffeur).filter(
				IndisponibiliteChauffeur.id_chauffeur == id_chauffeur,
				IndisponibiliteChauffeur.date_debut <= date_fin,
				IndisponibiliteChauffeur.date_fin >= date_debut
			)
		).scalar_one_or_none()
		
		if existing_indispos:
			return render_template('add_indispo_chauffeur.html',
								chauffeurs=chauffeurs, types_indispo=types_indispo,
								form_error=f"Le chauffeur est déjà indisponible du {existing_indispos.date_debut.strftime('%d/%m/%Y')} au {existing_indispos.date_fin.strftime('%d/%m/%Y')}.")

		new_indispo = IndisponibiliteChauffeur(
			id_chauffeur=id_chauffeur,
			id_type_indispo_chauffeur=id_type_indispo_chauffeur,
			date_debut=date_debut,
			date_fin=date_fin,
			description=description
		)
		db.session.add(new_indispo)
		db.session.commit()
		flash('Indisponibilité chauffeur ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_indispo_chauffeur'))
	
	return render_template('add_indispo_chauffeur.html', chauffeurs=chauffeurs, types_indispo=types_indispo, form_error=None)

@main.route('/indispo_chauffeur/edit/<int:indispo_id>', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def edit_indispo_chauffeur(indispo_id):
	indispo = db.session.execute(db.select(IndisponibiliteChauffeur).filter_by(id_indispo_chauffeur=indispo_id)).scalar_one_or_none()
	if indispo is None:
		flash("Indisponibilité chauffeur non trouvée.", 'danger')
		return redirect(url_for('main.liste_indispo_chauffeur'))

	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
	types_indispo = db.session.execute(db.select(TypeIndispoChauffeur).order_by(TypeIndispoChauffeur.nom_type)).scalars().all()

	if request.method == 'POST':
		new_id_chauffeur = request.form['id_chauffeur']
		new_id_type_indispo_chauffeur = request.form['id_type_indispo_chauffeur']
		new_date_debut_str = request.form['date_debut']
		new_date_fin_str = request.form['date_fin']
		new_description = request.form.get('description')

		try:
			new_date_debut = date.fromisoformat(new_date_debut_str)
			new_date_fin = date.fromisoformat(new_date_fin_str)
		except ValueError:
			return render_template('edit_indispo_chauffeur.html',
								indispo=indispo, chauffeurs=chauffeurs, types_indispo=types_indispo,
								form_error="Format de date invalide.")

		if new_date_fin < new_date_debut:
			return render_template('edit_indispo_chauffeur.html',
								indispo=indispo, chauffeurs=chauffeurs, types_indispo=types_indispo,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		existing_indispos_check = db.session.execute(
			db.select(IndisponibiliteChauffeur).filter(
				IndisponibiliteChauffeur.id_chauffeur == new_id_chauffeur,
				IndisponibiliteChauffeur.date_debut <= new_date_fin,
				IndisponibiliteChauffeur.date_fin >= new_date_debut,
				IndisponibiliteChauffeur.id_indispo_chauffeur != indispo_id
			)
		).scalar_one_or_none()

		if existing_indispos_check:
			return render_template('edit_indispo_chauffeur.html',
								indispo=indispo, chauffeurs=chauffeurs, types_indispo=types_indispo,
								form_error=f"Le chauffeur est déjà indisponible du {existing_indispos_check.date_debut.strftime('%d/%m/%Y')} au {existing_indispos_check.date_fin.strftime('%d/%m/%Y')}.")

		indispo.id_chauffeur = new_id_chauffeur
		indispo.id_type_indispo_chauffeur = new_id_type_indispo_chauffeur
		indispo.date_debut = new_date_debut
		indispo.date_fin = new_date_fin
		indispo.description = new_description
		
		db.session.commit()
		flash('Indisponibilité chauffeur modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_indispo_chauffeur'))
	
	return render_template('edit_indispo_chauffeur.html', indispo=indispo, chauffeurs=chauffeurs, types_indispo=types_indispo, form_error=None)

@main.route('/indispo_chauffeur/delete/<int:indispo_id>')
@login_required
@role_required('RH')
def delete_indispo_chauffeur(indispo_id):
	indispo = db.session.execute(db.select(IndisponibiliteChauffeur).filter_by(id_indispo_chauffeur=indispo_id)).scalar_one_or_none()
	if indispo:
		db.session.delete(indispo)
		db.session.commit()
		flash('Indisponibilité chauffeur supprimée avec succès !', 'success')
	else:
		flash('Indisponibilité chauffeur non trouvée.', 'danger')
	return redirect(url_for('main.liste_indispo_chauffeur'))


# --- Routes pour la gestion des Indisponibilités Véhicule ---
@main.route('/indispo_vehicule')
@login_required
@role_required('CHARGE_MAINTENANCE')
def liste_indispo_vehicule():
	indispos = db.session.execute(
		db.select(IndisponibiliteVehicule)
		.options(db.joinedload(IndisponibiliteVehicule.vehicule))
		.options(db.joinedload(IndisponibiliteVehicule.type_indispo_vehicule))
		.order_by(IndisponibiliteVehicule.date_debut.desc())
	).scalars().all()
	return render_template('list_indispo_vehicule.html', indispos=indispos)

@main.route('/indispo_vehicule/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_MAINTENANCE')
def add_indispo_vehicule():
	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()
	types_indispo = db.session.execute(db.select(TypeIndispoVehicule).order_by(TypeIndispoVehicule.nom_type)).scalars().all()

	if request.method == 'POST':
		id_vehicule = request.form['id_vehicule']
		id_type_indispo_vehicule = request.form['id_type_indispo_vehicule']
		date_debut_str = request.form['date_debut']
		date_fin_str = request.form['date_fin']
		description = request.form.get('description')

		try:
			date_debut = date.fromisoformat(date_debut_str)
			date_fin = date.fromisoformat(date_fin_str)
		except ValueError:
			return render_template('add_indispo_vehicule.html',
								vehicules=vehicules, types_indispo=types_indispo,
								form_error="Format de date invalide.")

		if date_fin < date_debut:
			return render_template('add_indispo_vehicule.html',
								vehicules=vehicules, types_indispo=types_indispo,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		existing_indispos = db.session.execute(
			db.select(IndisponibiliteVehicule).filter(
				IndisponibiliteVehicule.id_vehicule == id_vehicule,
				IndisponibiliteVehicule.date_debut <= date_fin,
				IndisponibiliteVehicule.date_fin >= date_debut
			)
		).scalar_one_or_none()
		
		if existing_indispos:
			return render_template('add_indispo_vehicule.html',
								vehicules=vehicules, types_indispo=types_indispo,
								form_error=f"Le véhicule est déjà indisponible du {existing_indispos.date_debut.strftime('%d/%m/%Y')} au {existing_indispos.date_fin.strftime('%d/%m/%Y')}.")


		new_indispo = IndisponibiliteVehicule(
			id_vehicule=id_vehicule,
			id_type_indispo_vehicule=id_type_indispo_vehicule,
			date_debut=date_debut,
			date_fin=date_fin,
			description=description
		)
		db.session.add(new_indispo)
		db.session.commit()
		flash('Indisponibilité véhicule ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_indispo_vehicule'))
	
	return render_template('add_indispo_vehicule.html', vehicules=vehicules, types_indispo=types_indispo, form_error=None)

@main.route('/indispo_vehicule/edit/<int:indispo_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_MAINTENANCE')
def edit_indispo_vehicule(indispo_id):
	indispo = db.session.execute(db.select(IndisponibiliteVehicule).filter_by(id_indispo_vehicule=indispo_id)).scalar_one_or_none()
	if indispo is None:
		flash("Indisponibilité véhicule non trouvée.", 'danger')
		return redirect(url_for('main.liste_indispo_vehicule'))

	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()
	types_indispo = db.session.execute(db.select(TypeIndispoVehicule).order_by(TypeIndispoVehicule.nom_type)).scalars().all()

	if request.method == 'POST':
		new_id_vehicule = request.form['id_vehicule']
		new_id_type_indispo_vehicule = request.form['id_type_indispo_vehicule']
		new_date_debut_str = request.form['date_debut']
		new_date_fin_str = request.form['date_fin']
		new_description = request.form.get('description')

		try:
			new_date_debut = date.fromisoformat(new_date_debut_str)
			new_date_fin = date.fromisoformat(new_date_fin_str)
		except ValueError:
			return render_template('edit_indispo_vehicule.html',
								indispo=indispo, vehicules=vehicules, types_indispo=types_indispo,
								form_error="Format de date invalide.")

		if new_date_fin < new_date_debut:
			return render_template('edit_indispo_vehicule.html',
								indispo=indispo, vehicules=vehicules, types_indispo=types_indispo,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		existing_indispos_check = db.session.execute(
			db.select(IndisponibiliteVehicule).filter(
				IndisponibiliteVehicule.id_vehicule == new_id_vehicule,
				IndisponibiliteVehicule.date_debut <= new_date_fin,
				IndisponibiliteVehicule.date_fin >= new_date_debut,
				IndisponibiliteVehicule.id_indispo_vehicule != indispo_id
			)
		).scalar_one_or_none()

		if existing_indispos_check:
			return render_template('edit_indispo_vehicule.html',
								indispo=indispo, vehicules=vehicules, types_indispo=types_indispo,
								form_error=f"Le véhicule est déjà indisponible du {existing_indispos_check.date_debut.strftime('%d/%m/%Y')} au {existing_indispos_check.date_fin.strftime('%d/%m/%Y')}.")

		indispo.id_vehicule = new_id_vehicule
		indispo.id_type_indispo_vehicule = new_id_type_indispo_vehicule
		indispo.date_debut = new_date_debut
		indispo.date_fin = new_date_fin
		indispo.description = new_description
		
		db.session.commit()
		flash('Indisponibilité véhicule modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_indispo_vehicule'))
	
	return render_template('edit_indispo_vehicule.html', indispo=indispo, vehicules=vehicules, types_indispo=types_indispo, form_error=None)

@main.route('/indispo_vehicule/delete/<int:indispo_id>')
@login_required
@role_required('CHARGE_MAINTENANCE')
def delete_indispo_vehicule(indispo_id):
	indispo = db.session.execute(db.select(IndisponibiliteVehicule).filter_by(id_indispo_vehicule=indispo_id)).scalar_one_or_none()
	if indispo:
		db.session.delete(indispo)
		db.session.commit()
		flash('Indisponibilité véhicule supprimée avec succès !', 'success')
	else:
		flash('Indisponibilité véhicule non trouvée.', 'danger')
	return redirect(url_for('main.liste_indispo_vehicule'))


@main.route('/vehicules_externes')
@login_required
@role_required('APPROVISIONNEUR')
def liste_vehicules_externes():
	vehicules_externes = db.session.execute(
		db.select(VehiculeExterne)
		.options(db.joinedload(VehiculeExterne.sous_traitant))
		.order_by(VehiculeExterne.immatriculation_ve)
	).scalars().all()
	return render_template('list_vehicules_externes.html', vehicules_externes=vehicules_externes)

@main.route('/vehicules_externes/add', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def add_vehicule_externe():
	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()

	if request.method == 'POST':
		immatriculation_ve = request.form['immatriculation_ve']
		categorie = request.form.get('categorie')
		description = request.form.get('description')
		id_sous_traitant = request.form['id_sous_traitant']

		if not immatriculation_ve or not id_sous_traitant:
			return render_template('add_vehicule_externe.html', 
								sous_traitants=sous_traitants,
								form_error="Immatriculation et sous-traitant sont obligatoires.",
								immatriculation_ve=immatriculation_ve, categorie=categorie, description=description, id_sous_traitant=id_sous_traitant)

		existing_vehicule = db.session.execute(db.select(VehiculeExterne).filter_by(immatriculation_ve=immatriculation_ve)).scalar_one_or_none()
		if existing_vehicule:
			return render_template('add_vehicule_externe.html', 
								sous_traitants=sous_traitants,
								form_error="Un véhicule externe avec cette immatriculation existe déjà.",
								immatriculation_ve=immatriculation_ve, categorie=categorie, description=description, id_sous_traitant=id_sous_traitant)

		new_vehicule = VehiculeExterne(
			immatriculation_ve=immatriculation_ve,
			categorie=categorie,
			description=description,
			id_sous_traitant=id_sous_traitant
		)
		db.session.add(new_vehicule)
		db.session.commit()
		flash('Véhicule externe ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_vehicules_externes'))
	
	return render_template('add_vehicule_externe.html', sous_traitants=sous_traitants, form_error=None)

@main.route('/vehicules_externes/edit/<int:vehicule_id>', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def edit_vehicule_externe(vehicule_id):
	vehicule_externe = db.session.execute(db.select(VehiculeExterne).filter_by(id_vehicule_externe=vehicule_id)).scalar_one_or_none()
	if vehicule_externe is None:
		flash('Véhicule externe non trouvé.', 'danger')
		return redirect(url_for('main.liste_vehicules_externes'))

	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()

	if request.method == 'POST':
		new_immatriculation = request.form['immatriculation_ve']
		vehicule_externe.categorie = request.form.get('categorie')
		vehicule_externe.description = request.form.get('description')
		vehicule_externe.id_sous_traitant = request.form['id_sous_traitant']

		if not new_immatriculation or not vehicule_externe.id_sous_traitant:
			return render_template('edit_vehicule_externe.html', 
								vehicule_externe=vehicule_externe, 
								sous_traitants=sous_traitants,
								form_error="Immatriculation et sous-traitant sont obligatoires.")

		existing_vehicule_check = db.session.execute(
			db.select(VehiculeExterne).filter(
				VehiculeExterne.immatriculation_ve == new_immatriculation,
				VehiculeExterne.id_vehicule_externe != vehicule_id
			)
		).scalar_one_or_none()
		if existing_vehicule_check:
			return render_template('edit_vehicule_externe.html', 
								vehicule_externe=vehicule_externe, 
								sous_traitants=sous_traitants,
								form_error="Un autre véhicule externe avec cette immatriculation existe déjà.")

		vehicule_externe.immatriculation_ve = new_immatriculation
		db.session.commit()
		flash('Véhicule externe modifié avec succès !', 'success')
		return redirect(url_for('main.liste_vehicules_externes'))
	
	return render_template('edit_vehicule_externe.html', vehicule_externe=vehicule_externe, sous_traitants=sous_traitants, form_error=None)

@main.route('/vehicules_externes/delete/<int:vehicule_id>')
@login_required
@role_required('APPROVISIONNEUR')
def delete_vehicule_externe(vehicule_id):
	vehicule_externe = db.session.execute(db.select(VehiculeExterne).filter_by(id_vehicule_externe=vehicule_id)).scalar_one_or_none()
	if vehicule_externe:
		db.session.delete(vehicule_externe)
		db.session.commit()
		flash('Véhicule externe supprimé avec succès !', 'success')
	else:
		flash('Véhicule externe non trouvé.', 'danger')
	return redirect(url_for('main.liste_vehicules_externes'))

# --- Routes pour la gestion des Chauffeurs Externes ---
@main.route('/chauffeurs_externes')
@login_required
@role_required('APPROVISIONNEUR')
def liste_chauffeurs_externes():
	chauffeurs_externes = db.session.execute(
		db.select(ChauffeurExterne)
		.options(db.joinedload(ChauffeurExterne.sous_traitant))
		.order_by(ChauffeurExterne.nom)
	).scalars().all()
	return render_template('list_chauffeurs_externes.html', chauffeurs_externes=chauffeurs_externes)

@main.route('/chauffeurs_externes/add', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def add_chauffeur_externe():
	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()

	if request.method == 'POST':
		nom = request.form['nom']
		prenom = request.form['prenom']
		numero_telephone = request.form.get('numero_telephone')
		email = request.form.get('email')
		categorie_permis = request.form.get('categorie_permis')
		id_sous_traitant = request.form['id_sous_traitant']

		if not nom or not prenom or not id_sous_traitant:
			return render_template('add_chauffeur_externe.html', 
								sous_traitants=sous_traitants,
								form_error="Nom, prénom et sous-traitant sont obligatoires.",
								nom=nom, prenom=prenom, numero_telephone=numero_telephone, 
								email=email, categorie_permis=categorie_permis, id_sous_traitant=id_sous_traitant)
		
		if email:
			existing_chauffeur = db.session.execute(db.select(ChauffeurExterne).filter_by(email=email)).scalar_one_or_none()
			if existing_chauffeur:
				return render_template('add_chauffeur_externe.html', 
									sous_traitants=sous_traitants,
									form_error="Un chauffeur externe avec cet email existe déjà.",
									nom=nom, prenom=prenom, numero_telephone=numero_telephone, 
									email=email, categorie_permis=categorie_permis, id_sous_traitant=id_sous_traitant)

		new_chauffeur = ChauffeurExterne(
			nom=nom, prenom=prenom,
			numero_telephone=numero_telephone, email=email,
			categorie_permis=categorie_permis,
			id_sous_traitant=id_sous_traitant
		)
		db.session.add(new_chauffeur)
		db.session.commit()
		flash('Chauffeur externe ajouté avec succès !', 'success')
		return redirect(url_for('main.liste_chauffeurs_externes'))
	
	return render_template('add_chauffeur_externe.html', sous_traitants=sous_traitants, form_error=None)

@main.route('/chauffeurs_externes/edit/<int:chauffeur_id>', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def edit_chauffeur_externe(chauffeur_id):
	chauffeur_externe = db.session.execute(db.select(ChauffeurExterne).filter_by(id_chauffeur_externe=chauffeur_id)).scalar_one_or_none()
	if chauffeur_externe is None:
		flash('Chauffeur externe non trouvé.', 'danger')
		return redirect(url_for('main.liste_chauffeurs_externes'))

	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()

	if request.method == 'POST':
		chauffeur_externe.nom = request.form['nom']
		chauffeur_externe.prenom = request.form['prenom']
		chauffeur_externe.numero_telephone = request.form.get('numero_telephone')
		new_email = request.form.get('email')
		chauffeur_externe.categorie_permis = request.form.get('categorie_permis')
		chauffeur_externe.id_sous_traitant = request.form['id_sous_traitant']

		if not chauffeur_externe.nom or not chauffeur_externe.prenom or not chauffeur_externe.id_sous_traitant:
			return render_template('edit_chauffeur_externe.html', 
								chauffeur_externe=chauffeur_externe, 
								sous_traitants=sous_traitants,
								form_error="Nom, prénom et sous-traitant sont obligatoires.")
		
		if new_email:
			existing_chauffeur_check = db.session.execute(
				db.select(ChauffeurExterne).filter(
					ChauffeurExterne.email == new_email,
					ChauffeurExterne.id_chauffeur_externe != chauffeur_id
				)
			).scalar_one_or_none()
			if existing_chauffeur_check:
				return render_template('edit_chauffeur_externe.html', 
									chauffeur_externe=chauffeur_externe, 
									sous_traitants=sous_traitants,
									form_error="Un autre chauffeur externe avec cet email existe déjà.")

		chauffeur_externe.email = new_email
		db.session.commit()
		flash('Chauffeur externe modifié avec succès !', 'success')
		return redirect(url_for('main.liste_chauffeurs_externes'))
	
	return render_template('edit_chauffeur_externe.html', chauffeur_externe=chauffeur_externe, sous_traitants=sous_traitants, form_error=None)

@main.route('/chauffeurs_externes/delete/<int:chauffeur_id>')
@login_required
@role_required('APPROVISIONNEUR')
def delete_chauffeur_externe(chauffeur_id):
	chauffeur_externe = db.session.execute(db.select(ChauffeurExterne).filter_by(id_chauffeur_externe=chauffeur_id)).scalar_one_or_none()
	if chauffeur_externe:
		db.session.delete(chauffeur_externe)
		db.session.commit()
		flash('Chauffeur externe supprimé avec succès !', 'success')
	else:
		flash('Chauffeur externe non trouvé.', 'danger')
	return redirect(url_for('main.liste_chauffeurs_externes'))

# --- Routes pour la gestion des Dates de Validation Chauffeur (DateCV) ---
@main.route('/dates_cv')
@login_required
@role_required('RH')
def liste_dates_cv():
	dates_cv = db.session.execute(
		db.select(DateCV)
		.options(db.joinedload(DateCV.chauffeur))
		.order_by(DateCV.date_fin.desc())
	).scalars().all()
	return render_template('list_dates_cv.html', dates_cv=dates_cv)

@main.route('/dates_cv/add', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def add_date_cv():
	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()

	if request.method == 'POST':
		id_chauffeur = request.form['id_chauffeur']
		date_debut_str = request.form['date_debut']
		date_fin_str = request.form['date_fin']
		description = request.form.get('description')

		try:
			date_debut = date.fromisoformat(date_debut_str)
			date_fin = date.fromisoformat(date_fin_str)
		except ValueError:
			return render_template('add_date_cv.html',
								chauffeurs=chauffeurs,
								form_error="Format de date invalide.")

		if date_fin < date_debut:
			return render_template('add_date_cv.html',
								chauffeurs=chauffeurs,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		new_date_cv = DateCV(
			id_chauffeur=id_chauffeur,
			date_debut=date_debut,
			date_fin=date_fin,
			description=description
		)
		db.session.add(new_date_cv)
		db.session.commit()
		flash('Date de validation chauffeur ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_dates_cv'))
	
	return render_template('add_date_cv.html', chauffeurs=chauffeurs, form_error=None)

@main.route('/dates_cv/edit/<int:date_id>', methods=['GET', 'POST'])
@login_required
@role_required('RH')
def edit_date_cv(date_id):
	date_cv = db.session.execute(db.select(DateCV).filter_by(id_date_cv=date_id)).scalar_one_or_none()
	if date_cv is None:
		flash("Date de validation chauffeur non trouvée.", 'danger')
		return redirect(url_for('main.liste_dates_cv'))

	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()

	if request.method == 'POST':
		date_cv.id_chauffeur = request.form['id_chauffeur']
		new_date_debut_str = request.form['date_debut']
		new_date_fin_str = request.form['date_fin']
		date_cv.description = request.form.get('description')

		try:
			date_cv.date_debut = date.fromisoformat(new_date_debut_str)
			date_cv.date_fin = date.fromisoformat(new_date_fin_str)
		except ValueError:
			return render_template('edit_date_cv.html',
								date_cv=date_cv, chauffeurs=chauffeurs,
								form_error="Format de date invalide.")

		if date_cv.date_fin < date_cv.date_debut:
			return render_template('edit_date_cv.html',
								date_cv=date_cv, chauffeurs=chauffeurs,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		db.session.commit()
		flash('Date de validation chauffeur modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_dates_cv') )
	
	return render_template('edit_date_cv.html', date_cv=date_cv, chauffeurs=chauffeurs, form_error=None)

@main.route('/dates_cv/delete/<int:date_id>')
@login_required
@role_required('RH')
def delete_date_cv(date_id):
	date_cv = db.session.execute(db.select(DateCV).filter_by(id_date_cv=date_id)).scalar_one_or_none()
	if date_cv:
		db.session.delete(date_cv)
		db.session.commit()
		flash('Date de validation chauffeur supprimée avec succès !', 'success')
	else:
		flash('Date de validation chauffeur non trouvée.', 'danger')
	return redirect(url_for('main.liste_dates_cv'))


# --- Routes pour la gestion des Dates Tracteur/Remorque (DateTR) ---
@main.route('/dates_tr')
@login_required
@role_required('CHARGE_MAINTENANCE')
def liste_dates_tr():
	dates_tr = db.session.execute(
		db.select(DateTR)
		.options(db.joinedload(DateTR.vehicule))
		.order_by(DateTR.date_fin.desc())
	).scalars().all()
	return render_template('list_dates_tr.html', dates_tr=dates_tr)

@main.route('/dates_tr/add', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_MAINTENANCE')
def add_date_tr():
	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()

	if request.method == 'POST':
		id_vehicule = request.form['id_vehicule']
		date_debut_str = request.form['date_debut']
		date_fin_str = request.form['date_fin']
		description = request.form.get('description')

		try:
			date_debut = date.fromisoformat(date_debut_str)
			date_fin = date.fromisoformat(date_fin_str)
		except ValueError:
			return render_template('add_date_tr.html',
								vehicules=vehicules,
								form_error="Format de date invalide.")

		if date_fin < date_debut:
			return render_template('add_date_tr.html',
								vehicules=vehicules,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		new_date_tr = DateTR(
			id_vehicule=id_vehicule,
			date_debut=date_debut,
			date_fin=date_fin,
			description=description
		)
		db.session.add(new_date_tr)
		db.session.commit()
		flash('Date de validité véhicule ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_dates_tr'))
	
	return render_template('add_date_tr.html', vehicules=vehicules, form_error=None)

@main.route('/dates_tr/edit/<int:date_id>', methods=['GET', 'POST'])
@login_required
@role_required('CHARGE_MAINTENANCE')
def edit_date_tr(date_id):
	date_tr = db.session.execute(db.select(DateTR).filter_by(id_date_tr=date_id)).scalar_one_or_none()
	if date_tr is None:
		flash("Date de validité véhicule non trouvée.", 'danger')
		return redirect(url_for('main.liste_dates_tr'))

	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()

	if request.method == 'POST':
		date_tr.id_vehicule = request.form['id_vehicule']
		new_date_debut_str = request.form['date_debut']
		new_date_fin_str = request.form['date_fin']
		date_tr.description = request.form.get('description')

		try:
			date_tr.date_debut = date.fromisoformat(new_date_debut_str)
			date_tr.date_fin = date.fromisoformat(new_date_fin_str)
		except ValueError:
			return render_template('edit_date_tr.html',
								date_tr=date_tr, vehicules=vehicules,
								form_error="Format de date invalide.")

		if date_tr.date_fin < date_tr.date_debut:
			return render_template('edit_date_tr.html',
								date_tr=date_tr, vehicules=vehicules,
								form_error="La date de fin doit être postérieure ou égale à la date de début.")

		db.session.commit()
		flash('Date de validité véhicule modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_dates_tr'))
	
	return render_template('edit_date_tr.html', date_tr=date_tr, vehicules=vehicules, form_error=None)

@main.route('/dates_tr/delete/<int:date_id>')
@login_required
@role_required('CHARGE_MAINTENANCE')
def delete_date_tr(date_id):
	date_tr = db.session.execute(db.select(DateTR).filter_by(id_date_tr=date_id)).scalar_one_or_none()
	if date_tr:
		db.session.delete(date_tr)
		db.session.commit()
		flash('Date de validité véhicule supprimée avec succès !', 'success')
	else:
		flash('Date de validité véhicule non trouvée.', 'danger')
	return redirect(url_for('main.liste_dates_tr'))

@main.route('/affretements')
@login_required
@role_required('APPROVISIONNEUR')
def liste_affretements():
	affretements = db.session.execute(
		db.select(Affretement)
		.options(db.joinedload(Affretement.detail_commande))
		.options(db.joinedload(Affretement.sous_traitant))
		.options(db.joinedload(Affretement.vehicule_externe))
		.options(db.joinedload(Affretement.chauffeur_externe))
		.order_by(Affretement.date_demande.desc())
	).scalars().all()
	return render_template('list_affretements.html', affretements=affretements)

@main.route('/affretements/add', methods=['GET', 'POST'])
@login_required
@role_required('PLANIFIER')
def add_affretement():
	details_commandes = db.session.execute(db.select(DetailCommande)
										.options(db.joinedload(DetailCommande.entete_commande))
										.order_by(DetailCommande.id_detail_commande)).scalars().all()
	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()
	vehicules_externes = db.session.execute(db.select(VehiculeExterne).order_by(VehiculeExterne.immatriculation_ve)).scalars().all()
	chauffeurs_externes = db.session.execute(db.select(ChauffeurExterne).order_by(ChauffeurExterne.nom)).scalars().all()

	if request.method == 'POST':
		date_demande = date.today()
		date_debut_souhaitee_str = request.form['date_debut_souhaitee']
		date_fin_souhaitee_str = request.form['date_fin_souhaitee']
		description_besoin = request.form['description_besoin']
		statut = request.form.get('statut', 'En attente')
		cout_estime = request.form.get('cout_estime')
		id_detail_commande = request.form.get('id_detail_commande')
		id_sous_traitant = request.form.get('id_sous_traitant')
		id_vehicule_externe = request.form.get('id_vehicule_externe')
		id_chauffeur_externe = request.form.get('id_chauffeur_externe')

		try:
			date_debut_souhaitee = date.fromisoformat(date_debut_souhaitee_str)
			date_fin_souhaitee = date.fromisoformat(date_fin_souhaitee_str)
			cout_estime = float(cout_estime) if cout_estime else None
		except ValueError:
			return render_template('add_affretement.html',
								details_commandes=details_commandes, sous_traitants=sous_traitants,
								vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
								form_error="Format de date ou de coût invalide.")

		if not description_besoin or not date_debut_souhaitee or not date_fin_souhaitee:
			return render_template('add_affretement.html',
								details_commandes=details_commandes, sous_traitants=sous_traitants,
								vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
								form_error="La description du besoin, la date de début et la date de fin souhaitées sont obligatoires.")
		
		if date_fin_souhaitee < date_debut_souhaitee:
			return render_template('add_affretement.html',
								details_commandes=details_commandes, sous_traitants=sous_traitants,
								vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
								form_error="La date de fin souhaitée doit être postérieure ou égale à la date de début souhaitée.")


		new_affretement = Affretement(
			date_demande=date_demande,
			date_debut_souhaitee=date_debut_souhaitee,
			date_fin_souhaitee=date_fin_souhaitee,
			description_besoin=description_besoin,
			statut=statut,
			cout_estime=cout_estime,
			id_detail_commande=id_detail_commande if id_detail_commande else None,
			id_sous_traitant=id_sous_traitant if id_sous_traitant else None,
			id_vehicule_externe=id_vehicule_externe if id_vehicule_externe else None,
			id_chauffeur_externe=id_chauffeur_externe if id_chauffeur_externe else None
		)
		db.session.add(new_affretement)
		db.session.commit()
		flash('Demande d\'affrètement ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_affretements'))
	
	return render_template('add_affretement.html',
						details_commandes=details_commandes, sous_traitants=sous_traitants,
						vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
						form_error=None)

@main.route('/affretements/edit/<int:affretement_id>', methods=['GET', 'POST'])
@login_required
@role_required('APPROVISIONNEUR')
def edit_affretement(affretement_id):
	affretement = db.session.execute(db.select(Affretement).filter_by(id_affretement=affretement_id)).scalar_one_or_none()
	if affretement is None:
		flash('Demande d\'affrètement non trouvée.', 'danger')
		return redirect(url_for('main.liste_affretements'))

	details_commandes = db.session.execute(db.select(DetailCommande)
										.options(db.joinedload(DetailCommande.entete_commande))
										.order_by(DetailCommande.id_detail_commande)).scalars().all()
	sous_traitants = db.session.execute(db.select(SousTraitant).order_by(SousTraitant.nom_entreprise)).scalars().all()
	vehicules_externes = db.session.execute(db.select(VehiculeExterne).order_by(VehiculeExterne.immatriculation_ve)).scalars().all()
	chauffeurs_externes = db.session.execute(db.select(ChauffeurExterne).order_by(ChauffeurExterne.nom)).scalars().all()

	statuts_affretement = ['En attente', 'Confirmé', 'Annulé', 'En cours', 'Terminé']

	if request.method == 'POST':
		new_date_debut_souhaitee_str = request.form['date_debut_souhaitee']
		new_date_fin_souhaitee_str = request.form['date_fin_souhaitee']
		affretement.description_besoin = request.form['description_besoin']
		affretement.statut = request.form['statut']
		new_cout_estime = request.form.get('cout_estime')
		affretement.id_detail_commande = request.form.get('id_detail_commande') if request.form.get('id_detail_commande') else None
		affretement.id_sous_traitant = request.form.get('id_sous_traitant') if request.form.get('id_sous_traitant') else None
		affretement.id_vehicule_externe = request.form.get('id_vehicule_externe') if request.form.get('id_vehicule_externe') else None
		affretement.id_chauffeur_externe = request.form.get('id_chauffeur_externe') if request.form.get('id_chauffeur_externe') else None

		try:
			affretement.date_debut_souhaitee = date.fromisoformat(new_date_debut_souhaitee_str)
			affretement.date_fin_souhaitee = date.fromisoformat(new_date_fin_souhaitee_str)
			affretement.cout_estime = float(new_cout_estime) if new_cout_estime else None
		except ValueError:
			return render_template('edit_affretement.html',
								affretement=affretement, details_commandes=details_commandes, sous_traitants=sous_traitants,
								vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
								statuts_affretement=statuts_affretement,
								form_error="Format de date ou de coût invalide.")
		
		if not affretement.description_besoin or not affretement.date_debut_souhaitee or not affretement.date_fin_souhaitee:
			return render_template('edit_affretement.html',
								affretement=affretement, details_commandes=details_commandes, sous_traitants=sous_traitants,
								vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
								statuts_affretement=statuts_affretement,
								form_error="La description du besoin, la date de début et la date de fin souhaitées sont obligatoires.")
		
		if affretement.date_fin_souhaitee < affretement.date_debut_souhaitee:
			return render_template('edit_affretement.html',
								affretement=affretement, details_commandes=details_commandes, sous_traitants=sous_traitants,
								vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
								statuts_affretement=statuts_affretement,
								form_error="La date de fin souhaitée doit être postérieure ou égale à la date de début souhaitée.")


		db.session.commit()
		flash('Demande d\'affrètement modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_affretements'))
	
	return render_template('edit_affretement.html',
						affretement=affretement, details_commandes=details_commandes, sous_traitants=sous_traitants,
						vehicules_externes=vehicules_externes, chauffeurs_externes=chauffeurs_externes,
						statuts_affretement=statuts_affretement,
						form_error=None)

@main.route('/affretements/delete/<int:affretement_id>')
@login_required
@role_required('APPROVISIONNEUR')
def delete_affretement(affretement_id):
	affretement = db.session.execute(db.select(Affretement).filter_by(id_affretement=affretement_id)).scalar_one_or_none()
	if affretement:
		db.session.delete(affretement)
		db.session.commit()
		flash('Demande d\'affrètement supprimée avec succès !', 'success')
	else:
		flash('Demande d\'affrètement non trouvée.', 'danger')
	return redirect(url_for('main.liste_affretements'))

@main.route('/feuilles_de_route')
@login_required
@role_required('PLANIFIER')
def liste_feuilles_de_route():
	feuilles_de_route = db.session.execute(
		db.select(FeuilleDeRoute)
		.options(joinedload(FeuilleDeRoute.chauffeur))
		.options(joinedload(FeuilleDeRoute.vehicule))
		.options(selectinload(FeuilleDeRoute.missions_affectees))
		.order_by(FeuilleDeRoute.date_depart_prevu.desc())
	).scalars().all()
	return render_template('list_feuilles_de_route.html', feuilles_de_route=feuilles_de_route)


@main.route('/feuilles_de_route/add', methods=['GET', 'POST'])
@login_required
@role_required('PLANIFIER')
def add_feuille_de_route():
	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()

	if request.method == 'POST':
		description = request.form.get('description')
		id_chauffeur = request.form['id_chauffeur']
		id_vehicule = request.form['id_vehicule']

		date_depart_prevu_str = request.form['date_depart_prevu']
		heure_depart_prevu_str = request.form['heure_depart_prevu']
		date_arrivee_prevue_str = request.form['date_arrivee_prevue']
		heure_arrivee_prevue_str = request.form['heure_arrivee_prevue']

		date_depart_reel_str = request.form.get('date_depart_reel')
		heure_depart_reel_str = request.form.get('heure_depart_reel')
		date_arrivee_reelle_str = request.form.get('date_arrivee_reelle')
		heure_arrivee_reelle_str = request.form.get('heure_arrivee_reelle')
		km_debut_str = request.form.get('km_debut')
		km_fin_str = request.form.get('km_fin')

		try:
			date_depart_prevu = date.fromisoformat(date_depart_prevu_str)
			heure_depart_prevu = time.fromisoformat(heure_depart_prevu_str)
			date_arrivee_prevue = date.fromisoformat(date_arrivee_prevue_str)
			heure_arrivee_prevue = time.fromisoformat(heure_arrivee_prevue_str)

			date_depart_reel = date.fromisoformat(date_depart_reel_str) if date_depart_reel_str else None
			heure_depart_reel = time.fromisoformat(heure_depart_reel_str) if heure_depart_reel_str else None
			date_arrivee_reelle = date.fromisoformat(date_arrivee_reelle_str) if date_arrivee_reelle_str else None
			heure_arrivee_reelle = time.fromisoformat(heure_arrivee_reelle_str) if heure_arrivee_reelle_str else None
			km_debut = float(km_debut_str) if km_debut_str else None
			km_fin = float(km_fin_str) if km_fin_str else None
		except ValueError:
			return render_template('add_feuille_de_route.html',
								chauffeurs=chauffeurs, vehicules=vehicules,
								form_error="Format de date, d'heure ou de kilométrage invalide.",
								description=description, id_chauffeur=id_chauffeur, id_vehicule=id_vehicule,
								date_depart_prevu=date_depart_prevu_str, heure_depart_prevu=heure_depart_prevu_str,
								date_arrivee_prevue=date_arrivee_prevue_str, heure_arrivee_prevue=heure_arrivee_prevue_str,
								date_depart_reel=date_depart_reel_str, heure_depart_reel=heure_depart_reel_str,
								date_arrivee_reelle=date_arrivee_reelle_str, heure_arrivee_reelle=heure_arrivee_reelle_str,
								km_debut=km_debut_str, km_fin=km_fin_str)

		if date_arrivee_prevue < date_depart_prevu or (date_arrivee_prevue == date_depart_prevu and heure_arrivee_prevue < heure_depart_prevu):
			return render_template('add_feuille_de_route.html',
								chauffeurs=chauffeurs, vehicules=vehicules,
								form_error="La date/heure d'arrivée prévue doit être postérieure à la date/heure de départ prévue.",
								description=description, id_chauffeur=id_chauffeur, id_vehicule=id_vehicule,
								date_depart_prevu=date_depart_prevu_str, heure_depart_prevu=heure_depart_prevu_str,
								date_arrivee_prevue=date_arrivee_prevue_str, heure_arrivee_prevue=heure_arrivee_prevue_str,
								date_depart_reel=date_depart_reel_str, heure_depart_reel=heure_depart_reel_str,
								date_arrivee_reelle=date_arrivee_reelle_str, heure_arrivee_reelle=heure_arrivee_reelle_str,
								km_debut=km_debut_str, km_fin=km_fin_str)

		if km_debut is not None and km_fin is not None and km_fin < km_debut:
			return render_template('add_feuille_de_route.html',
								chauffeurs=chauffeurs, vehicules=vehicules,
								form_error="Le kilométrage de fin ne peut pas être inférieur au kilométrage de début.",
								description=description, id_chauffeur=id_chauffeur, id_vehicule=id_vehicule,
								date_depart_prevu=date_depart_prevu_str, heure_depart_prevu=heure_depart_prevu_str,
								date_arrivee_prevue=date_arrivee_prevue_str, heure_arrivee_prevue=heure_arrivee_prevue_str,
								date_depart_reel=date_depart_reel_str, heure_depart_reel=heure_depart_reel_str,
								date_arrivee_reelle=date_arrivee_reelle_str, heure_arrivee_reelle=heure_arrivee_reelle_str,
								km_debut=km_debut_str, km_fin=km_fin_str)


		new_fdr = FeuilleDeRoute(
			description=description,
			date_depart_prevu=date_depart_prevu,
			heure_depart_prevu=heure_depart_prevu,
			date_arrivee_prevue=date_arrivee_prevue,
			heure_arrivee_prevue=heure_arrivee_prevue,
			date_depart_reel=date_depart_reel,
			heure_depart_reel=heure_depart_reel,
			date_arrivee_reelle=date_arrivee_reelle,
			heure_arrivee_reelle=heure_arrivee_reelle,
			km_debut=km_debut,
			km_fin=km_fin,
			id_chauffeur=id_chauffeur,
			id_vehicule=id_vehicule
		)
		db.session.add(new_fdr)
		db.session.commit()
		flash('Feuille de route ajoutée avec succès !', 'success')
		return redirect(url_for('main.liste_feuilles_de_route'))
	
	return render_template('add_feuille_de_route.html',
						chauffeurs=chauffeurs, vehicules=vehicules, form_error=None)

@main.route('/feuilles_de_route/edit/<int:fdr_id>', methods=['GET', 'POST'])
@login_required
@role_required('PLANIFIER')
def edit_feuille_de_route(fdr_id):
	fdr = db.session.execute(db.select(FeuilleDeRoute).filter_by(id_feuille_de_route=fdr_id)).scalar_one_or_none()
	if fdr is None:
		flash('Feuille de route non trouvée.', 'danger')
		return redirect(url_for('main.liste_feuilles_de_route'))

	chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
	vehicules = db.session.execute(db.select(Vehicule).order_by(Vehicule.immatriculation_ve)).scalars().all()

	if request.method == 'POST':
		fdr.description = request.form.get('description')
		fdr.id_chauffeur = request.form['id_chauffeur']
		fdr.id_vehicule = request.form['id_vehicule']

		date_depart_prevu_str = request.form['date_depart_prevu']
		heure_depart_prevu_str = request.form['heure_depart_prevu']
		date_arrivee_prevue_str = request.form['date_arrivee_prevue']
		heure_arrivee_prevue_str = request.form['heure_arrivee_prevue']

		date_depart_reel_str = request.form.get('date_depart_reel')
		heure_depart_reel_str = request.form.get('heure_depart_reel')
		date_arrivee_reelle_str = request.form.get('date_arrivee_reelle')
		heure_arrivee_reelle_str = request.form.get('heure_arrivee_reelle')
		km_debut_str = request.form.get('km_debut')
		km_fin_str = request.form.get('km_fin')

		try:
			fdr.date_depart_prevu = date.fromisoformat(date_depart_prevu_str)
			fdr.heure_depart_prevu = time.fromisoformat(heure_depart_prevu_str)
			fdr.date_arrivee_prevue = date.fromisoformat(date_arrivee_prevue_str)
			fdr.heure_arrivee_prevue = time.fromisoformat(heure_arrivee_prevue_str)

			fdr.date_depart_reel = date.fromisoformat(date_depart_reel_str) if date_depart_reel_str else None
			fdr.heure_depart_reel = time.fromisoformat(heure_depart_reel_str) if heure_depart_reel_str else None
			fdr.date_arrivee_reelle = date.fromisoformat(date_arrivee_reelle_str) if date_arrivee_reelle_str else None
			fdr.heure_arrivee_reelle = time.fromisoformat(heure_arrivee_reelle_str) if heure_arrivee_reelle_str else None
			km_debut = float(km_debut_str) if km_debut_str else None
			km_fin = float(km_fin_str) if km_fin_str else None
		except ValueError:
			return render_template('edit_feuille_de_route.html',
								fdr=fdr, chauffeurs=chauffeurs, vehicules=vehicules,
								form_error="Format de date, d'heure ou de kilométrage invalide.")

		if fdr.date_arrivee_prevue < fdr.date_depart_prevu or (fdr.date_arrivee_prevue == fdr.date_depart_prevu and fdr.heure_arrivee_prevue < fdr.heure_depart_prevu):
			return render_template('edit_feuille_de_route.html',
								fdr=fdr, chauffeurs=chauffeurs, vehicules=vehicules,
								form_error="La date/heure d'arrivée prévue doit être postérieure à la date/heure de départ prévue.")

		if fdr.km_debut is not None and fdr.km_fin is not None and fdr.km_fin < fdr.km_debut:
			return render_template('edit_feuille_de_route.html',
								fdr=fdr, chauffeurs=chauffeurs, vehicules=vehicules,
								form_error="Le kilométrage de fin ne peut pas être inférieur au kilométrage de début.")
		
		db.session.commit()
		flash('Feuille de route modifiée avec succès !', 'success')
		return redirect(url_for('main.liste_feuilles_de_route'))
	
	return render_template('edit_feuille_de_route.html',
						fdr=fdr, chauffeurs=chauffeurs, vehicules=vehicules, form_error=None)

@main.route('/feuilles_de_route/delete/<int:fdr_id>')
@login_required
@role_required('PLANIFIER')
def delete_feuille_de_route(fdr_id):
	fdr = db.session.execute(db.select(FeuilleDeRoute).filter_by(id_feuille_de_route=fdr_id)).scalar_one_or_none()
	if fdr:
		db.session.delete(fdr)
		db.session.commit()
		flash('Feuille de route supprimée avec succès !', 'success')
	else:
		flash('Feuille de route non trouvée.', 'danger')
	return redirect(url_for('main.liste_feuilles_de_route'))

@main.route('/commandes_non_planifiees')
@login_required
@role_required('PLANIFIER')
def liste_commandes_non_planifiees():
	unassigned_details = db.session.execute(
		db.select(DetailCommande)
		.filter(db.not_(DetailCommande.missions.any()))
		.options(joinedload(DetailCommande.entete_commande).joinedload(EnteteCommande.client_initial))
		.options(joinedload(DetailCommande.destination))
		.order_by(DetailCommande.id_detail_commande)
	).scalars().all()
	
	return render_template('list_commandes_non_planifiees.html', unassigned_details=unassigned_details)

@main.route('/missions_pour_affectation/<int:detail_id>')
@login_required
@role_required('PLANIFIER')
def liste_missions_pour_affectation(detail_id):
	detail_to_assign = db.session.execute(
		db.select(DetailCommande)
		.filter_by(id_detail_commande=detail_id)
		.options(joinedload(DetailCommande.entete_commande))
		.options(joinedload(DetailCommande.destination))
	).scalar_one_or_none()

	if not detail_to_assign:
		flash("Détail de commande non trouvé.", 'danger')
		return redirect(url_for('main.liste_commandes_non_planifiees'))
	
	if detail_to_assign.missions:
		flash(f"Le détail de commande '{detail_to_assign.entete_commande.reference if detail_to_assign.entete_commande else 'N/A'} (ID: {detail_id})' est déjà associé à une mission et ne peut pas être affecté à nouveau. Veuillez le retirer de la mission existante d'abord.", 'danger')
		return redirect(url_for('main.liste_commandes_non_planifiees'))

	missions = db.session.execute(
		db.select(Mission)
		.options(joinedload(Mission.chauffeur))
		.options(joinedload(Mission.vehicule))
		.options(joinedload(Mission.feuille_de_route))
		.order_by(Mission.date_debut.desc())
	).scalars().all()

	return render_template('liste_missions_pour_affectation.html', 
						detail_to_assign=detail_to_assign, 
						missions=missions)

@main.route('/gantt_missions')
@login_required
@role_required('PLANIFIER')
def gantt_missions():
	missions = db.session.execute(
		db.select(Mission)
		.options(joinedload(Mission.chauffeur))
		.options(joinedload(Mission.vehicule))
		.options(joinedload(Mission.feuille_de_route))
		.options(selectinload(Mission.details_commandes)
					.joinedload(DetailCommande.entete_commande))
		.options(selectinload(Mission.details_commandes)
					.joinedload(DetailCommande.destination))
		.order_by(Mission.date_debut)
	).scalars().all()

	gantt_tasks_data = []
	for mission in missions:
		chauffeur_nom = f"{mission.chauffeur.nom} {mission.chauffeur.prenom}" if mission.chauffeur else "N/A"
		vehicule_immat = mission.vehicule.immatriculation_ve if mission.vehicule else "N/A"

		description_courte = f"M{mission.id_mission}: {chauffeur_nom} - {vehicule_immat} ({mission.statut})" # Inclure statut
		
		if mission.feuille_de_route and mission.feuille_de_route.description:
			description_courte += f" (FDR: {mission.feuille_de_route.description})"
		elif mission.destination and mission.destination.description:
			description_courte += f" (Dest: {mission.destination.description})"

		description_longue = (
			f"<b>Mission ID:</b> {mission.id_mission}<br>"
			f"<b>Statut:</b> {mission.statut}<br>" # Inclure statut dans long
			f"<b>Chauffeur:</b> {chauffeur_nom}<br>"
			f"<b>Véhicule:</b> {vehicule_immat}<br>"
			f"<b>Début:</b> {mission.date_debut.strftime('%d/%m/%Y')} {mission.heure_debut.strftime('%H:%M')}<br>"
			f"<b>Fin:</b> {mission.date_fin.strftime('%d/%m/%Y')} {mission.heure_fin.strftime('%H:%M')}<br>"
		)
		if mission.feuille_de_route:
			description_longue += f"<b>Feuille de Route:</b> {mission.feuille_de_route.description or f'ID: {mission.feuille_de_route.id_feuille_de_route}'}<br>"
		if mission.destination:
			description_longue += f"<b>Destination Principale:</b> {mission.destination.description or 'N/A'}<br>"
		
		if mission.details_commandes:
			description_longue += "<b>Détails Commandes:</b><ul>"
			for detail in mission.details_commandes:
				entete_ref = detail.entete_commande.reference if detail.entete_commande else 'N/A'
				dest_desc = detail.destination.description if detail.destination else 'N/A'
				description_longue += (
					f"<li>Réf: {entete_ref} "
					f"(Qty: {detail.quantite}) "
					f"Dest: {dest_desc}</li>"
				)
			description_longue += "</ul>"


		gantt_tasks_data.append({
			'id': f'mission-{mission.id_mission}',
			'name': description_courte,
			'start': mission.date_debut.isoformat(),
			'end': mission.date_fin.isoformat(),
			'progress': 0,
			'dependencies': '',
			'start_date': mission.date_debut.isoformat(),
			'end_date': mission.date_fin.isoformat(),
			'description_courte': description_courte,
			'description_longue': description_longue
		})
	
	return render_template('gantt_missions.html', gantt_data=gantt_tasks_data)

@main.app_context_processor
def inject_global_vars():
	return dict(
		ROLES=ROLES,
		current_year=datetime.utcnow().year
	)

@main.route('/client/dashboard')
@login_required
@role_required('CLIENT')
def client_dashboard():
	if not current_user.id_client_initial:
		flash("Votre compte utilisateur n'est pas encore associé à un profil client. Veuillez contacter l'administration.", "warning")
		return render_template('client_dashboard.html', client_data=None, stats={})

	client_initial = db.session.get(ClientInitial, current_user.id_client_initial)
	if not client_initial:
		flash("Profil client introuvable. Veuillez contacter l'administration.", "danger")
		return render_template('client_dashboard.html', client_data=None, stats={})

	client_stats = {}
	nombre_commandes = db.session.scalar(
		db.select(db.func.count(EnteteCommande.id_entete_commande))
		.filter_by(id_client_initial=client_initial.id_client_initial)
	)
	client_stats['total_commandes'] = nombre_commandes
	
	return render_template('client_dashboard.html', client_data=client_initial, stats=client_stats)


@main.route('/client/commandes')
@login_required
@role_required('CLIENT')
def client_commandes_list():
	if not current_user.id_client_initial:
		flash("Votre compte utilisateur n'est pas encore associé à un profil client pour voir les commandes.", "warning")
		return redirect(url_for('main.client_dashboard'))

	client_initial = db.session.get(ClientInitial, current_user.id_client_initial)
	if not client_initial:
		flash("Profil client introuvable.", "danger")
		return redirect(url_for('main.client_dashboard'))

	commandes = db.session.execute(
		db.select(EnteteCommande)
		.filter_by(id_client_initial=client_initial.id_client_initial)
		.options(joinedload(EnteteCommande.service_client))
		.options(selectinload(EnteteCommande.details_commandes_rel)
					.joinedload(DetailCommande.destination)) 
		.order_by(EnteteCommande.date_commande.desc())
	).scalars().all()

	return render_template('client_commandes_list.html', commandes=commandes, client_data=client_initial)


@main.route('/client/commande/<int:entete_id>/details')
@login_required
@role_required('CLIENT')
def client_commande_details(entete_id):
	if not current_user.id_client_initial:
		flash("Accès non autorisé.", "warning")
		return redirect(url_for('main.client_dashboard'))

	entete = db.session.execute(
		db.select(EnteteCommande)
		.filter_by(id_entete_commande=entete_id, id_client_initial=current_user.id_client_initial)
		.options(joinedload(EnteteCommande.client_initial))
		.options(joinedload(EnteteCommande.service_client))
	).scalar_one_or_none()

	if entete is None:
		flash("Commande non trouvée ou non autorisée.", 'danger')
		return redirect(url_for('main.client_commandes_list'))
	
	details = db.session.execute(
		db.select(DetailCommande)
		.filter_by(id_entete_commande=entete_id)
		.options(joinedload(DetailCommande.type_vehicule))
		.options(joinedload(DetailCommande.client_final))
		.options(joinedload(DetailCommande.destination))
		.order_by(DetailCommande.id_detail_commande)
	).scalars().all()
	
	return render_template('client_commande_detail_view.html', entete=entete, details=details)


@main.route('/chauffeur/interface')
@login_required
@role_required('CHAUFFEUR')
def chauffeur_interface():
	# Vérification si l'utilisateur est bien lié à un chauffeur
	if not current_user.id_chauffeur:
		flash("Votre compte utilisateur n'est pas associé à un profil chauffeur.", "danger")
		return redirect(url_for('main.index')) 

	chauffeur = db.session.get(Chauffeur, current_user.id_chauffeur)
	if not chauffeur:
		flash("Profil chauffeur introuvable ou non associé à votre compte.", "danger")
		return redirect(url_for('main.index'))

	# Récupérer les missions du chauffeur connecté, chargées avec leurs détails
	chauffeur_missions = db.session.execute(
		db.select(Mission)
		.filter_by(id_chauffeur=chauffeur.id_chauffeur)
		.options(joinedload(Mission.vehicule))
		.options(joinedload(Mission.feuille_de_route))
		.options(joinedload(Mission.destination))
		.options(selectinload(Mission.details_commandes)
					.joinedload(DetailCommande.entete_commande)
					.joinedload(EnteteCommande.client_initial))
		.options(selectinload(Mission.details_commandes)
					.joinedload(DetailCommande.destination))
		.options(selectinload(Mission.details_commandes)
					.joinedload(DetailCommande.type_vehicule))
		.order_by(Mission.date_debut.desc())
	).scalars().all()

	# --- AJOUT IMPORTANT POUR LE DÉBOGAGE ---
	print(f"DEBUG: Chauffeur {chauffeur.nom_complet} (ID: {chauffeur.id_chauffeur})")
	print(f"DEBUG: Nombre de missions trouvées pour ce chauffeur: {len(chauffeur_missions)}")
	for mission in chauffeur_missions:
		print(f"  - Mission ID: {mission.id_mission}, Statut: {mission.statut}, Détails: {len(mission.details_commandes)}")
	# --- FIN DU DÉBOGAGE ---

	return render_template('chauffeur_interface.html', 
							chauffeur=chauffeur,
							chauffeur_missions=chauffeur_missions)

# app/routes/main_routes.py (Ajoutez cette route)

@main.route('/chauffeur_history_map')
@login_required
@role_required('PLANIFIER') # Généralement un planificateur ou admin verra l'historique
def chauffeur_history_map():
    chauffeurs = db.session.execute(db.select(Chauffeur).order_by(Chauffeur.nom)).scalars().all()
    return render_template('chauffeur_history_map.html', chauffeurs=chauffeurs)

# app/routes/main_routes.py (Ajoutez cette route)

@main.route('/missions/<int:mission_id>/report')
@login_required
@role_required('PLANIFIER') # Seuls les planificateurs et admins peuvent générer des rapports de mission
def mission_report(mission_id):
    # Charger la mission et toutes ses relations pour le rapport
    mission = db.session.execute(
        db.select(Mission)
        .filter_by(id_mission=mission_id)
        .options(joinedload(Mission.chauffeur))
        .options(joinedload(Mission.vehicule))
        .options(joinedload(Mission.destination)) # Destination principale de la mission
        .options(joinedload(Mission.feuille_de_route))
        .options(selectinload(Mission.details_commandes) # Charge les détails de commande liés
                 .joinedload(DetailCommande.entete_commande) # Charge l'entête de commande pour chaque détail
                 .joinedload(EnteteCommande.client_initial)) # Charge le client initial pour chaque entête
        .options(selectinload(Mission.details_commandes)
                 .joinedload(DetailCommande.client_final)) # Charge le client final pour chaque détail
        .options(selectinload(Mission.details_commandes)
                 .joinedload(DetailCommande.destination)) # Charge la destination pour chaque détail
        .options(selectinload(Mission.details_commandes)
                 .joinedload(DetailCommande.type_vehicule)) # Charge le type de véhicule pour chaque détail
    ).scalar_one_or_none()

    if mission is None:
        flash('Mission non trouvée pour le rapport.', 'danger')
        return redirect(url_for('main.liste_missions'))
    
    return render_template('mission_report.html', mission=mission)

# app/routes/main_routes.py (Ajoutez cette route)

@main.route('/feuilles_de_route/<int:fdr_id>/report')
@login_required
@role_required('PLANIFIER') # Seuls les planificateurs et admins peuvent générer des rapports de FDR
def feuille_de_route_report(fdr_id):
    # Charger la feuille de route et toutes ses relations pour le rapport
    fdr = db.session.execute(
        db.select(FeuilleDeRoute)
        .filter_by(id_feuille_de_route=fdr_id)
        .options(joinedload(FeuilleDeRoute.chauffeur))
        .options(joinedload(FeuilleDeRoute.vehicule))
        .options(selectinload(FeuilleDeRoute.missions_affectees) # Charge les missions liées
                 .joinedload(Mission.destination)) # Charge la destination principale de chaque mission
        .options(selectinload(FeuilleDeRoute.missions_affectees)
                 .selectinload(Mission.details_commandes) # Charge les détails de commande de chaque mission
                 .joinedload(DetailCommande.entete_commande)) # Et leur entête
        .options(selectinload(FeuilleDeRoute.missions_affectees)
                 .selectinload(Mission.details_commandes)
                 .joinedload(DetailCommande.destination)) # Et leur destination
    ).scalar_one_or_none()

    if fdr is None:
        flash('Feuille de route non trouvée pour le rapport.', 'danger')
        return redirect(url_for('main.liste_feuilles_de_route'))
    
    return render_template('feuille_de_route_report.html', fdr=fdr)

# app/routes/main_routes.py (Ajoutez cette nouvelle fonction utilitaire)


# app/routes/main_routes.py (Ajoutez cette nouvelle fonction utilitaire)

def check_vehicle_capacity(vehicule_id, mission_id=None):
    """
    Vérifie si le volume et le poids total des détails de commande associés à une mission
    ne dépassent pas la capacité du véhicule sélectionné.
    """
    vehicule = db.session.get(Vehicule, vehicule_id)
    if not vehicule:
        return "Véhicule non trouvé pour la vérification de capacité."

    # Définir les capacités max basées sur la catégorie du véhicule (hypothèse pour l'exemple)
    max_poids_kg = 1000.0  # Default
    max_volume_m3 = 10.0  # Default

    if vehicule.categorie == 'Camion':
        max_poids_kg = 5000.0
        max_volume_m3 = 30.0
    elif vehicule.categorie == 'Utilitaire':
        max_poids_kg = 1000.0
        max_volume_m3 = 10.0
    elif vehicule.categorie == 'Semi-remorque':
        max_poids_kg = 25000.0
        max_volume_m3 = 80.0
    # Ajoutez d'autres catégories si nécessaire

    # Récupérer la mission avec ses détails de commande pour calculer le poids/volume total
    # Si mission_id est fourni, on vérifie la mission existante
    # Si mission_id est None (nouvelle mission), on doit temporairement calculer depuis les détails sélectionnés
    # Pour simplifier, nous allons supposer que cette fonction est appelée APRES que les détails soient associés à la mission
    # ou qu'elle reçoit une liste de détails à vérifier.
    # Pour l'instant, on la rendra simple et on l'appellera sur la mission existante lors de l'EDIT.
    # Pour l'ADD, on devra l'adapter.

    # Pour la modification de mission, on récupère directement les détails liés à la mission
    if mission_id:
        mission = db.session.execute(
            db.select(Mission).filter_by(id_mission=mission_id)
            .options(selectinload(Mission.details_commandes))
        ).scalar_one_or_none()
        if not mission:
            return "Mission non trouvée pour la vérification de capacité."
        details_to_check = mission.details_commandes
    else:
        # Cette branche est plus complexe pour l'ADD car les détails ne sont pas encore liés à la mission.
        # Pour le moment, nous implémenterons la vérification uniquement pour l'EDIT,
        # et nous laisserons l'ADD simple pour ne pas complexifier trop.
        # Ou, nous pourrions exiger que tous les détails soient déjà liés pour l'ADD aussi.
        # Décision: Pour l'ADD, on ne vérifie pas encore la capacité.
        # On se concentrera sur l'EDIT où les détails sont déjà associés.
        return None # Pas de vérification si pas de mission_id (pour l'ADD)

    total_poids = 0.0
    total_volume = 0.0

    for detail in details_to_check:
        total_poids += float(detail.poids) if detail.poids is not None else 0.0
        total_volume += float(detail.volume) if detail.volume is not None else 0.0
    
    # Vérification finale
    if total_poids > max_poids_kg:
        return f"Le poids total des colis ({total_poids:.2f} kg) dépasse la capacité max du véhicule ({max_poids_kg:.2f} kg)."
    
    if total_volume > max_volume_m3:
        return f"Le volume total des colis ({total_volume:.2f} m³) dépasse la capacité max du véhicule ({max_volume_m3:.2f} m³)."
    
    return None # Tout est bon, pas de problème de capacité
