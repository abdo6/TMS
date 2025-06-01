# app/models/type_indispo_vehicule.py
from app import db

class TypeIndispoVehicule(db.Model):
    __tablename__ = 'type_indispo_vehicule'

    id_type_indispo_vehicule = db.Column(db.Integer, primary_key=True)
    nom_type = db.Column(db.String(100), unique=True, nullable=False) # Ex: Panne, Entretien, Contrôle Technique, Réparation

    def __repr__(self):
        return f"<TypeIndispoVehicule {self.nom_type}>"

    def to_dict(self):
        return {
            'id_type_indispo_vehicule': self.id_type_indispo_vehicule,
            'nom_type': self.nom_type
        }