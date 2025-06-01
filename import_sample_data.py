# import_sample_data.py (Version Complète)
import sys
import os
from datetime import date, time, datetime, timedelta
import random

# Ajouter le dossier parent (racine du projet) au PYTHONPATH
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db

# Importe tous les modèles
from app.models.user import User # Importez le modèle User pour créer des utilisateurs liés
from app.models.chauffeur import Chauffeur
from app.models.vehicule import Vehicule
from app.models.client_initial import ClientInitial
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
from app.models.affretement import Affretement
from app.models.feuille_de_route import FeuilleDeRoute
from app.models.mission import Mission
from app.models.mission_detail import MissionDetail
from app.models.ville import Ville 
from app.models.province import Province
from app.models.destination import Destination

def populate_sample_data():
    app = create_app()
    with app.app_context():
        print("\n--- Début du peuplement de données d'exemple (Version Complète) ---")

        # Vérifier si la base de données contient déjà des données pour éviter les duplicata
        if db.session.query(Chauffeur).count() > 0 or db.session.query(Mission).count() > 0:
            print("Des données existent déjà. Peuplement annulé pour éviter les doublons.")
            print("Pour recharger les données, veuillez :")
            print("1. Arrêter l'application Flask.")
            print("2. Supprimer/recréer la base de données 'tms_db' manuellement via pgAdmin ou psql.")
            print("3. Ré-exécuter les migrations : `flask db upgrade`.")
            print("4. Puis lancer ce script.")
            return

        # Récupération des villes/provinces existantes (assure que import_geo_data.py a été exécuté)
        try:
            villes = db.session.execute(db.select(Ville)).scalars().all()
            provinces = db.session.execute(db.select(Province)).scalars().all()
            if not villes or not provinces:
                raise Exception("Aucune ville ou province trouvée. Exécutez 'import_geo_data.py' d'abord.")
            casablanca_ville = next(v for v in villes if v.nom_ville == 'Casablanca')
            rabat_ville = next(v for v in villes if v.nom_ville == 'Rabat')
            marrakech_ville = next(v for v in villes if v.nom_ville == 'Marrakech')
            tanger_ville = next(v for v in villes if v.nom_ville == 'Tanger')

            casa_anfa_prov = next(p for p in provinces if p.nom_province == 'Casablanca-Anfa')
            rabat_prov = next(p for p in provinces if p.nom_province == 'Rabat')

        except Exception as e:
            print(f"Erreur: Impossible de récupérer les villes/provinces existantes. Assurez-vous d'avoir exécuté 'import_geo_data.py' avant ce script. Erreur: {e}")
            return

        # --- Création des données de base ---
        print("\nCréation des Chauffeurs...")
        chauffeurs_data = [
            {'nom':'Benani', 'prenom':'Ahmed', 'adresse':'Rue Hassan II, Casablanca', 'numero_telephone':'0600112233', 'email':'ahmed.b@example.com', 'categorie_ch':'C, E'},
            {'nom':'Alaoui', 'prenom':'Fatima', 'adresse':'Av. Mohammed V, Rabat', 'numero_telephone':'0611223344', 'email':'fatima.a@example.com', 'categorie_ch':'C'},
            {'nom':'Cherkaoui', 'prenom':'Youssef', 'adresse':'Bd Zerktouni, Marrakech', 'numero_telephone':'0622334455', 'email':'youssef.c@example.com', 'categorie_ch':'B, C'},
            {'nom':'Sami', 'prenom':'Nabil', 'adresse':'Rue Al Massira, Tanger', 'numero_telephone':'0633445566', 'email':'nabil.s@example.com', 'categorie_ch':'C, E'},
            {'nom':'El Fassi', 'prenom':'Sara', 'adresse':'Av. France, Fès', 'numero_telephone':'0644556677', 'email':'sara.f@example.com', 'categorie_ch':'B'},
        ]
        chauffeurs = [Chauffeur(**data) for data in chauffeurs_data]
        db.session.add_all(chauffeurs)
        db.session.commit()
        print(f"Ajouté {len(chauffeurs)} chauffeurs.")

        print("\nCréation des Véhicules...")
        vehicules_data = [
            {'immatriculation_ve':'A-12345-01', 'categorie':'Camion'},
            {'immatriculation_ve':'B-67890-02', 'categorie':'Utilitaire'},
            {'immatriculation_ve':'C-11223-03', 'categorie':'Semi-remorque'},
            {'immatriculation_ve':'D-44556-04', 'categorie':'Camion Froid'},
            {'immatriculation_ve':'E-78901-05', 'categorie':'Fourgonnette'},
            {'immatriculation_ve':'F-23456-06', 'categorie':'Poids Lourd'},
            {'immatriculation_ve':'G-78901-07', 'categorie':'Citerne'},
        ]
        vehicules = [Vehicule(**data) for data in vehicules_data]
        db.session.add_all(vehicules)
        db.session.commit()
        print(f"Ajouté {len(vehicules)} véhicules.")

        print("\nCréation des Clients Initiaux...")
        clients_initial_data = [
            {'nom':'Transport Express Maroc', 'prenom':'Service Client', 'adresse':'123 Rue Principale, Casablanca', 'numero_telephone':'0522112233', 'email':'contact@tem.ma'},
            {'nom':'Logistique Sans Frontières', 'prenom':'Commercial', 'adresse':'45 Av. de la Liberté, Rabat', 'numero_telephone':'0537445566', 'email':'info@lsf.ma'},
            {'nom':'DistriFrais SA', 'prenom':'Direction', 'adresse':'Zone Industrielle, Marrakech', 'numero_telephone':'0524789012', 'email':'contact@distrifrais.ma'},
        ]
        clients_initial = [ClientInitial(**data) for data in clients_initial_data]
        db.session.add_all(clients_initial)
        db.session.commit()
        print(f"Ajouté {len(clients_initial)} clients initiaux.")

        print("\nCréation des Types de Véhicules...")
        types_vehicule_data = [
            {'nom_type':'Camionnette'},
            {'nom_type':'Camion Froid'},
            {'nom_type':'Porte-conteneur'},
            {'nom_type':'Fourgon'},
            {'nom_type':'Semi-remorque frigorifique'},
        ]
        types_vehicule = [TypeVehicule(**data) for data in types_vehicule_data]
        db.session.add_all(types_vehicule)
        db.session.commit()
        print(f"Ajouté {len(types_vehicule)} types de véhicules.")

        print("\nCréation des Sous-traitants...")
        sous_traitants_data = [
            {'nom_entreprise':'Globus Trans', 'contact_personne':'Omar Rouchdi', 'numero_telephone':'0630405060', 'email':'omar.r@globustrans.ma', 'adresse':'Zone Industrielle, Tanger'},
            {'nom_entreprise':'Rapid Cargo', 'contact_personne':'Nadia El Mansour', 'numero_telephone':'0640506070', 'email':'nadia.m@rapidcargo.ma', 'adresse':'Agdal, Rabat'},
            {'nom_entreprise':'Sud Logistique Express', 'contact_personne':'Khalid Benali', 'numero_telephone':'0650607080', 'email':'khalid.b@sudlog.ma', 'adresse':'Sidi Ghanem, Marrakech'},
        ]
        sous_traitants = [SousTraitant(**data) for data in sous_traitants_data]
        db.session.add_all(sous_traitants)
        db.session.commit()
        print(f"Ajouté {len(sous_traitants)} sous-traitants.")

        print("\nCréation des Types d'Indisponibilité Chauffeur et Véhicule...")
        types_indispo_chauffeur_data = [
            {'nom_type':'Congé Annuel'}, {'nom_type':'Maladie'}, {'nom_type':'Formation'}, {'nom_type':'Permis suspendu'}
        ]
        types_indispo_chauffeur = [TypeIndispoChauffeur(**data) for data in types_indispo_chauffeur_data]
        db.session.add_all(types_indispo_chauffeur)
        db.session.commit()

        types_indispo_vehicule_data = [
            {'nom_type':'Panne Mécanique'}, {'nom_type':'Entretien Régulier'}, {'nom_type':'Contrôle Technique'}, {'nom_type':'Accident'}
        ]
        types_indispo_vehicule = [TypeIndispoVehicule(**data) for data in types_indispo_vehicule_data]
        db.session.add_all(types_indispo_vehicule)
        db.session.commit()
        print("Ajouté des types d'indisponibilité.")

        # --- Données avec dépendances de premier niveau ---
        print("\nCréation des Destinations...")
        destinations_data = [
            {'description':'Centre Commercial AnfaPlace, Casablanca', 'latitude':33.589886, 'longitude':-7.603869, 'ville':casablanca_ville, 'province':casa_anfa_prov},
            {'description':'Zone Industrielle Ain Sebaa, Casablanca', 'latitude':33.606277, 'longitude':-7.535079, 'ville':casablanca_ville, 'province':casa_anfa_prov},
            {'description':'Technopolis, Rabat', 'latitude':34.076865, 'longitude':-6.680073, 'ville':rabat_ville, 'province':rabat_prov},
            {'description':'Médina, Marrakech', 'latitude':31.629472, 'longitude':-7.981061, 'ville':marrakech_ville, 'province':None},
            {'description':'Port de Tanger Med, Tanger', 'latitude':35.882352, 'longitude':-5.352422, 'ville':tanger_ville, 'province':None}, # Supposons pas de province précise pour l'exemple
            {'description':'Usine de Fès, Oued Fès', 'latitude':34.020882, 'longitude':-5.006969, 'ville':next(v for v in villes if v.nom_ville == 'Fès'), 'province':None},
            {'description':'Aéroport Mohammed V, Nouaceur', 'latitude':33.367098, 'longitude':-7.589998, 'ville':casablanca_ville, 'province':next(p for p in provinces if p.nom_province == 'Nouaceur')},
        ]
        destinations = [Destination(**data) for data in destinations_data]
        db.session.add_all(destinations)
        db.session.commit()
        print(f"Ajouté {len(destinations)} destinations.")
        
        print("\nCréation des Services Clients...")
        services_clients_data = [
            {'nom_service':'Expédition Nationale', 'client_initial':clients_initial[0]},
            {'nom_service':'Livraison Express', 'client_initial':clients_initial[0]},
            {'nom_service':'Fret Routier International', 'client_initial':clients_initial[1]},
            {'nom_service':'Transport Réfrigéré', 'client_initial':clients_initial[2]},
            {'nom_service':'Transport Urgence', 'client_initial':clients_initial[0]},
        ]
        services_clients = [ServiceClient(**data) for data in services_clients_data]
        db.session.add_all(services_clients)
        db.session.commit()
        print(f"Ajouté {len(services_clients)} services clients.")

        # import_sample_data.py
