# app/models/indispo_vehicule.py
from app import db
from datetime import datetime

class IndisponibiliteVehicule(db.Model):
    __tablename__ = 'indisponibilite_vehicule'

    id_indispo_vehicule = db.Column(db.Integer, primary_key=True)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255)) # Raison spécifique de l'indisponibilité

    # Clés étrangères
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicule.id_vehicule'), nullable=False)
    id_type_indispo_vehicule = db.Column(db.Integer, db.ForeignKey('type_indispo_vehicule.id_type_indispo_vehicule'), nullable=False)

    # Relations
    vehicule = db.relationship('Vehicule', backref='indisponibilites', lazy=True)
    type_indispo_vehicule = db.relationship('TypeIndispoVehicule', backref='indisponibilites_vehicule', lazy=True)

    def __repr__(self):
        return f"<IndispoVehicule {self.vehicule.immatriculation_ve if self.vehicule else 'N/A'} du {self.date_debut} au {self.date_fin}>"

    def to_dict(self):
        return {
            'id_indispo_vehicule': self.id_indispo_vehicule,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat(),
            'description': self.description,
            'id_vehicule': self.id_vehicule,
            'vehicule_immatriculation': self.vehicule.immatriculation_ve if self.vehicule else 'N/A',
            'id_type_indispo_vehicule': self.id_type_indispo_vehicule,
            'type_indispo_nom': self.type_indispo_vehicule.nom_type if self.type_indispo_vehicule else 'N/A'
        }