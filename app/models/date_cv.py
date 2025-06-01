# app/models/date_cv.py
from app import db
from datetime import datetime

class DateCV(db.Model):
    __tablename__ = 'date_cv'

    id_date_cv = db.Column(db.Integer, primary_key=True)
    date_debut = db.Column(db.Date, nullable=False) # Date de début de validité (ex: date d'examen médical)
    date_fin = db.Column(db.Date, nullable=False) # Date de fin de validité (ex: date d'expiration du permis/examen médical)
    description = db.Column(db.String(255)) # Description du document/validité (ex: "Permis de conduire", "Visite médicale")

    # Clé étrangère vers Chauffeur
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeur.id_chauffeur'), nullable=False)

    # Relation pour accéder au chauffeur
    chauffeur = db.relationship('Chauffeur', backref='dates_cv', lazy=True)

    def __repr__(self):
        return f"<DateCV Chauffeur {self.chauffeur.nom if self.chauffeur else 'N/A'} du {self.date_debut} au {self.date_fin}>"

    def to_dict(self):
        return {
            'id_date_cv': self.id_date_cv,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat(),
            'description': self.description,
            'id_chauffeur': self.id_chauffeur,
            'chauffeur_nom_complet': f"{self.chauffeur.nom} {self.chauffeur.prenom}" if self.chauffeur else 'N/A'
        }