# app/models/chauffeur.py
from app import db

class Chauffeur(db.Model):
    __tablename__ = 'chauffeur'

    id_chauffeur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(255))
    numero_telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    categorie_ch = db.Column(db.String(50))

    # Relation vers les missions (si ce n'est pas déjà fait par un backref ailleurs)
    # missions = db.relationship('Mission', backref='chauffeur', lazy=True) # Déjà géré par Mission.chauffeur

    # NOUVELLE PROPRIÉTÉ pour le nom complet
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}" # Ou self.nom + " " + self.prenom, selon votre préférence

    def __repr__(self):
        return f"<Chauffeur {self.nom_complet}>" # Utilisation de la nouvelle propriété

    def to_dict(self):
        return {
            'id_chauffeur': self.id_chauffeur,
            'nom': self.nom,
            'prenom': self.prenom,
            'nom_complet': self.nom_complet, # Ajouter au to_dict
            'adresse': self.adresse,
            'numero_telephone': self.numero_telephone,
            'email': self.email,
            'categorie_ch': self.categorie_ch
        }