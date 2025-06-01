# app/models/feuille_de_route.py
from app import db
from datetime import date, datetime

class FeuilleDeRoute(db.Model):
    __tablename__ = 'feuille_de_route'

    id_feuille_de_route = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255)) # Ex: "Feuille de route pour la tournée Nord"

    # Dates et heures planifiées
    date_depart_prevu = db.Column(db.Date, nullable=False)
    heure_depart_prevu = db.Column(db.Time, nullable=False)
    date_arrivee_prevue = db.Column(db.Date, nullable=False)
    heure_arrivee_prevue = db.Column(db.Time, nullable=False)

    # Données réelles (pour enregistrement après le trajet)
    date_depart_reel = db.Column(db.Date)
    heure_depart_reel = db.Column(db.Time)
    date_arrivee_reelle = db.Column(db.Date)
    heure_arrivee_reelle = db.Column(db.Time)
    km_debut = db.Column(db.Numeric(10, 2))
    km_fin = db.Column(db.Numeric(10, 2))

    # Clés étrangères
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeur.id_chauffeur'), nullable=False)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicule.id_vehicule'), nullable=False)
    # L'id_sous_traitant et id_type_vehicule ne sont pas directement liés à FeuilleDeRoute dans le diagramme
    # mais sont indirectement liés via Chauffeur/Vehicule si ce sont des externes.
    # Si on veut stocker le type de véhicule spécifique assigné (ex: Camionnette), on peut le lier à TypeVehicule.
    # Pour l'instant, on se base sur les relations directes du diagramme pour la feuille de route.

    # Relations
    chauffeur = db.relationship('Chauffeur', backref='feuilles_de_route', lazy=True)
    vehicule = db.relationship('Vehicule', backref='feuilles_de_route', lazy=True)

    def __repr__(self):
        return f"<FeuilleDeRoute {self.id_feuille_de_route} - {self.description}>"

    def to_dict(self):
        return {
            'id_feuille_de_route': self.id_feuille_de_route,
            'description': self.description,
            'date_depart_prevu': self.date_depart_prevu.isoformat(),
            'heure_depart_prevu': self.heure_depart_prevu.isoformat(),
            'date_arrivee_prevue': self.date_arrivee_prevue.isoformat(),
            'heure_arrivee_prevue': self.heure_arrivee_prevue.isoformat(),
            'date_depart_reel': self.date_depart_reel.isoformat() if self.date_depart_reel else None,
            'heure_depart_reel': self.heure_depart_reel.isoformat() if self.heure_depart_reel else None,
            'date_arrivee_reelle': self.date_arrivee_reelle.isoformat() if self.date_arrivee_reelle else None,
            'heure_arrivee_reelle': self.heure_arrivee_reelle.isoformat() if self.heure_arrivee_reelle else None,
            'km_debut': float(self.km_debut) if self.km_debut else None,
            'km_fin': float(self.km_fin) if self.km_fin else None,
            'id_chauffeur': self.id_chauffeur,
            'chauffeur_nom': self.chauffeur.nom if self.chauffeur else 'N/A',
            'id_vehicule': self.id_vehicule,
            'vehicule_immat': self.vehicule.immatriculation_ve if self.vehicule else 'N/A'
        }