# ... (code précédent) ...

        # import_sample_data.py
# ... (code précédent) ...

        print("\nCréation des Entêtes de Commande...")
        entetes_commande_instances = [] # Renommer pour éviter la confusion
        for i in range(1, 10): # Créer 9 entêtes de commande
            ref = f'CMD-2024-{i:03d}'
            client_initial_choice = random.choice(clients_initial)
            available_services = [s for s in services_clients if s.id_client_initial == client_initial_choice.id_client_initial]
            if not available_services:
                service_client_choice = random.choice(services_clients)
            else:
                service_client_choice = random.choice(available_services)
    
    # AJUSTER ICI : Créer l'instance EnteteCommande directement
        new_entete = EnteteCommande(reference=ref, client_initial=client_initial_choice, service_client=service_client_choice, date_commande=date.today() - timedelta(days=random.randint(0, 30)))
        entetes_commande_instances.append(new_entete)

        db.session.add_all(entetes_commande_instances) # Ajouter les instances directement
        db.session.commit()
        entetes_commande = entetes_commande_instances # Garder la liste pour les références futures
        print(f"Ajouté {len(entetes_commande)} entêtes de commande.")

# ... (code suivant) ...




        print("\nCréation des Clients Finaux...")
        
        clients_final_data = [
            {'nom':'Kettani', 'prenom':'Nour', 'adresse':'Quartier Maarif, Casablanca', 'numero_telephone':'0655667788', 'email':'nour.k@example.com', 'client_initial':clients_initial[0]},
            {'nom':'Bennani', 'prenom':'Omar', 'adresse':'Hay Riad, Rabat', 'numero_telephone':'0666778899', 'email':'omar.b@example.com', 'client_initial':clients_initial[1]},
            {'nom':'Ziani', 'prenom':'Sarah', 'adresse':'Gueliz, Marrakech', 'numero_telephone':'0677889900', 'email':'sarah.z@example.com', 'client_initial':clients_initial[0]},
            {'nom':'Daoudi', 'prenom':'Amine', 'adresse':'Av. Moulay Youssef, Tanger', 'numero_telephone':'0688990011', 'email':'amine.d@example.com', 'client_initial':clients_initial[1]},
            {'nom':'Guessous', 'prenom':'Imane', 'adresse':'Ville Nouvelle, Fès', 'numero_telephone':'0699001122', 'email':'imane.g@example.com', 'client_initial':clients_initial[2]},
        ]
        clients_final = [ClientFinal(**data) for data in clients_final_data]
        db.session.add_all(clients_final)
        db.session.commit()
        print(f"Ajouté {len(clients_final)} clients finaux.")

        print("\nCréation des Détails de Commande...")
        details_commande_data = []
        for i in range(1, 20): # Créer 19 détails de commande
            entete_choice = random.choice(entetes_commande)
            client_final_choice = random.choice([cf for cf in clients_final if cf.id_client_initial == entete_choice.id_client_initial]) if [cf for cf in clients_final if cf.id_client_initial == entete_choice.id_client_initial] else random.choice(clients_final)
            details_commande_data.append({
                'quantite': random.randint(1, 100),
                'description_colis': f'Colis {i} - {random.choice(["fragile", "standard", "volumineux"])}',
                'volume': round(random.uniform(0.1, 5.0), 2),
                'poids': round(random.uniform(10.0, 1000.0), 2),
                'entete_commande': entete_choice,
                'type_vehicule': random.choice(types_vehicule),
                'client_final': client_final_choice,
                'destination': random.choice(destinations)
            })
        details_commande = [DetailCommande(**data) for data in details_commande_data]
        db.session.add_all(details_commande)
        db.session.commit()
        print(f"Ajouté {len(details_commande)} détails de commande.")

        print("\nCréation des Trajets...")
        trajets_data = [
            {'description':'Trajet Casablanca-Casablanca (Urbain)', 'distance_km':25.5, 'duree_heures':0.8, 'destination':destinations[0]},
            {'description':'Trajet Casablanca-Rabat (Interurbain)', 'distance_km':90.0, 'duree_heures':1.5, 'destination':destinations[2]},
            {'description':'Trajet Casablanca-Marrakech', 'distance_km':240.0, 'duree_heures':3.0, 'destination':destinations[3]},
            {'description':'Trajet Tanger-Casablanca', 'distance_km':350.0, 'duree_heures':4.5, 'destination':destinations[0]},
            {'description':'Trajet Fès-Rabat', 'distance_km':200.0, 'duree_heures':2.8, 'destination':destinations[2]},
        ]
        trajets = [Trajet(**data) for data in trajets_data]
        db.session.add_all(trajets)
        db.session.commit()
        print(f"Ajouté {len(trajets)} trajets.")

        print("\nCréation des Indisponibilités Chauffeur et Véhicule...")
        today = date.today()
        indispo_chauffeur_data = [
            {'chauffeur':chauffeurs[0], 'type_indispo_chauffeur':types_indispo_chauffeur[0], 'date_debut':today + timedelta(days=30), 'date_fin':today + timedelta(days=45), 'description':'Congés annuels planifiés'},
            {'chauffeur':chauffeurs[1], 'type_indispo_chauffeur':types_indispo_chauffeur[1], 'date_debut':today - timedelta(days=5), 'date_fin':today + timedelta(days=2), 'description':'Grippe'},
            {'chauffeur':chauffeurs[2], 'type_indispo_chauffeur':types_indispo_chauffeur[2], 'date_debut':today + timedelta(days=10), 'date_fin':today + timedelta(days=12), 'description':'Formation sécurité'},
            {'chauffeur':chauffeurs[3], 'type_indispo_chauffeur':types_indispo_chauffeur[0], 'date_debut':today - timedelta(days=10), 'date_fin':today - timedelta(days=3), 'description':'Anciens congés'}
        ]
        indispo_chauffeur = [IndisponibiliteChauffeur(**data) for data in indispo_chauffeur_data]
        db.session.add_all(indispo_chauffeur)
        db.session.commit()

        indispo_vehicule_data = [
            {'vehicule':vehicules[0], 'type_indispo_vehicule':types_indispo_vehicule[1], 'date_debut':today + timedelta(days=10), 'date_fin':today + timedelta(days=12), 'description':'Remplacement freins'},
            {'vehicule':vehicules[1], 'type_indispo_vehicule':types_indispo_vehicule[0], 'date_debut':today - timedelta(days=3), 'date_fin':today, 'description':'Panne de batterie'},
            {'vehicule':vehicules[2], 'type_indispo_vehicule':types_indispo_vehicule[2], 'date_debut':today + timedelta(days=20), 'date_fin':today + timedelta(days=21), 'description':'Pré-contrôle technique'},
        ]
        indispo_vehicule = [IndisponibiliteVehicule(**data) for data in indispo_vehicule_data]
        db.session.add_all(indispo_vehicule)
        db.session.commit()
        print("Ajouté des indisponibilités.")
        
        print("\nCréation des Véhicules Externes et Chauffeurs Externes...")
        vehicules_externes_data = [
            {'immatriculation_ve':'GT-45678', 'categorie':'Porteur', 'description':'Camion 10T', 'sous_traitant':sous_traitants[0]},
            {'immatriculation_ve':'RC-90123', 'categorie':'Fourgon', 'description':'Fourgonnette de livraison', 'sous_traitant':sous_traitants[1]},
            {'immatriculation_ve':'SL-11223', 'categorie':'Semi-remorque', 'description':'Semi-remorque de 38T', 'sous_traitant':sous_traitants[2]},
        ]
        vehicules_externes = [VehiculeExterne(**data) for data in vehicules_externes_data]
        db.session.add_all(vehicules_externes)
        db.session.commit()

        chauffeurs_externes_data = [
            {'nom':'Idrissi', 'prenom':'Khalid', 'numero_telephone':'0680900011', 'email':'khalid.i@example.com', 'categorie_permis':'C, E', 'sous_traitant':sous_traitants[0]},
            {'nom':'Amrani', 'prenom':'Samira', 'numero_telephone':'0690011223', 'email':'samira.a@example.com', 'categorie_permis':'B', 'sous_traitant':sous_traitants[1]},
            {'nom':'Kadi', 'prenom':'Yassine', 'numero_telephone':'0670809000', 'email':'yassine.k@example.com', 'categorie_permis':'C', 'sous_traitant':sous_traitants[2]},
        ]
        chauffeurs_externes = [ChauffeurExterne(**data) for data in chauffeurs_externes_data]
        db.session.add_all(chauffeurs_externes)
        db.session.commit()
        print("Ajouté des véhicules et chauffeurs externes.")

        print("\nCréation des Demandes d'Affrètement...")
        affretements_data = [
            {'date_demande':today, 'date_debut_souhaitee':today + timedelta(days=7), 'date_fin_souhaitee':today + timedelta(days=7),
             'description_besoin':'Transport urgent de médicaments vers Marrakech', 'statut':'En attente', 'cout_estime':500.0,
             'id_detail_commande':details_commande[random.randint(0, len(details_commande)-1)].id_detail_commande,
             'id_sous_traitant':None, 'id_vehicule_externe':None, 'id_chauffeur_externe':None},
            {'date_demande':today - timedelta(days=10), 'date_debut_souhaitee':today - timedelta(days=5), 'date_fin_souhaitee':today - timedelta(days=5),
             'description_besoin':'Retour de vide de Rabat', 'statut':'Terminé', 'cout_estime':200.0,
             'id_detail_commande':None,
             'sous_traitant':sous_traitants[1], 'vehicule_externe':vehicules_externes[1], 'chauffeur_externe':chauffeurs_externes[1]},
            {'date_demande':today - timedelta(days=2), 'date_debut_souhaitee':today + timedelta(days=1), 'date_fin_souhaitee':today + timedelta(days=3),
             'description_besoin':'Dépannage de transport frigorifique', 'statut':'Confirmé', 'cout_estime':750.0,
             'id_detail_commande':details_commande[random.randint(0, len(details_commande)-1)].id_detail_commande,
             'sous_traitant':sous_traitants[0], 'vehicule_externe':vehicules_externes[0], 'chauffeur_externe':chauffeurs_externes[0]},
        ]
        affretements = [Affretement(**data) for data in affretements_data]
        db.session.add_all(affretements)
        db.session.commit()
        print(f"Ajouté {len(affretements)} demandes d'affrètement.")

        print("\nCréation des Feuilles de Route...")
        feuilles_de_route_data = [
            {'description':'Tournée quotidienne Casablanca Nord', 'chauffeur':chauffeurs[0], 'vehicule':vehicules[0],
                           'date_depart_prevu':today + timedelta(days=1), 'heure_depart_prevu':time(8,0),
                           'date_arrivee_prevue':today + timedelta(days=1), 'heure_arrivee_prevue':time(17,0)},
            {'description':'Livraison spéciale Rabat', 'chauffeur':chauffeurs[1], 'vehicule':vehicules[1],
                           'date_depart_prevu':today + timedelta(days=2), 'heure_depart_prevu':time(9,0),
                           'date_arrivee_prevue':today + timedelta(days=2), 'heure_arrivee_prevue':time(14,0)},
            {'description':'Navette Marrakech-Fès', 'chauffeur':chauffeurs[2], 'vehicule':vehicules[2],
                           'date_depart_prevu':today - timedelta(days=3), 'heure_depart_prevu':time(7,0),
                           'date_arrivee_prevue':today - timedelta(days=2), 'heure_arrivee_prevue':time(18,0)},
        ]
        feuilles_de_route = [FeuilleDeRoute(**data) for data in feuilles_de_route_data]
        db.session.add_all(feuilles_de_route)
        db.session.commit()
        print(f"Ajouté {len(feuilles_de_route)} feuilles de route.")

        # import_sample_data.py
