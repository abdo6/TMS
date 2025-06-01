# app/models/chauffeur_externe.py
from app import db

class ChauffeurExterne(db.Model):
    __tablename__ = 'chauffeur_externe'

    id_chauffeur_externe = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    numero_telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    categorie_permis = db.Column(db.String(50)) # Catégorie du permis de conduire

    # Clé étrangère vers SousTraitant
    id_sous_traitant = db.Column(db.Integer, db.ForeignKey('sous_traitant.id_sous_traitant'), nullable=False)

    # Relation pour accéder au sous-traitant
    sous_traitant = db.relationship('SousTraitant', backref='chauffeurs_externes', lazy=True)

    def __repr__(self):
        return f"<ChauffeurExterne {self.nom} {self.prenom} (Sous-traitant: {self.sous_traitant.nom_entreprise if self.sous_traitant else 'N/A'})>"

    def to_dict(self):
        return {
            'id_chauffeur_externe': self.id_chauffeur_externe,
            'nom': self.nom,
            'prenom': self.prenom,
            'numero_telephone': self.numero_telephone,
            'email': self.email,
            'categorie_permis': self.categorie_permis,
            'id_sous_traitant': self.id_sous_traitant,
            'sous_traitant_nom': self.sous_traitant.nom_entreprise if self.sous_traitant else None
        }