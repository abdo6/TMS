# app/models/ville.py
from app import db

class Ville(db.Model):
    __tablename__ = 'ville'

    id_ville = db.Column(db.Integer, primary_key=True)
    code_ville = db.Column(db.String(50), unique=True, nullable=False)
    nom_ville = db.Column(db.String(100), nullable=False)

    # Modifier cette ligne pour spécifier le chemin complet du modèle Province
    provinces = db.relationship('app.models.province.Province', backref='ville', lazy=True) # <-- MODIFIÉ

    def __repr__(self):
        return f"<Ville {self.nom_ville}>"

    def to_dict(self):
        return {
            'id_ville': self.id_ville,
            'code_ville': self.code_ville,
            'nom_ville': self.nom_ville
        }