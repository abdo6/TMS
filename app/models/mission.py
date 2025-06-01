# app/models/mission.py
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship # <-- AJOUTEZ CET IMPORT SI NON PRÉSENT

class Mission(db.Model):
    __tablename__ = 'mission'

    id_mission = db.Column(db.Integer, primary_key=True)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)

    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeur.id_chauffeur'), nullable=False)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicule.id_vehicule'), nullable=False)
    
    id_destination = db.Column(db.Integer, db.ForeignKey('destination.id_destination')) 

    # NOUVELLE CLÉ ÉTRANGÈRE VERS FEUILLE DE ROUTE
    id_feuille_de_route = db.Column(db.Integer, db.ForeignKey('feuille_de_route.id_feuille_de_route')) # Peut être NULL si la mission n'est pas encore sur une FDR

    statut = db.Column(db.String(50), default='Planifiée', nullable=False) # <--- NOUVELLE COLONNE DE STATUT (valeurs possibles: 'Planifiée', 'En cours', 'Terminée', 'Annulée')




    chauffeur = db.relationship('Chauffeur', backref='missions')
    vehicule = db.relationship('Vehicule', backref='missions')
    destination = db.relationship('Destination', backref='missions_as_main_dest', lazy=True) 

    details_commandes = db.relationship(
        'DetailCommande',
        secondary='mission_detail', 
        backref='missions',          
        lazy='selectin'               
    )
    
    # NOUVELLE RELATION VERS FEUILLE DE ROUTE
    feuille_de_route = db.relationship('FeuilleDeRoute', backref='missions_affectees', lazy=True)


    def __repr__(self):
        return f"<Mission {self.id_mission} | Chauffeur: {self.chauffeur.nom if self.chauffeur else 'N/A'} | Véhicule: {self.vehicule.immatriculation_ve if self.vehicule else 'N/A'}>"

    def to_dict(self):
        return {
            'id_mission': self.id_mission,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat(),
            'heure_debut': self.heure_debut.isoformat(),
            'heure_fin': self.heure_fin.isoformat(),
            'chauffeur_id': self.id_chauffeur,
            'vehicule_id': self.id_vehicule,
            'destination_id': self.id_destination,
            'chauffeur_nom_complet': f"{self.chauffeur.nom} {self.chauffeur.prenom}" if self.chauffeur else 'N/A',
            'vehicule_immatriculation': self.vehicule.immatriculation_ve if self.vehicule else 'N/A',
            'destination_description': self.destination.description if self.destination else 'N/A',
            'destination_latitude': float(self.destination.latitude) if self.destination and self.destination.latitude else None,
            'destination_longitude': float(self.destination.longitude) if self.destination and self.destination.longitude else None,
            'id_feuille_de_route': self.id_feuille_de_route, # <-- AJOUTÉ ICI
            'feuille_de_route_description': self.feuille_de_route.description if self.feuille_de_route else 'N/A' # <-- AJOUTÉ ICI
        }