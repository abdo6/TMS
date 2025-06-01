# app/models/trajet.py
from app import db

class Trajet(db.Model):
    __tablename__ = 'trajet'

    id_trajet = db.Column(db.Integer, primary_key=True)
    distance_km = db.Column(db.Numeric(10, 2)) # Distance en kilomètres
    duree_heures = db.Column(db.Numeric(10, 2)) # Durée en heures
    description = db.Column(db.String(255)) # Description du trajet (ex: "Livraison de Casablanca à Rabat")

    # Clé étrangère vers Destination (la destination finale du trajet, ou le point d'arrivée)
    # Votre diagramme montre une relation entre Trajet et Destination.
    # On pourrait aussi avoir un id_destination_depart et un id_destination_arrivee
    # Pour l'instant, simplifions en supposant que `id_destination` est la destination finale.
    id_destination = db.Column(db.Integer, db.ForeignKey('destination.id_destination'), nullable=False)

    # Relation pour accéder à la destination
    destination = db.relationship('Destination', backref='trajets', lazy=True)

    # Note: Dans un système plus complexe, un trajet pourrait être une séquence de destinations
    # ou une route calculée par un moteur de routage. Ici, c'est une entité simple liée à une destination.

    def __repr__(self):
        return f"<Trajet {self.id_trajet} vers {self.destination.description if self.destination else 'N/A'}>"

    def to_dict(self):
        return {
            'id_trajet': self.id_trajet,
            'distance_km': float(self.distance_km) if self.distance_km else None,
            'duree_heures': float(self.duree_heures) if self.duree_heures else None,
            'description': self.description,
            'id_destination': self.id_destination,
            'destination_description': self.destination.description if self.destination else None
        }