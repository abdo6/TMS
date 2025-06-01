# app/models/client_initial.py
from app import db

class ClientInitial(db.Model):
    __tablename__ = 'client_initial'

    id_client_initial = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    adresse = db.Column(db.String(255))
    numero_telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True) # Généralement unique pour un client principal

    # Relations (définies sur l'autre côté pour éviter les dépendances circulaires)
    # entetes_commandes = db.relationship('EnteteCommande', backref='client_initial', lazy=True)
    # services_clients = db.relationship('ServiceClient', backref='client_initial', lazy=True)

    def __repr__(self):
        return f"<ClientInitial {self.nom} {self.prenom or ''}>"

    def to_dict(self):
        return {
            'id_client_initial': self.id_client_initial,
            'nom': self.nom,
            'prenom': self.prenom,
            'adresse': self.adresse,
            'numero_telephone': self.numero_telephone,
            'email': self.email
        }