# app/models/vehicule.py
from app import db # Importe l'instance 'db' depuis votre application principale

class Vehicule(db.Model):
    __tablename__ = 'vehicule' # Nom de la table dans la base de données

    id_vehicule = db.Column(db.Integer, primary_key=True)
    immatriculation_ve = db.Column(db.String(50), unique=True, nullable=False)
    categorie = db.Column(db.String(100)) # Ex: Camion, Utilitaire, etc.

    # Ajoutez d'autres attributs si nécessaire selon votre diagramme de classes
    # Exemple:
    # id_vehicule_type = db.Column(db.Integer, db.ForeignKey('type_vehicule.id_vehicule_type'))
    # id_sous_traitant = db.Column(db.Integer, db.ForeignKey('sous_traitant.id_sous_traitant'))
    # type_vehicule = db.relationship('TypeVehicule', backref='vehicules')
    # sous_traitant = db.relationship('SousTraitant', backref='vehicules')

    def __repr__(self):
        return f"<Vehicule {self.immatriculation_ve} ({self.categorie})>"

    def to_dict(self):
        return {
            'id_vehicule': self.id_vehicule,
            'immatriculation_ve': self.immatriculation_ve,
            'categorie': self.categorie
            # Ajoutez d'autres champs ici
        }