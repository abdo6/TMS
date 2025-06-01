# app/models/date_tr.py
from app import db
from datetime import datetime

class DateTR(db.Model):
    __tablename__ = 'date_tr'

    id_date_tr = db.Column(db.Integer, primary_key=True)
    date_debut = db.Column(db.Date, nullable=False) # Date de début de validité (ex: date du contrôle technique)
    date_fin = db.Column(db.Date, nullable=False) # Date de fin de validité (ex: date d'expiration du contrôle technique)
    description = db.Column(db.String(255)) # Description du document/validité (ex: "Contrôle technique", "Assurance")

    # Clé étrangère vers Vehicule (puisque le diagramme pointe vers Vehicule et non un Tracteur/Remorque spécifique)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicule.id_vehicule'), nullable=False)

    # Relation pour accéder au véhicule
    vehicule = db.relationship('Vehicule', backref='dates_tr', lazy=True)

    def __repr__(self):
        return f"<DateTR Vehicule {self.vehicule.immatriculation_ve if self.vehicule else 'N/A'} du {self.date_debut} au {self.date_fin}>"

    def to_dict(self):
        return {
            'id_date_tr': self.id_date_tr,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat(),
            'description': self.description,
            'id_vehicule': self.id_vehicule,
            'vehicule_immatriculation': self.vehicule.immatriculation_ve if self.vehicule else 'N/A'
        }