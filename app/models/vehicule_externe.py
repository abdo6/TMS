# app/models/vehicule_externe.py
from app import db

class VehiculeExterne(db.Model):
    __tablename__ = 'vehicule_externe'

    id_vehicule_externe = db.Column(db.Integer, primary_key=True)
    immatriculation_ve = db.Column(db.String(50), unique=True, nullable=False)
    categorie = db.Column(db.String(100)) # Ex: Camion, Utilitaire, etc.
    description = db.Column(db.String(255)) # Autres détails spécifiques au véhicule

    # Clé étrangère vers SousTraitant
    id_sous_traitant = db.Column(db.Integer, db.ForeignKey('sous_traitant.id_sous_traitant'), nullable=False)

    # Relation pour accéder au sous-traitant
    sous_traitant = db.relationship('SousTraitant', backref='vehicules_externes', lazy=True)

    def __repr__(self):
        return f"<VehiculeExterne {self.immatriculation_ve} (Sous-traitant: {self.sous_traitant.nom_entreprise if self.sous_traitant else 'N/A'})>"

    def to_dict(self):
        return {
            'id_vehicule_externe': self.id_vehicule_externe,
            'immatriculation_ve': self.immatriculation_ve,
            'categorie': self.categorie,
            'description': self.description,
            'id_sous_traitant': self.id_sous_traitant,
            'sous_traitant_nom': self.sous_traitant.nom_entreprise if self.sous_traitant else None
        }