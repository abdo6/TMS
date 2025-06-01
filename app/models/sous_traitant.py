# app/models/sous_traitant.py
from app import db

class SousTraitant(db.Model):
    __tablename__ = 'sous_traitant'

    id_sous_traitant = db.Column(db.Integer, primary_key=True)
    nom_entreprise = db.Column(db.String(255), unique=True, nullable=False)
    contact_personne = db.Column(db.String(100))
    numero_telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    adresse = db.Column(db.String(255))

    # Relations (si nécessaire, pour des véhicules ou chauffeurs externes par exemple)
    # vehicules_externes = db.relationship('VehiculeExterne', backref='sous_traitant', lazy=True)
    # chauffeurs_externes = db.relationship('ChauffeurExterne', backref='sous_traitant', lazy=True)

    def __repr__(self):
        return f"<SousTraitant {self.nom_entreprise}>"

    def to_dict(self):
        return {
            'id_sous_traitant': self.id_sous_traitant,
            'nom_entreprise': self.nom_entreprise,
            'contact_personne': self.contact_personne,
            'numero_telephone': self.numero_telephone,
            'email': self.email,
            'adresse': self.adresse
        }