# app/models/indispo_chauffeur.py
from app import db
from datetime import datetime

class IndisponibiliteChauffeur(db.Model):
    __tablename__ = 'indisponibilite_chauffeur'

    id_indispo_chauffeur = db.Column(db.Integer, primary_key=True)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255)) # Raison spécifique de l'indisponibilité

    # Clés étrangères
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeur.id_chauffeur'), nullable=False)
    id_type_indispo_chauffeur = db.Column(db.Integer, db.ForeignKey('type_indispo_chauffeur.id_type_indispo_chauffeur'), nullable=False)

    # Relations
    chauffeur = db.relationship('Chauffeur', backref='indisponibilites', lazy=True)
    type_indispo_chauffeur = db.relationship('TypeIndispoChauffeur', backref='indisponibilites_chauffeur', lazy=True)

    def __repr__(self):
        return f"<IndispoChauffeur {self.chauffeur.nom if self.chauffeur else 'N/A'} du {self.date_debut} au {self.date_fin}>"

    def to_dict(self):
        return {
            'id_indispo_chauffeur': self.id_indispo_chauffeur,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat(),
            'description': self.description,
            'id_chauffeur': self.id_chauffeur,
            'chauffeur_nom_complet': f"{self.chauffeur.nom} {self.chauffeur.prenom}" if self.chauffeur else 'N/A',
            'id_type_indispo_chauffeur': self.id_type_indispo_chauffeur,
            'type_indispo_nom': self.type_indispo_chauffeur.nom_type if self.type_indispo_chauffeur else 'N/A'
        }