# ... (code précédent) ...

        print("\nCréation des Missions...")
        missions_instances = [] # Renommer pour éviter la confusion
        missions_data_list_of_dicts = [ # Ancienne structure, pour référence rapide
            {'date_debut':today + timedelta(days=1), 'date_fin':today + timedelta(days=1), 'heure_debut':time(8,0), 'heure_fin':time(12,0),
            'chauffeur':chauffeurs[0], 'vehicule':vehicules[0], 'destination':destinations[0], 'feuille_de_route':feuilles_de_route[0], 'statut':'Planifiée'},
            {'date_debut':today + timedelta(days=1), 'date_fin':today + timedelta(days=1), 'heure_debut':time(13,0), 'heure_fin':time(17,0),
            'chauffeur':chauffeurs[0], 'vehicule':vehicules[0], 'destination':destinations[1], 'feuille_de_route':feuilles_de_route[0], 'statut':'Planifiée'},
            {'date_debut':today + timedelta(days=2), 'date_fin':today + timedelta(days=2), 'heure_debut':time(9,0), 'heure_fin':time(14,0),
            'chauffeur':chauffeurs[1], 'vehicule':vehicules[1], 'destination':destinations[2], 'feuille_de_route':feuilles_de_route[1], 'statut':'Planifiée'},
            {'date_debut':today - timedelta(days=1), 'date_fin':today - timedelta(days=1), 'heure_debut':time(10,0), 'heure_fin':time(18,0),
            'chauffeur':chauffeurs[random.randint(0,len(chauffeurs)-1)], 'vehicule':vehicules[random.randint(0,len(vehicules)-1)], 'destination':destinations[random.randint(0,len(destinations)-1)], 'feuille_de_route':None, 'statut':'En cours'},
            {'date_debut':today - timedelta(days=5), 'date_fin':today - timedelta(days=4), 'heure_debut':time(7,0), 'heure_fin':time(19,0),
            'chauffeur':chauffeurs[random.randint(0,len(chauffeurs)-1)], 'vehicule':vehicules[random.randint(0,len(vehicules)-1)], 'destination':destinations[random.randint(0,len(destinations)-1)], 'feuille_de_route':feuilles_de_route[2], 'statut':'Terminée'},
            {'date_debut':today + timedelta(days=3), 'date_fin':today + timedelta(days=3), 'heure_debut':time(6,0), 'heure_fin':time(10,0),
            'chauffeur':chauffeurs[random.randint(0,len(chauffeurs)-1)], 'vehicule':vehicules[random.randint(0,len(vehicules)-1)], 'destination':destinations[random.randint(0,len(destinations)-1)], 'feuille_de_route':None, 'statut':'Annulée'},
            ]
        missions = [] # Initialiser une nouvelle liste vide pour les instances de Mission
        for data in missions_data_list_of_dicts: # Utiliser l'ancienne liste de dictionnaires
            missions.append(Mission(**data)) # Créer l'instance de Mission ici

        db.session.add_all(missions) # Ajouter les instances de Mission
        db.session.commit()
        print(f"Ajouté {len(missions)} missions.")

