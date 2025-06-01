# app/models/province.py
from app import db

class Province(db.Model): # <-- Changé de Daira à Province
    __tablename__ = 'province' # <-- Changé de 'daira' à 'province'

    id_province = db.Column(db.Integer, primary_key=True) # <-- Changé de id_daira à id_province
    nom_province = db.Column(db.String(100), nullable=False) # <-- Changé de nom_daira à nom_province

    # Clé étrangère vers Ville
    id_ville = db.Column(db.Integer, db.ForeignKey('ville.id_ville'), nullable=False)

    def __repr__(self):
        return f"<Province {self.nom_province}>" # <-- Changé de nom_daira

    def to_dict(self):
        return {
            'id_province': self.id_province, # <-- Changé de id_daira
            'nom_province': self.nom_province, # <-- Changé de nom_daira
            'id_ville': self.id_ville,
            'ville_nom': self.ville.nom_ville if self.ville else None
        }