# app/models/localisation.py
from app import db
from datetime import datetime

class Localisation(db.Model):
    __tablename__ = 'localisation'

    id_localisation = db.Column(db.Integer, primary_key=True)
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeur.id_chauffeur'), nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=False) # Précision pour les coordonnées géographiques
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Quand la position a été enregistrée

    # Relation avec le modèle Chauffeur
    chauffeur = db.relationship('Chauffeur', backref='localisations', lazy=True)

    def __repr__(self):
        return f"<Localisation {self.id_localisation} | Chauffeur: {self.id_chauffeur} | Lat: {self.latitude}, Long: {self.longitude} at {self.timestamp}>"

    def to_dict(self):
        return {
            'id_localisation': self.id_localisation,
            'id_chauffeur': self.id_chauffeur,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'timestamp': self.timestamp.isoformat(),
            'chauffeur_nom': self.chauffeur.nom_complet if self.chauffeur else 'N/A'
        }