# ... (code suivant) ...

        print("\nAssociation des Détails de Commande aux Missions (MissionDetail)...")
        # Associer des détails de commande aux missions
        # Assigner au moins un détail à chaque mission existante, si possible
        for mission in missions:
            if not mission.details_commandes: # Si la mission n'a pas encore de détails
                # Choisir des détails qui ne sont pas déjà affectés ou qui sont peu affectés
                unassigned_details_query = db.session.execute(
                    db.select(DetailCommande)
                    .filter(db.not_(DetailCommande.missions.any()))
                    .limit(random.randint(1, 3)) # Essayer d'affecter 1 à 3 détails non assignés
                ).scalars().all()
                
                if unassigned_details_query:
                    for detail in unassigned_details_query:
                        mission.details_commandes.append(detail)
                else: # Si tous les détails sont assignés, prendre un au hasard (peut être un doublon)
                    mission.details_commandes.append(random.choice(details_commande))
        db.session.commit()
        print("Détails de commande associés aux missions.")

        print("\nCréation des Utilisateurs liés (CHAUFFEUR, CLIENT)...")
        # Créer un utilisateur pour le premier chauffeur (Ahmed Benani)
        chauffeur_user = User(username='chauffeur1', email='chauffeur1@example.com', role='CHAUFFEUR', id_chauffeur=chauffeurs[0].id_chauffeur)
        chauffeur_user.set_password('passchauffeur')
        db.session.add(chauffeur_user)

        # Créer un utilisateur pour un client initial (Transport Express Maroc)
        client_user = User(username='client1', email='client1@example.com', role='CLIENT', id_client_initial=clients_initial[0].id_client_initial)
        client_user.set_password('passclient')
        db.session.add(client_user)

        db.session.commit()
        print("Ajouté des utilisateurs liés (CHAUFFEUR, CLIENT).")

        print("\n--- Peuplement des données d'exemple terminé avec succès ! ---")

if __name__ == '__main__':
    populate_sample_data()