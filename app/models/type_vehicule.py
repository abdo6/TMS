# app/models/type_vehicule.py
from app import db

class TypeVehicule(db.Model):
    __tablename__ = 'type_vehicule'

    id_type_vehicule = db.Column(db.Integer, primary_key=True)
    nom_type = db.Column(db.String(100), unique=True, nullable=False) # Ex: Camionnette, Poids Lourd, etc.

    # Relations (définies sur l'autre côté pour éviter les dépendances circulaires)
    # details_commandes = db.relationship('DetailCommande', backref='type_vehicule', lazy=True)
    # vehicules = db.relationship('Vehicule', backref='type_vehicule', lazy=True) # Si vous reliez Vehicule à TypeVehicule

    def __repr__(self):
        return f"<TypeVehicule {self.nom_type}>"

    def to_dict(self):
        return {
            'id_type_vehicule': self.id_type_vehicule,
            'nom_type': self.nom_type
        }