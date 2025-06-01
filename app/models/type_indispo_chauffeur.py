# app/models/type_indispo_chauffeur.py
from app import db

class TypeIndispoChauffeur(db.Model):
    __tablename__ = 'type_indispo_chauffeur'

    id_type_indispo_chauffeur = db.Column(db.Integer, primary_key=True)
    nom_type = db.Column(db.String(100), unique=True, nullable=False) # Ex: Congé Annuel, Maladie, Accident, Formation

    def __repr__(self):
        return f"<TypeIndispoChauffeur {self.nom_type}>"

    def to_dict(self):
        return {
            'id_type_indispo_chauffeur': self.id_type_indispo_chauffeur,
            'nom_type': self.nom_type
        }