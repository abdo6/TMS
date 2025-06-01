# app/routes/api_routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.localisation import Localisation
from app.models.chauffeur import Chauffeur # Pour vérifier l'existence du chauffeur
from datetime import datetime
from sqlalchemy import func # <-- CETTE LIGNE DOIT ÊTRE PRÉSENTE
from sqlalchemy.orm import joinedload # <-- ET CELLE-CI AUSSI
from app.models.mission import Mission # <--- ASSUREZ-VOUS QUE C'EST BIEN IMPORTÉ
from datetime import datetime, timedelta # <--- Assurez-vous que timedelta est importé !
from app.models.mission import Mission


api = Blueprint('api', __name__)

@api.route('/location', methods=['POST'])
def receive_location():
    # Assurez-vous que la requête contient du JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Récupérer les données envoyées
    chauffeur_id = data.get('chauffeur_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Validation des données
    if not all([chauffeur_id, latitude, longitude]):
        return jsonify({"error": "Missing data: chauffeur_id, latitude, and longitude are required"}), 400

    try:
        chauffeur_id = int(chauffeur_id)
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"error": "Invalid data types for chauffeur_id, latitude or longitude"}), 400

    # Vérifier si le chauffeur existe
    chauffeur = db.session.get(Chauffeur, chauffeur_id)
    if not chauffeur:
        return jsonify({"error": f"Chauffeur with ID {chauffeur_id} not found"}), 404

    # Créer une nouvelle instance de Localisation
    new_location = Localisation(
        id_chauffeur=chauffeur_id,
        latitude=latitude,
        longitude=longitude,
        timestamp=datetime.utcnow() # Utilise l'heure actuelle du serveur (UTC)
    )

    try:
        db.session.add(new_location)
        db.session.commit()
        return jsonify({"message": "Location saved successfully", "location_id": new_location.id_localisation}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save location: {str(e)}"}), 500
    
@api.route('/locations/latest', methods=['GET'])
def get_latest_locations_api():
    # Cette logique est la même que celle que nous avons ajoutée précédemment dans main_routes.py
    # pour récupérer la dernière localisation de chaque chauffeur.
    latest_locations_subquery = db.session.query(
        Localisation.id_chauffeur,
        func.max(Localisation.timestamp).label('max_timestamp')
    ).group_by(Localisation.id_chauffeur).subquery()

    chauffeur_locations = db.session.execute(
        db.select(Localisation)
        .join(latest_locations_subquery,
              (Localisation.id_chauffeur == latest_locations_subquery.c.id_chauffeur) &
              (Localisation.timestamp == latest_locations_subquery.c.max_timestamp))
        .options(joinedload(Localisation.chauffeur)) # Charger les données du chauffeur
    ).scalars().all()

    # Préparer les données pour la réponse JSON
    chauffeur_locations_data = []
    for loc in chauffeur_locations:
        chauffeur_locations_data.append(loc.to_dict())
    
    return jsonify(chauffeur_locations_data)

@api.route('/mission/<int:mission_id>/status', methods=['POST'])
def update_mission_status(mission_id): # <--- AJOUTEZ 'mission_id' ICI
    # La ligne suivante n'est plus nécessaire car mission_id vient de l'URL
    # mission_id = data.get('mission_id') 

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Récupérer le nouveau statut envoyé
    new_status = data.get('status')
    # mission_id est déjà disponible via l'argument de la fonction


    # Validation des données
    if not new_status: # mission_id est déjà validé par Flask s'il est de type int
        return jsonify({"error": "Missing data: status is required"}), 400
    
    # Vérifier si la mission existe
    mission = db.session.get(Mission, mission_id)
    if not mission:
        return jsonify({"error": f"Mission with ID {mission_id} not found"}), 404

    # Validation du statut (optionnel mais recommandé pour éviter des statuts arbitraires)
    allowed_statuses = ['Planifiée', 'En cours', 'Terminée', 'Annulée']
    if new_status not in allowed_statuses:
        return jsonify({"error": f"Invalid status. Allowed statuses are: {', '.join(allowed_statuses)}"}), 400

    mission.statut = new_status

    try:
        db.session.commit()
        return jsonify({"message": f"Mission {mission_id} status updated to {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update mission status: {str(e)}"}), 500
    
	# app/routes/api_routes.py (Ajouter ce code à la fin du fichier)

@api.route('/locations/history/<int:chauffeur_id>', methods=['GET'])
def get_chauffeur_location_history(chauffeur_id):
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({"error": "Missing start_date or end_date parameters"}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Pour inclure toute la journée de fin, ajouter 1 jour pour la comparaison
        end_date_inclusive = end_date + timedelta(days=1)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Vérifier si le chauffeur existe
    chauffeur = db.session.get(Chauffeur, chauffeur_id)
    if not chauffeur:
        return jsonify({"error": f"Chauffeur with ID {chauffeur_id} not found"}), 404

    # Récupérer l'historique des localisations pour le chauffeur et la période
    # Nous voulons toutes les localisations entre le début de start_date et la fin de end_date
    history_locations = db.session.execute(
        db.select(Localisation)
        .filter(
            Localisation.id_chauffeur == chauffeur_id,
            db.cast(Localisation.timestamp, db.Date) >= start_date, # Comparez seulement la date
            db.cast(Localisation.timestamp, db.Date) < end_date_inclusive # Excluez le jour après la fin
        )
        .order_by(Localisation.timestamp) # Ordonner chronologiquement
    ).scalars().all()

    if not history_locations:
            # Retourner une liste vide pour que le frontend puisse appeler .map() sans erreur,
            # et le frontend gérera l'affichage du message "aucune donnée".
            return jsonify([]), 200 # <-- CORRECTION ICI

    # Formater les données pour la réponse JSON
    locations_data = [loc.to_dict() for loc in history_locations]
    
    return jsonify(locations_data)